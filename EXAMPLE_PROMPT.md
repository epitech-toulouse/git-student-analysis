# Exemples de Prompts pour Tester le Skill

## 1. Analyse Simple d'un Repo Local

```
Peux-tu analyser les commits de ce repo ? Je voudrais voir les contributions de chaque étudiant.
```

*Contexte :* Exécutez cette commande depuis un dossier git local. Le skill détectera automatiquement le repo.

---

## 2. Analyse avec Branche Spécifique

```
Fais-moi une analyse git du repo /Users/nicolasmoreau/Epitech/myTeamsReview/repos/myteams-3 sur la branche main
```

*Résultat attendu :*
- Rapport Markdown : `/Users/nicolasmoreau/Epitech/myTeamsReview/repos/myteams-3/git-analysis-report-myteams-3-YYYY-MM-DD.md`
- Fichier Excel : `/Users/nicolasmoreau/Epitech/myTeamsReview/repos/myteams-3/git-analysis-report-myteams-3-YYYY-MM-DD.xlsx`

---

## 3. Analyse Détaillée des Commits

```
Peux-tu vérifier la qualité des messages de commit et me donner un rapport détaillé sur les contributions ?
```

*Ce qui déclenche :* Les triggers "qualité des messages", "rapport détaillé"

---

## 4. Analyse de Plusieurs Repos

```
Dans le dossier myTeamsReview/repos/, peux-tu analyser tous les repos myteams-* et me dire qui a fait quoi ?
```

*Note :* Le skill analysera chaque repo individuellement et générera un rapport par projet.

---

## Vérifications Automatiques

Le skill s'occupe automatiquement de :

- ✅ Créer le venv Python (première utilisation)
- ✅ Installer pandas, openpyxl, python-dateutil
- ✅ Extraire tous les commits de la branche
- ✅ Dédupliquer les auteurs (même personne, emails différents)
- ✅ Calculer les métriques (commits, lignes, qualité messages)
- ✅ Générer le Markdown + Excel à la racine du projet

---

## Localisation des Rapports

**Avant (❌) :** Rapports dans `/tmp/` → difficiles à retrouver

**Maintenant (✅) :** Rapports dans le dossier du projet analysé
- `git-analysis-report-myteams-3-2026-04-04.md`
- `git-analysis-report-myteams-3-2026-04-04.xlsx`

---

## Test Rapide

```bash
cd /Users/nicolasmoreau/Epitech/myTeamsReview/repos/myteams-3
~/.copilot/skills/git-student-analysis/scripts/run_analysis.sh . main
ls -lh git-analysis-report-*
```

Vous devriez voir :
- Un rapport Markdown de ~2KB
- Un fichier Excel de ~8KB
