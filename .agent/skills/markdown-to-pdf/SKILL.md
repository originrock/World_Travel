---
name: markdown-to-pdf
description: Convert Markdown files to high-quality PDF with Mermaid diagrams, Pygments highlighting, and professional styles. Supports orientation control.
version: 1.2.0
author: MagicBox Team
category: Documentation Tools
---

# Markdown to PDF Tool Reference

This skill provides an advanced pipeline for converting technical Markdown documents into professionally formatted PDFs. It is specifically optimized for Odoo 19 development standards and general technical documentation.

## Functional Capabilities

### 🎨 Premium Themes
- `odoo_doc`: Official Odoo-branded style (purple theme, specialized alerts).
- `technical`: Dark theme optimized for code-heavy developer guides.
- `default`: Clean, high-contrast academic/professional layout.

### 🔄 Orientation Control
- **Portrait (Default)**: Standard vertical layout for reading.
- **Landscape**: Horizontal layout (`--landscape`), ideal for wide tables and Gantt charts.

### 📁 Directory Tools
- **Batch Markdown to PDF**: Convert all `.md` files in a directory via `batch_process.py`.
- **Merge PDFs**: Combine `.pdf` files from a directory into one output via `merge.py`.
- **Pipeline**: Run batch conversion, optional merge, and cleanup via `pipeline.py`.

### 📊 Diagram Support
Full integrated support for **Mermaid.js** (Gantt, Sequence, ER, Mindmap, etc.).

### 💻 Syntax Highlighting
Uses `Pygments` to provide IDE-quality highlighting for 300+ languages.

---

## Technical Configuration

The tool follows a strict priority for settings:
1. **CLI Arguments**: `-i`, `-o`, `--style`, `--landscape` take precedence.
2. **Internal Configuration**: Variables `DEFAULT_INPUT`, `DEFAULT_OUTPUT`, `DEFAULT_LANDSCAPE` inside `converter.py`.

---

## Command Interface

### Single File
```bash
# Standard
python converter.py -i input.md -o output.pdf

# Landscape with Odoo Style
python converter.py -i wide_table.md -o output.pdf --landscape --style odoo_doc
```

### Batch Mode
```bash
python converter.py --batch -i ./docs_dir -o ./pdf_dir --landscape
```

### Merge Mode
```bash
python converter.py --merge -i file1.md file2.md -o combined.pdf
```

### Directory Batch (Markdown -> PDF)
```bash
python batch_process.py -i ./docs_dir -o ./pdf_dir --style technical
```

### Directory Merge (PDFs -> PDF)
```bash
python merge.py -i ./pdf_dir -o ./combined/merged.pdf
```

### Pipeline (Batch + Merge + Cleanup)
```bash
python pipeline.py -i ./docs_dir -o ./pdf_dir --auto-merge --auto-delete
```

---

## Technical Specifications

| Feature | Support Level | Implementation Detail |
|---------|---------------|-----------------------|
| GitHub Alerts | Native | `> [!NOTE]` style with multi-line support |
| Math Formulas | Advanced | **Matplotlib** (SVG) with text fallback |
| Bookmarks | Automatic | Headings (H1/H2) generate PDF bookmarks |
| Orientation | Switchable | Portrait vs Landscape (@page size override) |
| PDF Directory Merge | Standard | Uses `pikepdf` or `pypdf/PyPDF2` when available |

## File Organization
- `converter.py`: Core orchestration and CLI logic.
- `batch_process.py`: Batch convert Markdown directory to PDFs.
- `merge.py`: Merge PDFs in a directory.
- `pipeline.py`: Batch + merge + optional cleanup flow.
- `styles/`: CSS theme definitions.
- `README.md`: Installation and setup guide.
