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
`records` (recursively) and writes an HTML report for each to a time-stamped
subdirectory of `results`:

```
python generate_html.py
```

After execution the directory structure will resemble:

```
VCAScribe-AuditRecords/
├── records/
│   └── some_file.json
├── results/
│   └── 20240605-123456/
│       └── some_file.html
└── generate_html.py
```
