---
name: git-student-analysis
description: >
  Analyse l'activité Git des étudiants sur un repository GitHub pour produire un rapport pédagogique.
  Utiliser ce skill dès que l'utilisateur mentionne : analyser un repo, voir les commits des étudiants,
  évaluer les contributions Git, rapport de commits, activité GitHub d'un groupe, qui a le plus contribué,
  qualité des messages de commit, fréquence des commits par étudiant. Fonctionne avec une URL GitHub
  publique ou un répertoire déjà cloné en local. Produit systématiquement un rapport Markdown + un fichier
  Excel (.xlsx) exportable.
---

# Git Student Analysis Skill

Analyse les contributions Git d'un repo et produit un rapport pédagogique structuré par étudiant.

## Ce que ce skill produit

- **Rapport Markdown** : synthèse lisible dans le chat, par étudiant
- **Fichier Excel** : tableau exportable, un onglet résumé + un onglet détail des commits

---

## Étape 0 — Collecter les infos manquantes

Si l'utilisateur n'a pas précisé, demander :
- **Source** : URL GitHub ou chemin local ?
- **Branche(s)** à analyser (défaut : `main` ou branche par défaut)
- **Mapping identités** : y a-t-il une liste nom/email des étudiants ? (optionnel, améliore le regroupement)
- **Convention de messages** (optionnel, informatif / conversationnel) : `message_convention: conventional | free | custom`
  - **Important** : ce paramètre n'est pas appliqué automatiquement comme filtre strict ; il sert à cadrer la demande et peut être mentionné dans le rapport. La détection automatique des conventions alternatives et des verbes français est intégrée au scoring.
  - `conventional` (défaut) : valorise Conventional Commits en EN et FR, accepte les conventions alternatives cohérentes
  - `free` : valorise tout message clair et informatif, quelle que soit la convention
  - `custom` : l'enseignant précise sa convention attendue (ex: `[TYPE] description`, `#ref - message`) pour contexte

---

## Étape 1 — Préparer le repo

### Cas A — URL GitHub fournie

```bash
# Clone léger (sans fichiers binaires, historique complet)
git clone --filter=blob:none <URL> /tmp/repo_analyse
cd /tmp/repo_analyse
```

Si le clone échoue (repo privé, réseau), signaler à l'utilisateur qu'il doit fournir un chemin local cloné manuellement.

### Cas B — Chemin local fourni

```bash
cd <chemin_fourni>
git fetch --all   # s'assurer d'avoir tous les commits distants
```

---

## Étape 2 — Extraire les données brutes

**Le skill utilise automatiquement un environnement Python isolé (venv)** qui est créé au premier lancement. Vous n'avez rien à installer manuellement.

Utiliser le script principal qui gère tout le workflow :

```bash
bash scripts/run_analysis.sh <chemin_repo> [<branche>]
```

Ce script :
1. Configure automatiquement le venv Python (si nécessaire)
2. Extrait tous les commits
3. Analyse et déduplique les auteurs
4. Génère le rapport Markdown **à la racine du repo analysé**
5. Génère le fichier Excel **à la racine du repo analysé**

**Outputs** (générés à la racine du projet) :
- `git-analysis-report-YYYY-MM-DD.md` - Rapport Markdown
- `git-analysis-report-YYYY-MM-DD.xlsx` - Fichier Excel

---

## Étape 3 — Regrouper les auteurs (déduplication)

**Règle critique** : un même étudiant peut avoir poussé avec des noms différents ou des emails différents.

Stratégie de déduplication :
1. **Email non-générique** → La clé de regroupement est l'**email** (peu importe le nom affiché)
   - Ex: "John Doe" + "JohnD" avec email `john@epitech.eu` → fusionnés en 1 seul auteur
   - Le **nom le plus fréquent** parmi les commits est choisi comme nom canonique
   - Les noms alternatifs sont listés dans le rapport avec une alerte
2. **Email générique** (`noreply`, etc.) → Grouper par **nom normalisé** (minuscules, sans accents)
3. **Mapping manuel** (`mapping.csv`) → Priorité absolue : `email,nom_canonique`

Signaler dans le rapport :
- Les fusions réalisées (noms alternatifs détectés)
- Le nom canonique choisi (le plus fréquent)

---

## Étape 4 — Calculer les métriques par étudiant

