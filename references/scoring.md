# Grilles de scoring pédagogique

## Qualité des messages de commit (score 0–3)

| Score | Label | Critères |
|---|---|---|
| **3** ⭐⭐⭐ | Excellent | Message explicite : verbe d'action + contexte + pourquoi. Ex : `fix(auth): correct token expiry check to avoid logout loop` |
| **2** ⭐⭐ | Correct | Message court mais compréhensible. Ex : `add login page`, `fix null pointer in UserService` |
| **1** ⭐ | Insuffisant | Message vague, trop court, ou non informatif. Ex : `fix`, `wip`, `update`, `test`, `ok`, `asdfgh` |
| **0** ⚠️ | Inexistant/Inutile | Message vide, un seul caractère, ou copié-collé de la commande. Ex : `""`, `.`, `commit` |

**Heuristiques de détection automatique :**
- Score 0 : len(message) <= 3 ou message in ['commit', 'update', 'fix', 'wip', 'test', 'ok', 'done', '.', '..']
- Score 1 : len(message) < 15 ou message sans verbe ni contexte
- Score 2 : message entre 15–72 caractères avec un verbe reconnaissable
- Score 3 : message respectant Conventional Commits (`type(scope): description`) OU > 40 chars avec contexte clair

**Score global étudiant :** moyenne des scores de ses commits, arrondie.

---

## Pertinence des modifications (appréciation qualitative)

Claude analyse les diffs pour produire une appréciation en 2–3 phrases. Points à évaluer :

### Signaux positifs
- Modifications cohérentes avec le message de commit
- Commits atomiques (une fonctionnalité / un fix par commit)
- Fichiers modifiés en rapport avec la feature annoncée
- Ratio insertions/deletions cohérent (pas de 1000 lignes ajoutées pour "fix typo")

### Signaux négatifs / alertes
- **Commit fourre-tout** : beaucoup de fichiers non liés modifiés ensemble
- **Copier-coller massif** : insertions très élevées d'un coup sans suppression
- **Modification uniquement de fichiers de config ou lock** (yarn.lock, package-lock) sans code métier
- **Suppression de code sans explication** : deletions >> insertions sans message clair
- **Burst de commits** : 5+ commits en moins d'1h (signe de travail de dernière minute ou de découpage artificiel)
- **Commits sur une seule journée** couvrant 80%+ du travail total

### Template de commentaire pertinence
```
Modifications cohérentes avec les messages de commit. Les commits sont bien atomiques.
[OU]
Plusieurs commits fourre-tout détectés (ex : commit du <date> touche 12 fichiers non liés).
Ratio insertions/deletions inhabituel sur <N> commits. À vérifier.
```

---

## Analyse de fréquence

Calculer : `commits_par_semaine = total_commits / max(1, nb_semaines_projet)`

| Pattern | Interprétation |
|---|---|
| Commits réguliers tout au long du projet | ✅ Travail progressif |
| Commits concentrés sur 1–2 jours | ⚠️ Rush probable, vérifier la qualité |
| Aucun commit pendant > 50% de la durée | 🔴 Participation tardive |
| 0 commit | 🔴 Pas de contribution détectée |

Afficher aussi : date du 1er commit et date du dernier commit par étudiant.

---

## Ratio insertions/deletions — détection du refactoring

### Principe

Le ratio `insertions / max(1, deletions)` est un indicateur de la nature du travail effectué. Il complète le LOA brut et évite de pénaliser le refactoring.

### Interprétation du ratio

| Ratio | Interprétation | Signal |
|---|---|---|
| > 5.0 | Beaucoup plus d'ajouts que de suppressions | 📝 Ajout de fonctionnalités ou copier-coller — vérifier |
| 1.0 – 5.0 | Équilibre normal | ✅ Travail productif standard |
| 0.3 – 1.0 | Plus de suppressions que d'ajouts | 🔧 Refactoring ou nettoyage probable — **signal positif** |
| < 0.3 | Suppressions très importantes | 🔧 Refactoring majeur ou nettoyage de dette technique — **à valoriser** |

### Application dans la note

**Un ratio deletions élevé ne doit PAS être pénalisé.** Le refactoring est souvent signe d'une meilleure maîtrise du code :
- Supprimer 1000 lignes pour en écrire 300 meilleures = travail de qualité
- Nettoyer de la dette technique = contribution précieuse au projet

**Formulation recommandée dans le rapport :**
```
🔧 Ratio suppressions élevé (ratio: 0.3) sur N commits — peut indiquer du refactoring de qualité (à vérifier avec les messages de commit et les diffs).
```

**Ne jamais écrire :** `"Bob a moins de lignes ajoutées que les autres"` sans mentionner le contexte de ses deletions.
