# Grilles de scoring pédagogique

## Qualité des messages de commit (score 0–3)

> **⚠️ Principe directeur** : Le scoring évalue la **clarté et l'utilité** du message, pas sa longueur ni sa langue. Un message en français, en espagnol ou en anglais peut obtenir le score maximum s'il est clair et informatif.

| Score | Label | Critères |
|---|---|---|
| **3** ⭐⭐⭐ | Excellent | Message explicite : verbe d'action + contexte + pourquoi. Ex : `fix(auth): correct token expiry` / `Corrige la fuite mémoire dans le parser` / `[FEATURE] #42 - Ajout du login OAuth` |
| **2** ⭐⭐ | Correct | Message court mais compréhensible — on sait ce qui a changé. Ex : `add login page`, `fix null pointer`, `Ajoute la page de connexion` |
| **1** ⭐ | Insuffisant | Message vague ou trop court pour comprendre le changement. Ex : `asdfgh`, `changes`, `modif` |
| **0** ⚠️ | Inexistant/Inutile | Message vide, ≤ 3 caractères, ou purement générique. Ex : `""`, `.`, `fix`, `wip`, `ok`, `commit` |

**Heuristiques de détection automatique (langue-agnostiques) :**
- Score 0 : `len(message) <= 3` ou message dans la liste de mots vides (`commit`, `wip`, `test`, `ok`, `done`, `.`, `..`)
- Score 1 : message < 10 caractères ET pas de verbe reconnaissable
- Score 2 : message informatif en **toute langue** — contient un verbe d'action et un objet
- Score 3 : message respectant une convention claire : Conventional Commits EN/FR (`type(scope): desc` ou `type: desc`), ou convention alternative cohérente (`[TYPE]`, `#ref -`, `TYPE:`) avec description informative

**Conventions alternatives acceptables (score 3 si appliquées de façon cohérente) :**
- `[FEATURE] Ajout du module d'authentification` → score 3
- `#42 - Correction du bug de déconnexion` → score 3
- `FEAT: implement OAuth login` → score 3
- `fix: auth loop` (14 chars, Conventional Commits) → score 3 ✅ (la clarté prime sur la longueur)
- `Corrige la fuite mémoire dans le parser HTTP` → score 3 ✅ (français, clair et informatif)

**Score global étudiant :** moyenne des scores de ses commits, arrondie. Signaler si l'équipe utilise une convention différente de Conventional Commits mais l'applique de façon cohérente.

### Paramètre de convention (`message_convention`)

L'enseignant peut préciser un cadrage conversationnel pour l'évaluation des messages :

| Mode | Valeur | Usage |
|---|---|---|
| Conventional Commits | `conventional` (défaut) | Indique que la promotion/l'équipe vise une convention de type `type(scope): description` |
| Libre mais clair | `free` | Indique qu'aucune convention formelle n'est attendue, tant que le message reste informatif |
| Convention personnalisée | `custom` | L'enseignant décrit la convention attendue ; cette information sert à contextualiser l'analyse et le rapport |

> **Note** : ce paramètre est conversationnel — il permet de contextualiser la demande et peut être mentionné dans le rapport, mais n'active pas à lui seul un mode de scoring distinct dans les scripts. Les heuristiques automatiques restent celles décrites plus haut, notamment la détection de conventions alternatives (`[TYPE]`, `#ref -`, `TYPE:`) et de verbes en français dans `analyze.py`.

Par exemple, avec le cadrage `free`, un message comme `"Réunion d'équipe — on a décidé de réécrire l'auth"` peut être considéré comme informatif même sans convention formelle.

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
📈 Analyse temporelle (projet du `date_debut` au `date_fin`) :
- Phase 1 (`date_debut` → `1/3`) : X commits (Y% du total étudiant)
- Phase 2 (`1/3` → `2/3`) : X commits (Y% du total étudiant)  
- Phase 3 (`2/3` → `date_fin`) : X commits (Y% du total étudiant)
→ Dynamique : montée en puissance / stable / décroissante / rush final
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

Le ratio `insertions / deletions` est un indicateur de la nature du travail effectué lorsque `deletions > 0`. Il complète le volume brut de lignes ajoutées/supprimées et évite de pénaliser le refactoring.

**Cas particulier important :** si `deletions == 0`, le ratio n'est pas calculable au sens habituel (on peut le noter non défini / ∞ si `insertions > 0`). Ce cas doit être interprété explicitement comme un commit d'ajout pur, et non être mélangé artificiellement avec les ratios numériques via `max(1, deletions)`.

### Interprétation du ratio

| Ratio | Interprétation | Signal |
|---|---|---|
| `deletions = 0` | Cas particulier : ajout pur (ratio non défini / ∞ si `insertions > 0`) | 📝 Ajout de fonctionnalités possible ; à distinguer d'un simple ratio `> 5.0` |
| > 5.0 *(si `deletions > 0`)* | Beaucoup plus d'ajouts que de suppressions | 📝 Ajout de fonctionnalités ou copier-coller — vérifier |
| 1.0 – 5.0 *(si `deletions > 0`)* | Équilibre normal | ✅ Travail productif standard |
| 0.3 – 1.0 *(si `deletions > 0`)* | Plus de suppressions que d'ajouts | 🔧 Refactoring ou nettoyage probable — **signal positif** |
| < 0.3 *(si `deletions > 0`)* | Suppressions très importantes | 🔧 Refactoring majeur ou nettoyage de dette technique — **à valoriser** |

### Application dans la note

**Un ratio insertions/deletions faible (suppressions élevées) ne doit PAS être pénalisé.** Le refactoring est souvent signe d'une meilleure maîtrise du code :
- Supprimer 1000 lignes pour en écrire 300 meilleures = travail de qualité
- Nettoyer de la dette technique = contribution précieuse au projet

**Formulation recommandée dans le rapport :**
```
🔧 Ratio insertions/deletions faible (ratio: 0.3) sur N commits — peut indiquer du refactoring de qualité (à vérifier avec les messages de commit et les diffs).
```

**Ne jamais écrire :** `"Bob a moins de lignes ajoutées que les autres"` sans mentionner le contexte de ses suppressions.
