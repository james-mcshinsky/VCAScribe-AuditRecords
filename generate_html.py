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
import re
import html
from pathlib import Path
from html import escape

def safe(value):
    """Return HTML‑escaped text or an empty string."""
    return escape(str(value)) if value is not None else ""


def strip_tags(text: str) -> str:
    """Remove basic HTML tags and unescape entities."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text)

def render_html(payload: dict) -> str:
    pieces = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'>",
        "<style>body{font-family:Arial} table{border-collapse:collapse} ",
        "th,td{border:1px solid #ccc;padding:4px;}</style>",
        "</head><body>"
    ]

    for appt in payload.get("data", []):
        pieces.append(f"<h1>Appointment {safe(appt.get('appointmentId'))}</h1>")
        pieces.append("<table>")
        rows = [
            ("Client", f"{safe(appt.get('clientFirstName'))} {safe(appt.get('clientLastName'))}"),
            ("Pet", safe(appt.get('petName'))),
            ("Reason", safe(appt.get('appointmentReason'))),
            ("Doctor", safe(appt.get('resourceName'))),
        ]
        pieces.extend(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
        pieces.append("</table>")

        for scribe in appt.get("scribes", []):
            pieces.append(f"<h2>{safe(scribe.get('scribeTitle'))}</h2>")
            pieces.append(f"<p>{safe(scribe.get('transcriptionText'))}</p>")

            model = scribe.get("transcriptionModelOne")
            if model:
                try:
                    model = json.loads(model)

                    # TPR section
                    tpr = model.get("TPR", {})
                    if tpr:
                        pieces.append("<h3>TPR</h3><ul>")
                        for vital, info in tpr.items():
                            line = f"{vital}: {info.get('Value')} {info.get('Unit') or ''}"
                            if info.get("Comment"):
                                line += f" ({info['Comment']})"
                            pieces.append(f"<li>{safe(line.strip())}</li>")
                        pieces.append("</ul>")

                    # Physical exam findings
                    exam = model.get("PhysicalExamFindings", {})
                    if exam:
                        pieces.append("<h3>Physical Exam Findings</h3><ul>")
                        for _, findings in exam.items():
                            for item in findings:
                                text = f"{item.get('StructureOrCharacteristic')}: {item.get('Finding')}"
                                pieces.append(f"<li>{safe(text)}</li>")
                        pieces.append("</ul>")

                    # Assessment and plan
                    plans = model.get("AssessmentAndPlan", [])
                    if plans:
                        pieces.append("<h3>Assessment &amp; Plan</h3>")
                        for block in plans:
                            pieces.append(f"<strong>{safe(', '.join(block.get('ProblemsOrConcerns', [])))}"+"</strong><br>")
                            assess = block.get("Assessment", {}).get("Assessment")
                            if assess:
                                pieces.append(f"Assessment: {safe(assess)}<br>")
                            plan = block.get("Plan", {})
                            for key, val in plan.items():
                                if val:
                                    pieces.append(f"{safe(key)}: {safe(val)}<br>")

                except json.JSONDecodeError:
                    pieces.append("<p><em>Failed to parse transcriptionModelOne</em></p>")

            card = scribe.get("transcriptionCardModel")
            if card:
                try:
                    card = json.loads(card)

                    concerns = card.get("Concerns", [])
                    if concerns:
                        pieces.append("<h3>Concerns</h3><ul>")
                        for c in concerns:
                            name = c.get("concern") or c.get("concernName") or c.get("label")
                            if name:
                                pieces.append(f"<li>{safe(name)}</li>")
                        pieces.append("</ul>")

                    tpr_list = card.get("TPR", [])
                    if tpr_list:
                        pieces.append("<h3>TPR (Card Model)</h3><ul>")
                        for item in tpr_list:
                            label = item.get("label") or item.get("key") or "TPR"
                            parts = []
                            if item.get("value") is not None:
                                parts.append(str(item.get("value")))
                            if item.get("unit"):
                                parts.append(item.get("unit"))
                            line = f"{label}: {' '.join(parts)}".strip()
                            if item.get("comment"):
                                line += f" ({item['comment']})"
                            pieces.append(f"<li>{safe(line)}</li>")
                        pieces.append("</ul>")

                    plans = card.get("AssessmentAndPlan", [])
                    if plans:
                        pieces.append("<h3>Assessment &amp; Plan (Card Model)</h3>")
                        for block in plans:
                            assess = strip_tags(block.get("assessment", {}).get("assessment"))
                            if assess:
                                pieces.append(f"Assessment: {safe(assess)}<br>")
                            plan_text = strip_tags(block.get("plan", {}).get("plan"))
                            if plan_text:
                                pieces.append(f"Plan: {safe(plan_text)}<br>")
                except json.JSONDecodeError:
                    pieces.append("<p><em>Failed to parse transcriptionCardModel</em></p>")

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
