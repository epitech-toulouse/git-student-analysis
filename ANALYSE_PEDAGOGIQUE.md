# 📚 Analyse Pédagogique — `git-student-analysis-copilot`

> Rapport rédigé suite à une analyse critique du skill du point de vue pédagogique.  
> Date : 2026-04-04

---

## 🎯 Verdict général

Le skill a une **bonne intention pédagogique** (objectivité, traçabilité) mais souffre de **biais quantitatifs majeurs** qui peuvent introduire des injustices réelles si le rapport est utilisé sans discernement.

> Il mesure l'*activité observable* dans Git, **pas** la qualité du travail ni l'apprentissage.

---

## 1. 🔴 Biais des métriques Git comme indicateur pédagogique

### Problème A — "Nombre de commits" récompense les mauvaises pratiques
**Sévérité : 🔴 Critique**

Le SKILL.md calcule :
> "Nombre de commits : Count" et "% de commits : commits_étudiant / total_commits × 100"

**Scénario pervers :**
- Alice : 5 commits fonctionnels, 2 000 lignes utiles
- Bob : 25 micro-commits ("fix typo", "add space", "rename var"), 400 lignes

→ Bob apparaît plus productif en % de commits. Alice, qui a fait le travail architectural, passe pour "moins contributrice".

Un étudiant ayant compris la métrique peut **gonfler artificiellement sa contribution** avec des micro-commits vides.

**Recommandation :**
- Ajouter une métrique **"Poids moyen par commit"** : `total_lignes / nombre_commits`
- Signaler les anomalies : "Bob : 25 commits × 16 lignes en moyenne — pattern micro-commits détecté"
- Accompagner le % d'une mise en garde : *"Cette métrique ne reflète pas la qualité ni la complexité du travail"*

---

### Problème B — "Lignes ajoutées" pénalise le refactoring
**Sévérité : 🔴 Critique**

> "Lignes ajoutées / supprimées : Somme insertions / deletions"

**Paradoxe :**
- Un étudiant qui copie 500 lignes d'un tutoriel = forte métrique LOA
- Un étudiant qui refactorise 1 000 lignes en 300 lignes élégantes = métrique basse (voire négative)

Le refactoring, qui est souvent le signe d'une meilleure maîtrise technique, est **pénalisé** par ce skill.

**Recommandation :**
- Ajouter une colonne **"Ratio insertions/deletions"** et signaler les cas extrêmes
- Détecter les "diffs anormaux" : un commit qui ajoute 500 lignes d'un coup mérite un flag
- Mentionner dans le rapport : *"Un ratio suppressions élevé peut indiquer du refactoring de qualité — à vérifier"*

---

### Problème C — Impossible de distinguer "faire" vs "orchestrer"
**Sévérité : 🟡 Moyen**

Un lead technique peut avoir 10% des commits mais avoir conçu 90% de l'architecture, mergé les PRs, géré la CI/CD et fait les code reviews. Git ne voit pas ce travail.

Le skill n'a aucun moyen de le détecter et attribue 10% de crédit à cette personne.

**Recommandation :**
- Catégoriser les commits par type : `feat`, `fix`, `chore`, `ci`, `docs`, `merge`
- Isoler les commits `ci/chore/merge` dans une colonne séparée
- Permettre à l'enseignant d'ajouter des **rôles manuels** dans le mapping : `email,nom,Lead`
- Afficher : *"Jean : 8% commits mais 40% commits d'infrastructure et CI/CD"*

---

### Problème D — La "fréquence" peut mal interpréter des pratiques légitimes
**Sévérité : 🟡 Moyen**

Le skill détecte les "rushes" (commits concentrés en fin de projet) comme signal négatif.

**Mais :**
- Un étudiant qui travaille offline et push en batch = pattern "rush" détecté → pénalisé injustement
- Un étudiant qui fait 1 commit/jour pendant 14 jours avec messages vides = pattern "régulier" → valorisé à tort

**Recommandation :**
- Analyser la **distribution temporelle** : calculer l'écart-type des commits par semaine
- Distinguer "rush final" (>60% des commits dans les 2 derniers jours) de "batch push" (commits espacés)
- Signaler : *"60% des commits dans les 48h avant la deadline — à discuter avec l'étudiant"*

---

## 2. 🔴 Scoring des messages de commit — trop réducteur

### Problème A — Heuristiques biaisées (anglais, longueur ≠ qualité)
**Sévérité : 🔴 Critique**

