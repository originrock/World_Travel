# Markdown to PDF Converter

A professional-grade tool to convert Markdown files to beautifully styled PDFs. Optimized for technical documentation, Odoo-style manuals, and developer guides.

## Features

- ✅ **Smart Pipeline**: Markdown to HTML via `python-markdown` with advanced extensions.
- ✅ **Mermaid Diagrams**: Full support for diagrams with automatic SVG rendering (requires `mmdc`).
- ✅ **Code Highlighting**: Professional syntax highlighting via `Pygments`.
- ✅ **Premium Styling**: High-quality PDF generation using `WeasyPrint` with full CSS support.
- ✅ **Flexible Workflow**: Supports single file, batch processing, and merging multiple files.
- ✅ **Directory Scripts**: Batch conversion, merge, and pipeline workflows via dedicated scripts.

---

## Installation

### 1. Python Dependencies
Activate your virtual environment (e.g., Odoo 19 environment) and install the core packages:

```bash
source /Users/originrock/dev/Venv/Box_19/bin/activate
pip install markdown pymdown-extensions pygments weasyprint beautifulsoup4 matplotlib
```

Optional for PDF directory merging:
```bash
pip install pikepdf pypdf
```

### 2. Mermaid CLI (Optional)
If you want to render Mermaid diagrams, install the CLI tool:

```bash
npm install -g @mermaid-js/mermaid-cli
```

### 3. System Libraries (macOS)
WeasyPrint requires some system-level libraries for font and image rendering:

```bash
brew install pango gdk-pixbuf libffi
```

---

## Quick Start

### 1. Set Defaults (Optional)
Open `converter.py` and set your preferred paths:
```python
DEFAULT_INPUT = "my_doc.md"
DEFAULT_OUTPUT = "output.pdf"
```

### 2. Run Single Conversion
```bash
# Using defaults
python converter.py

# Overriding with arguments
python converter.py -i README.md -o manual.pdf --style odoo_doc

# Landscape mode for wide documents
python converter.py -i wide_table.md -o output.pdf --landscape
```

### 3. Batch and Merge
```bash
# Batch convert a directory
python converter.py --batch -i ./docs -o ./pdf_out --style technical

# Merge files into one PDF
python converter.py --merge -i file1.md file2.md -o combined.pdf
```

### 4. Directory Scripts
```bash
# Batch convert all Markdown files in a directory
python batch_process.py -i ./docs -o ./pdf_out --style odoo_doc

# Merge all PDFs in a directory into one file
python merge.py -i ./pdf_out -o ./combined/merged.pdf

# Batch -> merge -> cleanup
python pipeline.py -i ./docs -o ./pdf_out --auto-merge --auto-delete
```

---

## Troubleshooting

### macOS Library Error (libgobject / pango)
如果您看到 `OSError: cannot load library 'libgobject-2.0-0'`：

1.  **脚本自愈**: 最新版本的 `converter.py` 已包含自动检测 Homebrew 路径的代码。
2.  **PyCharm 设置**: 如果在 PyCharm 中依然报错，请点击菜单的 **Run -> Edit Configurations**，在 **Environment variables** 中添加：
    *   Name: `DYLD_LIBRARY_PATH`
    *   Value: `/opt/homebrew/lib`
3.  **全局设置**: 或者在您的 `~/.zshrc` 中添加：
    ```bash
    export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
    ```

For more detailed technical specifications and style options, see [skill.md](SKILL.md).