| Métrique | Calcul |
|---|---|
| **Nombre de commits** | Count |
| **% de commits** | commits_étudiant / total_commits × 100 |
| **Lignes ajoutées / supprimées** | Somme insertions / deletions |
| **Fichiers modifiés (distincts)** | Union des fichiers touchés |
| **Fréquence** | commits / durée_projet_jours ; détecter les rushes |
| **Qualité messages** | Score 0–3 (voir `references/scoring.md`) |
| **Pertinence modifications** | Appréciation qualitative (voir `references/scoring.md`) |
| **Ratio insertions/deletions** | si `deletions > 0` : `insertions / deletions` ; si `deletions == 0` : afficher `∞` ou `N/A` et interpréter comme “ajout net, aucune suppression” |

---

## Étape 5 — Générer le rapport Markdown

Le script `run_analysis.sh` génère automatiquement le rapport à la racine du projet analysé.

**Emplacement** : `<repo_root>/git-analysis-report-YYYY-MM-DD.md`

```
# Analyse Git — <nom_repo> — <date>

## ⚠️ Utilisation responsable de ce rapport
Ce rapport mesure l'activité Git observable, pas la qualité du travail ni l'apprentissage.
- Nombre de commits ≠ impact technique
- Lignes ajoutées ≠ fonctionnalités implémentées
- % de commits ≠ responsabilité du projet
Ne pas utiliser seul pour calculer une note.

## Résumé global
- Total commits : X  |  Période : <début> → <fin>
- Auteurs bruts : N  →  après déduplication : M

## Par étudiant

### 👤 <Prénom Nom> (<email_canonique>)
- Commits : X (Y%)
- Lignes : +Z / -W  |  Fichiers distincts : N
- Ratio insertions/deletions : X.X → [🔧 refactoring probable si ratio < 0.3] [📝 ajout net si ratio > 5.0] (voir `references/scoring.md` pour la grille détaillée)
- Fréquence : régulière / rush fin de projet / absente
- Qualité des messages : ⭐⭐⭐ / ⭐⭐ / ⭐ / ⚠️ inexistants
- Pertinence des modifications : <texte>
- ⚠️ Alertes : ex. "10 commits en 2h avant deadline", "messages vides", "❓ 5 commits consécutifs avec message identique — s'agit-il de 5 changements distincts ?"

[Identités fusionnées : ancien_email → email_canonique]
```

**Patterns suspects à signaler (comme questions, jamais comme accusations) :**
- Messages identiques sur 3+ commits consécutifs → `❓ X commits avec le même message "..." — ce message décrit-il X changements distincts ?`
- Micro-commits (< 5 lignes modifiées en série) → `❓ N micro-commits détectés — s'agit-il d'un découpage intentionnel ?`
- Burst > 10 commits en < 30 minutes → `❓ N commits en M minutes — ce backlog correspond-il à du travail progressif ?`

---

## Étape 6 — Générer le fichier Excel

Utiliser `openpyxl` selon le skill `xlsx`. Structure du classeur :

- **Onglet "Résumé"** : une ligne par étudiant, toutes métriques, en-têtes colorés
- **Onglet "Commits"** : liste complète, auteur canonique, date, message, score qualité
- **Onglet "Alertes"** : lignes surlignées en orange (commits suspects, étudiants inactifs)

Sauvegarder dans `/mnt/user-data/outputs/analyse_git_<nom_repo>_<YYYYMMDD>.xlsx`.
Recalculer les formules avec `scripts/recalc.py` si des formules Excel sont utilisées.

---

## Étape 7 — Présenter les résultats

1. Afficher le rapport Markdown complet dans le chat
2. Appeler `present_files` avec le `.xlsx`
3. Proposer des actions de suivi :
   - Filtrer sur une période précise
   - Ajouter un mapping manuel d'identités
   - Exporter seulement certains étudiants

---

## Références

- `references/scoring.md` — Grilles de scoring détaillées
- `scripts/extract_commits.sh` — Extraction Git brute
- `scripts/analyze.py` — Analyse, déduplication, métriques
- `scripts/generate_xlsx.py` — Génération du classeur Excel

---

## Cas limites à gérer

| Situation | Comportement attendu |
|---|---|
| Repo vide / 0 commits | Signaler et arrêter |
| Un seul auteur | Rapport simplifié, pas de % |
| Merge commits nombreux | Inclure + alerter (workflow non maîtrisé) |
| Commits vides (`--allow-empty`) | Compter + noter en alerte |
| Réseau bloqué (clone impossible) | Demander chemin local |