Le scoring (d'après `references/scoring.md`) :
- Score 0 : message ≤ 3 chars ou dans la liste `['commit', 'fix', 'wip', 'ok', '.']`
- Score 1 : < 15 chars ou sans verbe
- Score 2 : 15–72 chars avec verbe
- Score 3 : Conventional Commits ou > 40 chars avec contexte

**Problèmes :**

1. **Longueur ≠ qualité** : `"fix: auth loop"` (14 chars, très clair) = Score 1 ; `"Fixed the authentication redirect where expiry caused loop in login flow"` (70 chars, verbeux) = Score 3

2. **Biais linguistique** : Les heuristiques testent des mots-clés anglais. Un message en français comme *"Corrige la fuite mémoire dans le parser"* risque d'être mal scoré

3. **Conventional Commits = convention US** : Une équipe qui utilise `[FEATURE] desc` ou `#42 - desc` ne décroche pas Score 3, même si leur convention est cohérente et lisible

**Recommandation :**
- Ajouter un paramètre `--message-convention [conventional|free|custom]`
- Accepter les messages en français avec les mêmes seuils
- Documenter clairement dans le rapport : *"Scoring appliqué : Conventional Commits EN, >40 chars"*

---

### Problème B — Aucune valorisation de la progression
**Sévérité : 🟡 Moyen**

Le skill calcule un **score moyen global**. Si un étudiant avait des messages médiocres au début du projet mais s'est amélioré, cela n'apparaît nulle part.

Or, **l'apprentissage progressif est exactement ce qu'un contexte pédagogique doit valoriser**.

**Recommandation :**
- Ajouter une **analyse de progression** : score moyen des 3 premiers commits vs 3 derniers commits
- Afficher dans le rapport : *"Alice : Score moyen 0.8 → 2.4 — nette amélioration détectée ✅"*
- Intégrer dans le fichier Excel un mini-graphique de progression par étudiant

---

## 3. 🔴 Contribution individuelle en groupe — risques d'injustice

### Problème A — Co-authorship ignoré
**Sévérité : 🔴 Critique**

**Scénario réel et fréquent :**
Alice code 3h en pair programming, Bob pushes le commit depuis son laptop.

Git enregistre : **100% des commits = Bob**  
Skill affiche : **Bob 100%, Alice 0%**  
Réalité pédagogique : Alice a peut-être fait 50% du travail.

Le standard Git `Co-authored-by: Alice <alice@epitech.eu>` dans le message de commit permet de créditer les co-auteurs, mais le skill ne le parse pas.

**Recommandation :**
- Détecter et parser les trailers Git `Co-authored-by:` (format RFC 2822)
- Créditer les co-auteurs dans les métriques individuelles
- Afficher dans le rapport : *"Alice : 12 commits directs + 8 commits en co-authorship"*
- Documenter dans `README.md` : *"Recommandez à vos étudiants d'utiliser `Co-authored-by:` en pair programming"*

---

### Problème B — Le "gaming" des métriques n'est pas détecté
**Sévérité : 🔴 Critique**

Un étudiant ayant compris les métriques peut facilement les manipuler :

| Stratégie | Effet sur les métriques | Détecté ? |
|-----------|------------------------|-----------|
| 20 micro-commits (`"add line"`) | ↑ Count commits | ❌ Non |
| Squash avant push (1 commit = 10 jours de travail) | ↓ Count visible | ❌ Non |
| Commits en burst juste avant deadline | Alerte "rush" | ⚠️ Partiel |
| Copier-coller 500 lignes d'un tuto | ↑ LOA | ❌ Non |
| Messages parfaits sur du code inutile | ↑ Score qualité | ❌ Non |

**Recommandation :**
- Ajouter un **détecteur de patterns suspects** :
  - Messages identiques sur 3+ commits consécutifs
  - Commits avec < 5 lignes modifiées (hors style/typo)
  - Burst > 10 commits en < 30 minutes
- Afficher dans le rapport : *"⚠️ Pattern détecté : 15 commits en 20 minutes — à vérifier avec l'étudiant"*
- Formuler ces alertes comme **questions à poser** à l'étudiant, pas comme accusations

---

### Problème C — Déduplication d'auteurs : cas limites non couverts
**Sévérité : 🟡 Moyen**

Le skill fusionne les identités par email (principal) ou nom normalisé (fallback). Mais :

- Commit via web GitHub = `user@noreply.github.com` (générique) + nom affiché parfois différent → risque de non-fusion avec les commits CLI du même étudiant
- Étudiant avec `.gitconfig` différent à la maison et à l'école (même email, noms légèrement différents : `"Alice M."` vs `"Alice Martin"`) → fusion correcte ?

**Recommandation :**
- Documenter la règle de normalisation exacte dans `README.md`
- Ajouter un **warning dans le rapport** pour chaque fusion réalisée : *"Alice Martin et Alice M. fusionnés — vérifier que c'est correct"*
- Permettre la **correction interactive** lors de l'analyse : *"Fusionner aussi `alice@gmail.com` ? (o/n)"*

---

## 4. 🔴 Limites pédagogiques non documentées

### Problème A — Aucun avertissement que "Git metrics ≠ qualité de code"
**Sévérité : 🔴 Critique**

Le README mentionne :
> "Obtenez des données objectives sur qui a réellement travaillé"

Cette formulation est **dangereuse** : elle suggère que les métriques Git = réalité du travail.

Un enseignant lit `Alice 45% commits` et peut intuitivement penser `Alice ≈ 45% de la note`. Ce raccourci est pédagogiquement faux.

**Recommandation :**
Ajouter en tête du rapport Markdown un bloc d'avertissement obligatoire :

```markdown
## ⚠️ Utilisation responsable de ce rapport

Ce rapport mesure l'**activité Git observable**, pas la qualité du travail ni l'apprentissage.

- Nombre de commits ≠ impact technique
- Lignes ajoutées ≠ fonctionnalités implémentées  
- % de commits ≠ responsabilité du projet

**À utiliser comme complément à :**
- Code review manuelle
- Entretiens individuels avec les étudiants
- Tests de compétence
- Analyse du code source

**Ne pas utiliser seul** pour calculer une note ou identifier des "étudiants passifs".
```

---

### Problème B — Absence de dimension temporelle (progression)
**Sévérité : 🔴 Critique**

Le rapport montre les métriques totales sur toute la durée du projet. Il ne montre pas si un étudiant a progressé, régressé, ou travaillé de façon régulière.

**Ce qui manque :**
- Un étudiant qui ne contribue pas en semaine 1-2 puis devient moteur en semaine 5-8 → apparaît comme "peu contributeur" dans les totaux
- Un étudiant régulier vs un étudiant en rush final → mêmes métriques totales, profils très différents

**Recommandation :**
- Diviser le projet en **phases temporelles** (semaines ou tiers du projet)
- Calculer le % de contribution par étudiant par phase
- Ajouter un **onglet "Progression"** dans le fichier Excel avec graphique par semaine
- Signaler : *"Alice : contribution faible en phase 1 (5%), forte en phase 3 (55%) — accélération progressive"*

---

### Problème C — Merge commits mal gérés
**Sévérité : 🟡 Moyen**

Le SKILL.md mentionne :
> "Merge commits nombreux | Inclure + alerter (workflow non maîtrisé)"

Mais un merge commit dans un workflow GitHub Flow/GitFlow normal ne signifie pas "workflow non maîtrisé". Au contraire, une équipe qui merge proprement ses branches est bien organisée.

De plus, les merge commits peuvent comptabiliser le travail de plusieurs personnes en double (les lignes mergées apparaissent dans les stats du merger).

**Recommandation :**
- **Exclure par défaut les merge commits** des métriques LOA/count (option `--include-merges` pour les inclure)
- Catégoriser les merge commits séparément dans le rapport
- Reformuler l'alerte : *"Nombreux merge commits détectés — peut indiquer un workflow par branches (positif) ou des conflits fréquents (à vérifier)"*

---

## 5. 🟡 Positionnement et risques d'injustice

### Problème A — Le rapport peut créer des injustices par lecture superficielle
**Sévérité : 🔴 Critique**

**Scénario :**
Un enseignant ouvre le fichier Excel, trie par `% commits` décroissant, regarde les 3 premiers et les 3 derniers. Bob est dernier → mauvaise note.

**Réalité :** Bob a refactorisé 800 lignes en 200 lignes propres (3 commits, -600 LOA), conçu l'architecture, et fait 8 code reviews.

L'UI actuelle du rapport Excel **facilite** cette lecture superficielle.

**Recommandation :**
- Ajouter une colonne `"⚠️ À vérifier"` (TRUE/FALSE) mise à TRUE automatiquement si :
  - Écart de contribution > 3x la médiane
  - Pattern de micro-commits détecté
  - Rush en dernières 48h
  - Co-authorship non utilisé (indice de pair programming non tracé)
- Mettre la colonne alertes **en première position visible** dans l'Excel

---

### Problème B — Le skill favorise la "forme Git" au lieu du "fond technique"
**Sévérité : 🟡 Moyen**

En utilisant ce skill, un enseignant évalue involontairement :
- La régularité des commits ✅
- La qualité des messages ✅
- Le volume de lignes ✅

Mais pas :
- La correctness du code ❌
- La qualité de l'architecture ❌
- La présence et qualité des tests ❌
- La documentation du code ❌
- L'apprentissage réel ❌

Un étudiant peut faire 50 commits parfaits sur du code qui ne fonctionne pas.

**Recommandation :**
Ajouter une section `"Ce que ce rapport NE mesure PAS"` dans le README et en fin de rapport :
```markdown
## 🚫 Limites de ce rapport

Ce rapport ne mesure pas :
- La correctness du code (des commits bien formés peuvent contenir des bugs)
- La qualité de l'architecture ou des tests
- L'apprentissage réel de l'étudiant
- Les contributions non commitées (design, revue, organisation)

Complétez avec : code review, entretien individuel, tests de compétence.
```

---

## 📊 Récapitulatif des problèmes

| Axe | Problème | Sévérité |
|-----|----------|----------|
| Métriques Git | Commits count récompense le micro-commit artificiel | 🔴 Critique |
| Métriques Git | LOA pénalise le refactoring | 🔴 Critique |
| Métriques Git | Impossible de distinguer "faire" vs "orchestrer" | 🟡 Moyen |
| Métriques Git | Fréquence mal interprétée (offline batch vs rush) | 🟡 Moyen |
| Scoring messages | Heuristiques biaisées (longueur, anglais) | 🔴 Critique |
| Scoring messages | Aucune valorisation de la progression | 🟡 Moyen |
| Contribution groupe | Co-authorship ignoré → injustices directes | 🔴 Critique |
| Contribution groupe | Gaming des métriques non détecté | 🔴 Critique |
| Contribution groupe | Déduplication incomplète (noreply, alias) | 🟡 Moyen |
| Limites | Aucun avertissement "Git ≠ qualité de code" | 🔴 Critique |
| Limites | Absence de dimension temporelle / progression | 🔴 Critique |
| Limites | Merge commits mal gérés | 🟡 Moyen |
| Positionnement | Rapport Excel facilite la lecture superficielle | 🔴 Critique |
| Positionnement | Favorise forme Git plutôt que fond technique | 🟡 Moyen |

---

## 🎯 Top 5 — Améliorations prioritaires

### 1. 🔴 Ajouter un avertissement pédagogique obligatoire en tête du rapport
Prévenir 80% des mauvaises interprétations. Bloc rouge visible, pas en footnote.  
**Effort :** ~30 min. **Impact :** Maximal.

### 2. 🔴 Détecter et parser le Co-authorship Git (`Co-authored-by:`)
Éliminer le risque d'injustice le plus grave (pair programming non tracé).  
**Effort :** ~2h (parsing commits + logique de crédit). **Impact :** Critique.

### 3. 🔴 Ajouter l'analyse temporelle (progression par semaine/phase)
Révéler la dynamique d'équipe et valoriser l'apprentissage progressif.  
**Effort :** ~3h (data + graphique Excel). **Impact :** Élevé.

### 4. 🔴 Détecter les patterns suspects (micro-commits, burst, copier-coller)
Signaler les situations à vérifier sans accuser. Formuler comme "questions à poser".  
**Effort :** ~2h (heuristiques + alertes). **Impact :** Élevé.

### 5. 🟡 Revoir le scoring des messages (support français, conventions alternatives)
Éviter le biais Conventional Commits EN. Accepter des conventions cohérentes même non-standard.  
**Effort :** ~1h (paramétrage + doc). **Impact :** Moyen.

---

## 💡 Recommandation de fond

Ce skill est **utile pour préparer un entretien avec les étudiants**, pas pour noter directement.

Sa vraie valeur : identifier les **anomalies à investiguer** (rush suspect, contribution asymétrique, messages vides) et **préparer les questions** à poser lors d'un oral ou d'une soutenance.

> "Ce rapport vous dit **à qui parler** et **quoi demander**, pas **qui noter comment**."

Reformuler cet objectif dès le `README.md` changerait fondamentalement la façon dont les enseignants l'utilisent.
