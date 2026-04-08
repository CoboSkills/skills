---
name: ntriq-document-intelligence-mcp
description: "Document OCR, classification, table extraction, and summarization using local AI vision. Supports invoices, contracts, forms, reports."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [document,ocr,extraction]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Document Intelligence MCP

Document OCR, classification, table extraction, and summarization using local AI vision. Supports invoices, contracts, forms, and reports in PDF, PNG, TIFF, and JPEG. Returns structured JSON — no cloud upload required.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_url` | string | ✅ | URL or base64 of document image/PDF |
| `tasks` | array | ✅ | Tasks: `ocr`, `classify`, `extract_tables`, `summarize` |
| `doc_type_hint` | string | ❌ | Hint: `invoice`, `contract`, `form`, `report` |
| `language` | string | ❌ | Document language ISO code (auto-detected) |

## Example Response

```json
{
  "classification": "invoice",
  "confidence": 0.98,
  "ocr_text": "INVOICE #INV-2024-0847
Date: March 15, 2024
Vendor: Acme Supplies Ltd.",
  "tables": [
    {
      "headers": ["Item", "Qty", "Unit Price", "Total"],
      "rows": [["Widget A", "100", "$4.50", "$450.00"], ["Shipping", "1", "$25.00", "$25.00"]]
    }
  ],
  "summary": "Invoice from Acme Supplies for 100 Widget A units plus shipping. Total: $475.00"
}
```

## Use Cases

- Accounts payable invoice processing automation
- Legal contract review and clause extraction
- Medical records digitization for EMR systems

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/document-intelligence-mcp) · [x402 micropayments](https://x402.ntriq.co.kr)
