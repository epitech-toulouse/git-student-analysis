#!/usr/bin/env bash
# Usage: bash extract_commits.sh <repo_path> [branch]
# Output: TSV sur stdout : hash|author_name|author_email|date_iso|insertions|deletions|files_changed|message
# Co-authored-by trailers sont détectés et génèrent des lignes supplémentaires (type=coauthor)

REPO_PATH="${1:-.}"
BRANCH="${2:-HEAD}"

cd "$REPO_PATH" || { echo "ERROR: cannot cd to $REPO_PATH" >&2; exit 1; }

git log "$BRANCH" \
  --format="COMMIT_SEP%H|%aN|%aE|%aI|%B" \
  --numstat \
  2>/dev/null | \
awk '
BEGIN { OFS="|"; hash=""; name=""; email=""; date=""; msg=""; ins=0; del=0; files=0 }

function print_commit(    coauthor, parts, n, i, cname, cemail) {
    if (hash == "") return
    print hash, name, email, date, ins, del, files, msg
    # Parse Co-authored-by trailers from the full body (stored in msg)
    n = split(msg, parts, "\n")
    for (i = 1; i <= n; i++) {
        coauthor = parts[i]
        if (match(coauthor, /^Co-authored-by:[[:space:]]*(.*)<(.*)>[[:space:]]*$/, arr)) {
            cname = arr[1]
            cemail = arr[2]
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", cname)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", cemail)
            # Emit a coauthor row sharing the same stats (attributed to the co-author)
            print hash "_coauthor_" cemail, cname, cemail, date, ins, del, files, "[co-author] " msg
        } else if (match(coauthor, /^Co-authored-by:[[:space:]]*(.+)<(.+)>/, arr)) {
            cname = arr[1]
            cemail = arr[2]
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", cname)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", cemail)
            print hash "_coauthor_" cemail, cname, cemail, date, ins, del, files, "[co-author] " msg
        }
    }
}

/^COMMIT_SEP/ {
    print_commit()
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
    print_commit()
}
'
