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

## Analyse temporelle — progression par phase

### Principe

Diviser la durée totale du projet en 3 phases égales et analyser la contribution de chaque étudiant par phase. Cette analyse révèle la **dynamique** de contribution, invisible dans les totaux.

### Interprétation des patterns temporels

| Pattern | Interprétation pédagogique |
|---|---|
| Contribution croissante (5% → 30% → 55%) | ✅ Montée en compétence, implication progressive |
| Contribution stable (30% → 35% → 35%) | ✅ Travail régulier et équilibré |
| Contribution décroissante (50% → 30% → 10%) | ⚠️ Désengagement progressif — à explorer |
| Contribution uniquement phase 3 (0% → 5% → 95%) | 🔴 Rush de dernière minute |
| Contribution uniquement phase 1 (90% → 5% → 5%) | ⚠️ Implication initiale forte puis abandon |

### Application dans la note

- La **progression croissante** doit être valorisée : un étudiant qui monte en puissance démontre un apprentissage réel
- Ne pas pénaliser automatiquement une faible phase 1 — l'étudiant peut avoir été en phase d'apprentissage
- Un rush de phase 3 mérite une discussion, pas une sanction automatique

### Format de présentation dans le rapport

```
📈 Analyse temporelle (projet du <date_début> au <date_fin>) :
- Phase 1 (<date_début> → <1/3>) : X commits (Y% du total étudiant)
- Phase 2 (<1/3> → <2/3>) : X commits (Y% du total étudiant)  
- Phase 3 (<2/3> → <date_fin>) : X commits (Y% du total étudiant)
→ Dynamique : montée en puissance / stable / décroissante / rush final
```

Calculer : `commits_par_semaine = total_commits / max(1, nb_semaines_projet)`

| Pattern | Interprétation |
|---|---|
| Commits réguliers tout au long du projet | ✅ Travail progressif |
| Commits concentrés sur 1–2 jours | ⚠️ Rush probable, vérifier la qualité |
| Aucun commit pendant > 50% de la durée | 🔴 Participation tardive |
| 0 commit | 🔴 Pas de contribution détectée |

Afficher aussi : date du 1er commit et date du dernier commit par étudiant.
