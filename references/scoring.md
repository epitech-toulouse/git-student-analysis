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

## Analyse de fréquence

Calculer : `commits_par_semaine = total_commits / max(1, nb_semaines_projet)`

| Pattern | Interprétation |
|---|---|
| Commits réguliers tout au long du projet | ✅ Travail progressif |
| Commits concentrés sur 1–2 jours | ⚠️ Rush probable, vérifier la qualité |
| Aucun commit pendant > 50% de la durée | 🔴 Participation tardive |
| 0 commit | 🔴 Pas de contribution détectée |

Afficher aussi : date du 1er commit et date du dernier commit par étudiant.
