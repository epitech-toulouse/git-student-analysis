#!/usr/bin/env bash
# Usage: bash extract_commits.sh <repo_path> [branch] [--include-merges]
# Output: TSV sur stdout : hash|author_name|author_email|date_iso|insertions|deletions|files_changed|message
# Par défaut, les merge commits sont EXCLUS des métriques (évite la double comptabilisation).
# Passer --include-merges pour les inclure (ils seront marqués avec le préfixe [merge]).
# Co-authored-by trailers sont détectés et génèrent des lignes supplémentaires (type=coauthor)

REPO_PATH="${1:-.}"
BRANCH="${2:-HEAD}"
INCLUDE_MERGES="${3:-}"

cd "$REPO_PATH" || { echo "ERROR: cannot cd to $REPO_PATH" >&2; exit 1; }

# Exclure les merge commits par défaut pour éviter la double comptabilisation
GIT_NO_MERGES=""
if [ "$INCLUDE_MERGES" != "--include-merges" ]; then
    GIT_NO_MERGES="--no-merges"
fi

git log "$BRANCH" $GIT_NO_MERGES \
  --format="COMMIT_SEP%H|%aN|%aE|%aI|%P|%B" \
  --numstat \
  2>/dev/null | \
awk -v include_merges="$INCLUDE_MERGES" '
BEGIN { OFS="|"; hash=""; name=""; email=""; date=""; parents=""; msg=""; ins=0; del=0; files=0 }

function is_merge(    nparents) {
    nparents = split(parents, p, " ")
    return nparents > 1
}

function print_commit(    coauthor, parts, n, i, cname, cemail, label) {
    if (hash == "") return
    label = ""
    if (is_merge()) {
        if (include_merges != "--include-merges") return
        label = "[merge] "
    }
    print hash, name, email, date, ins, del, files, label msg
    # Parse Co-authored-by trailers from the full body
    n = split(msg, parts, "\n")
    for (i = 1; i <= n; i++) {
        coauthor = parts[i]
        if (match(coauthor, /^Co-authored-by:[[:space:]]*(.*)<(.*)>[[:space:]]*$/, arr)) {
            cname = arr[1]
            cemail = arr[2]
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", cname)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", cemail)
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
    line = substr($0, length("COMMIT_SEP") + 1)
    n = split(line, parts, "|")
    hash = parts[1]; name = parts[2]; email = parts[3]; date = parts[4]; parents = parts[5]
    msg = ""
    for (i=6; i<=n; i++) msg = msg (i>6 ? "|" : "") parts[i]
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
