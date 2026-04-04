#!/usr/bin/env bash
# Usage: bash extract_commits.sh [--include-merges] <repo_path> [branch]
# Output: TSV sur stdout : hash|author_name|author_email|date_iso|insertions|deletions|files_changed|message
# Par défaut, les merge commits sont EXCLUS des métriques (évite la double comptabilisation).
# Passer --include-merges pour les inclure (ils seront marqués avec le préfixe [merge]).
# Les trailers Co-authored-by sont détectés et génèrent des lignes TSV supplémentaires au même format,
# sans colonne `type` dédiée : hash synthétique suffixé par `_coauthor_...` et message préfixé par `[co-author]`.

REPO_PATH="."
BRANCH="HEAD"
INCLUDE_MERGES=""
POSITIONAL_COUNT=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --include-merges)
            INCLUDE_MERGES="--include-merges"
            ;;
        --)
            shift
            while [ "$#" -gt 0 ]; do
                POSITIONAL_COUNT=$((POSITIONAL_COUNT + 1))
                case "$POSITIONAL_COUNT" in
                    1) REPO_PATH="$1" ;;
                    2) BRANCH="$1" ;;
                    *)
                        echo "ERROR: too many arguments" >&2
                        echo "Usage: bash extract_commits.sh [--include-merges] <repo_path> [branch]" >&2
                        exit 1
                        ;;
                esac
                shift
            done
            break
            ;;
        -*)
            echo "ERROR: unknown option: $1" >&2
            echo "Usage: bash extract_commits.sh [--include-merges] <repo_path> [branch]" >&2
            exit 1
            ;;
        *)
            POSITIONAL_COUNT=$((POSITIONAL_COUNT + 1))
            case "$POSITIONAL_COUNT" in
                1) REPO_PATH="$1" ;;
                2) BRANCH="$1" ;;
                *)
                    echo "ERROR: too many arguments" >&2
                    echo "Usage: bash extract_commits.sh [--include-merges] <repo_path> [branch]" >&2
                    exit 1
                    ;;
            esac
            ;;
    esac
    shift
done

cd "$REPO_PATH" || { echo "ERROR: cannot cd to $REPO_PATH" >&2; exit 1; }

# Exclure les merge commits par défaut pour éviter la double comptabilisation
GIT_NO_MERGES=""
if [ "$INCLUDE_MERGES" != "--include-merges" ]; then
    GIT_NO_MERGES="--no-merges"
fi

git log "$BRANCH" $GIT_NO_MERGES \
  --format="COMMIT_SEP%H|%aN|%aE|%aI|%P|%s|%(trailers:key=Co-authored-by,valueonly,separator=%x09)" \
  --numstat \
  2>/dev/null | \
awk -v include_merges="$INCLUDE_MERGES" '
BEGIN { OFS="|"; hash=""; name=""; email=""; date=""; parents=""; msg=""; coauthors=""; ins=0; del=0; files=0 }

function is_merge(    nparents) {
    nparents = split(parents, p, " ")
    return nparents > 1
}

function print_commit(    n, i, cname, cemail, parts, label) {
    if (hash == "") return
    label = ""
    if (is_merge()) {
        if (include_merges != "--include-merges") return
        label = "[merge] "
    }
    print hash, name, email, date, ins, del, files, label msg
    # Parse Co-authored-by trailers (tab-separated "Name <email>" values from %(trailers:...))
    if (coauthors != "") {
        n = split(coauthors, parts, "\t")
        for (i = 1; i <= n; i++) {
            if (match(parts[i], /^([^<]*)<([^>]*)>/, arr)) {
                cname = arr[1]
                cemail = arr[2]
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", cname)
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", cemail)
                if (cemail != "") {
                    print hash "_coauthor_" cemail, cname, cemail, date, ins, del, files, "[co-author] " msg
                }
            }
        }
    }
}

/^COMMIT_SEP/ {
    print_commit()
    line = substr($0, length("COMMIT_SEP") + 1)
    n = split(line, parts, "|")
    hash = parts[1]; name = parts[2]; email = parts[3]; date = parts[4]; parents = parts[5]
    msg = parts[6]
    coauthors = (n >= 7) ? parts[7] : ""
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
