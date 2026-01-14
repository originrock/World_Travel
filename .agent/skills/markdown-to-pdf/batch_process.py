#!/usr/bin/env python3
"""
Batch convert Markdown files in a directory to PDF using converter.py.
"""

import argparse
import sys
from pathlib import Path
from typing import List

SKILL_DIR = Path(__file__).resolve().parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from converter import Processor, DEFAULT_STYLE, DEFAULT_LANDSCAPE  # noqa: E402

DEFAULT_INPUT_DIR = "/Users/originrock/dev/World_Travel/destinations/Australia"
DEFAULT_OUTPUT_DIR = "/Users/originrock/dev/World_Travel/destinations/Australia"
DEFAULT_INTERMEDIATE_DIR = None  # User can set this in the script
DEFAULT_PATTERN = "*.md"
DEFAULT_RECURSIVE = True


def collect_markdown_files(input_dir: Path, pattern: str, recursive: bool) -> List[Path]:
    if recursive:
        candidates = input_dir.rglob(pattern)
    else:
        candidates = input_dir.glob(pattern)
    return sorted([p for p in candidates if p.is_file()])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch convert Markdown files in a directory to PDF."
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input directory (Overrides DEFAULT_INPUT_DIR)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory (Overrides DEFAULT_OUTPUT_DIR)",
    )
    parser.add_argument(
        "--style",
        help=f"CSS style name (default in script: {DEFAULT_STYLE})",
    )
    parser.add_argument(
        "--pattern",
        help=f"Glob pattern for Markdown files (default in script: {DEFAULT_PATTERN})",
    )
    parser.add_argument(
        "--landscape",
        action="store_true",
        help="Use landscape orientation",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Disable recursive search",
    )
    parser.add_argument(
        "--intermediate-dir",
        "--output-dir",
        dest="intermediate_dir",
        help="Directory to save generated PDFs (Overrides DEFAULT_INTERMEDIATE_DIR)",
    )
    parser.add_argument(
        "--header-left",
        help="Text for the top-left header",
    )

    args = parser.parse_args()

    final_input_dir = Path(args.input or DEFAULT_INPUT_DIR)
    
    # Resolve intermediate/output directory
    # Priority: CLI -> Script Default -> Output Arg
    intermediate_path = args.intermediate_dir or DEFAULT_INTERMEDIATE_DIR
    if intermediate_path:
        final_output_dir = Path(intermediate_path)
    else:
        final_output_dir = Path(args.output or DEFAULT_OUTPUT_DIR)

    final_style = args.style or DEFAULT_STYLE
    final_pattern = args.pattern or DEFAULT_PATTERN
    final_landscape = args.landscape or DEFAULT_LANDSCAPE
    final_recursive = DEFAULT_RECURSIVE and not args.no_recursive

    if not final_input_dir.exists() or not final_input_dir.is_dir():
        parser.error(f"Input directory not found: {final_input_dir}")

    markdown_files = collect_markdown_files(final_input_dir, final_pattern, final_recursive)
    if not markdown_files:
        print(f"No Markdown files found in {final_input_dir} (pattern: {final_pattern}).")
        return

    final_output_dir.mkdir(parents=True, exist_ok=True)
    processor = Processor(SKILL_DIR / "styles")

    errors = 0
    for md_path in markdown_files:
        rel_path = md_path.relative_to(final_input_dir)
        out_path = final_output_dir / rel_path.with_suffix(".pdf")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            processor.process(md_path, out_path, theme=final_style, landscape=final_landscape, header_left=args.header_left)
        except Exception as exc:
            errors += 1
            print(f"[ERROR] Failed to convert {md_path}: {exc}")

    total = len(markdown_files)
    print(f"Batch complete: {total - errors}/{total} succeeded. Output: {final_output_dir}")


if __name__ == "__main__":
    main()
