---
name: document-generator
description: Creates professional documents from scratch or templates. Use this skill whenever the user needs to generate Word (.docx), Excel (.xlsx), or PDF documents with rich formatting, tables, images, or dynamic content. Ideal for reports, invoices, manuals, and data-driven documents.
compatibility:
  tools:
    - exec
  dependencies:
    - python-docx
    - openpyxl
    - fpdf2
    - weasyprint
    - jinja2
---

# Document Generator 📄

A comprehensive document generation system that creates professional Word, Excel, and PDF documents programmatically. Supports rich formatting, multi-level headings, tables, images, templates, and dynamic data insertion.

## When to Use This Skill

Trigger this skill when the user:
- Requests creation of any document (Word/Excel/PDF) from scratch or data
- Needs formatted reports, invoices, manuals, or certificates
- Requires tables, multi-level headings, images with captions, or custom styling
- Mentions "generate document", "create report", "make invoice", "export to PDF/Word/Excel"
- Works with structured data that needs to be turned into a polished document

Avoid for simple plain-text outputs; use direct file writes instead.

## Core Capabilities

### Word Documents (.docx)
- Create blank or templated documents
- Multi-level headings (levels 1-9)
- Tables with headers, custom styles, column widths
- Images with width, alignment, captions
- Paragraphs, bullet/numbered lists
- Rich styling: font size, color, bold, italic, underline, alignment
- Headers and footers

### Excel Workbooks (.xlsx)
- Create workbooks and worksheets
- Fill cells with data
- Apply cell formatting (number formats, colors, borders)
- Add formulas and references
- Generate basic charts (bar, line, pie)

### PDF Documents (.pdf)
- Convert HTML to PDF (high-quality via WeasyPrint)
- Generate from plain text with custom styles
- Add headers, footers, page numbers
- Control page layout and margins

### Template System
- Predefined templates for common document types
- Custom template support (HTML-based for PDFs, JSON structure for Word)
- Variable substitution with Jinja2
- Dynamic content from JSON data

## Quick Start

### Basic Usage

```bash
# Create a Word document with simple content
python3 create_word.py "report.docx" --title "Quarterly Report" --content "Summary text here"

# Create Excel from JSON data
python3 create_excel.py "data.xlsx" --data '{"sheet1": [{"A1": "Name", "B1": "Score"}]}'

# Create PDF from HTML
python3 create_pdf.py "output.pdf" --html "<h1>Hello</h1><p>World</p>"
```

### Advanced: Rich JSON Content for Word

For complex documents, use a JSON content structure:

```json
{
  "sections": [
    {
      "heading": "Project Overview",
      "level": 1,
      "content": [
        {
          "type": "paragraph",
          "text": "This project aims to develop an advanced document generation system...",
          "bold": true,
          "font_size": 14
        }
      ]
    },
    {
      "heading": "Technical Architecture",
      "level": 2,
      "content": [
        {
          "type": "list",
          "list_type": "bullet",
          "items": [
            "Document parsing engine",
            "Template rendering system",
            "Format conversion module"
          ]
        },
        {
          "type": "table",
          "headers": ["Component", "Technology", "Version", "Status"],
          "data": [
            ["Word generation", "python-docx", "0.8.11", "Stable"]
          ],
          "style": "Light Grid Accent 1"
        }
      ]
    }
  ]
}
```

Run with:
```bash
python3 create_word.py "report.docx" --content-file "content.json" --title "Technical Doc"
```

## File Structure

```
document-generator/
├── SKILL.md               # This file
├── create_word.py         # Word document generator
├── create_excel.py        # Excel workbook generator
├── create_pdf.py          # PDF generator
├── install_dependencies.py # Install required Python packages
├── demo_example.py        # Example script with rich content
└── USER_GUIDE.md          # Detailed user guide (optional)
```

## Dependencies

This skill requires Python packages to be installed **beforehand** by the user:

```bash
pip install python-docx openpyxl fpdf2 weasyprint jinja2
```

Do not run `apt install` inside the skill; the system should already have a working Python environment. If dependencies are missing, the skill will raise an error prompting the user to install them.

System libraries for WeasyPrint (optional but recommended on Linux):
```bash
apt install libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev
```

## Examples

### Example 1: Sales Report with Table

```python
import json

content = {
    "sections": [
        {
            "heading": "2026 Q1 Sales Report",
            "level": 1,
            "content": [
                {
                    "type": "paragraph",
                    "text": "Regional performance summary:"
                },
                {
                    "type": "table",
                    "headers": ["Region", "Revenue (10k)", "Growth", "Rank"],
                    "data": [
                        ["East", 1250, "+15.2%", 1],
                        ["South", 980, "+8.5%", 2],
                        ["North", 820, "+12.3%", 3]
                    ],
                    "style": "Light Shading Accent 2"
                }
            ]
        }
    ]
}

with open('sales.json', 'w') as f:
    json.dump(content, f, indent=2)

# Generate
# python3 create_word.py "sales_report.docx" --content-file "sales.json" --title "Q1 Sales"
```

### Example 2: PDF from HTML Template

```bash
# template.html
<!DOCTYPE html>
<html>
<head>
    <style>
      body { font-family: 'Microsoft YaHei'; }
      h1 { color: #2c3e50; }
    </style>
</head>
<body>
    <h1>{{title}}</h1>
    <p>{{date}}</p>
    <div>{{content}}</div>
</body>
</html>

# Generate
python3 create_pdf.py "newsletter.pdf" --template "template.html" --variables "title=Weekly News,date=2026-03-18,content=..."
```

### Example 3: Excel with Formulas and Chart

```bash
python3 create_excel.py "budget.xlsx" \
  --data '{"Sheet1": [{"A1": "Item", "B1": "Budget", "C1": "Actual"},
                     {"A2": "Marketing", "B2": 10000, "C2": 9500},
                     {"A2": "R&D", "B2": 20000, "C2": 22000}]}' \
  --formula "C3=SUM(C2:C10)" \
  --chart "Bar Chart of Budget vs Actual"
```

## Tips & Best Practices

- For large documents, use `--content-file` instead of inline JSON to avoid command-line length limits
- Table styles use Excel/Word built-in styles; common ones: `Light Grid Accent 1`, `Light Shading Accent 2`
- Image paths can be absolute or relative; for cross-platform, use absolute paths
- PDF generation via WeasyPrint requires system libraries (Pango, Cairo) on Linux; if missing, fall back to fpdf2 with `--backend fpdf`

## Security Considerations

- This skill **does not** perform any network I/O or system modifications beyond generating files in the specified output directory.
- All Python scripts are deterministic and only act on user-provided data and templates.
- The `install_dependencies.py` script is provided for convenience; it only installs Python packages via pip. Recommend reviewing it before running.
- For first-time use, test in an isolated environment to verify behavior matches expectations.
- No hidden or background processes are initiated.

## Troubleshooting

- **Import errors**: Ensure dependencies installed in correct Python environment
- **WeasyPrint build failures**: Install system deps: `apt install libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev`
- **File not found**: Use absolute paths for images and templates
- **Permission denied**: Write to current directory or a writable path

## Performance Notes

- Large Excel files (>10k rows): stream with `openpyxl` in write-only mode
- Big images: resize before insertion to keep file size manageable
- Batch generation: reuse a single script invocation with multiple output targets

---

**Skill name**: `document-generator`  
**Version**: 1.1.0  
**Status**: ✅ Production-ready  
**Last updated**: 2026-03-15
