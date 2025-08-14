#!/usr/bin/env python3
"""Generate HTML reports from appointment JSON payloads.

The script reads all ``.json`` or ``.txt`` files in the ``records`` directory
and writes an HTML report for each into a time-stamped subdirectory of
``results``. It is designed to run with no command line arguments:

```
python generate_html.py
```
"""
import json
from pathlib import Path
from html import escape
from datetime import datetime


def safe(value):
    """Return HTML-escaped text or an empty string."""
    return escape(str(value)) if value is not None else ""


def to_html(value):
    """Recursively convert ``value`` into a nested ``<ul>`` structure."""

    if value in (None, ""):
        return ""
    if isinstance(value, dict):
        items = [
            f"<li><strong>{escape(str(k))}:</strong> {to_html(v)}</li>" for k, v in value.items()
        ]
        return "<ul>" + "".join(items) + "</ul>"
    if isinstance(value, list):
        items = [f"<li>{to_html(v)}</li>" for v in value]
        return "<ul>" + "".join(items) + "</ul>"
    return escape(str(value))


def format_patient_history_model_one(_):
    return ""


def format_patient_history_card_model(data):
    if not data:
        return ""
    if isinstance(data, list):
        return "<br>".join(safe(item) for item in data if item)
    return safe(data)


def format_tpr_model_one(data):
    if not data:
        return ""
    lines = []
    for name, vital in data.items():
        parts = []
        val = vital.get("Value")
        unit = vital.get("Unit")
        comment = vital.get("Comment")
        if val is not None:
            parts.append(str(val))
        if unit:
            parts.append(unit)
        if comment:
            parts.append(comment)
        line = f"{name}: {' '.join(parts)}" if parts else name
        lines.append(line)
    return "<br>".join(safe(line) for line in lines)


def format_tpr_card_model(data):
    if not data:
        return ""
    cells = []
    for vital in data:
        label = vital.get("label") or vital.get("key") or ""
        unit = vital.get("unit")
        value = vital.get("value")
        comment = vital.get("comment")
        label_text = f"{label} ({unit})" if unit else label
        pieces = [
            '<td style="max-width: 180px; padding: 0 8px;">',
            '<section class="display_grid">',
            f"<h4>{safe(label_text)}</h4>",
        ]
        if value is not None:
            pieces.append(f"<span>{safe(value)}</span>")
        if comment:
            pieces.append(f"<span>{safe(comment)}</span>")
        pieces.append("</section></td>")
        cells.append("".join(pieces))
    row = (
        '<tr class="display_flex gap-16" style="flex-flow: wrap;">'
        + "".join(cells)
        + "</tr>"
    )
    return "<table><tbody>" + row + "</tbody></table>"


def format_pef_model_one(data):
    if not data:
        return ""
    lines = []
    for items in data.values():
        for item in items:
            struct = item.get("StructureOrCharacteristic")
            finding = item.get("Finding")
            if struct or finding:
                lines.append(f"{struct}: {finding}")
    return "<br>".join(safe(line) for line in lines)


def format_pef_card_model(data):
    if not data:
        return ""
    lines = []
    for item in data:
        sub = item.get("subCategory") or item.get("category")
        obs = item.get("observation")
        comment = item.get("comment")
        parts = [p for p in [obs, comment] if p]
        if sub and parts:
            lines.append(f"{sub}: {' - '.join(parts)}")
    return "<br>".join(safe(line) for line in lines)


def format_hsa_card_model(data):
    if not data:
        return ""
    if isinstance(data, list):
        return "<br>".join(to_html(item) for item in data)
    return to_html(data)


def format_ap_model_one(data):
    if not data:
        return ""
    pieces = []
    for item in data:
        problems = ", ".join(item.get("ProblemsOrConcerns", []))
        assessment = item.get("Assessment", {}).get("Assessment")
        plan = item.get("Plan", {})
        plan_parts = []
        labels = [
            ("DiscussionWithOwner", "Discussion With Owner"),
            ("Diagnostics", "Diagnostics"),
            ("InHospitalTreatments", "In Hospital Treatments"),
            ("Vaccines", "Vaccines"),
            ("Medications", "Medications"),
            ("RecommendedRecheck", "Recommended Recheck"),
        ]
        for key, label in labels:
            val = plan.get(key)
            if val:
                plan_parts.append(f"<strong>{label}:</strong> {safe(val)}")
        block = []
        if problems:
            block.append(f"<strong>Problems/Concerns:</strong> {safe(problems)}")
        if assessment:
            block.append(f"<strong>Assessment:</strong> {safe(assessment)}")
        if plan_parts:
            block.append("<strong>Plan:</strong> " + "<br>".join(plan_parts))
        pieces.append("<p>" + "<br>".join(block) + "</p>")
    return "".join(pieces)


