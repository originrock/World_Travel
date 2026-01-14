#!/usr/bin/env python3
"""
Advanced Markdown to PDF Converter
Supports:
- Professional Technical Styling (WeasyPrint)
- Code Highlighting (Pygments)
- Mermaid Diagrams (mermaid-cli)
- GitHub Alerts
- Batch & Merge Processing
"""

import io
import os
import re
import sys
import hashlib
import tempfile
import argparse
import subprocess
import json
import markdown

from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime


# ==========================================
# 默认配置 (Default Configuration)
# ==========================================
# 您可以在这里预设输入和输出，以便在不带参数时直接运行。
# 支持文件路径字符串或 Path 对象。

DEFAULT_INPUT = "/Users/originrock/dev/MagicBox_19/.claude/skills/markdown-to-pdf/test_document.md"   # 示例: "test_document.md" 或 "doc/folder"
DEFAULT_OUTPUT = "/Users/originrock/dev/MagicBox_19/.claude/skills/markdown-to-pdf/test_document.pdf"  # 示例: "output.pdf" 或 "output_dir"
DEFAULT_STYLE = 'odoo_doc'
DEFAULT_LANDSCAPE = False  # 是否默认横版 (True 为横版, False 为竖版)
DEFAULT_HEADER = ""  # 留空则从文件名自动生成，如 "My Project Documentation"

# ==========================================

# Try importing Matplotlib for Math rendering
try:
    import matplotlib
    matplotlib.use('Agg') # Force headless backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[WARN] Matplotlib not found. Math formulas will be rendered as text.")



# --- macOS Library Path Fix (Self-Healing) ---
# 解决在 PyCharm 或其他 IDE 中运行无法找到 Homebrew 安装库的问题
if sys.platform == 'darwin':
    paths = ['/opt/homebrew/lib', '/opt/homebrew/opt/libffi/lib']
    existing_dyld = os.environ.get('DYLD_LIBRARY_PATH', '')
    new_paths = [p for p in paths if os.path.exists(p) and p not in existing_dyld]
    if new_paths:
        os.environ['DYLD_LIBRARY_PATH'] = ":".join(new_paths) + (f":{existing_dyld}" if existing_dyld else "")
# ---------------------------------------------

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except OSError as e:
    print(f"\n[ERROR] WeasyPrint 核心库加载失败: {e}")
    print("\n这是由于系统无法找到所需的图形及排版库导致的。")
    print("如果您已使用 Homebrew 安装了相关软件，请确保执行以下操作:")
    print("1. 终端运行: export DYLD_LIBRARY_PATH=\"/opt/homebrew/lib:$DYLD_LIBRARY_PATH\"")
    print("2. 如果是在 PyCharm 中运行，请在 Run Configuration -> Environment Variables 中添加上述变量。")
    print("\n安装命令: brew install pango gdk-pixbuf libffi")
    sys.exit(1)

class MarkdownPipeline:
    """Handles Markdown to HTML conversion with advanced extensions."""
    
    def __init__(self):
        self.extensions = [
            'extra',
            'tables',
            'toc',
            'admonition',
            'codehilite',
            'fenced_code',
            'nl2br',
            'sane_lists',
            'pymdownx.superfences',
            'pymdownx.magiclink',
            'pymdownx.tasklist',
            'pymdownx.tilde',
            'pymdownx.caret',
            'pymdownx.arithmatex',
        ]
        self.extension_configs = {
            'codehilite': {
                'css_class': 'codehilite',
                'guess_lang': False,
                'use_pygments': True,
                'noclasses': False,
            },
            'pymdownx.arithmatex': {
                'generic': True
            },
            'pymdownx.superfences': {
                'custom_fences': [
                    {
                        'name': 'mermaid',
                        'class': 'mermaid',
                        'format': self._mermaid_format
                    }
                ]
            }
        }

    def _mermaid_format(self, source, language, class_name, options, md, **kwargs):
        """Preserve mermaid source in a special div for post-processing."""
        return f'<div class="mermaid-container" data-mermaid-source="{source.strip()}"></div>'

    def convert(self, md_text: str) -> str:
        """Convert Markdown text to HTML body content."""
        html = markdown.markdown(
            md_text, 
            extensions=self.extensions,
            extension_configs=self.extension_configs
        )
        return html

