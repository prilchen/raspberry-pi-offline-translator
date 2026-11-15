#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Grafische Oberfläche für den Prilchen-LABS-Offline-Übersetzer.

Erwartete Verzeichnisstruktur:
    ~/translator/
    ├── app/
    │   ├── gui.py
    │   └── translator.py
    └── venv/
        └── bin/
            └── python

Start:
    ~/translator/venv/bin/python ~/translator/app/gui.py
"""

import subprocess
import threading
import tkinter as tk
from pathlib import Path

BASE_DIR = Path.home() / "translator"
PYTHON = BASE_DIR / "venv" / "bin" / "python3"
TRANSLATOR_SCRIPT = BASE_DIR / "app" / "translator.py"

AUFNAHME_SEKUNDEN = 7


def schreibe_text(text: str) -> None:
    """Schreibt Text im Tkinter-Hauptthread in das Ausgabefeld."""
    text_feld.insert(tk.END, text)
    text_feld.see(tk.END)


def setze_buttons_aktiv(aktiv: bool) -> None:
    """Aktiviert oder sperrt beide Übersetzungsschaltflächen."""
    status = tk.NORMAL if aktiv else tk.DISABLED
    button_de_en.config(state=status)
    button_en_de.config(state=status)


def starte_uebersetzung(quellsprache: str, zielsprache: str) -> None:
    """Startet den Übersetzer in einem Hintergrund-Thread."""
    setze_buttons_aktiv(False)
    text_feld.delete("1.0", tk.END)
    schreibe_text(
        f"Übersetzung {quellsprache.upper()} → {zielsprache.upper()}\n"
        f"Aufnahme läuft ... Bitte {AUFNAHME_SEKUNDEN} Sekunden sprechen!\n\n"
    )

    def aufgabe() -> None:
        try:
            if not PYTHON.is_file():
                raise FileNotFoundError(
                    f"Python-Umgebung nicht gefunden: {PYTHON}\n"
                    "Bitte zuerst die virtuelle Umgebung installieren."
                )

            if not TRANSLATOR_SCRIPT.is_file():
                raise FileNotFoundError(
                    f"Übersetzer-Skript nicht gefunden: {TRANSLATOR_SCRIPT}"
                )

            befehl = [
                str(PYTHON),
                str(TRANSLATOR_SCRIPT),
                "--from", quellsprache,
                "--to", zielsprache,
                "--seconds", str(AUFNAHME_SEKUNDEN),
            ]

            prozess = subprocess.Popen(
                befehl,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            if prozess.stdout is not None:
                for zeile in prozess.stdout:
                    root.after(0, schreibe_text, zeile)

            rueckgabewert = prozess.wait()

            if rueckgabewert == 0:
                root.after(0, schreibe_text, "\nÜbersetzung abgeschlossen.\n")
            else:
                root.after(
                    0,
                    schreibe_text,
                    f"\nDer Übersetzer wurde mit Fehlercode {rueckgabewert} beendet.\n",
                )

        except Exception as fehler:
            root.after(0, schreibe_text, f"\nFehler: {fehler}\n")

        finally:
            root.after(0, setze_buttons_aktiv, True)

    threading.Thread(target=aufgabe, daemon=True).start()


# -------------------- Fenster aufbauen --------------------

root = tk.Tk()
root.title("Prilchen LABS – Offline-Übersetzer")
root.geometry("520x380")
root.minsize(420, 320)

# Für ein LCD im Vollbildmodus die folgende Zeile aktivieren:
# root.attributes("-fullscreen", True)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=12)

button_de_en = tk.Button(
    frame_buttons,
    text="DE → EN",
    font=("Arial", 20, "bold"),
    width=10,
    height=2,
    command=lambda: starte_uebersetzung("de", "en"),
)
button_de_en.pack(side=tk.LEFT, padx=10)

button_en_de = tk.Button(
    frame_buttons,
    text="EN → DE",
    font=("Arial", 20, "bold"),
    width=10,
    height=2,
    command=lambda: starte_uebersetzung("en", "de"),
)
button_en_de.pack(side=tk.LEFT, padx=10)

frame_ausgabe = tk.Frame(root)
frame_ausgabe.pack(padx=10, pady=(4, 10), fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_ausgabe)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_feld = tk.Text(
    frame_ausgabe,
    font=("Arial", 12),
    wrap=tk.WORD,
    height=8,
    yscrollcommand=scrollbar.set,
)
text_feld.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=text_feld.yview)

schreibe_text("Bereit. Bitte eine Übersetzungsrichtung auswählen.\n")

root.mainloop()
