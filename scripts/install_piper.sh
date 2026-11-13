python3 -m venv ~/translator/venv
source ~/translator/venv/bin/activate
# Sobald die Umgebung aktiviert wurde, erscheint links vor der Eingabezeile ein (venv)
python -m pip install --upgrade pip
python -m pip install piper-tts requests
cd ~/translator/voices/de
python -m piper.download_voices de_DE-thorsten-medium
cd ~/translator/voices/en
python -m piper.download_voices en_GB-alan-medium
find ~/translator/voices -type f \( -name "*.onnx" -o -name "*.onnx.json" \) -print
