# translator.example.py
# Beispiel-Konfiguration für den Prilchen LABS Offline-Übersetzer

from pathlib import Path

# --------------------------------------------------
# Verzeichnisse
# --------------------------------------------------

BASE_DIR = Path.home() / "translator"
WORK_DIR = BASE_DIR / "work"
LOG_FILE = BASE_DIR / "log" / "translator.log"

# --------------------------------------------------
# Whisper.cpp – Spracherkennung
# --------------------------------------------------

WHISPER_BIN = Path.home() / "whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = Path.home() / "whisper.cpp/models/ggml-base.bin"

# --------------------------------------------------
# Ollama – Übersetzung
# --------------------------------------------------

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"
OLLAMA_TIMEOUT = 180

# --------------------------------------------------
# Mikrofon und Lautsprecher
# --------------------------------------------------

MIC_DEVICE = "plughw:2,0"
PLAYBACK_DEVICE = "default"

# --------------------------------------------------
# Piper – Sprachausgabe
# --------------------------------------------------

PIPER_BIN = BASE_DIR / "venv" / "bin" / "piper"

PIPER_VOICE_DE = (
    BASE_DIR / "voices/de/de_DE-thorsten-medium.onnx"
)

PIPER_VOICE_EN = (
    BASE_DIR / "voices/en/en_GB-alan-medium.onnx"
)

# --------------------------------------------------
# Allgemeine Einstellungen
# --------------------------------------------------

RECORDING_SECONDS = 7
SAMPLE_RATE = 16000
CHANNELS = 1
