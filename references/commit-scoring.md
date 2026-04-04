# Barème de notation des messages de commit

## Score de 0 à 10

### Score 0 — Message nul ou inutile
- Exemples : `"."`, `"fix"`, `"wip"`, `"ok"`, `"asdf"`, `"update"` seul, `"commit"`, `"save"`
- Caractéristiques : aucune information sur ce qui a été fait

### Score 1-2 — Très mauvais
- Exemples : `"fixed stuff"`, `"changes"`, `"some modifications"`, `"test commit"`
- Caractéristiques : vague, aucun contexte, impossible de savoir ce qui a changé

### Score 3-4 — Passable
- Exemples : `"fix login bug"`, `"update css"`, `"add file"`
- Caractéristiques : indique vaguement quoi mais pas pourquoi ni comment

### Score 5-6 — Acceptable
- Exemples : `"fix authentication redirect loop"`, `"add user profile endpoint"`
- Caractéristiques : clair, action + objet, suffisant pour comprendre le changement

### Score 7-8 — Bon
- Exemples : `"fix: redirect loop after OAuth token expiry"`, `"feat(auth): add JWT refresh token support"`
- Caractéristiques : suit une convention, précis, contexte clair

### Score 9-10 — Excellent
- Exemples :
  ```
  fix(auth): resolve infinite redirect loop on token expiry (#42)
  
  Token was not refreshed before redirect, causing a loop when the
  session cookie expired. Added pre-check in middleware.
  ```
- Caractéristiques : sujet clair + corps explicatif + référence ticket

---

## Conventions acceptées

### Conventional Commits (recommandé)
```
<type>(<scope>): <description>

[body optionnel]

[footer optionnel]
```

Types valides : `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`

### Format simple (acceptable)
```
[Type] Description courte
```
Ou simplement un verbe d'action suivi d'une description :
```
Add user authentication middleware
Fix SQL injection in search endpoint
```

### En français (acceptable à Epitech)
```
Ajoute le système d'authentification JWT
Corrige la fuite mémoire dans le gestionnaire de connexions
```

---

## Red flags dans les messages

| Pattern | Problème |
|---------|----------|
| Tout en MAJUSCULES | Non-convention, manque de soin |
| `fix bug`, `update code` | Trop vague |
| Messages identiques sur plusieurs commits | Copy-paste ou script |
| Emojis seuls comme message | Inutilisable pour un reviewer |
| `Merge branch 'main' into main` | Mauvaise gestion des branches |
| Plus de 5 commits avec score < 3 | Problème systémique de qualité |

---

## Note pédagogique

Pour les étudiants Epitech, rappeler que :
1. Le commit message est la première chose qu'un reviewer (ou un recruteur) lit
2. En entreprise, des messages pauvres ralentissent les code reviews
3. Les outils de génération de changelog (semantic-release) dépendent des conventions
4. Un bon historique Git = documentation gratuite du projet

Ressource à conseiller : https://www.conventionalcommits.org/fr/
