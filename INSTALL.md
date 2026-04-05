# Installation du Skill git-student-analysis

## 📦 Prérequis

- GitHub Copilot CLI installé et configuré
- Python 3.7+ (déjà sur macOS/Linux)
- Git 2.0+
- Bash

## 🚀 Installation Rapide

### Option 1 : Installation Globale (Recommandé)

```bash
# Copier le skill dans le dossier global
cp -r git-student-analysis ~/.copilot/skills/git-student-analysis

# Rendre les scripts exécutables
chmod +x ~/.copilot/skills/git-student-analysis/scripts/*.sh
```

Le skill sera accessible depuis **n'importe quel dossier** dans votre terminal.

### Option 2 : Installation par Projet

```bash
# Depuis la racine de votre projet
mkdir -p .github/skills
cp -r git-student-analysis .github/skills/git-student-analysis
chmod +x .github/skills/git-student-analysis/scripts/*.sh
```

Le skill sera accessible uniquement pour **ce projet spécifique**.

### Option 3 : Depuis GitHub (après publication)

```bash
# Installation globale
git clone https://github.com/Nico-TekToulouse/git-student-analysis.git \
  ~/.copilot/skills/git-student-analysis

# Installation par projet
git clone https://github.com/Nico-TekToulouse/git-student-analysis.git \
  .github/skills/git-student-analysis
```

## ✅ Vérification

Testez que le skill est bien installé :

```bash
# Vérifier que les fichiers sont présents
ls ~/.copilot/skills/git-student-analysis/

# Devrait afficher : LICENSE README.md SKILL.md skill.yaml scripts/ references/
```

## 🧪 Premier Test

```bash
# Aller dans un repo git
cd /path/to/your/git/repo

# Lancer l'analyse manuellement
~/.copilot/skills/git-student-analysis/scripts/run_analysis.sh . main

# Vérifier les rapports générés
ls -lh git-analysis-report-*.md git-analysis-report-*.xlsx
```

## 🤖 Utilisation avec Copilot CLI

Une fois installé, le skill s'active automatiquement avec des prompts comme :

```
Peux-tu analyser les commits de ce repo ?
```

```
Fais-moi une analyse git détaillée sur la qualité des messages
```

```
Qui a contribué à ce projet ? Je veux voir les statistiques
```

Le skill génère automatiquement :
- `git-analysis-report-YYYY-MM-DD.md` - Rapport Markdown
- `git-analysis-report-YYYY-MM-DD.xlsx` - Fichier Excel

## 🔧 Configuration Automatique

Au **premier lancement**, le skill :

1. ✅ Crée automatiquement un venv Python
2. ✅ Installe les dépendances (pandas, openpyxl, python-dateutil)
3. ✅ Configure l'environnement

**Vous n'avez rien à faire !** Tout est automatique.

## 🗑️ Désinstallation

```bash
# Installation globale
rm -rf ~/.copilot/skills/git-student-analysis

# Installation par projet
rm -rf .github/skills/git-student-analysis
```

## 🆘 Résolution de Problèmes

### Le skill ne se déclenche pas

1. Vérifiez que Copilot CLI est bien installé : `gh copilot --version`
2. Rechargez le shell : `exec $SHELL`
3. Vérifiez l'installation : `ls ~/.copilot/skills/git-student-analysis/skill.yaml`

### Erreur Python "module not found"

Le venv devrait se créer automatiquement. Si problème :

```bash
# Supprimer le venv et le laisser se recréer
rm -rf ~/.copilot/skills/git-student-analysis/.venv
# Relancer l'analyse
```

### Permissions refusées

```bash
# Rendre les scripts exécutables
chmod +x ~/.copilot/skills/git-student-analysis/scripts/*.sh
```

## 📚 Documentation

- [README.md](./README.md) - Documentation complète du skill
- [SKILL.md](./SKILL.md) - Instructions pour Copilot CLI
- [EXAMPLE_PROMPT.md](./EXAMPLE_PROMPT.md) - Exemples de prompts

## 📧 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation dans `README.md`
