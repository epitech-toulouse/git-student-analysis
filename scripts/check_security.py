#!/usr/bin/env python3
"""
Vérification de sécurité des commits : détecte les fichiers compromettants.

Détecte:
- Fichiers de secrets (.env, .env.local, .env.*.local, secrets.yml, etc.)
- Clés privées (RSA, DSA, EC, PGP)
- Tokens d'authentification (AWS, GitHub, API keys, etc.)
- URLs sensibles (credentials en plaintext)
- Patterns de vulnérabilités communes
- Fichiers de configuration sensibles

Usage: python check_security.py commits_raw.tsv [--strict]
"""

import sys
import re
import json
from pathlib import Path
from collections import defaultdict

# Patterns sensibles à détecter
SENSITIVE_PATTERNS = {
    "env_files": {
        "pattern": r"^\.env(\.(local|development|staging|production|test|example))?$",
        "severity": "CRITICAL",
        "description": "Fichier de variables d'environnement",
    },
    "secret_files": {
        "pattern": r"(secrets?\.yml|secrets?\.json|secrets?\.yaml|\.secrets|\.aws/credentials|\.aws/config|\.ssh/|\.gnupg/)",
        "severity": "CRITICAL",
        "description": "Fichier de secrets ou de configuration sensible",
    },
    "private_keys": {
        "pattern": r"(BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY|-----BEGIN PRIVATE KEY|\.pem$|\.key$|id_rsa|id_dsa|id_ecdsa)",
        "severity": "CRITICAL",
        "description": "Clé privée détectée",
    },
    "api_keys": {
        "pattern": r"(api[_-]?key|apikey|api[_-]?secret|secret[_-]?key|sk_live_|sk_test_|rk_live_|rk_test_|pk_live_|pk_test_)",
        "severity": "HIGH",
        "description": "Clé API ou token d'authentification",
    },
    "aws_credentials": {
        "pattern": r"(AKIA[0-9A-Z]{16}|aws_access_key_id|aws_secret_access_key|aws_session_token)",
        "severity": "CRITICAL",
        "description": "Identifiant AWS détecté",
    },
    "github_token": {
        "pattern": r"(ghp_[A-Za-z0-9_]{36,255}|gho_[A-Za-z0-9_]{36,255}|ghu_[A-Za-z0-9_]{36,255}|github[_-]?token)",
        "severity": "CRITICAL",
        "description": "Token GitHub détecté",
    },
    "database_urls": {
        "pattern": r"(mongodb\+srv://|postgres://|mysql://|user:password@|mongodb://.*:.*@|sql[_-]?password)",
        "severity": "CRITICAL",
        "description": "URL de base de données avec identifiants",
    },
    "jwt_tokens": {
        "pattern": r"eyJhbGciOiJ|jwt[_-]?token|authorization:\s*bearer",
        "severity": "HIGH",
        "description": "Token JWT détecté",
    },
    "private_urls": {
        "pattern": r"(https?://[^:]*:[^@]*@|//.*:.*@|user=.*&password=|passwd=|pwd=)",
        "severity": "HIGH",
        "description": "URL avec identifiants en plaintext",
    },
    "firebase_config": {
        "pattern": r"(firebase[_-]?key|firebase[_-]?url|apiKey.*firebase|databaseURL.*firebase|storageBucket)",
        "severity": "HIGH",
        "description": "Configuration Firebase détectée",
    },
    "oauth_tokens": {
        "pattern": r"(refresh[_-]?token|access[_-]?token|oauth[_-]?token|bearer\s+[A-Za-z0-9._\-]+)",
        "severity": "HIGH",
        "description": "Token OAuth/Bearer détecté",
    },
    "stripe_keys": {
        "pattern": r"(sk_live_|sk_test_|rk_live_|rk_test_|pk_live_|pk_test_)",
        "severity": "CRITICAL",
        "description": "Clé Stripe détectée",
    },
    "ssh_config": {
        "pattern": r"(\.ssh/config|\.ssh/authorized_keys|\.ssh/known_hosts|Host\s+\*|IdentityFile\s+~)",
        "severity": "HIGH",
        "description": "Fichier de configuration SSH sensible",
    },
    "docker_secrets": {
        "pattern": r"(docker[_-]?password|registry[_-]?auth|docker[_-]?config|\.docker/config\.json)",
        "severity": "HIGH",
        "description": "Secrets Docker détectés",
    },
}


