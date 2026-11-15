# 📖 Schritt-für-Schritt-Anleitung für Einsteiger: Raspberry Pi Offline-Übersetzer

Willkommen! Diese Anleitung führt dich Schritt für Schritt durch die komplette Einrichtung des Offline-Übersetzers auf deinem Raspberry Pi. Sie ist speziell für Einsteiger geschrieben – du benötigst also keine tiefgehenden Vorkenntnisse in Linux, um das Projekt erfolgreich nachzubauen.

![Projektbild des Offline-Übersetzers](images/beitragsbild4.png)

---

## 📋 Inhaltsverzeichnis
1. [Was du vorab benötigst (Voraussetzungen)](#1-was-du-vorab-benötigst-voraussetzungen)
2. [Das System vorbereiten](#2-das-system-vorbereiten)
3. [Audio testen (Mikrofon & Lautsprecher)](#3-audio-testen-mikrofon--lautsprecher)
4. [Das Projekt herunterladen](#4-das-projekt-herunterladen)
5. [Die Software installieren](#5-die-software-installieren)
6. [Konfiguration anpassen](#6-konfiguration-anpassen)
7. [Den Offline-Übersetzer starten](#7-den-offline-übersetzer-starten)
8. [Optional: Automatischer Start beim Einschalten (Autostart)](#8-optional-automatischer-start-beim-einschalten-autostart)
9. [Häufige Probleme und Lösungen (FAQ)](#9-häufige-probleme-und-lösungen-faq)

---

## 1. Was du vorab benötigst (Voraussetzungen)

Bevor wir mit der Installation beginnen, stelle sicher, dass folgende Dinge bereitliegen:
* **Hardware:** Ein Raspberry Pi (empfohlen wird ein Raspberry Pi 4 oder 5 mit mindestens 4 GB oder 8 GB Arbeitsspeicher), ein Mikrofon (z. B. per USB), ein Lautsprecher und optional ein kleines Display. Eine genaue Liste findest du in der [Hardware-Übersicht](hardware.md).
* **Betriebssystem:** Ein fertig auf einer microSD-Karte installiertes **Raspberry Pi OS (64-Bit)**. *(Wichtig: Die 64-Bit-Version wird zwingend für die lokale KI benötigt!)*
* **Internetverbindung:** Während dieser Einrichtung benötigt der Raspberry Pi einmalig WLAN oder ein Netzwerkkabel, um alle Programme und Sprachmodelle herunterzuladen. Später im Betrieb funktioniert alles komplett **offline**.

---

## 2. Das System vorbereiten

Starte deinen Raspberry Pi und öffne das **Terminal** (die Eingabeaufforderung für Textbefehle). 
* **Am Bildschirm:** Klicke oben links in der Menüleiste auf das schwarze Symbol mit der Aufschrift `>_`.
* **Über das Netzwerk:** Alternativ kannst du dich auch von deinem normalen PC aus per SSH verbinden.

Bringe dein System zuerst auf den neuesten Stand und installiere das Werkzeug **Git** sowie grundlegende Audio-Werkzeuge. Kopiere dazu den folgenden Befehl, füge ihn im Terminal (meist per Rechtsklick -> *Einfügen*) ein und drücke die **Eingabetaste (Enter)**:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3-pip python3-venv alsa-utils -y
```
*(Hinweis: Das System lädt nun Aktualisierungen herunter. Das kann einige Minuten dauern.)*

---

## 3. Audio testen (Mikrofon & Lautsprecher)

Ein Übersetzer muss gut hören und sprechen können. Prüfe kurz, ob dein Raspberry Pi Mikrofon und Lautsprecher erkannt hat:

### 3.1 Lautstärke einstellen
Tippe folgenden Befehl ein und bestätige mit **Enter**:
```bash
alsamixer
```
* Es öffnet sich ein buntes Menü. Mit der Taste **F6** kannst du deine Soundkarte / dein USB-Mikrofon auswählen.
* Mit den **Pfeiltasten (hoch/runter)** regelst du die Lautstärke.
* Steht unter einem Balken `MM`, ist der Kanal stummgeschaltet. Drücke die Taste **M**, um ihn zu aktivieren (es erscheint `00`).
* Mit der Taste **Esc** verlässt du das Menü wieder.

### 3.2 Kurze Testaufnahme machen
Sprich für 5 Sekunden in dein Mikrofon, indem du diesen Befehl ausführst:
```bash
arecord -d 5 test.wav
```
Spiele die Aufnahme danach ab, um zu hören, ob Mikrofon und Lautsprecher funktionieren:
```bash
aplay test.wav
```
Wenn du dich selbst gehört hast, lösche die Testdatei wieder mit `rm test.wav` und gehe weiter zu Schritt 4!

---

## 4. Das Projekt herunterladen

Stelle sicher, dass du dich in deinem persönlichen Benutzerordner befindest, lade alle Projektdateien herunter und wechsle direkt in den neuen Projektordner:

```bash
cd ~
git clone https://github.com/DEIN-BENUTZERNAME/raspberry-pi-offline-translator.git
cd raspberry-pi-offline-translator
```
> **Hinweis:** Ersetze `DEIN-BENUTZERNAME` im Befehl oben durch den tatsächlichen GitHub-Nutzernamen des Repositories. Falls du das Projekt als ZIP-Datei heruntergeladen und entpackt hast, heißt der Ordner `raspberry-pi-offline-translator-main`. Wechsle dann mit `cd ~/raspberry-pi-offline-translator-main` hinein.

---

## 5. Die Software installieren

Damit du nicht jedes Programm mühsam von Hand einrichten musst, liegen im Ordner `scripts/` fertige Installations-Skripte bereit.

### Was wird hier eigentlich installiert?
1. **Whisper (`install_whisper.sh`):** Wandelt deine gesprochene Sprache über das Mikrofon blitzschnell in Text um (Speech-to-Text).
2. **Ollama (`install_ollama.sh`):** Das Herzstück. Eine lokale Künstliche Intelligenz (Sprachmodell), die den Text ohne Internet in die Zielsprache übersetzt.
3. **Piper (`install_piper.sh`):** Erzeugt aus dem übersetzten Text eine natürlich klingende Sprachausgabe für den Lautsprecher (Text-to-Speech).
4. **LCD-Treiber (`install_lcd.sh`):** Richtet bei Bedarf ein kleines aufgestecktes Display ein.

### Schritt 5.1: Skripte ausführbar machen
Gib dem Raspberry Pi zunächst die Berechtigung, die Skripte als Programme zu starten:

```bash
chmod +x scripts/*.sh
chmod +x gui/*.sh
```

### Schritt 5.2: Hauptinstallation starten
Führe nun das zentrale Installationsskript aus:

```bash
./scripts/install.sh
```

### Schritt 5.3: Einzelne Komponenten prüfen (falls nötig)
Je nachdem, wie du dein Setup zusammenstellst, kannst du die Bausteine bei Bedarf auch einzeln nachinstallieren:

```bash
./scripts/install_whisper.sh
./scripts/install_ollama.sh
./scripts/install_piper.sh
```
*(Optional: Wenn du das passende Display aus der Hardware-Liste verwendest, führe zusätzlich `./scripts/install_lcd.sh` aus. Achtung: Danach startet der Raspberry Pi meist automatisch neu!)*

> ☕ **Geduld mitbringen:** Das Herunterladen der KI-Sprachmodelle (mehrere Gigabyte) dauert je nach Internetgeschwindigkeit und microSD-Karte zwischen 10 und 30 Minuten.

---

## 6. Konfiguration anpassen

Im Ordner `config/` liegt eine Vorlage für die Einstellungen (`translator.example.py`). Damit das Programm deine Einstellungen findet, kopieren wir diese Vorlage zur aktiven Konfigurationsdatei `translator.py`:

```bash
cp config/translator.example.py config/translator.py
```

Jetzt kannst du die Einstellungen (wie Ausgangssprache, Zielsprache, Pfade oder das KI-Modell) im einfachen Texteditor `nano` betrachten und anpassen:

```bash
nano config/translator.py
```
**So bedienst du den Editor:**
* Nutze die **Pfeiltasten**, um durch den Text zu navigieren.
* Drücke **Strg + O** und danach **Enter**, um deine Änderungen zu speichern.
* Drücke **Strg + X**, um den Editor wieder zu verlassen.

---

## 7. Den Offline-Übersetzer starten

Geschafft! Alle Bauteile und Programme sind bereit. Du kannst das Internet nun testweise ausschalten – ab jetzt läuft alles lokal auf deinem Raspberry Pi.

### Möglichkeit A: Mit grafischer Oberfläche (für Display / Monitor)
Wenn du einen Bildschirm am Raspberry Pi nutzt, starte die grafische Benutzeroberfläche (GUI) über das Start-Skript:

```bash
./gui/gui.sh
```
*(Alternativ kannst du die Oberfläche auch direkt über Python aufrufen: `python3 app/gui.py`)*

### Möglichkeit B: Direkt im Terminal (ohne Bildschirm / Headless)
Wenn du den Übersetzer ohne eigenen Bildschirm direkt in der Textkonsole verwenden möchtest, starte das Hauptprogramm so:

```bash
python3 app/translator.py
```

---

## 8. Optional: Automatischer Start beim Einschalten (Autostart)

Wenn dein Übersetzer wie ein echtes mobiles Gerät sofort nach dem Einstecken des Stromkabels die grafische Oberfläche starten soll, kannst du eine Autostart-Datei anlegen:

1. Erstelle den Autostart-Ordner (falls noch nicht vorhanden) und öffne eine neue Datei:
   ```bash
   mkdir -p ~/.config/autostart
   nano ~/.config/autostart/translator.desktop
   ```
2. Kopiere folgenden Inhalt hinein *(passe `pi` im Pfad an, falls dein Benutzername anders lautet)*:
   ```ini
   [Desktop Entry]
   Type=Application
   Name=Offline Translator
   Exec=/home/pi/raspberry-pi-offline-translator/gui/gui.sh
   Terminal=false
   ```
3. Speichere wieder mit **Strg + O** -> **Enter** und schließe mit **Strg + X**. Beim nächsten Neustart (`sudo reboot`) öffnet sich die Übersetzer-Oberfläche ganz von allein!

---

## 9. Häufige Probleme und Lösungen (FAQ)

* **Fehler: `bash: ./scripts/install.sh: Permission denied` (Keine Berechtigung)**
  * *Lösung:* Du hast Schritt 5.1 übersprungen. Führe `chmod +x scripts/*.sh` und `chmod +x gui/*.sh` aus, um die Dateien freizuschalten.
* **Fehler: `FileNotFoundError` oder fehlende Konfiguration beim Start**
  * *Lösung:* Prüfe, ob du Schritt 6 ausgeführt hast (`cp config/translator.example.py config/translator.py`) und ob du dich beim Starten wirklich im Hauptordner des Projekts befindest.
* **Die allererste Übersetzung nach dem Einschalten dauert sehr lange**
  * *Erklärung:* Das ist völlig normal! Beim ersten Satz lädt `Ollama` das große Sprachmodell von der SD-Karte in den Arbeitsspeicher (RAM). Alle darauffolgenden Übersetzungen gehen deutlich schneller.
* **Ollama meldet einen Verbindungsfehler (`Connection refused`)**
  * *Lösung:* Prüfe, ob der Hintergrunddienst von Ollama läuft, indem du `sudo systemctl status ollama` eingibst. Falls er gestoppt ist, starte ihn mit `sudo systemctl start ollama`.
* **Das Programm erkennt meine Sprache kaum oder bricht sofort ab**
  * *Lösung:* Öffne noch einmal `alsamixer` (siehe Schritt 3.1) und erhöhe den Regler für dein Mikrofon (`Capture` oder `Mic`). Oft ist das Mikrofon ab Werk zu leise eingestellt.

---
*Viel Spaß beim Ausprobieren und Übersetzen! Falls du Fragen hast oder einen Fehler findest, erstelle gerne ein Issue hier im Repository.*