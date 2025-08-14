# VCAScribe-AuditRecords

Utility for converting appointment JSON payloads into simple HTML reports.

## Usage

Place the JSON or text files to be processed in a folder named `records` at
the repository root:

```
VCAScribe-AuditRecords/
├── generate_html.py
├── records/
└── ...
```

Running the script with no arguments converts every `.json` or `.txt` file in
`records` and writes the HTML reports to `results/<filename>/<filename>.html`:

```
python generate_html.py
```

After execution the directory structure will resemble:

```
VCAScribe-AuditRecords/
├── records/
│   └── some_file.json
├── results/
│   └── some_file/
│       └── some_file.html
└── generate_html.py
```
