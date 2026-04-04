#!/usr/bin/env python3
"""
Analyse les commits extraits par extract_commits.sh.
Usage: python analyze.py commits_raw.tsv [mapping.csv] > report.json
"""
import sys, json, unicodedata, re, math
from collections import defaultdict
from datetime import datetime

GENERIC_EMAILS = {"", "noreply", "users.noreply.github.com"}
WEAK_MESSAGES = {"commit","update","fix","wip","test","ok","done",".","..","...","feat","add","init","initial"}

# Language-agnostic action verb detection (English + French)
_ACTION_VERBS_RE = re.compile(
    r"\b(add|fix|remove|update|refactor|implement|create|delete|change|improve|rename|move|merge|revert|"
    r"ajoute[rz]?|corrige[rz]?|supprime[rz]?|modifie[rz]?|impl[eé]mente[rz]?|cr[eé][eé][rz]?|"
    r"d[eé]place[rz]?|remplace[rz]?|r[eé]sou[st]|r[eé]soudre|r[eé][eé]crit|initialise[rz]?|int[eè]gre[rz]?)\b",
    re.IGNORECASE,
)

# Conventional Commits pattern (EN type names, case-insensitive, with optional scope and !)
_CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?!?:\s.{2,}",
    re.IGNORECASE,
)

# Alternative convention patterns: [TYPE] desc, #ref - desc, ALL_CAPS: desc
_ALT_CONVENTION_RE = re.compile(
    r"^(\[[A-Z][A-Z0-9_-]+\]\s.{5,}|#[A-Za-z0-9_-]+\s*-\s*.{5,}|[A-Z]{2}[A-Z0-9_]*:\s.{5,})"
)

def normalize_name(name: str) -> str:
    name = name.strip().lower()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = re.sub(r"\s+", " ", name)
    return name

def score_message(msg: str) -> int:
    msg = msg.strip()
    # Score 0: empty, ≤ 3 chars, or purely generic
    if len(msg) <= 3 or msg.lower() in WEAK_MESSAGES:
        return 0
    # Score 3: matches a clear convention (Conventional Commits or coherent alternative)
    if _CONVENTIONAL_RE.match(msg) or _ALT_CONVENTION_RE.match(msg):
        return 3
    # Score 2/3: has a recognizable verb → at least informative
    if _ACTION_VERBS_RE.search(msg):
        # Score 3 if long enough to be clearly contextual
        return 3 if len(msg) >= 40 else 2
    # Score 1: very short with no recognizable verb
    if len(msg) < 10:
        return 1
    # Score 2: long enough to be informative without a detected verb
    if len(msg) >= 40:
        return 2
    return 1

def load_mapping(path: str) -> dict:
    """CSV: email,canonical_name"""
    mapping = {}
    try:
        with open(path) as f:
            for line in f:
                parts = line.strip().split(",", 1)
                if len(parts) == 2:
                    mapping[parts[0].strip().lower()] = parts[1].strip()
    except FileNotFoundError:
        pass
    return mapping

def is_generic_email(email: str) -> bool:
    email = email.lower()
    return (not email or
            "noreply" in email or
            email.endswith("users.noreply.github.com"))

def canonical_key(name: str, email: str, mapping: dict) -> str:
    """Returns canonical key for grouping (email for non-generic, normalized name otherwise)"""
    email_l = email.lower()
    # Mapping manuel prioritaire
    if email_l in mapping:
        return email_l
    # Email non-générique → clé = email (ignore le nom pour permettre la fusion)
    if not is_generic_email(email):
        return email_l
    # Email générique → clé = nom normalisé
    return normalize_name(name)

def parse_tsv(path: str) -> list[dict]:
    commits = []
    with open(path) as f:
        for line in f:
            parts = line.rstrip("\n").split("|", 7)
            if len(parts) < 8:
                continue
            commits.append({
                "hash": parts[0],
                "author_name": parts[1],
                "author_email": parts[2],
                "date": parts[3],
                "insertions": int(parts[4]) if parts[4].isdigit() else 0,
                "deletions": int(parts[5]) if parts[5].isdigit() else 0,
                "files_changed": int(parts[6]) if parts[6].isdigit() else 0,
                "message": parts[7],
            })
    return commits

def _normalize_message_excerpt(message: str, max_len: int = 50) -> str:
    """Normalise un extrait de message pour l'inclure dans une question."""
    return message[:max_len].strip().replace("\n", " ").replace("\r", "").replace('"', "'")


