#!/usr/bin/env python3
"""Lokaler Sprachübersetzer für Raspberry Pi.

Ablauf:
1. Sprache mit arecord aufnehmen
2. Aufnahme mit whisper.cpp transkribieren
3. Text lokal über Ollama/Gemma übersetzen
4. Übersetzung mit Piper ausgeben

Die Audio- und Text-Zwischendateien werden nach dem Durchlauf gelöscht.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence

import requests


# ---------------------------------------------------------------------------
# Pfade und Einstellungen
# ---------------------------------------------------------------------------

BASE = Path.home() / "translator"
WORK = BASE / "work"
LOG = BASE / "log" / "translator.log"

WHISPER = Path.home() / "whisper.cpp" / "build" / "bin" / "whisper-cli"
WHISPER_MODEL = Path.home() / "whisper.cpp" / "models" / "ggml-base.bin"

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
GEMMA_MODEL = "gemma3:1b"

# Hier die Audio-Geräte des eigenen Raspberry Pi eintragen.
# Verfügbare Geräte lassen sich z. B. mit `arecord -l` und `aplay -l` anzeigen.
MIC_DEVICE = "plughw:2,0"
PLAYBACK_DEVICE = "default"

PIPER = BASE / "venv" / "bin" / "piper"

VOICES = {
    "de": BASE / "voices" / "de" / "de_DE-thorsten-medium.onnx",
    "en": BASE / "voices" / "en" / "en_GB-alan-medium.onnx",
}

LANGUAGE_NAMES = {
    "de": "Deutsch",
    "en": "Englisch",
}


# ---------------------------------------------------------------------------
# Verzeichnisse und Protokollierung
# ---------------------------------------------------------------------------

WORK.mkdir(parents=True, exist_ok=True)
LOG.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def run(
    cmd: Sequence[object],
    input_text: Optional[str] = None,
) -> subprocess.CompletedProcess:
    """Führt einen externen Befehl aus und protokolliert Fehler."""
    command = [str(item) for item in cmd]
    logging.info("Starte Befehl: %s", " ".join(command))

    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Programm nicht gefunden: {command[0]}"
        ) from exc

    if result.stdout:
        logging.info("STDOUT: %s", result.stdout.strip())

    if result.stderr:
        logging.info("STDERR: %s", result.stderr.strip())

    if result.returncode != 0:
        error_text = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(
            f"Befehl fehlgeschlagen (Exit-Code {result.returncode}): "
            f"{' '.join(command)}\n{error_text}"
        )

    return result


def check_required_files() -> None:
    """Prüft zentrale Dateien, bevor die Aufnahme gestartet wird."""
    required = {
        "Whisper-Programm": WHISPER,
        "Whisper-Sprachmodell": WHISPER_MODEL,
        "Piper-Programm": PIPER,
    }

    for description, path in required.items():
        if not path.is_file():
            raise FileNotFoundError(
                f"{description} nicht gefunden: {path}"
            )


# ---------------------------------------------------------------------------
# Aufnahme und Spracherkennung
# ---------------------------------------------------------------------------

def record(seconds: int) -> Path:
    """Nimmt über arecord eine WAV-Datei mit 16 kHz/Mono auf."""
    if seconds < 1:
        raise ValueError("Die Aufnahmedauer muss mindestens 1 Sekunde betragen.")

    wav_file = WORK / "input.wav"
    wav_file.unlink(missing_ok=True)

    run([
        "arecord",
        "-D", MIC_DEVICE,
        "-f", "S16_LE",
        "-r", "16000",
        "-c", "1",
        "-d", seconds,
        wav_file,
    ])

    if not wav_file.is_file() or wav_file.stat().st_size < 1000:
        raise RuntimeError("Die Aufnahme fehlt oder ist ungewöhnlich klein.")

    return wav_file


def transcribe(wav_file: Path, language: str) -> str:
    """Wandelt die WAV-Aufnahme mit whisper.cpp in Text um."""
    transcript_base = WORK / "transcript"
    transcript_file = transcript_base.with_suffix(".txt")
    transcript_file.unlink(missing_ok=True)

    run([
        WHISPER,
        "-m", WHISPER_MODEL,
        "-f", wav_file,
        "-l", language,
        "-nt",
        "-otxt",
        "-of", transcript_base,
    ])

    if not transcript_file.is_file():
        raise RuntimeError("Whisper hat keine Textdatei erzeugt.")

    recognized_text = transcript_file.read_text(
        encoding="utf-8",
        errors="replace",
    ).strip()

    if not recognized_text:
        raise RuntimeError("Whisper hat keinen verständlichen Text erkannt.")

    return recognized_text


# ---------------------------------------------------------------------------
# Übersetzung mit Ollama
# ---------------------------------------------------------------------------

def translate(text: str, target: str) -> str:
    """Übersetzt den erkannten Text lokal über die Ollama-API."""
    if target not in LANGUAGE_NAMES:
        raise ValueError(f"Nicht unterstützte Zielsprache: {target}")

    target_language = LANGUAGE_NAMES[target]
    prompt = (
        f"Übersetze den folgenden Text exakt ins {target_language}. "
        "Gib ausschließlich die Übersetzung aus, ohne Erklärung, "
        "Anführungszeichen oder Präfix.\n\n"
        f"Text:\n{text}"
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": GEMMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=180,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Ollama ist nicht erreichbar oder hat einen Fehler gemeldet: {exc}"
        ) from exc
    except ValueError as exc:
        raise RuntimeError("Ollama hat keine gültige JSON-Antwort geliefert.") from exc

    translated_text = result.get("response", "").strip()
    if not translated_text:
        raise RuntimeError("Gemma hat keine Übersetzung geliefert.")

    return translated_text


# ---------------------------------------------------------------------------
# Sprachausgabe mit Piper
# ---------------------------------------------------------------------------

def speak(text: str, target: str) -> Path:
    """Erzeugt mit Piper eine WAV-Datei und spielt sie ab."""
    if target not in VOICES:
        raise ValueError(f"Keine Piper-Stimme für Sprache '{target}' konfiguriert.")

    voice_model = VOICES[target]
    voice_config = Path(str(voice_model) + ".json")

    if not voice_model.is_file():
        raise FileNotFoundError(f"Piper-Sprachmodell fehlt: {voice_model}")

    if not voice_config.is_file():
        raise FileNotFoundError(
            f"Piper-Konfigurationsdatei fehlt: {voice_config}"
        )

    if not PIPER.is_file():
        raise FileNotFoundError(f"Piper-Programm fehlt: {PIPER}")

    output_file = WORK / "translation.wav"
    output_file.unlink(missing_ok=True)

    run([
        PIPER,
        "--model", voice_model,
        "--output_file", output_file,
    ], input_text=text)

    if not output_file.is_file() or output_file.stat().st_size < 1000:
        raise RuntimeError("Piper hat keine gültige Audiodatei erzeugt.")

    run([
        "aplay",
        "-D", PLAYBACK_DEVICE,
        output_file,
    ])

    return output_file


# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lokaler Sprachübersetzer mit Whisper, Ollama und Piper."
    )
    parser.add_argument(
        "--from",
        dest="source",
        choices=["de", "en"],
        required=True,
        help="Gesprochene Ausgangssprache: de oder en",
    )
    parser.add_argument(
        "--to",
        dest="target",
        choices=["de", "en"],
        required=True,
        help="Zielsprache: de oder en",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=7,
        help="Aufnahmedauer in Sekunden (Standard: 7)",
    )

    args = parser.parse_args()

    if args.source == args.target:
        parser.error("Quell- und Zielsprache müssen verschieden sein.")

    if args.seconds < 1:
        parser.error("--seconds muss mindestens 1 sein.")

    temporary_files = [
        WORK / "input.wav",
        WORK / "transcript.txt",
        WORK / "translation.wav",
    ]

    try:
        check_required_files()

        print("Aufnahme startet ...")
        recording = record(args.seconds)

        print("Spracherkennung läuft ...")
        recognized_text = transcribe(recording, args.source)
        print("Erkannt:", recognized_text)

        print("Übersetzung läuft ...")
        translated_text = translate(recognized_text, args.target)
        print("Übersetzt:", translated_text)

        print("Sprachausgabe startet ...")
        speak(translated_text, args.target)

        print("Übersetzung abgeschlossen.")
        return 0

    except Exception as exc:
        logging.exception("Fehler bei der Übersetzung")
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 1

    finally:
        # Temporäre Sprach- und Textdateien nach dem Durchlauf entfernen.
        for file_path in temporary_files:
            try:
                file_path.unlink(missing_ok=True)
            except OSError:
                logging.exception(
                    "Temporäre Datei konnte nicht gelöscht werden: %s",
                    file_path,
                )


if __name__ == "__main__":
    raise SystemExit(main())

