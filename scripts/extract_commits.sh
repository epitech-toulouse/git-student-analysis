#!/usr/bin/env bash
# Usage: bash extract_commits.sh <repo_path> [branch]
# Output: TSV sur stdout : hash|author_name|author_email|date_iso|insertions|deletions|files_changed|row_type|message
#
# Contrat de sortie : 1 ligne = 1 contribution (auteur ou co-auteur), pas 1 ligne = 1 commit.
# Un commit avec co-auteurs produit plusieurs lignes partageant le même hash :
#   - row_type=author   : ligne canonique du commit
#   - row_type=coauthor : ligne supplémentaire pour chaque co-auteur (pair programming)
# Pour compter les commits uniques, filtrer row_type=author ; ne pas utiliser wc -l sur tout le TSV.
# Note: row_type est placé AVANT message pour que message (qui peut contenir '|') reste en dernière colonne.
#
# Prérequis : git >= 2.18 (pour %(trailers:...))

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

# Vérifier la version de git (%(trailers:...) requiert git >= 2.18)
_git_version=$(git --version | awk '{print $3}')
_git_major=$(echo "$_git_version" | cut -d. -f1)
_git_minor=$(echo "$_git_version" | cut -d. -f2)
if [ "$_git_major" -lt 2 ] || { [ "$_git_major" -eq 2 ] && [ "$_git_minor" -lt 18 ]; }; then
    echo "ERROR: git >= 2.18 requis pour %(trailers:...). Version actuelle : $_git_version" >&2
    exit 1
fi

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
    print hash, name, email, date, ins, del, files, "author", msg
    if (coauthors == "") return
    n = split(coauthors, parts, "\034")
    for (i = 1; i <= n; i++) {
        val = trim(parts[i])
        if (match(val, /^(.+)<(.+)>$/, arr)) {
            cname = trim(arr[1])
            cemail = trim(arr[2])
            if (cemail != "")
                print hash, cname, cemail, date, ins, del, files, "coauthor", msg
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
