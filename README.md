# VCAScribe-AuditRecords

Utility for converting appointment JSON payloads into simple HTML reports.

## Usage

Process a single JSON file:

    python generate_html.py input.json output.html

Process a directory of JSON or text files (each containing JSON) and write the HTML reports to subfolders:

    python generate_html.py input_dir results_dir

Each input file produces `results_dir/<filename>/<filename>.html`.

### Folder layout

The script expects you to provide explicit paths for the input and output folders. A common layout is:

- Place the JSON or text files to be processed in a folder named `records` at the repository root:

  `VCAScribe-AuditRecords/records/`

- Choose a folder for the generated HTML, such as `results`, also at the repository root:

  `VCAScribe-AuditRecords/results/`

Run the command using these paths:

```
python generate_html.py records results
```

Each JSON file in `records` will produce an HTML report in `results/<filename>/<filename>.html`.
