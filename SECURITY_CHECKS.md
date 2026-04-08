# 🔒 Vérification de Sécurité - Documentation

## Vue d'ensemble

Le module de vérification de sécurité (`check_security.py`) analyse les commits Git pour détecter les fichiers et contenus compromettants qui pourraient exposer des secrets, identifiants ou données sensibles.

## ⚠️ Problèmes Détectés

### 🔴 CRITICAL (Critique)

Ces problèmes représentent une faille de sécurité grave et **doivent être corrigés immédiatement** :

#### 1. **Fichiers de variables d'environnement**
- Fichiers `.env`, `.env.local`, `.env.development`, etc.
- **Risque** : Contiennent généralement des tokens, clés API, identifiants de base de données
- **Action** : Ne jamais commiter les fichiers `.env` réels, utiliser `.env.example` à la place

#### 2. **Clés privées**
- Fichiers RSA, DSA, EC, OpenSSH, PGP
- Extensions : `.pem`, `.key`, `id_rsa`, `id_dsa`, `id_ecdsa`
- **Risque** : Accès non autorisé aux systèmes distants (SSH, GPG)
- **Action** : Régénérer immédiatement les clés compromises

#### 3. **Identifiants AWS**
- Patterns : `AKIA[0-9A-Z]{16}`, `aws_access_key_id`, `aws_secret_access_key`
- **Risque** : Accès aux ressources AWS (EC2, S3, bases de données)
- **Action** : Révoquer les clés via AWS IAM immédiatement

#### 4. **Tokens GitHub**
- Patterns : `ghp_*`, `gho_*`, `ghu_*`
- **Risque** : Accès au compte GitHub, push de code malveillant
- **Action** : Révoquer le token dans les paramètres GitHub

#### 5. **URLs de bases de données avec identifiants**
- Patterns : `mongodb+srv://user:password@`, `postgres://`, `mysql://`
- **Risque** : Accès direct à la base de données de production
- **Action** : Changer le mot de passe, nettoyer l'historique Git

#### 6. **Clés Stripe**
- Patterns : `sk_live_*`, `sk_test_*`, `rk_live_*`, `pk_live_*`
- **Risque** : Accès aux paiements, fraude
- **Action** : Révoquer et générer nouvelles clés via le dashboard Stripe

### 🟠 HIGH (Élevé)

Ces problèmes représentent des risques de sécurité importants :

#### 1. **Clés et tokens API**
- Patterns : `api_key`, `api_secret`, `secret_key`
- **Risque** : Accès à des services externes (Twilio, SendGrid, etc.)
- **Action** : Révoquer les clés, nettoyer l'historique

#### 2. **Tokens JWT**
- Patterns JWT standards et décodables
- **Risque** : Usurpation d'identité, accès à des comptes utilisateurs
- **Action** : Régénérer les tokens, invalider les anciens

#### 3. **URLs avec identifiants en plaintext**
- Patterns : `https://user:password@host`, `//user:password@`
- **Risque** : Exposition des credentials
- **Action** : Supprimer de l'historique, utiliser des variables d'environnement

#### 4. **Configuration Firebase**
- Patterns : `firebase_key`, `firebase_url`, `apiKey.*firebase`
- **Risque** : Accès à la base de données Firebase
- **Action** : Régénérer les clés, restreindre les règles de sécurité

#### 5. **Tokens OAuth/Bearer**
- Patterns : `refresh_token`, `access_token`, `bearer`
- **Risque** : Usurpation d'identité utilisateur
- **Action** : Révoquer les tokens, implémenter la rotation

#### 6. **Configuration SSH sensible**
- Fichiers : `.ssh/config`, `.ssh/authorized_keys`, `.ssh/known_hosts`
- **Risque** : Information sur l'infrastructure, accès SSH
- **Action** : Ne jamais commiter, utiliser `.ssh/config.example`

#### 7. **Secrets Docker**
- Patterns : `docker_password`, `registry_auth`, `.docker/config.json`
- **Risque** : Accès aux registres privés d'images Docker
- **Action** : Utiliser Docker secrets ou variables d'environnement

## 🛠️ Comment Utiliser

### Utilisation Directe

```bash
python scripts/check_security.py <fichier_commits.tsv>
```

### Exemple de Sortie

```
⚠️  PROBLÈMES DE SÉCURITÉ DÉTECTÉS
============================================================

👤 Alice Martin
----------------------------------------
  🔴 [CRITICAL] Fichier de variables d'environnement
      Fichier: src/.env
      Commit: a1b2c3d4
      Date: 2026-03-15 14:23:00

  🟠 [HIGH] Token GitHub détecté
      Fichier: config.js
      Commit: e5f6g7h8
      Date: 2026-03-16 10:45:00
```

### Mode Strict

```bash
python scripts/check_security.py <fichier_commits.tsv> --strict
```

