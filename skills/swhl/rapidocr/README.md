# RapidOCR CLI

A lightweight and efficient command-line version of RapidOCR, designed for local image text recognition with no complex configuration required.

## Overview

RapidOCR CLI is the official command-line implementation of RapidOCR (v3.x), focusing on fast and accurate Chinese-English mixed OCR recognition for local images. It supports mainstream image formats and provides structured output, making it ideal for daily office scenarios such as image-to-text conversion, invoice recognition, and screenshot text extraction.

### Key Features

- **Mainstream Image Support**: Compatible with JPG, PNG, and WEBP formats, adapting to daily screenshots, photos, and scanned documents.
- **Chinese-English Mixed Recognition**: Accurately identifies Chinese, English, and numbers, meeting the needs of various multilingual scenarios.
- **Structured Output**: Returns recognized text by default; location coordinates and confidence levels can be output via parameter configuration.
- **Flexible Configuration**: Supports confidence filtering, visual bounding box generation, and orientation classification (for rotated images).
- **Offline Usage**: No internet connection required after dependency installation, ensuring data security and stable recognition.

## Prerequisites

- Python 3.7+ (Python 3.8-3.11 is recommended for better compatibility)
- pip (Python package manager, usually included with Python installation)

## Installation

Follow these steps to install RapidOCR CLI and its dependencies:

1. Ensure Python 3.7+ is installed on your local machine. You can check the Python version by running:

   ```bash
   python --version  # Or python3 --version on some systems
   ```

2. Install the required dependencies using pip:

   ```bash
   pip install rapidocr onnxruntime
   ```

3. Verify the installation is successful by running:

   ```bash
   rapidocr check
   ```

   If the terminal displays the RapidOCR version information, the installation is complete.

## Usage

RapidOCR CLI supports two usage methods: basic call (default output) and parameterized call (customized output).

### Basic Usage (Default Output: Recognized Text)

Use the following command to recognize text from an image (replace `/path/to/image` with your actual image path):

```bash
rapidocr -img /path/to/image
# Example: rapidocr -img ./test.png
```

### Advanced Usage (With Parameters)

You can add parameters to customize the recognition process and output results. Below are common parameter combinations and their uses:

```bash
# High-confidence filtering (retain results with confidence ≥ 0.8)
rapidocr -img /path/to/image --text_score 0.8

# Generate visual bounding box image (saved to ./out directory)
rapidocr -img /path/to/image --vis_res --vis_save_dir ./out

# Enable orientation classification (adapt for rotated images to avoid recognition errors)
rapidocr -img /path/to/image --use_cls true

# Output single-character coordinates (accurately locate each character's position)
rapidocr -img /path/to/image --return_word_box

# Recommended combination: high confidence + visualization + orientation classification
rapidocr -img /path/to/image --text_score 0.7 --vis_res --use_cls true
```

## Parameter Details

| Parameter                | Description                                  | Accepted Values/Examples      |
|--------------------------|----------------------------------------------|-------------------------------|
| -img / --img_path        | Required. Local path or URL of the image     | ./test.png, https://xxx.jpg   |
| --text_score             | Optional. Confidence threshold to filter blurry results | 0.5-1.0 (Default: 0.5)         |
| --vis_res                | Optional. Generate visual image with text bounding boxes | No value needed; add the parameter |
| --vis_save_dir           | Optional. Directory to save visual images     | ./out, ~/Desktop/ocr_vis      |
| --use_cls                | Optional. Enable image orientation classification | true / false (Default: false)  |
| --return_word_box        | Optional. Output single-character coordinate information | No value needed; add the parameter |
| --lang_type              | Optional. Specify recognition language       | ch (Chinese), en (English), etc. |
| -h / --help              | Optional. View all parameter descriptions     | No value needed; run directly |

## Example Input & Output

### Example 1: Basic Usage

- Input Command:

  ```bash
  rapidocr -img ./invoice.png
  ```

- Output Result:

  ```text
  [RapidOCR Recognition Result]
  Invoice Number: NO.20260408
  Invoice Date: April 08, 2026
  Amount: ¥1,999.00
  Payee: XXX Technology Co., Ltd.
  ```

### Example 2: Advanced Usage (High Confidence + Visualization)

- Input Command:

  ```bash
  rapidocr -img ./screenshot.png --text_score 0.8 --vis_res
  ```

- Output Result:

  ```text
  [RapidOCR Recognition Result]
  Title: ClawHub Skill Release Guide
  Content: 1. Prepare Skill folder 2. Write SKILL.md 3. Upload and release
  Confidence: 0.92

  [Hint] The visual bounding box image has been saved to ./out/screenshot_vis.png
  ```

## Notes

1. **Correct Image Path**: If the terminal prompts "File not found", check if the image path is correct. The relative path must match the terminal's current working directory.
2. **Dependency Installation Failure**: If pip installation fails, try using a domestic mirror source to speed up the installation:

   ```bash
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple rapidocr onnxruntime
   ```

3. **Garbled Text/Inaccurate Recognition**: If recognition results are garbled or inaccurate, add the `--use_cls true` parameter to enable orientation classification, or adjust the `--text_score` threshold to improve accuracy.
4. **PDF Not Supported**: This tool only supports image recognition. To recognize text from PDF files, convert the PDF to images first (e.g., using tools like pdf2image).
5. **Output Object Explanation**: The RapidOutput object returned by RapidOCR CLI is the official standard output carrier, which contains all core information required for recognition. No additional configuration is needed, and it does not affect the tool's usage or result display.

## Frequently Asked Questions (FAQ)

1. Q: Why does the terminal prompt "Command not found" when entering `rapidocr`?
   A: Ensure that the dependencies are installed successfully. If the problem persists, restart the terminal or check if the Python environment variables are configured correctly.
2. Q: How to speed up the recognition process?
   A: Reduce optional parameters (such as `--return_word_box`) or lower the `--text_score` threshold to improve recognition speed.
3. Q: Can RapidOCR CLI recognize handwritten text?
   A: Currently, it only supports printed text recognition. The accuracy of handwritten text recognition is low and not recommended.

## Author & License

- **Author**: RapidAI
- **Email**: liekkaskono@163.com
- **Homepage**: https://rapidai.github.io/RapidOCRDocs
- **License**: Apache 2.0 License
