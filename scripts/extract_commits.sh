#!/usr/bin/env bash
# Usage: bash extract_commits.sh <repo_path> [branch]
# Output: TSV sur stdout : hash|author_name|author_email|date_iso|insertions|deletions|files_changed|message|row_type
# row_type=author pour les commits normaux, row_type=coauthor pour les lignes de co-auteurs (pair programming)

REPO_PATH="${1:-.}"
BRANCH="${2:-HEAD}"

cd "$REPO_PATH" || { echo "ERROR: cannot cd to $REPO_PATH" >&2; exit 1; }

# Format : COMMIT_SEP<hash>|<name>|<email>|<date>|<sujet>\x1E<co-auteurs séparés par \x1C>
# \x1E (RS) sépare le sujet des trailers ; \x1C (FS) sépare plusieurs co-auteurs
git log "$BRANCH" \
  --format="COMMIT_SEP%H|%aN|%aE|%aI|%s%x1E%(trailers:key=Co-authored-by,valueonly,separator=%x1C)" \
  --numstat \
  2>/dev/null | \
awk '
BEGIN { OFS="|"; hash=""; name=""; email=""; date=""; msg=""; coauthors=""; ins=0; del=0; files=0 }

function trim(s) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", s); return s }

function print_commit(    i, n, parts, val, cname, cemail) {
    if (hash == "") return
    print hash, name, email, date, ins, del, files, msg, "author"
    if (coauthors == "") return
    n = split(coauthors, parts, "\034")
    for (i = 1; i <= n; i++) {
        val = trim(parts[i])
        if (match(val, /^(.+)<(.+)>$/, arr)) {
            cname = trim(arr[1])
            cemail = trim(arr[2])
            if (cemail != "")
                print hash, cname, cemail, date, ins, del, files, msg, "coauthor"
        }
    }
}

/^COMMIT_SEP/ {
    print_commit()
    line = substr($0, length("COMMIT_SEP") + 1)
    # Séparer le sujet des trailers au niveau du séparateur RS (\036)
    rs_idx = index(line, "\036")
    if (rs_idx > 0) {
        main_part = substr(line, 1, rs_idx - 1)
        coauthors  = substr(line, rs_idx + 1)
    } else {
        main_part = line
        coauthors  = ""
    }
    n = split(main_part, parts, "|")
    hash = parts[1]; name = parts[2]; email = parts[3]; date = parts[4]
    msg = ""
    for (i = 5; i <= n; i++) msg = msg (i > 5 ? "|" : "") parts[i]
    ins=0; del=0; files=0
    next
}
$0 ~ /^([0-9]+|-)\t([0-9]+|-)\t/ {
    if ($1 != "-") ins += $1
    if ($2 != "-") del += $2
    files++; next
}
END { print_commit() }
'