def detect_suspicious_patterns(commits: list[dict], dates: list[datetime]) -> list[str]:
    """Détecte les patterns suspects et formule des questions à poser à l'étudiant."""
    questions = []

    # Trier chronologiquement pour que les séries soient détectées dans l'ordre naturel
    commits = sorted(commits, key=lambda c: c["date"])

    # 1. Messages identiques sur 3+ commits consécutifs
    messages = [c["message"].strip().lower() for c in commits]
    i = 0
    while i < len(messages) - 2:
        msg = messages[i]
        if msg and messages[i+1] == msg and messages[i+2] == msg:
            count = 3
            while i + count < len(messages) and messages[i + count] == msg:
                count += 1
            excerpt = _normalize_message_excerpt(commits[i]["message"])
            questions.append(
                f"❓ {count} commits consécutifs avec un message identique (\"{excerpt}\") "
                f"— ce message décrit-il vraiment {count} changements distincts ?"
            )
            i += count
        else:
            i += 1

    # 2. Micro-commits : séries consécutives de commits avec < 5 lignes modifiées
    micro_commit_max_changed_lines = 4
    micro_commit_min_run_length = 5
    run_start = None
    run_length = 0

    for idx, commit in enumerate(commits):
        changed_lines = commit["insertions"] + commit["deletions"]
        is_micro_commit = 0 < changed_lines <= micro_commit_max_changed_lines

        if is_micro_commit:
            if run_length == 0:
                run_start = idx
            run_length += 1
        else:
            if run_length >= micro_commit_min_run_length:
                run_excerpt = _normalize_message_excerpt(commits[run_start]["message"])
                questions.append(
                    f"❓ {run_length} micro-commits consécutifs détectés "
                    f"(< {micro_commit_max_changed_lines + 1} lignes modifiées chacun) "
                    f"(à partir de \"{run_excerpt}\") "
                    f"— s'agit-il d'un découpage intentionnel du travail ou d'une séquence de corrections ?"
                )
            run_start = None
            run_length = 0

    if run_length >= micro_commit_min_run_length:
        run_excerpt = _normalize_message_excerpt(commits[run_start]["message"])
        questions.append(
            f"❓ {run_length} micro-commits consécutifs détectés "
            f"(< {micro_commit_max_changed_lines + 1} lignes modifiées chacun) "
            f"(à partir de \"{run_excerpt}\") "
            f"— s'agit-il d'un découpage intentionnel du travail ou d'une séquence de corrections ?"
        )

    # 3. Burst > 10 commits en < 30 minutes — sliding window O(n)
    burst_window_minutes = 30
    min_burst_commits = 11  # strictement > 10 commits
    if len(dates) >= min_burst_commits:
        dates_sorted = sorted(dates)
        left = 0
        max_burst_size = 0
        max_burst_start = 0
        max_burst_end = 0

        for right in range(len(dates_sorted)):
            while (dates_sorted[right] - dates_sorted[left]).total_seconds() / 60 >= burst_window_minutes:
                left += 1
            window_size = right - left + 1
            if window_size > max_burst_size:
                max_burst_size = window_size
                max_burst_start = left
                max_burst_end = right

        if max_burst_size >= min_burst_commits:
            delta_minutes = (dates_sorted[max_burst_end] - dates_sorted[max_burst_start]).total_seconds() / 60
            if delta_minutes < 1:
                duration_phrase = "en moins d'une minute"
            elif delta_minutes < 10:
                duration_phrase = f"en {delta_minutes:.1f} minutes"
            else:
                duration_phrase = f"en {math.ceil(delta_minutes)} minutes"

            questions.append(
                f"❓ {max_burst_size} commits {duration_phrase} "
                f"(autour du {dates_sorted[max_burst_start].strftime('%Y-%m-%d %H:%M')}) "
                f"— ce backlog de commits correspond-il à du travail effectué progressivement ?"
            )

    return questions


def detect_bursts(dates: list[datetime], threshold_hours: int = 1, min_commits: int = 5) -> list[str]:
    alerts = []
    dates_sorted = sorted(dates)
    for i in range(len(dates_sorted) - min_commits + 1):
        window = dates_sorted[i:i + min_commits]
        delta = (window[-1] - window[0]).total_seconds() / 3600
        if delta <= threshold_hours:
            alerts.append(f"{min_commits} commits en {delta:.1f}h autour du {window[0].strftime('%Y-%m-%d %H:%M')}")
            break
    return alerts

def select_canonical_name(commits_list: list[dict]) -> str:
    """Sélectionne le nom le plus fréquent parmi les commits"""
    from collections import Counter
    name_counts = Counter(c["author_name"] for c in commits_list)
    # Retourner le nom le plus fréquent (ou le plus récent en cas d'égalité)
    return name_counts.most_common(1)[0][0]

