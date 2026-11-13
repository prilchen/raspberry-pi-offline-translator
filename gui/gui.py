import tkinter as tk
import subprocess
import threading

def starte_uebersetzung(quellsprache, zielsprache):
# Buttons sperren, damit man nicht doppelt klickt
button_de_en.config(state=tk.DISABLED)
button_en_de.config(state=tk.DISABLED)

text_feld.delete(1.0, tk.END)
text_feld.insert(tk.END, f"Aufnahme läuft... Bitte 7 Sekunden sprechen!\n\n")

def aufgabe():
# Passe hier /home/admin/ an deinen tatsächlichen Benutzerpfad an!
befehl = [
"/home/admin/translator/venv/bin/python",
"/home/admin/translator/app/translator.py",
"--from", quellsprache,
"--to", zielsprache,
"--seconds", "7"
]
try:
prozess = subprocess.Popen(
befehl, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)
for zeile in prozess.stdout:
root.after(0, text_feld.insert, tk.END, zeile)
root.after(0, text_feld.see, tk.END)
prozess.wait()
root.after(0, text_feld.insert, tk.END, "\nFertig!")
except Exception as fehler:
root.after(0, text_feld.insert, tk.END, f"\nFehler: {fehler}")
finally:
root.after(0, button_de_en.config, {'state': tk.NORMAL})
root.after(0, button_en_de.config, {'state': tk.NORMAL})

threading.Thread(target=aufgabe, daemon=True).start()

root = tk.Tk()
root.title("Prilchen LABS - Übersetzer")
root.geometry("480x320")
# Für den Vollbildmodus auf dem LCD die # in der nächsten Zeile entfernen:
# root.attributes("-fullscreen", True)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

button_de_en = tk.Button(frame_buttons, text="DE -> EN", font=("Arial", 20, "bold"), width=10, height=3, command=lambda: starte_uebersetzung("de", "en"))
button_de_en.pack(side=tk.LEFT, padx=10)

button_en_de = tk.Button(frame_buttons, text="EN -> DE", font=("Arial", 20, "bold"), width=10, height=3, command=lambda: starte_uebersetzung("en", "de"))
button_en_de.pack(side=tk.RIGHT, padx=10)

text_feld = tk.Text(root, font=("Arial", 14), wrap=tk.WORD, height=8)
text_feld.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
