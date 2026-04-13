---
name: RapidOCR
slug: rapidocr
version: 1.0.0
description: The latest official RapidOCR command-line version, supporting Chinese-English mixed OCR text recognition for local images (JPG/PNG/WEBP). No complex configuration needed, one-click terminal call. Returns structured text, location information, and confidence levels, suitable for daily office work, image-to-text and other high-frequency scenarios.
tags: [ocr, vision, cli, rapidocr, text recognition, Chinese-English recognition, tool, latest]
author: RapidAI
email: liekkaskono@163.com
homepage: https://rapidai.github.io/RapidOCRDocs
license: Apache-2.0 License
tools:
  - exec:run
  - file:read
  - file:write
install: |
  # Dependency Installation Steps (auto-shown to users when installing the Skill)
  1. Ensure Python 3.7+ is installed locally (3.8-3.11 recommended)
  2. Install dependencies with this command: pip install rapidocr onnxruntime
  3. Verify installation: Enter `rapidocr check` in terminal. Version info means successful installation.
main: rapidocr -img {{img_path}}
---

# RapidOCR Skill User Guide
## Feature Introduction
Developed based on the latest official RapidOCR (v3.x), this Skill focuses on lightweight and efficient local image OCR recognition. No internet connection is required (except for dependency installation). It supports the following core functions:
1. **Mainstream Image Format Support**: JPG, PNG, WEBP; compatible with daily screenshots, photos, and scanned documents
2. **Chinese-English Mixed Recognition**: Accurately identifies Chinese, English, and numbers, suitable for various scenarios (e.g., invoices, documents, screenshots)
3. **Structured Output**: Returns recognized text by default; location coordinates and confidence levels can be configured via parameters
4. **Flexible Configuration**: Supports confidence filtering, visual bounding box selection, and orientation classification (adapted for rotated images)

## Triggers
This Skill is automatically triggered when the user enters the following instructions in ClawHub:
- "Use RapidOCR to recognize this image"
- "Extract text from image with OCR"
- "Call RapidOCR to process image"
- "Convert image to text"

## Usage Methods (Two Options for Users)
### Method 1: Basic Usage (Default Output: Recognized Text)
```bash
rapidocr -img /path/to/image  # Example: rapidocr -img ./test.png
```

### Method 2: Usage with Parameters (Customize as Needed)
```bash
# High-confidence filtering (keep results with confidence ≥ 0.8)
rapidocr -img {{img_path}} --text_score 0.8

# Generate visual bounding box image (saved to ./out directory)
rapidocr -img {{img_path}} --vis_res --vis_save_dir ./out

# Enable orientation classification (adapt for rotated images, avoid recognition errors)
rapidocr -img {{img_path}} --use_cls true

# Output single-character coordinates (accurately locate each character's position)
rapidocr -img {{img_path}} --return_word_box

# Combine multiple parameters (Recommended Common Combination)
rapidocr -img {{img_path}} --text_score 0.7 --vis_res --use_cls true
```

## Detailed Parameter Explanation (Easy for Quick Reference)
| Parameter                | Description                                  | Accepted Values/Examples      |
|--------------------------|----------------------------------------------|-------------------------------|
| -img / --img_path        | Required. Local path or URL of the image    | ./test.png, https://xxx.jpg   |
| --text_score             | Optional. Confidence threshold to filter blurry results | 0.5-1.0 (Default: 0.5)         |
| --vis_res                | Optional. Generate visual image with text bounding boxes | No value needed; add the parameter |
| --vis_save_dir           | Optional. Directory to save visual images     | ./out, ~/Desktop/ocr_vis      |
| --use_cls                | Optional. Enable image orientation classification | true / false (Default: false)  |
| --return_word_box        | Optional. Output single-character coordinate information | No value needed; add the parameter |
| --lang_type              | Optional. Specify recognition language       | ch (Chinese), en (English), etc. |
| -h / --help              | Optional. View all parameter descriptions     | No value needed; run directly |

## Example Input & Output
### Example 1: Basic Usage
- Input Command: `rapidocr -img ./invoice.png`
- Output Result:
```
[RapidOCR Recognition Result]
Invoice Number: NO.20260408
Invoice Date: April 08, 2026
Amount: ¥1,999.00
Payee: XXX Technology Co., Ltd.
```

### Example 2: Usage with Parameters (High Confidence + Visualization)
- Input Command: `rapidocr -img ./screenshot.png --text_score 0.8 --vis_res`
- Output Result:
```
[RapidOCR Recognition Result]
Title: ClawHub Skill Release Guide
Content: 1. Prepare Skill folder 2. Write SKILL.md 3. Upload and release
Confidence: 0.92

[Hint] The visual bounding box image has been saved to ./out/screenshot_vis.png
```

## Notes (Key Tips for Better User Experience)
1. **Correct Image Path**: If prompted "File not found", check the image path (relative path must match the terminal's current directory).
2. **Dependency Installation Failure**: If pip installation fails, try changing the mirror source: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple rapidocr onnxruntime`.
3. **Garbled Text/Inaccurate Recognition**: Add `--use_cls true` or adjust the `--text_score` threshold to improve recognition accuracy.
4. **PDF Not Supported**: This Skill only supports image recognition currently. For PDF recognition, convert PDF to images first.
5. **Output Object Explanation**: The RapidOutput object returned by RapidOCR CLI is the official standard output carrier, containing all core information required for recognition. No extra configuration is needed, and it does not affect the Skill's invocation or result display.

## Frequently Asked Questions (FAQ)
1. Q: Why does the terminal prompt "Command not found" when entering rapidocr?
   A: Ensure dependencies are installed successfully. If the problem persists, restart the terminal or check if the Python environment variables are configured correctly.
2. Q: How to speed up recognition?
   A: Reduce optional parameters like `--return_word_box` or lower the `--text_score` threshold to improve speed.
3. Q: Can it recognize handwritten text?
   A: Currently only supports printed text recognition. Handwritten text recognition accuracy is low and not recommended.