#!/bin/bash

# Prilchen LABS – Offline Translator
# Startet die grafische Oberfläche

BASE_DIR="$HOME/translator"

PYTHON="$BASE_DIR/venv/bin/python3"
GUI="$BASE_DIR/app/gui.py"

# Prüfen, ob Python vorhanden ist
if [ ! -x "$PYTHON" ]; then
    echo "Fehler: Python-Umgebung nicht gefunden!"
    exit 1
fi

# Prüfen, ob GUI vorhanden ist
if [ ! -f "$GUI" ]; then
    echo "Fehler: gui.py nicht gefunden!"
    exit 1
fi

# GUI starten
exec "$PYTHON" "$GUI"
