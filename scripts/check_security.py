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
        "pattern": r"(api[_-]?key|apikey|api[_-]?secret|secret[_-]?key)",
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

# Patterns supplémentaires activés uniquement en mode --strict
STRICT_PATTERNS = {
    "password_in_code": {
        "pattern": r"(password\s*=\s*['\"][^'\"]{3,}['\"]|passwd\s*=\s*['\"][^'\"]{3,}['\"])",
        "severity": "HIGH",
        "description": "Mot de passe en clair dans le code",
    },
    "ip_addresses": {
        "pattern": r"\b(?:192\.168|10\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01]))\.\d+\b",
        "severity": "HIGH",
        "description": "Adresse IP privée exposée",
    },
    "generic_token": {
        "pattern": r"(token\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]|secret\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"])",
        "severity": "HIGH",
        "description": "Token ou secret générique potentiel",
    },
}


def check_file_path(filepath: str, strict: bool = False) -> list:
    """Vérifie les patterns dans le chemin du fichier."""
    issues = []
    filepath_lower = filepath.lower()
    # Le nom de fichier seul (sans répertoire), pour les patterns avec ancres ^ $
    filename_lower = Path(filepath).name.lower()

    patterns = dict(SENSITIVE_PATTERNS)
    if strict:
        patterns.update(STRICT_PATTERNS)

    for check_id, check in patterns.items():
        # env_files utilise des ancres ^ et $ → matcher sur le nom de fichier seul
        target = filename_lower if check_id == "env_files" else filepath_lower
        if re.search(check["pattern"], target, re.IGNORECASE):
            severity = check["severity"]
            # En mode strict, les HIGH deviennent CRITICAL
            if strict and severity == "HIGH":
                severity = "CRITICAL"
            issues.append(
                {
                    "type": check_id,
                    "severity": severity,
                    "description": check["description"],
                    "location": "filename",
                }
            )

    return issues


def check_content(filename: str, content: str, already_found: set = None, strict: bool = False) -> list:
    """Vérifie les patterns dans le contenu d'un texte (message de commit ou diff).

    already_found: ensemble de check_id déjà détectés via check_file_path pour éviter les doublons.
    """
    issues = []
    if already_found is None:
        already_found = set()

    # Ne check pas les fichiers binaires ou trop volumineux
    try:
        if len(content) > 100000 or "\x00" in content[:1000]:
            return issues
    except Exception:
        return issues

    content_lower = content.lower()

    patterns = dict(SENSITIVE_PATTERNS)
    if strict:
        patterns.update(STRICT_PATTERNS)

    for check_id, check in patterns.items():
        if check_id in already_found:
            continue
        if re.search(check["pattern"], content_lower, re.IGNORECASE):
            severity = check["severity"]
            if strict and severity == "HIGH":
                severity = "CRITICAL"
            issues.append(
                {
                    "type": check_id,
                    "severity": severity,
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

                commit_has_issues = False
                found_types: set = set()
                for filepath in file_list:
                    path_issues = check_file_path(filepath, strict=strict)
                    if path_issues:
                        commit_has_issues = True
                        for issue in path_issues:
                            found_types.add(issue["type"])
                            security_issues[author].append(
                                {
                                    "commit": commit_hash,
                                    "date": date,
                                    "file": filepath,
                                    "issue": issue,
                                }
                            )

                # Analyse du message de commit pour détecter des secrets exposés
                message_issues = check_content("commit_message", message, already_found=found_types, strict=strict)
                if message_issues:
                    commit_has_issues = True
                    for issue in message_issues:
                        security_issues[author].append(
                            {
                                "commit": commit_hash,
                                "date": date,
                                "file": "(commit message)",
                                "issue": issue,
                            }
                        )

                commits_by_author[author].append(
                    {
                        "commit": commit_hash,
                        "date": date,
                        "message": message,
                        "files": file_list,
                        "has_issues": commit_has_issues,
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
        print(f"Usage: {sys.argv[0]} <commits_tsv> [--strict] [--output <file.json>]", file=sys.stderr)
        sys.exit(1)

    commits_file = sys.argv[1]
    strict = "--strict" in sys.argv

    output_file = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
        else:
            print("Error: --output requires a file path argument", file=sys.stderr)
            sys.exit(1)

    analysis = analyze_commits(commits_file, strict)

    # Affiche le rapport lisible sur stdout
    report = format_report(analysis)
    print(report)

    # Exporte les données JSON dans un fichier si --output est spécifié
    if output_file:
        with open(output_file, "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"📄 Rapport JSON exporté : {output_file}", file=sys.stderr)

    # Retourne un code d'erreur si des problèmes critiques sont trouvés
    critical_count = sum(
        1 for author_issues in analysis["security_issues"].values()
        for issue in author_issues
        if issue["issue"]["severity"] == "CRITICAL"
    )

    sys.exit(1 if critical_count > 0 else 0)


if __name__ == "__main__":
    main()