class MermaidRenderer:
    """Renders Mermaid diagrams using mmdc."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "mermaid_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.mmdc_path = self._find_mmdc()

    def _find_mmdc(self) -> str:
        """Find the mermaid-cli executable."""
        try:
            result = subprocess.run(['which', 'mmdc'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "mmdc"

    def render_all(self, html_content: str) -> str:
        """Find all mermaid containers and replace them with rendered SVGs.
        
        Also handles WeasyPrint compatibility by converting foreignObject text
        to native SVG text elements.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        containers = soup.find_all('div', class_='mermaid-container')
        
        if not containers:
            return html_content

        for container in containers:
            source = container.get('data-mermaid-source', '')
            if not source:
                continue
            
            svg_content = self._render_diagram(source)
            if svg_content:
                # Inject SVG directly into HTML
                svg_soup = BeautifulSoup(svg_content, 'xml')
                svg_tag = svg_soup.find('svg')
                if svg_tag:
                    # FIX: Convert foreignObject text to native SVG text for WeasyPrint
                    self._convert_foreign_objects_to_text(svg_soup, svg_tag)
                    
                    # Injects explicit styling for text visibility
                    style_tag = svg_soup.new_tag('style')
                    style_tag.string = """
                        text, tspan, .nodeLabel, .edgeLabel, .label, .mindmap-node text, .converted-text { 
                            font-family: sans-serif !important;
                            font-weight: normal !important;
                        }
                        .converted-text {
                            fill: #333333;
                        }
                    """
                    svg_tag.insert(0, style_tag)
                    container.replace_with(svg_tag)
            else:
                container.string = "[Error rendering Mermaid diagram]"
        
        return str(soup)
    
    def _convert_foreign_objects_to_text(self, svg_soup, svg_tag):
        """Convert foreignObject elements to native SVG text elements.
        
        WeasyPrint does not properly render foreignObject, especially for
        ER diagrams and Mindmaps. This method extracts text content and
        replaces foreignObject with native SVG <text> elements.
        """
        import re
        
        # Find all foreignObject elements
        foreign_objects = svg_tag.find_all('foreignObject')
        
        for fo in foreign_objects:
            # Get the parent g element (which has the transform)
            parent_g = fo.find_parent('g')
            
            # Extract text content
            text_content = ''
            node_label = fo.find(class_='nodeLabel')
            if node_label:
                # Get text, handling <p> tags inside
                p_tag = node_label.find('p')
                if p_tag:
                    text_content = p_tag.get_text(strip=True)
                else:
                    text_content = node_label.get_text(strip=True)
            else:
                # Fallback: get all text
                text_content = fo.get_text(strip=True)
            
            if not text_content:
                continue
            
            # Get foreignObject dimensions
            width = fo.get('width', '0')
            height = fo.get('height', '0')
            
            # Handle 'NaN' or invalid values
            try:
                w = float(width) if width and width != 'NaN' else 100
                h = float(height) if height and height != 'NaN' else 24
            except ValueError:
                w, h = 100, 24
            
            # Calculate text position (center of the foreignObject)
            x = w / 2
            y = h / 2 + 4  # Slight offset for vertical centering
            
            # Create replacement SVG text element
            text_elem = svg_soup.new_tag('text')
            text_elem['x'] = str(x)
            text_elem['y'] = str(y)
            text_elem['text-anchor'] = 'middle'
            text_elem['dominant-baseline'] = 'middle'
            text_elem['class'] = 'converted-text'
            text_elem['font-size'] = '14'
            text_elem['fill'] = '#333333'
            text_elem.string = text_content
            
            # Replace foreignObject with text element
            fo.replace_with(text_elem)

    def _render_diagram(self, source: str) -> Optional[str]:
        """Render a single mermaid diagram to SVG."""
        content_hash = hashlib.md5(source.encode()).hexdigest()
        mmd_file = self.cache_dir / f"{content_hash}.mmd"
        svg_file = self.cache_dir / f"{content_hash}.svg"
        
        # Create a temporary config file for Mermaid to force darker text
        config_file = self.cache_dir / "mermaid_config.json"
        config_data = {
            "themeVariables": {
                "primaryTextColor": "#333333",
                "secondaryTextColor": "#333333",
                "tertiaryTextColor": "#333333",
                "textColor": "#333333",
                "lineColor": "#666666"
            },
            "mindmap": {
                "padding": 20
            }
        }
        config_file.write_text(json.dumps(config_data), encoding='utf-8')

        if svg_file.exists():
            return svg_file.read_text(encoding='utf-8')

        mmd_file.write_text(source, encoding='utf-8')
        
        try:
            # Use neutral theme + custom config + white bg
            cmd = [
                self.mmdc_path, 
                '-i', str(mmd_file), 
                '-o', str(svg_file), 
                '-t', 'neutral', 
                '-b', 'white', 
                '--scale', '2',
                '-c', str(config_file)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Mermaid error: {result.stderr}")
                return None
        except Exception as e:
            print(f"Failed to call mmdc: {e}")
            return None
        finally:
            if mmd_file.exists():
                mmd_file.unlink()

        return svg_file.read_text(encoding='utf-8') if svg_file.exists() else None

class ThemeManager:
    """Manages CSS themes and HTML wrapping."""
    
    def __init__(self, style_dir: Path):
        self.style_dir = style_dir

    def get_full_html(self, body_content: str, title: str, theme_name: str = 'default', landscape: bool = False, header_text: str = "") -> str:
        css_path = self.style_dir / f"{theme_name}.css"
        css_content = css_path.read_text(encoding='utf-8') if css_path.exists() else ""
        
        # Dynamic header injection - override CSS @page @top-right content
        header_display = header_text or title
        header_css = f"""@page {{ @top-right {{ content: \"{header_display}\"; }} }}"""
        
        # Orientation CSS override
        orientation_css = "@page { size: A4 landscape !important; }" if landscape else ""
        
        # GitHub Alert CSS (Inject standard alerts)
        alert_css = """
        .alert { padding: 1em; margin: 1em 0; border-left: 4px solid; border-radius: 4px; }
        .alert-title { font-weight: bold; margin-bottom: 0.5em; display: block; }
        .alert-note { background: #e3f2fd; border-color: #2196f3; color: #0d47a1; }
        .alert-tip { background: #f1f8e9; border-color: #8bc34a; color: #33691e; }
        .alert-important { background: #f3e5f5; border-color: #9c27b0; color: #4a148c; }
        .alert-warning { background: #fff3e0; border-color: #ff9800; color: #e65100; }
        .alert-caution { background: #ffebee; border-color: #f44336; color: #b71c1c; }
        """
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        {alert_css}
        {css_content}
        {header_css}
        {orientation_css}
    </style>
</head>
<body>
    <div class="container">
        {self._process_math(self._process_alerts(body_content), theme_name)}
    </div>
</body>
</html>"""

    def _process_alerts(self, html: str) -> str:
        """Convert standard blockquote alerts to styled divs while preserving internal structure."""
        ALERT_TYPES = {
            'NOTE': 'note', 'TIP': 'tip', 'IMPORTANT': 'important',
            'WARNING': 'warning', 'CAUTION': 'caution'
        }
        
        soup = BeautifulSoup(html, 'html.parser')
        for bq in soup.find_all('blockquote'):
            # Check if it starts with [!TYPE]
            # Use find(text=True) to look for the marker in the first content node
            first_text = bq.find(string=lambda t: any(f'[!{k}]' in t for k in ALERT_TYPES))
            if not first_text:
                continue

            matched_key = None
            for key in ALERT_TYPES:
                marker = f'[!{key}]'
                if marker in first_text:
                    matched_key = key
                    break
            
            if matched_key:
                val = ALERT_TYPES[matched_key]
                marker = f'[!{matched_key}]'
                
                # Create new alert structure
                new_div = soup.new_tag('div', attrs={'class': f'alert alert-{val}'})
                
                # Add Title
                title_div = soup.new_tag('div', attrs={'class': 'alert-title'})
                title_div.string = matched_key.capitalize()
                new_div.append(title_div)
                
                # Remove the marker from the text node
                new_text = first_text.replace(marker, '', 1).lstrip()
                first_text.replace_with(new_text)

                # Move all contents of blockquote to the new div
                # We use list(bq.contents) to avoid modification issues during iteration
                for child in list(bq.contents):
                    new_div.append(child)
                
                bq.replace_with(new_div)
        
        return str(soup)

    def _process_math(self, html: str, theme_name: str = 'default') -> str:
        """Improve math formula appearance using Matplotlib (SVG) or text beautification."""
        
        # Theme colors for Math
        THEME_COLORS = {
            'technical': '#dcdcaa',
            'odoo_doc': '#333333',
            'default': '#333333'
        }
        text_color = THEME_COLORS.get(theme_name, '#333333')

        soup = BeautifulSoup(html, 'html.parser')
        
        for math_tag in soup.find_all(class_='arithmatex'):
            content = math_tag.get_text()
            
            # 1. Detect Block vs Inline
            # standard arithmatex generic output uses \[...\] for block and \(...\) for inline
            is_block = '\\[' in content or '$$' in content
            
            # 2. Clean up delimiters
            clean_tex = content
            for delim in ['$$', '\\[', '\\]', '\\(', '\\)']:
                clean_tex = clean_tex.replace(delim, '')
            clean_tex = clean_tex.strip()

            rendered = False
            
            # 3. Try Rendering via Matplotlib
            if MATPLOTLIB_AVAILABLE and clean_tex:
                try:
                    svg_data = self._render_latex_to_svg(clean_tex, text_color)
                    if svg_data:
                        # Parse SVG and insert
                        svg_soup = BeautifulSoup(svg_data, 'xml')
                        svg_element = svg_soup.find('svg')
                        if svg_element:
                            # Add class for sizing
                            base_class = 'math-svg'
                            layout_class = 'math-block' if is_block else 'math-inline'
                            svg_element['class'] = f"{base_class} {layout_class}"
                            
                            math_tag.replace_with(svg_element)
                            rendered = True
                except Exception as e:
                    print(f"[Math Render Error] '{clean_tex}': {e}")

            # 4. Fallback: Text Beautification
            if not rendered:
                # Simple unicode replacements for common symbols
                replacements = {
                    '\\pm': '±', '\\times': '×', '\\div': '÷',
                    '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ',
                    '\\delta': 'δ', '\\pi': 'π', '\\theta': 'θ',
                    '\\infty': '∞', '\\neq': '≠', '\\leq': '≤', '\\geq': '≥',
                    '^2': '²', '^3': '³', '_{0}': '₀'
                }
                display_text = clean_tex
                for tex, uni in replacements.items():
                    display_text = display_text.replace(tex, uni)
                
                math_tag.string = display_text
            
        return str(soup)

    def _render_latex_to_svg(self, latex: str, color: str) -> Optional[str]:
        """Render TeX string to SVG using Matplotlib."""
        try:
            fig = plt.figure(figsize=(0.01, 0.01))
            fig.patch.set_alpha(0)  # Transparent bg
            
            # Setup text
            # We wrap in $...$ for MathText
            text = fig.text(0, 0, f"${latex}$", fontsize=14, color=color)
            
            # Save to buffer
            output = io.BytesIO()
            fig.savefig(output, format='svg', bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            
            return output.getvalue().decode('utf-8')
        except Exception:
            try:
                plt.close(fig)
            except:
                pass
            raise
        # Add a simple client-side MathJax script if we were in browser, 
        # but since we are in WeasyPrint, we add a placeholder CSS for math center alignment

class PDFEngine:
    """Generates PDF using WeasyPrint."""
    
    def generate(self, html_content: str, output_path: Path):
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        html.write_pdf(str(output_path), font_config=font_config)

class Processor:
    """Orchestrates the conversion process."""
    
    def __init__(self, style_dir: Path):
        self.pipeline = MarkdownPipeline()
        self.mermaid = MermaidRenderer()
        self.themes = ThemeManager(style_dir)
        self.engine = PDFEngine()

    def process(self, input_path: Path, output_path: Path, theme: str = 'default', **kwargs):
        print(f"Processing {input_path.name}...")
        md_text = input_path.read_text(encoding='utf-8')
        
        # 1. MD -> HTML
        html_body = self.pipeline.convert(md_text)
        
        # 2. Render Mermaid
        html_body = self.mermaid.render_all(html_body)
        
        # 3. Wrap with Theme
        title = input_path.stem.replace('_', ' ').title()
        full_html = self.themes.get_full_html(html_body, output_path.stem.title(), theme, kwargs.get('landscape', False))
        
        # 4. Generate PDF
        self.engine.generate(full_html, output_path)
        print(f"Created: {output_path}")

    def batch(self, input_dir: Path, output_dir: Path, pattern: str = "*.md", theme: str = 'default', **kwargs):
        output_dir.mkdir(parents=True, exist_ok=True)
        files = list(input_dir.glob(pattern))
        print(f"Batch processing {len(files)} files...")
        for f in files:
            rel_path = f.relative_to(input_dir)
            out_f = output_dir / rel_path.with_suffix('.pdf')
            out_f.parent.mkdir(parents=True, exist_ok=True)
            try:
                self.process(f, out_f, theme, **kwargs)
            except Exception as e:
                print(f"Error processing {f}: {e}")

    def merge(self, input_paths: List[Path], output_path: Path, theme: str = 'default', **kwargs):
        print(f"Merging {len(input_paths)} files into {output_path.name}...")
        combined_body = []
        for i, p in enumerate(input_paths):
            md_text = p.read_text(encoding='utf-8')
            html_body = self.pipeline.convert(md_text)
            html_body = self.mermaid.render_all(html_body)
            # Add section break and page break
            combined_body.append(f'<section id="part-{i}" style="page-break-after: always;">{html_body}</section>')
        
        full_html = self.themes.get_full_html("\n".join(combined_body), "Merged Document", theme)
        self.engine.generate(full_html, output_path)
        print(f"Merged PDF created: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Advanced Markdown to PDF Converter')
    parser.add_argument('-i', '--input', nargs='+', help='Input file(s) or directory (Overrides DEFAULT_INPUT)')
    parser.add_argument('-o', '--output', help='Output file or directory (Overrides DEFAULT_OUTPUT)')
    parser.add_argument('--style', help=f'CSS style name (default in script: {DEFAULT_STYLE})')
    parser.add_argument('--batch', action='store_true', help='Batch process directory')
    parser.add_argument('--merge', action='store_true', help='Merge multiple files')
    parser.add_argument('--landscape', action='store_true', help='Use landscape orientation')
    
    args = parser.parse_args()
    
    # 采用逻辑: 命令行参数 > 脚本内部定义 > 报错
    final_input = args.input or ([DEFAULT_INPUT] if DEFAULT_INPUT else None)
    final_output = args.output or DEFAULT_OUTPUT
    final_style = args.style or DEFAULT_STYLE
    final_landscape = args.landscape or DEFAULT_LANDSCAPE
    
    if not final_input:
        parser.error("错误: 未指定输入源！请使用 -i 参数或在脚本中设置 DEFAULT_INPUT。")
    if not final_output:
        parser.error("错误: 未指定输出路径！请使用 -o 参数或在脚本中设置 DEFAULT_OUTPUT。")
    
    skill_dir = Path(__file__).parent
    processor = Processor(skill_dir / 'styles')
    
    if args.merge:
        inputs = [Path(p) for p in final_input]
        processor.merge(inputs, Path(final_output), final_style, landscape=final_landscape)
    elif args.batch:
        processor.batch(Path(final_input[0]), Path(final_output), theme=final_style, landscape=final_landscape)
    else:
        processor.process(Path(final_input[0]), Path(final_output), final_style, landscape=final_landscape)

if __name__ == "__main__":
    main()