Mode strict applique des vérifications plus agressives et peut générer plus de faux positifs.

## 🔄 Intégration dans l'Analyse

Le script `check_security.py` peut être intégré :

### 1. **Comme vérification pré-commit**

```bash
# Dans .git/hooks/pre-commit
python scripts/check_security.py /tmp/commits.tsv
if [ $? -eq 1 ]; then
  echo "❌ Problèmes de sécurité détectés, commit annulé"
  exit 1
fi
```

### 2. **Comme étape du rapport pédagogique**

```bash
# Dans le script d'analyse principal
python scripts/check_security.py commits_raw.tsv > security_report.md
```

### 3. **En validation de Pull Request**

Ajouter une étape GitHub Actions :

```yaml
- name: Check for security issues
  run: python scripts/check_security.py commits.tsv
  continue-on-error: true
```

## 📋 Patterns Détectés

### Pattern Matching Details

| Type | Patterns | Exemples |
|------|----------|----------|
| **Fichiers .env** | `.env`, `.env.local`, `.env.*local` | `.env`, `.env.development.local` |
| **Secrets** | `secrets.yml`, `.secrets`, `.aws/credentials` | `secrets.json`, `.gnupg/` |
| **Clés privées** | `BEGIN PRIVATE KEY`, `id_rsa`, `.pem` | RSA/DSA/EC/SSH keys |
| **AWS** | `AKIA...`, `aws_access_key_id` | AWS Access Key IDs |
| **GitHub** | `ghp_*`, `gho_*`, `ghu_*` | GitHub Personal Tokens |
| **JWT** | Tokens JWT standards | `eyJhbGciOiJ...` |
| **URLs DB** | `mongodb://user:pass@`, `postgres://` | URLs avec credentials |
| **Firebase** | `firebase_key`, `apiKey`, `databaseURL` | Config Firebase |
| **Stripe** | `sk_live_*`, `pk_live_*` | Clés Stripe |
| **Docker** | `.docker/config.json`, `docker_password` | Docker credentials |

## 🚫 Limites Connues

1. **Analyse de contenu basique** : Le script détecte les patterns dans les noms de fichiers. L'analyse profonde du contenu nécessite l'accès aux diffs Git complets.

2. **Faux positifs possibles** : Certains patterns génériques peuvent créer de faux positifs (ex: `password=` dans un commentaire)

3. **Patterns de regex** : Les patterns ne couvrent pas **tous** les types de secrets (ex: secrets personnalisés)

4. **Fichiers binaires** : Les fichiers binaires ne sont pas analysés pour éviter les faux positifs

## 🔐 Bonnes Pratiques pour Étudiants

### 1. ✅ Avant de Commiter

```bash
# Vérifier qu'aucun .env réel n'est commité
git status | grep -E "\.env|secrets|\.key"

# Ajouter au .gitignore
echo ".env*" >> .gitignore
echo "*.key" >> .gitignore
echo "secrets/" >> .gitignore
```

### 2. ✅ Créer un Fichier d'Exemple

```bash
# Créer .env.example avec la structure
cp .env .env.example
# Puis nettoyer les valeurs sensibles dans .env.example
# Commiter .env.example, PAS .env
```

### 3. ✅ Variables d'Environnement

```javascript
// ✅ BON
const apiKey = process.env.API_KEY;

// ❌ MAUVAIS
const apiKey = "sk_live_abc123...";
```

### 4. ✅ Gérer les Secrets en Production

```bash
# Utiliser un gestionnaire de secrets
# - HashiCorp Vault
# - AWS Secrets Manager
# - GitHub Secrets (pour CI/CD)
# - Environment variables du serveur
```

### 5. ✅ Si un Secret a été Commité

```bash
# 1. IMMÉDIATEMENT: changer le secret
# 2. Nettoyer l'historique Git avec BFG Repo-Cleaner
# 3. Forcer le push
# 4. Notifier l'équipe
```

## 📊 Rapport de Sécurité dans l'Excel

Le fichier Excel généré peut inclure une colonne **⚠️ Security Flags** :

| Étudiant | Commits | Risques Détectés |
|----------|---------|------------------|
| Alice    | 51      | 2 problèmes CRITICAL, 1 HIGH |
| Bob      | 42      | ✅ Aucun |

## 🤝 Contribution

Pour améliorer la détection :

1. Proposer de nouveaux patterns dans une issue
2. Contribuer des améliorations au regex
3. Partager des faux positifs/négatifs rencontrés

## 📚 Ressources Externes

- [OWASP - Secrets Management](https://owasp.org/www-community/Sensitive_Data_Exposure)
- [GitHub - Security Best Practices](https://docs.github.com/en/code-security)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) - Nettoyer l'historique Git
- [git-secrets](https://github.com/awslabs/git-secrets) - Pré-commit hook AWS

---

**Sécurité d'abord ! 🔒**
