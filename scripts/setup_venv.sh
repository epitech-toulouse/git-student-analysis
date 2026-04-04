#!/bin/bash
# Script pour gérer le venv Python du skill git-student-analysis
# Crée automatiquement le venv et installe les dépendances si nécessaire

set -e

# Déterminer le dossier du skill
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$SKILL_DIR/.venv"
REQUIREMENTS="pandas openpyxl python-dateutil"

# Couleurs pour output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour créer le venv
create_venv() {
    echo -e "${YELLOW}🔧 Création du venv Python pour git-student-analysis...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Venv créé dans $VENV_DIR${NC}"
}

# Fonction pour installer les dépendances
install_dependencies() {
    echo -e "${YELLOW}📦 Installation des dépendances Python...${NC}"
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet $REQUIREMENTS
    echo -e "${GREEN}✅ Dépendances installées : $REQUIREMENTS${NC}"
}

# Vérifier si le venv existe
if [ ! -d "$VENV_DIR" ]; then
    create_venv
    install_dependencies
else
    # Vérifier si les dépendances sont installées
    if ! "$VENV_DIR/bin/python3" -c "import pandas, openpyxl" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Dépendances manquantes, réinstallation...${NC}"
        install_dependencies
    fi
fi

# Exporter le chemin du Python du venv
export PYTHON_BIN="$VENV_DIR/bin/python3"
export PIP_BIN="$VENV_DIR/bin/pip"

# Si appelé directement (pas sourcé), afficher le chemin
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo "$PYTHON_BIN"
fi