def check_file_path(filepath: str) -> list:
    """Vérifie les patterns dans le chemin du fichier."""
    issues = []
    filepath_lower = filepath.lower()

    for check_id, check in SENSITIVE_PATTERNS.items():
        if re.search(check["pattern"], filepath_lower, re.IGNORECASE):
            issues.append(
                {
                    "type": check_id,
                    "severity": check["severity"],
                    "description": check["description"],
                    "location": "filename",
                }
            )

    return issues


def check_content(filename: str, content: str) -> list:
    """Vérifie les patterns dans le contenu du fichier (résumé)."""
    issues = []
    
    # Ne check pas les fichiers binaires ou trop volumineux
    try:
        if len(content) > 100000 or "\x00" in content[:1000]:
            return issues
    except:
        return issues

    content_lower = content.lower()

    for check_id, check in SENSITIVE_PATTERNS.items():
        if re.search(check["pattern"], content_lower, re.IGNORECASE):
            # Évite les doubles: api_keys est souvent dans le chemin
            if check_id == "api_keys" and "filename" not in str(issues):
                issues.append(
                    {
                        "type": check_id,
                        "severity": check["severity"],
                        "description": check["description"],
                        "location": "content",
                    }
                )

    return issues


def analyze_commits(commits_file: str, strict: bool = False) -> dict:
    """Analyse les commits pour détecter les fichiers compromettants."""
    security_issues = defaultdict(list)
    commits_by_author = defaultdict(list)

    try:
        with open(commits_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split("\t")
                if len(parts) < 6:
                    continue

                commit_hash, author, email, date, message, files = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]

                # Parse les fichiers (séparés par |)
                file_list = [f.strip() for f in files.split("|") if f.strip()]

                for filepath in file_list:
                    # Vérification du chemin
                    path_issues = check_file_path(filepath)
                    if path_issues:
                        for issue in path_issues:
                            security_issues[author].append(
                                {
                                    "commit": commit_hash,
                                    "date": date,
                                    "file": filepath,
                                    "issue": issue,
                                }
                            )

                    # Note: l'analyse de contenu nécessiterait d'accéder aux vrais diffs
                    # qui ne sont pas disponibles dans ce format TSV simplifié
                    # Les patterns de contenu peuvent être ajoutés si les diffs sont fournis

                commits_by_author[author].append(
                    {
                        "commit": commit_hash,
                        "date": date,
                        "message": message,
                        "files": file_list,
                        "has_issues": len(path_issues) > 0,
                    }
                )

    except FileNotFoundError:
        print(f"Error: File {commits_file} not found", file=sys.stderr)
        sys.exit(1)

    return {
        "security_issues": dict(security_issues),
        "commits_by_author": dict(commits_by_author),
    }


def format_report(analysis: dict) -> str:
    """Génère un rapport lisible des problèmes de sécurité."""
    issues = analysis["security_issues"]

    if not issues:
        return "✅ Aucun problème de sécurité détecté.\n"

    report = "⚠️  PROBLÈMES DE SÉCURITÉ DÉTECTÉS\n"
    report += "=" * 60 + "\n\n"

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    for author in sorted(issues.keys()):
        author_issues = issues[author]
        # Tri par sévérité
        author_issues.sort(
            key=lambda x: severity_order.get(x["issue"]["severity"], 999)
        )

        report += f"\n👤 {author}\n"
        report += "-" * 40 + "\n"

        for item in author_issues:
            severity = item["issue"]["severity"]
            emoji = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡"
            report += f"  {emoji} [{severity}] {item['issue']['description']}\n"
            report += f"      Fichier: {item['file']}\n"
            report += f"      Commit: {item['commit'][:8]}\n"
            report += f"      Date: {item['date']}\n\n"

    return report


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <commits_tsv> [--strict]", file=sys.stderr)
        sys.exit(1)

    commits_file = sys.argv[1]
    strict = "--strict" in sys.argv

    analysis = analyze_commits(commits_file, strict)

    # Affiche le rapport
    report = format_report(analysis)
    print(report)

    # Retourne les données en JSON sur stderr pour intégration
    print(json.dumps(analysis, indent=2), file=sys.stderr)

    # Retourne un code d'erreur si des problèmes critiques sont trouvés
    critical_count = sum(
        1 for author_issues in analysis["security_issues"].values()
        for issue in author_issues
        if issue["issue"]["severity"] == "CRITICAL"
    )

    sys.exit(1 if critical_count > 0 else 0)


if __name__ == "__main__":
    main()
