# VCAScribe-AuditRecords

Utility for converting appointment JSON payloads into simple HTML reports.

## Usage

Process a single JSON file:

    python generate_html.py input.json output.html

Process a directory of JSON or text files (each containing JSON) and write the HTML reports to subfolders:

    python generate_html.py input_dir results_dir

Each input file produces `results_dir/<filename>/<filename>.html`.
