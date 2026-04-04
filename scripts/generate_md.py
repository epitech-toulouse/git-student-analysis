#!/usr/bin/env python3
"""
Génère le rapport Markdown à partir des données d'analyse.
Usage: python generate_md.py <analysis_data.json> <output.md> <repo_name>
"""

import json
import sys
from datetime import datetime


def score_emoji(score, max_score=10):
    ratio = score / max_score
    if ratio >= 0.75:
        return "🟢"
    elif ratio >= 0.50:
        return "🟡"
    else:
        return "🔴"


def note_emoji(note):
    if note >= 15:
        return "🟢"
    elif note >= 10:
        return "🟡"
    else:
        return "🔴"


def generate_markdown(data, repo_name, output_path):
    summary = data.get("repo_summary", {})
    total = summary.get("total_commits", 0)
    authors = data.get("students", [])
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append(f"# 📊 Analyse Git — `{repo_name}`")
    lines.append(f"")
    lines.append(f"> Généré le {now}  ")
    lines.append(f"> **Total commits** : {total} | **Étudiants** : {len(authors)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Tableau résumé
    lines.append("## 📋 Résumé global")
    lines.append("")
    lines.append("| Étudiant | Commits | % | Lignes +/− | Msg /5 | Noms alternatifs | 🏆 Note /20 |")
    lines.append("|:---------|--------:|--:|-----------:|-------:|-----------------:|------------:|")

    for a in authors:
        name = a.get("display_name", "Inconnu")
        n = a.get("commit_count", 0)
        pct = a.get("commit_pct", 0)
        added = a.get("insertions", 0)
        removed = a.get("deletions", 0)
        msg = a.get("avg_message_score", 0)
        alt_names = a.get("alternate_names", [])
        
        # Calcul d'une note simplifiée sur 20
        note = round(min(20, (msg * 4)), 1)  # msg est sur 5
        emoji = note_emoji(note)
        
        # Colonne noms alternatifs
        alt_str = ", ".join(alt_names) if alt_names else "-"
        
        lines.append(
            f"| {name} | {n} | {pct:.1f}% | +{added}/−{removed} | "
            f"{msg:.1f}/5 {score_emoji(msg*2)} | {alt_str} | {emoji} **{note}** |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")

    # Détail par étudiant
    lines.append("## 👤 Détail par étudiant")
    lines.append("")

    for a in authors:
        name = a.get("display_name", "Inconnu")
        msg = a.get("avg_message_score", 0)
        note = round(min(20, (msg * 4)), 1)
        alt_names = a.get("alternate_names", [])
        
        lines.append(f"### {note_emoji(note)} {name} — {note}/20")
        lines.append("")
        lines.append(f"- **Clé canonique** : `{a.get('canonical_key', 'N/A')}`")
        
        # Afficher les noms alternatifs si présents
        if alt_names:
            lines.append(f"- **Noms alternatifs** : {', '.join(f'`{n}`' for n in alt_names)}")

        if a.get("first_commit") and a.get("last_commit"):
            fd = a["first_commit"][:10]
            ld = a["last_commit"][:10]
            lines.append(f"- **Activité** : du `{fd}` au `{ld}` ({a.get('frequency_label', 'N/A')})")

        lines.append(f"- **Commits** : {a.get('commit_count', 0)} ({a.get('commit_pct', 0):.1f}% du total)")
        if a.get("coauthored_commits", 0) > 0:
            lines.append(f"- **🤝 Co-auteur** : {a.get('coauthored_commits', 0)} commit(s) en pair programming détectés")
        lines.append(f"- **Lignes** : +{a.get('insertions', 0)} / −{a.get('deletions', 0)}")
        lines.append(f"- **Fichiers distincts** : {a.get('files_distinct', 0)}")
        lines.append(f"- **Qualité des messages** : {a.get('avg_message_score', 0):.1f}/5 {score_emoji(a.get('avg_message_score', 0)*2)}")

        # Alertes
        alerts = a.get("alerts", [])
        if alerts:
            lines.append("")
            lines.append("  **⚠️ Alertes :**")
            for alert in alerts:
                lines.append(f"  - {alert}")

        # Exemples de commits
        commits = a.get("commits", [])
        if commits:
            lines.append("")
            lines.append("  **Exemples de commits (3 derniers) :**")
            for c in commits[-3:]:
                date = c.get("date", "")[:10] if c.get("date") else ""
                score = c.get("score", 0)
                msg = c.get("message", "")[:60]
                lines.append(f"  - `{date}` [{score}/5] {msg}")

        lines.append("")

    lines.append("---")
    lines.append("")

    # Section alertes globales
    all_flags = [(a.get("display_name", "Inconnu"), f) for a in authors for f in a.get("red_flags", [])]
    if all_flags:
        lines.append("## ⚠️ Points d'attention pédagogiques")
        lines.append("")
        for name, flag in all_flags:
            lines.append(f"- **{name}** : {flag}")
        lines.append("")

    # Étudiants sans contribution (ni auteur ni co-auteur)
    no_commit = [a for a in authors if a.get("commit_count", 0) == 0 and a.get("coauthored_commits", 0) == 0]
    if no_commit:
        lines.append("## 🚨 Étudiants sans contribution")
        lines.append("")
        for a in no_commit:
            lines.append(f"- {a.get('display_name', 'Inconnu')} (`{a.get('canonical_key', '')}`)")
        lines.append("")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Rapport Markdown généré : {output_path}")
    return content


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_md.py <data.json> <repo_name> <output.md>")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)

    generate_markdown(data, sys.argv[2], sys.argv[3])
