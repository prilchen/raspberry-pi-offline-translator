# Schritt-für-Schritt-Anleitung für Einsteiger: Raspberry Pi Offline-Übersetzer

Willkommen! Diese Anleitung führt dich Schritt für Schritt durch die Einrichtung des Offline-Übersetzers auf deinem Raspberry Pi (Einplatinencomputer). Du benötigst keine tiefgehenden Vorkenntnisse in Linux (freies Betriebssystem), um das Projekt erfolgreich nachzubauen.

---

## 1. Was du vorab benötigst (Voraussetzungen)

Bevor wir mit der Software starten, stelle sicher, dass folgende Dinge bereitliegen:
* **Hardware:** Dein fertig verkabelter Raspberry Pi samt Mikrofon, Lautsprecher und optionalem Bildschirm[cite: 1]. Eine genaue Übersicht der Bauteile findest du in der Datei [Hardware-Übersicht](hardware.md)[cite: 1].
* **Betriebssystem:** Ein fertig eingerichtetes Raspberry Pi OS (Operating System / Betriebssystem) auf einer Speicherkarte.
* **Internetverbindung:** Während der Installation wird eine aktive Internetverbindung benötigt, um die Sprachmodelle und Programme herunterzuladen. Später arbeitet der Übersetzer komplett ohne Internet (offline).

---

## 2. Das System vorbereiten

Öffne das **Terminal** (die Eingabeaufforderung für Textbefehle) auf deinem Raspberry Pi. Du findest es oben links in der Menüleiste über das schwarze Symbol mit der Aufschrift `>_` oder indem du dich von deinem Computer aus per SSH (Secure Shell / sichere Netzwerkverbindung) verbindest.

Bringe dein System zunächst auf den neuesten Stand und installiere das Werkzeug **Git** (Programm zur Versionsverwaltung), falls es noch nicht vorhanden ist. Kopiere dazu folgenden Befehl, füge ihn im Terminal ein und bestätige mit der **Eingabetaste (Enter)**:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git -y