def analyze(tsv_path: str, mapping_path: str = None) -> dict:
    mapping = load_mapping(mapping_path) if mapping_path else {}
    commits = parse_tsv(tsv_path)

    if not commits:
        return {"error": "Aucun commit trouvé dans le fichier TSV."}

    # Group by canonical key (now string, not tuple)
    groups: dict[str, list] = defaultdict(list)
    all_names_by_key: dict[str, set] = defaultdict(set)  # Track all names used per key
    
    for c in commits:
        key = canonical_key(c["author_name"], c["author_email"], mapping)
        groups[key].append(c)
        all_names_by_key[key].add(c["author_name"])
    
    # Determine canonical display name for each key (most frequent name)
    canonical_names: dict[str, str] = {}
    for key, clist in groups.items():
        # Si mapping manuel existe, utiliser le nom du mapping
        if key in mapping:
            canonical_names[key] = mapping[key]
        else:
            canonical_names[key] = select_canonical_name(clist)

    total_commits = len(commits)
    all_dates = [datetime.fromisoformat(c["date"]) for c in commits if c["date"]]
    project_start = min(all_dates) if all_dates else None
    project_end = max(all_dates) if all_dates else None
    project_days = max(1, (project_end - project_start).days) if project_start and project_end else 1

    students = []
    for key, clist in groups.items():
        dates = []
        for c in clist:
            try:
                dates.append(datetime.fromisoformat(c["date"]))
            except Exception:
                pass

        scores = [score_message(c["message"]) for c in clist]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0

        first_commit = min(dates).isoformat() if dates else None
        last_commit = max(dates).isoformat() if dates else None

        bursts = detect_bursts(dates)

        # Frequency pattern
        n = len(clist)
        if dates:
            span_days = max(1, (max(dates) - min(dates)).days)
            commits_in_last_quarter = sum(1 for d in dates if (project_end - d).days <= project_days // 4)
            if commits_in_last_quarter / n > 0.7:
                freq_label = "rush en fin de projet"
            elif span_days <= 2:
                freq_label = "concentrée sur 1–2 jours"
            else:
                freq_label = "régulière"
        else:
            freq_label = "inconnue"

        # Count distinct files
        files_set = set()
        for c in clist:
            files_set.add(c.get("hash", "")[:8])  # Approximation via hash
        
        # Alerts
        alerts = []
        if freq_label == "rush en fin de projet":
            alerts.append(f"Activité concentrée en fin de projet ({commits_in_last_quarter} commits sur dernier quart)")
        elif freq_label == "concentrée sur 1–2 jours":
            alerts.append(f"Activité concentrée ({freq_label})")
        if bursts:
            alerts.extend(bursts)

        # Suspicious patterns (questions à poser, pas des accusations)
        suspicious_questions = detect_suspicious_patterns(clist, dates)
        if suspicious_questions:
            alerts.extend(suspicious_questions)
        
        # Check for name variations
        name_variations = list(all_names_by_key[key])
        if len(name_variations) > 1:
            alerts.append(f"Plusieurs noms détectés: {', '.join(sorted(name_variations))}")

        student = {
            "canonical_key": key,
            "display_name": canonical_names[key],
            "alternate_names": sorted(name_variations) if len(name_variations) > 1 else [],
            "commit_count": n,
            "commit_pct": round(100 * n / total_commits, 1),
            "insertions": sum(c["insertions"] for c in clist),
            "deletions": sum(c["deletions"] for c in clist),
            "files_distinct": len(files_set),
            "first_commit": first_commit,
            "last_commit": last_commit,
            "frequency_label": freq_label,
            "avg_message_score": avg_score,
            "alerts": alerts,
            "suspicious_patterns": suspicious_questions,
            "commits": [
                {
                    "hash": c["hash"][:8],
                    "date": c["date"],
                    "message": c["message"],
                    "score": score_message(c["message"]),
                }
                for c in clist
            ],
        }
        students.append(student)

    students.sort(key=lambda s: s["commit_count"], reverse=True)

    return {
        "repo_summary": {
            "total_commits": total_commits,
            "project_start": project_start.isoformat() if project_start else None,
            "project_end": project_end.isoformat() if project_end else None,
            "project_days": project_days,
            "authors_raw": sum(len(all_names_by_key[k]) for k in groups.keys()),
            "authors_deduplicated": len(groups),
        },
        "students": students,
    }

if __name__ == "__main__":
    tsv = sys.argv[1] if len(sys.argv) > 1 else "/tmp/commits_raw.tsv"
    mapping = sys.argv[2] if len(sys.argv) > 2 else None
    result = analyze(tsv, mapping)
    print(json.dumps(result, ensure_ascii=False, indent=2))
