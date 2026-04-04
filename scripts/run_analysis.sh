#!/bin/bash
# Script principal pour analyser un repo Git
# Gère le venv, extrait les commits, génère les rapports
# Usage: ./run_analysis.sh <repo_path> [branch]

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Déterminer les chemins
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_PATH="${1:-.}"  # Par défaut le dossier courant
BRANCH="${2:-main}"  # Par défaut main
DATE=$(date +%Y-%m-%d)

# Setup du venv
echo -e "${BLUE}🔧 Configuration de l'environnement Python...${NC}"
source "$SCRIPT_DIR/setup_venv.sh"

# Aller dans le repo
cd "$REPO_PATH"
REPO_ROOT="$(pwd)"
REPO_NAME="$(basename "$REPO_ROOT")"

echo -e "${BLUE}📂 Analyse du repo: $REPO_NAME${NC}"
echo -e "${BLUE}📂 Chemin: $REPO_ROOT${NC}"
echo -e "${BLUE}🌿 Branche: $BRANCH${NC}"
echo ""

# Créer dossier temporaire pour fichiers intermédiaires
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Étape 1: Extraire les commits
echo -e "${YELLOW}1️⃣  Extraction des commits...${NC}"
bash "$SCRIPT_DIR/extract_commits.sh" "$REPO_ROOT" "$BRANCH" > "$TMP_DIR/commits_raw.tsv"
COMMIT_COUNT=$(wc -l < "$TMP_DIR/commits_raw.tsv")
echo -e "${GREEN}✅ $COMMIT_COUNT commits extraits${NC}"
echo ""

# Étape 2: Analyser les données
echo -e "${YELLOW}2️⃣  Analyse des contributions...${NC}"
"$PYTHON_BIN" "$SCRIPT_DIR/analyze.py" "$TMP_DIR/commits_raw.tsv" > "$TMP_DIR/analysis.json"
echo -e "${GREEN}✅ Analyse terminée${NC}"
echo ""

# Étape 3: Générer le rapport Markdown
echo -e "${YELLOW}3️⃣  Génération du rapport Markdown...${NC}"
MD_OUTPUT="$REPO_ROOT/git-analysis-report-$DATE.md"
"$PYTHON_BIN" "$SCRIPT_DIR/generate_md.py" "$TMP_DIR/analysis.json" "$REPO_NAME" "$MD_OUTPUT"
if [ -f "$MD_OUTPUT" ]; then
    echo -e "${GREEN}✅ Rapport Markdown: $MD_OUTPUT${NC}"
else
    echo -e "${RED}❌ Erreur lors de la génération du rapport Markdown${NC}"
fi
echo ""

# Étape 4: Générer le fichier Excel
echo -e "${YELLOW}4️⃣  Génération du fichier Excel...${NC}"
XLSX_OUTPUT="$REPO_ROOT/git-analysis-report-$DATE.xlsx"
"$PYTHON_BIN" "$SCRIPT_DIR/generate_xlsx.py" "$TMP_DIR/analysis.json" "$XLSX_OUTPUT"
if [ -f "$XLSX_OUTPUT" ]; then
    echo -e "${GREEN}✅ Fichier Excel: $XLSX_OUTPUT${NC}"
else
    echo -e "${RED}❌ Erreur lors de la génération du fichier Excel${NC}"
fi
echo ""

# Résumé final
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Analyse terminée !${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "📄 Rapport Markdown : ${BLUE}$MD_OUTPUT${NC}"
echo -e "📊 Fichier Excel    : ${BLUE}$XLSX_OUTPUT${NC}"
echo ""