def format_ap_card_model(data):
    if not data:
        return ""
    pieces = []
    for item in data:
        assessment = item.get("assessment", {}).get("assessment", "")
        plan = item.get("plan", {}).get("plan", "")
        pieces.append(assessment + plan)
    return "".join(pieces)


def render_sections(model_one_str: str, card_model_str: str) -> str:
    m1 = json.loads(model_one_str) if model_one_str else {}
    cm = json.loads(card_model_str) if card_model_str else {}

    sections = [
        (
            "Patient History",
            format_patient_history_model_one(m1.get("PatientHistory")),
            format_patient_history_card_model(cm.get("PatientHistory")),
        ),
        ("Vitals", format_tpr_model_one(m1.get("TPR")), format_tpr_card_model(cm.get("TPR"))),
        (
            "Physical Exam Findings",
            format_pef_model_one(m1.get("PhysicalExamFindings")),
            format_pef_card_model(cm.get("PhysicalExamFindings")),
        ),
        (
            "HSA",
            "",
            format_hsa_card_model(cm.get("HealthStatusAssessment")),
        ),
        (
            "Assessment and Plan",
            format_ap_model_one(m1.get("AssessmentAndPlan")),
            format_ap_card_model(cm.get("AssessmentAndPlan")),
        ),
    ]

    pieces = ["<section class=\"note-section\">"]
    for name, left, right in sections:
        pieces.append(
            "<section class=\"display_grid gap-16\" style=\"margin-bottom: 16px;\">"
            f"<h3 style=\"text-decoration: underline; text-transform: uppercase; letter-spacing: 1px; text-underline-offset: 4px;\">{name}</h3>"
            "<div class=\"display_grid grid-template-columns_1fr_1fr gap-16\">"
            "<table><thead><tr><th>Original AI Output</th></tr></thead>"
            f"<tbody><tr><td>{left}</td></tr></tbody></table>"
            "<table><thead><tr><th>Sent to WOOFware</th></tr></thead>"
            f"<tbody><tr><td>{right}</td></tr></tbody></table>"
            "</div></section>"
        )
    pieces.append("</section>")
    return "".join(pieces)


def render_html(payload: dict) -> str:
    """Render an HTML report with appointment details and transcriptions."""

    pieces = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'>",
        (
            "<style>body{font-family:Arial;margin:20px auto;max-width:900px}"
            " table{border-collapse:collapse;width:100%}"
            " th,td{border:1px solid #ccc;padding:8px;text-align:left;vertical-align:top;white-space:pre-wrap;word-break:break-word}"
            " .transcription{border:1px solid #ccc;padding:10px;margin:20px 0}"
            " .note-section{border:1px solid #ccc;padding:16px;margin:20px 0}"
            " .display_grid{display:grid}"
            " .gap-16{gap:16px}"
            " .grid-template-columns_1fr_1fr{grid-template-columns:1fr 1fr}"
            " .note-section table th{background:#f0f0f0}"
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
            section_table = render_sections(
                scribe.get("transcriptionModelOne", ""),
                scribe.get("transcriptionCardModel", ""),
            )

            scribe_sections.append([transcription_text, section_table])

        pieces.extend(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in appt_rows + scribe_info)
        pieces.append("</table>")

        for transcription_text, section_table in scribe_sections:
            pieces.append(
                "<div class='transcription'><h2>Transcription</h2><p>"
                + transcription_text
                + "</p></div>"
            )
            pieces.append(section_table)

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
    dest_root = Path("results")

    if not src.exists() or not src.is_dir():
        raise SystemExit("records directory not found")

    run_dir = dest_root / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    for file in src.iterdir():
        if file.suffix.lower() not in {".json", ".txt"}:
            continue
        out_file = run_dir / (file.stem + ".html")
        process_file(file, out_file)

if __name__ == "__main__":
    main()
