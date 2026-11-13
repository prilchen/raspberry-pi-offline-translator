

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
