#!/usr/bin/env python3
import argparse, logging, subprocess, sys
from pathlib import Path
import requests

BASE = Path.home() / "translator"
WORK = BASE / "work"
LOG = BASE / "log/translator.log"
WHISPER = Path.home() / "whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = Path.home() / "whisper.cpp/models/ggml-base.bin"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
GEMMA_MODEL = "gemma3:1b"

# HIER DEINE AUDIO-GERÄTE EINTRAGEN:
MIC_DEVICE = "plughw:2,0"
PLAYBACK_DEVICE = "default"

VOICES = {
"de": BASE / "voices/de/de_DE-thorsten-medium.onnx",
"en": BASE / "voices/en/en_GB-alan-medium.onnx",
}

WORK.mkdir(parents=True, exist_ok=True)
LOG.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=LOG, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def run(cmd, input_text=None):
cmd=[str(x) for x in cmd]
logging.info("CMD: %s", " ".join(cmd))
r=subprocess.run(cmd,input=input_text,text=True,capture_output=True)
if r.stdout: logging.info("STDOUT: %s",r.stdout.strip())
if r.stderr: logging.info("STDERR: %s",r.stderr.strip())
if r.returncode:
raise RuntimeError(f"Befehl fehlgeschlagen ({r.returncode}): {' '.join(cmd)}\n{r.stderr.strip()}")
return r

def record(seconds):
wav=WORK/"input.wav"; wav.unlink(missing_ok=True)
run(["arecord","-D",MIC_DEVICE,"-f","S16_LE","-r","16000","-c","1","-d",seconds,wav])
if not wav.is_file() or wav.stat().st_size<1000: raise RuntimeError("Aufnahme fehlt oder ist zu klein")
return wav

def transcribe(wav,lang):
stem=WORK/"transcript"; txt=stem.with_suffix(".txt"); txt.unlink(missing_ok=True)
run([WHISPER,"-m",WHISPER_MODEL,"-f",wav,"-l",lang,"-nt","-otxt","-of",stem])
if not txt.is_file(): raise RuntimeError("Whisper erzeugte keine Textdatei")
text=txt.read_text(encoding="utf-8",errors="replace").strip()
if not text: raise RuntimeError("Whisper lieferte keinen Text")
return text

def translate(text,target):
language="Deutsch" if target=="de" else "Englisch"
prompt=f"Übersetze exakt ins {language}. Gib ausschließlich die Übersetzung aus, ohne Erklärung, Anführungszeichen oder Präfix. Text: {text}"
r=requests.post(OLLAMA_URL,json={"model":GEMMA_MODEL,"prompt":prompt,"stream":False,"options":{"temperature":0}},timeout=180)
r.raise_for_status(); out=r.json()["response"].strip()
if not out: raise RuntimeError("Gemma lieferte keine Übersetzung")
return out

def speak(text,target):
model=VOICES[target]; config=Path(str(model)+".json")
if not model.is_file(): raise FileNotFoundError(f"TTS-Modell fehlt: {model}")
if not config.is_file(): raise FileNotFoundError(f"TTS-Konfiguration fehlt: {config}")
out=WORK/"translation.wav"; out.unlink(missing_ok=True)
run([BASE/"venv/bin/piper","--model",model,"--output_file",out],text)
run(["aplay","-D",PLAYBACK_DEVICE,out]); return out

def main():
ap=argparse.ArgumentParser();
ap.add_argument("--from",dest="source",choices=["de","en"],required=True)
ap.add_argument("--to",dest="target",choices=["de","en"],required=True);
ap.add_argument("--seconds",type=int,default=7)
a=ap.parse_args()
if a.source==a.target: sys.exit("Quell- und Zielsprache müssen verschieden sein")
try:
print("Aufnahme startet ...")
text=transcribe(record(a.seconds),a.source)
print("Erkannt:",text)
out=translate(text,a.target)
print("Übersetzt:",out)
speak(out,a.target)
except Exception as e:
logging.exception("Fehler")
print(f"FEHLER: {e}",file=sys.stderr)
sys.exit(1)

if __name__=="__main__": main()
