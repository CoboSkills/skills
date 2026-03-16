---
name: doc2slides
version: 1.0.3
description: "Convert documents to slides. PDF/Word/Markdown → PPT. Runs on your machine, no external APIs."
license: MIT-0
author: lifei68801
tags: [ppt, slides, document, conversion]
---

# Doc2Slides

Convert PDF, Word, Markdown documents to PowerPoint slides.

## Quick Start

```bash
# Install dependencies (one-time setup)
pip install playwright python-pptx pdfplumber python-docx
playwright install chromium

# Generate slides
python scripts/main.py input.pdf output_dir
```

## Features

- **Multiple Formats**: PDF, Word, Markdown supported
- **Professional Design**: 18 layout templates
- **No External APIs**: All processing on your machine

## How It Works

1. Reads document content
2. Generates HTML slides
3. Converts to images (Playwright)
4. Assembles PowerPoint file

## Requirements

- Python 3.9+
- Chromium browser (via `playwright install`)

## Metadata

```yaml
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      pypi: ["playwright", "python-pptx", "pdfplumber", "python-docx"]
    permissions:
      - "file:read"
      - "file:write"
    behavior:
      external_api: none
      telemetry: none
      credentials: none
```
