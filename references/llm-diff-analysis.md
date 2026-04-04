# Analyse qualitative des diffs via LLM

Ce fichier contient les prompts à utiliser pour analyser la pertinence des
modifications de code via un appel LLM, quand le repo est assez petit pour
que ce soit faisable (<500 commits ou <10k lignes de diff total).

---

## Quand utiliser l'analyse LLM ?

Utiliser l'analyse LLM en complément du scoring automatique quand :
- Le nombre de commits est < 200
- L'utilisateur veut une analyse qualitative approfondie
- Des modifications semblent suspectes (grosse diff d'un coup, fichiers inhabituels)

Pour les gros repos, se fier uniquement au scoring par extension/répertoire.

---

## Prompt d'analyse de diff

```
Tu es un évaluateur pédagogique expert en génie logiciel.
Analyse le diff Git suivant et réponds UNIQUEMENT en JSON.

Projet : {repo_name}
Auteur : {author_name}
Message du commit : {commit_subject}
Date : {commit_date}

Diff :
{diff_content}

Réponds avec ce JSON exact :
{
  "pertinence": <0-10>,
  "qualite_code": <0-10>,
  "commentaire": "<2 phrases max expliquant le score>",
  "anomalie": <true|false>,
  "detail_anomalie": "<vide si pas d'anomalie, sinon description courte>"
}

Critères pour pertinence :
- 9-10 : modification fonctionnelle claire, logique, bien intégrée au projet
- 7-8  : modification correcte mais mineure ou partielle
- 5-6  : modification neutre (config, doc, style)
- 3-4  : modification peu pertinente ou hasardeuse
- 0-2  : modification contre-productive, fichiers non liés, copier-coller évident

Critères pour qualité_code :
- 9-10 : code propre, idiomatique, bien structuré
- 7-8  : code fonctionnel avec quelques imperfections mineures
- 5-6  : code fonctionnel mais perfectible
- 3-4  : code fonctionnel mais mauvaises pratiques
- 0-2  : code non fonctionnel, copié-collé sans adaptation, ou hors sujet

Anomalies à détecter :
- Copier-coller évident depuis Stack Overflow ou autre (patterns trop génériques)
- Suppression de fonctionnalités existantes sans raison apparente
- Ajout massif de fichiers générés (lock files, dist/, etc.)
- Commit qui annule le travail d'un autre étudiant
```

---

## Intégration dans le workflow

```python
import subprocess

def get_commit_diff(repo_path, sha, max_lines=200):
    """Récupère le diff d'un commit, tronqué si trop long."""
    result = subprocess.run(
        ["git", "-C", repo_path, "show", "--stat", "-p", sha],
        capture_output=True, text=True
    )
    lines = result.stdout.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append(f"... (tronqué à {max_lines} lignes)")
    return "\n".join(lines)
```

---

## Limitations

- Ne pas envoyer des diffs > 500 lignes à l'API (trop coûteux et peu fiable)
- Échantillonner : analyser au maximum 5 commits par auteur
- Toujours combiner avec le scoring automatique, ne pas remplacer
- Signaler à l'utilisateur que cette analyse est un complément indicatif
