#!/usr/bin/env python3
"""
generate_html.py

Usage:
    python generate_html.py input.json output.html
    python generate_html.py input_dir output_dir
"""
import json
import sys
from pathlib import Path
from html import escape

def safe(value):
    """Return HTML‑escaped text or an empty string."""
    return escape(str(value)) if value is not None else ""

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

    pieces.append("</body></html>")
    return "\n".join(pieces)


def process_file(src: Path, dest: Path) -> None:
    payload = json.loads(src.read_text(encoding="utf-8"))
    html = render_html(payload)
    dest.write_text(html, encoding="utf-8")
    print(f"Report written to {dest}")


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python generate_html.py input.json output.html\n"
            "       python generate_html.py input_dir output_dir"
        )
        sys.exit(1)

    src = Path(sys.argv[1])
    dest = Path(sys.argv[2])

    if src.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        for file in src.iterdir():
            if file.suffix.lower() not in {".json", ".txt"}:
                continue
            subdir = dest / file.stem
            subdir.mkdir(parents=True, exist_ok=True)
            out_file = subdir / (file.stem + ".html")
            process_file(file, out_file)
    else:
        if dest.is_dir():
            dest = dest / (src.stem + ".html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        process_file(src, dest)

if __name__ == "__main__":
    main()
