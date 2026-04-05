# 🎓 Git Student Analysis - Copilot CLI Skill

[![Install with skills CLI](https://img.shields.io/badge/skills.sh-install-blue?logo=github)](https://skills.sh/Nico-TekToulouse/git-student-analysis-copilot)
[![Agent Skills](https://img.shields.io/badge/agent--skills-compatible-green)](https://github.com/vercel-labs/skills)
[![Copilot CLI](https://img.shields.io/badge/Copilot-CLI-blue?logo=github)](https://github.com/features/copilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](skill.yaml)

> Analyse l'activité Git des étudiants sur un repository GitHub et produit un rapport pédagogique détaillé avec métriques et exports.

## ⚡ Installation rapide

```bash
npx skills add Nico-TekToulouse/git-student-analysis-copilot -g -a github-copilot
```

## 📖 Description

Ce skill pour **GitHub Copilot CLI** permet aux enseignants et formateurs d'analyser automatiquement les contributions Git de leurs étudiants sur un projet collaboratif. Il produit :

- ✅ **Rapport Markdown** : synthèse lisible directement dans le terminal
- ✅ **Fichier Excel** : tableau exportable avec onglets résumé + détail des commits
- ✅ **Métriques complètes** : commits, lignes modifiées, qualité des messages, fréquence
- ✅ **Déduplication intelligente** : regroupe automatiquement les multiples identités d'un même étudiant

## 🚀 Installation

### Via skills CLI (Recommandée)

```bash
npx skills add Nico-TekToulouse/git-student-analysis-copilot -g -a github-copilot
```

### Installation manuelle (Alternative)

Le skill sera disponible dans tous vos projets :

```bash
# Créer le dossier de skills s'il n'existe pas
mkdir -p ~/.copilot/skills

# Cloner le skill
cd ~/.copilot/skills
git clone https://github.com/[votre-username]/git-student-analysis-copilot.git git-student-analysis

# Vérifier l'installation
ls ~/.copilot/skills/git-student-analysis
```

### Installation Projet (Alternative)

Pour utiliser le skill uniquement dans un projet spécifique :

```bash
# Dans le dossier racine de votre projet
mkdir -p .github/skills
cd .github/skills
git clone https://github.com/[votre-username]/git-student-analysis-copilot.git git-student-analysis
```

### Vérification

Lancez Copilot CLI et vérifiez que le skill est chargé :

```bash
copilot
```

Dans le CLI, tapez :
```
/skills
```

Vous devriez voir **git-student-analysis** dans la liste.

## 📝 Utilisation

### Cas d'Usage 1 : Analyser un Repository GitHub Public

```bash
copilot
```

Puis dans le CLI :
```
Analyse les contributions des étudiants sur ce repo : https://github.com/org/student-project
```

### Cas d'Usage 2 : Analyser un Repository Local

```bash
cd /chemin/vers/repo-etudiant
copilot
```

Puis :
```
Analyse les contributions Git de ce projet
```

### Cas d'Usage 3 : Même Étudiant, Noms Différents (Auto-détecté)

Le skill gère **automatiquement** le cas d'un étudiant qui a commité sous des noms différents avec le **même email** :

```
john@epitech.eu | John Doe   → 5 commits
john@epitech.eu | JohnD      → 3 commits
john@epitech.eu | J. Doe     → 2 commits
```

→ Ils seront **fusionnés** en un seul auteur "John Doe" (nom le plus fréquent) avec une alerte dans le rapport.

### Cas d'Usage 4 : Avec Mapping des Identités

Si plusieurs emails correspondent à la même personne, créez un `mapping.csv` :
```csv
email,nom_canonique
john.doe@gmail.com,John Doe
j.doe@student.edu,John Doe
alice123@outlook.com,Alice Martin
```

Puis demandez l'analyse avec mapping :
```
Analyse les contributions avec le mapping mapping.csv
```

### Cas d'Usage 5 : Pair Programming avec Co-authored-by (Auto-détecté)

En pair programming, si Bob pousse depuis son laptop, Git enregistrerait 100% du travail à Bob et 0% à Alice. Pour éviter cette injustice, encouragez vos étudiants à utiliser le trailer standard `Co-authored-by:` :

```bash
git commit -m "feat: implement auth module

Co-authored-by: Alice Martin <alice@epitech.eu>"
```

Le skill **détecte automatiquement** ces trailers et attribue les contributions aux deux auteurs. GitHub affiche également les deux auteurs sur l'interface web.

**Recommandation pédagogique** : Demandez à vos étudiants d'utiliser systématiquement `Co-authored-by:` lors de leurs sessions de pair programming.

## 🎯 Ce que le Skill Produit

### 1. Rapport Markdown (dans le terminal)

```markdown
# Analyse Git — student-project — 2026-04-04

## Résumé global
- Total commits : 147
- Période : 2026-03-01 → 2026-04-04
- Auteurs : 5 étudiants

## Par Étudiant

### Alice Martin — 34.7% des commits
- Commits : 51 (34.7%)
- Insertions : 2,431 lignes
- Deletions : 876 lignes
- Fichiers modifiés : 23 fichiers
- Qualité messages : ⭐⭐⭐ (2.8/3)
- Pattern : Contributions régulières, bon respect des conventions

### Bob Durant — 28.6% des commits
...
```

### 2. Fichier Excel (`git-analysis-report-YYYY-MM-DD.xlsx`)

**Généré automatiquement à la racine du projet analysé.**

**Onglet 1 - Résumé** :
| Étudiant | Commits | % | Insertions | Deletions | Fichiers | Qualité | Note Globale |
|----------|---------|---|------------|-----------|----------|---------|--------------|
| Alice    | 51      | 34.7% | 2,431   | 876       | 23       | 2.8/3   | A           |
| Bob      | 42      | 28.6% | 1,879   | 543       | 18       | 2.1/3   | B+          |

**Onglet 2 - Détail des Commits** :
Liste exhaustive de tous les commits avec auteur, date, message, stats.

## ⚙️ Configuration Automatique

### Environnement Python Isolé

Le skill utilise **automatiquement un venv Python**. Rien à installer manuellement !

Au premier lancement :
- Un venv est créé dans `~/.copilot/skills/git-student-analysis/.venv/`
- Les dépendances sont installées automatiquement (pandas, openpyxl)
- Vos packages Python globaux ne sont pas affectés

**Avantages** :
- ✅ Isolation complète
- ✅ Pas de conflit de versions
- ✅ Setup automatique

### Localisation des Rapports

Les rapports sont générés **à la racine du projet analysé** :
- `git-analysis-report-YYYY-MM-DD.md` - Rapport Markdown
- `git-analysis-report-YYYY-MM-DD.xlsx` - Fichier Excel

**Plus besoin de chercher dans /tmp !** Les rapports sont directement dans votre projet.

### Variables d'Environnement (Optionnel)

```bash
# Branche par défaut à analyser
export GIT_ANALYSIS_DEFAULT_BRANCH="main"
```

### Nettoyage

Si besoin de réinitialiser le venv :
```bash
rm -rf ~/.copilot/skills/git-student-analysis/.venv
# Il sera recréé automatiquement au prochain lancement
```

### Fichier de Mapping

Pour gérer les multiples identités d'un étudiant, créez `mapping.csv` :

```csv
email,nom_canonique
j.doe@gmail.com,John Doe
john.doe@student.edu,John Doe
```

Le skill appliquera automatiquement la fusion.

## 📊 Métriques Calculées

| Métrique | Description |
|----------|-------------|
| **Nombre de commits** | Total de commits par étudiant |
| **% de commits** | Pourcentage du total |
| **Lignes ajoutées/supprimées** | Somme des insertions et deletions |
| **Fichiers modifiés** | Nombre de fichiers distincts touchés |
| **Fréquence** | Commits par jour, détection des "rushes" |
| **Qualité messages** | Score 0-3 basé sur longueur, clarté, conventions |
| **Pertinence** | Évaluation qualitative des modifications |

### Scoring des Messages de Commit

Le skill évalue automatiquement la qualité :

- ⭐⭐⭐ (3/3) : Messages clairs, conventions respectées, descriptifs
- ⭐⭐ (2/3) : Messages corrects mais améliorables
- ⭐ (1/3) : Messages vagues ("fix", "update", "WIP")
- ⚠️ (0/3) : Messages absents ou non-informatifs

## 🛠️ Dépendances

Le skill s'occupe de tout automatiquement !

**Requis (pré-installé sur macOS/Linux)** :
- **Git** (version 2.0+)
- **Python 3** (version 3.7+)
- **Bash** (shell Unix)

**Installé automatiquement dans le venv** :
- pandas
- openpyxl  
- python-dateutil

Vous n'avez **rien à installer manuellement** ! 🎉

## 📁 Structure du Projet

```
git-student-analysis-copilot/
├── skill.yaml              # Configuration Copilot CLI
├── SKILL.md               # Instructions détaillées pour l'agent
├── README.md              # Ce fichier
├── LICENSE                # Licence MIT
├── .gitignore
├── scripts/
│   ├── extract_commits.sh # Extraction des commits (bash)
│   ├── analyze.py         # Analyse et déduplication (python)
│   ├── generate_md.py     # Génération rapport Markdown
│   └── generate_xlsx.py   # Génération fichier Excel
└── references/
    ├── scoring.md         # Documentation du scoring
    ├── commit-scoring.md  # Critères d'évaluation
    └── llm-diff-analysis.md # Guide d'analyse LLM
```

## ⚠️ Utilisation responsable

> **Ces métriques mesurent l'activité Git observable, pas la qualité du travail ni l'apprentissage.**

Cette section constitue une **recommandation d'interprétation des résultats** et doit être prise en compte lors de l'exploitation pédagogique des métriques.
Avant d'utiliser ce skill pour évaluer des étudiants, gardez à l'esprit :

| Métrique Git | ≠ | Réalité |
|---|---|---|
| Nombre de commits | ≠ | Impact technique |
| Lignes ajoutées | ≠ | Fonctionnalités implémentées |
| % de commits | ≠ | Responsabilité du projet |
| Messages de commit | ≠ | Qualité du code |

**Ne jamais utiliser ces métriques seules pour calculer une note.** Elles constituent un point de départ pour une discussion, pas une vérité objective.

Cas courants qui faussent les métriques :
- Le pair programming : une seule personne pousse le code écrit à deux
- Le refactoring : supprimer 1000 lignes pour en écrire 300 meilleures = travail de qualité
- Les générateurs de code : beaucoup de lignes ajoutées ≠ maîtrise
- La division du travail : un étudiant conçoit l'architecture (peu de commits), un autre l'implémente

## 🎓 Cas d'Usage Pédagogiques

### Évaluation de Projet de Groupe

Obtenez une vue d'ensemble de l'activité Git de chaque étudiant pour identifier les contributions et engager des discussions sur la répartition du travail.

### Détection des Contributions Tardives

Identifiez les étudiants qui ont commit 90% du code la veille de la deadline.

### Encouragement des Bonnes Pratiques

Montrez aux étudiants l'importance de messages de commit clairs et descriptifs.

### Équité dans les Notes

Complétez vos évaluations avec des métriques d'activité Git, en les croisant avec d'autres observations (revues de code, démos, entretiens individuels).

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Forkez le repository
2. Créez une branche feature (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -am 'feat: ajout fonctionnalité X'`)
4. Pushez vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE) - vous êtes libre de l'utiliser, le modifier et le distribuer.

## 🙏 Remerciements

- Inspiré par les besoins des enseignants d'Epitech et autres écoles d'informatique
- Basé sur les best practices Git et les conventions de commit
- Optimisé pour GitHub Copilot CLI

## 📞 Support

Des questions ? Des suggestions ?

- Ouvrez une [Issue](https://github.com/[votre-username]/git-student-analysis-copilot/issues)
- Consultez la [documentation complète](SKILL.md)
- Rejoignez les discussions GitHub

---

**Fait avec ❤️ pour les enseignants et formateurs**

*Compatible avec GitHub Copilot CLI v1.0+*
