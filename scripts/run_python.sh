#!/bin/bash
# Wrapper pour exécuter les scripts Python avec le venv du skill

set -e

# Sourcer le setup du venv
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/setup_venv.sh"

# Exécuter le script Python demandé avec le Python du venv
PYTHON_SCRIPT="$1"
shift  # Retirer le premier argument

if [ -z "$PYTHON_SCRIPT" ]; then
    echo "Usage: $0 <python_script.py> [args...]"
    exit 1
fi

# Exécuter avec le Python du venv
exec "$PYTHON_BIN" "$SCRIPT_DIR/$PYTHON_SCRIPT" "$@"
