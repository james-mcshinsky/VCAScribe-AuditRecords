#!/usr/bin/env python3
"""Generate HTML reports from appointment JSON payloads.

The script reads all ``.json`` or ``.txt`` files in the ``records`` directory
and writes an HTML report for each into a matching subdirectory of
``results``. It is designed to run with no command line arguments:

```
python generate_html.py
```
"""
import json
from pathlib import Path
from html import escape


def safe(value):
    """Return HTML-escaped text or an empty string."""
    return escape(str(value)) if value is not None else ""


def safe_pre(value):
    """Escape text for use inside a ``<pre>`` block, preserving quotes."""
    return escape(str(value), quote=False) if value is not None else ""

def format_json(value: str) -> str:
    """Return pretty-printed JSON for ``value`` if possible."""

    if not value:
        return ""
    try:
        parsed = json.loads(value)
    except Exception:
        return value
    return json.dumps(parsed, indent=2, sort_keys=True)


def render_html(payload: dict) -> str:
    """Render an HTML report with appointment details and transcriptions."""

    pieces = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'>",
        (
            "<style>body{font-family:Arial;margin:20px}"
            " table{border-collapse:collapse}"
            " th,td{border:1px solid #ccc;padding:4px;text-align:left}"
            " .transcription{border:1px solid #ccc;padding:10px;margin:20px 0}"
            " .models{display:flex;gap:20px}"
            " .model{flex:1}"
            " .model pre{border:1px solid #ccc;padding:10px;overflow:auto}"
            "</style>"
        ),
        "</head><body>",
    ]

    for appt in payload.get("data", []):
        pieces.append("<h1>Appointment and Patient Information</h1>")
        pieces.append("<table>")
        appt_rows = [
            ("Client First Name", safe(appt.get("clientFirstName"))),
            ("Client Last Name", safe(appt.get("clientLastName"))),
            ("Pet Name", safe(appt.get("petName"))),
            ("Chart Number", safe(appt.get("chartNumber"))),
            ("Hospital ID", safe(appt.get("hospitalId"))),
            ("Hospital Name", safe(appt.get("hospitalName"))),
            ("Gender ID", safe(appt.get("genderId"))),
            ("Species ID", safe(appt.get("speciesId"))),
            ("Species Name", safe(appt.get("speciesName"))),
            ("Breeds", safe(appt.get("breeds"))),
            ("Sex", safe(appt.get("sex"))),
            ("Neutered", safe(appt.get("neutered"))),
            ("Pet Age", safe(appt.get("petAge"))),
        ]

        scribe_info = []
        scribe_sections = []
        for scribe in appt.get("scribes", []):
            scribe_info.extend(
                [
                    ("Scribe ID", safe(scribe.get("scribeId"))),
                    ("Appointment ID", safe(scribe.get("appointmentId"))),
                    ("Recorded Duration", safe(scribe.get("recordedDuration"))),
                    ("Scribe Title", safe(scribe.get("scribeTitle"))),
                    ("Created By", safe(scribe.get("createdBy"))),
                    ("Updated By", safe(scribe.get("updatedBy"))),
                    ("Created Time", safe(scribe.get("createdTime"))),
                    ("Patient ID", safe(scribe.get("patientId"))),
                    ("Pet Appointment ID", safe(scribe.get("petAppointmentId"))),
                    ("Patient Name", safe(scribe.get("patientName"))),
                    ("Exam ID", safe(scribe.get("examId"))),
                    ("Medical Note ID", safe(scribe.get("medicalNoteId"))),
                    ("Resource Name", safe(scribe.get("resourceName"))),
                ]
            )

            transcription_text = safe(scribe.get("transcriptionText"))
            model_one = safe_pre(format_json(scribe.get("transcriptionModelOne")))
            card_model = safe_pre(format_json(scribe.get("transcriptionCardModel")))

            scribe_sections.append(
                [transcription_text, model_one, card_model]
            )

        pieces.extend(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in appt_rows + scribe_info)
        pieces.append("</table>")

        for transcription_text, model_one, card_model in scribe_sections:
            pieces.append("<div class='transcription'><h2>Transcription</h2><p>" + transcription_text + "</p></div>")
            pieces.append("<div class='models'>")
            pieces.append(
                "<div class='model'><h2>Original AI Output</h2><pre>"
                + model_one
                + "</pre></div>"
            )
            pieces.append(
                "<div class='model'><h2>Sent to WOOFware</h2><pre>"
                + card_model
                + "</pre></div>"
            )
            pieces.append("</div>")

    pieces.append("</body></html>")
    return "\n".join(pieces)


def process_file(src: Path, dest: Path) -> None:
    payload = json.loads(src.read_text(encoding="utf-8"))
    html = render_html(payload)
    dest.write_text(html, encoding="utf-8")
    print(f"Report written to {dest}")


def main() -> None:
    """Convert all files in ``records`` to HTML in ``results``."""
    src = Path("records")
    dest = Path("results")

    if not src.exists() or not src.is_dir():
        raise SystemExit("records directory not found")

    dest.mkdir(parents=True, exist_ok=True)

    for file in src.iterdir():
        if file.suffix.lower() not in {".json", ".txt"}:
            continue
        subdir = dest / file.stem
        subdir.mkdir(parents=True, exist_ok=True)
        out_file = subdir / (file.stem + ".html")
        process_file(file, out_file)

if __name__ == "__main__":
    main()
