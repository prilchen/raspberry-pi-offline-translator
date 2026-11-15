#!/bin/bash

BASE_DIR="$HOME/translator"
cd "$BASE_DIR"
exec "$BASE_DIR/venv/bin/python3" "$BASE_DIR/app/gui.py"
