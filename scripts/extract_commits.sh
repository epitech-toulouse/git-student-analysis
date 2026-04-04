#!/usr/bin/env bash
# Usage: bash extract_commits.sh <repo_path> [branch]
# Output: TSV sur stdout : hash|author_name|author_email|date_iso|insertions|deletions|files_changed|message

REPO_PATH="${1:-.}"
BRANCH="${2:-HEAD}"

cd "$REPO_PATH" || { echo "ERROR: cannot cd to $REPO_PATH" >&2; exit 1; }

git log "$BRANCH" \
  --format="COMMIT_SEP%H|%aN|%aE|%aI|%s" \
  --numstat \
  2>/dev/null | \
awk '
BEGIN { OFS="|"; hash=""; name=""; email=""; date=""; msg=""; ins=0; del=0; files=0 }
/^COMMIT_SEP/ {
    if (hash != "") {
        print hash, name, email, date, ins, del, files, msg
    }
    line = substr($0, 12)
    n = split(line, parts, "|")
    hash = parts[1]; name = parts[2]; email = parts[3]; date = parts[4]
    msg = ""
    for (i=5; i<=n; i++) msg = msg (i>5 ? "|" : "") parts[i]
    ins=0; del=0; files=0
    next
}
/^[0-9]/ {
    ins += $1; del += $2; files++; next
}
/^-/ {
    files++; next
}
END {
    if (hash != "") print hash, name, email, date, ins, del, files, msg
}
'
