#!/usr/bin/env python3
"""
Merge PDF files in a directory into a single PDF.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

SKILL_DIR = Path(__file__).resolve().parent


DEFAULT_INPUT_DIR = "/Users/originrock/dev/World_Travel/pdf"
DEFAULT_OUTPUT = "/Users/originrock/dev/World_Travel/pdf"
DEFAULT_OUTPUT_NAME = "Oceania_Trip_Plan.pdf"
DEFAULT_PATTERN = "*.pdf"

DEFAULT_SORT_ORDER = "desc"  # Default to descending order     choices=["asc", "desc"],

DEFAULT_RECURSIVE = True




def select_backend() -> Tuple[Optional[str], Optional[object]]:
    try:
        import pikepdf  # type: ignore
        return "pikepdf", pikepdf
    except ImportError:
        pass

    try:
        from pypdf import PdfMerger  # type: ignore
        return "pypdf", PdfMerger
    except ImportError:
        pass

    try:
        from PyPDF2 import PdfMerger  # type: ignore
        return "pypdf2", PdfMerger
    except ImportError:
        return None, None


def collect_pdf_files(input_dir: Path, pattern: str, recursive: bool, sort_order: str = "desc") -> List[Path]:
    if recursive:
        candidates = input_dir.rglob(pattern)
    else:
        candidates = input_dir.glob(pattern)
    
    is_reverse = (sort_order.lower() == "desc")
    return sorted([p for p in candidates if p.is_file()], reverse=is_reverse)


def resolve_output_path(output_arg: Optional[str]) -> Path:
    output_path = Path(output_arg) if output_arg else Path(DEFAULT_OUTPUT)
    if output_path.suffix.lower() != ".pdf":
        output_path = output_path / DEFAULT_OUTPUT_NAME
    return output_path


def merge_with_pikepdf(pikepdf_module: object, input_paths: List[Path], output_path: Path) -> None:
    pdf = pikepdf_module.Pdf.new()
    for path in input_paths:
        with pikepdf_module.open(path) as src:
            pdf.pages.extend(src.pages)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(output_path)


def merge_with_pypdf(merger_cls: object, input_paths: List[Path], output_path: Path) -> None:
    merger = merger_cls()
    for path in input_paths:
        merger.append(str(path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        merger.write(handle)
    merger.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge PDF files in a directory into one PDF."
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input directory (Overrides DEFAULT_INPUT_DIR)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF path or directory (Overrides DEFAULT_OUTPUT)",
    )
    parser.add_argument(
        "--pattern",
        help=f"Glob pattern for PDF files (default in script: {DEFAULT_PATTERN})",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Disable recursive search",
    )
    parser.add_argument(
        "--sort-order",
        choices=["asc", "desc"],
        help=f"Sort order for merging (default in script: {DEFAULT_SORT_ORDER})",
    )
    parser.add_argument(
        "--header-left",
        help="Text for the top-left header",
    )

    args = parser.parse_args()

    final_input_dir = Path(args.input or DEFAULT_INPUT_DIR)
    final_pattern = args.pattern or DEFAULT_PATTERN
    final_recursive = DEFAULT_RECURSIVE and not args.no_recursive
    final_sort_order = args.sort_order or DEFAULT_SORT_ORDER
    final_output_path = resolve_output_path(args.output)

    if not final_input_dir.exists() or not final_input_dir.is_dir():
        parser.error(f"Input directory not found: {final_input_dir}")

    backend_name, backend = select_backend()
    if not backend:
        print("No PDF merge backend available. Install pikepdf or pypdf/PyPDF2.")
        sys.exit(1)

    pdf_files = collect_pdf_files(final_input_dir, final_pattern, final_recursive, final_sort_order)
    output_resolved = final_output_path.resolve()
    pdf_files = [p for p in pdf_files if p.resolve() != output_resolved]

    if not pdf_files:
        print(f"No PDF files found in {final_input_dir} (pattern: {final_pattern}).")
        return

    if backend_name == "pikepdf":
        merge_with_pikepdf(backend, pdf_files, final_output_path)
    else:
        merge_with_pypdf(backend, pdf_files, final_output_path)

    print(f"Merged {len(pdf_files)} PDFs into {final_output_path}")


if __name__ == "__main__":
    main()
