#!/usr/bin/env python3
"""
Run batch Markdown conversion, optional merge, and optional cleanup.
"""

import argparse
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent

DEFAULT_INPUT_DIR = "/Users/originrock/dev/World_Travel/global_plan"
DEFAULT_INTERMEDIATE_DIR = "/Users/originrock/dev/World_Travel/pdf/intermediate/global_plan"  # User can set this in the script
DEFAULT_OUTPUT_DIR = "/Users/originrock/dev/World_Travel/pdf"
DEFAULT_MERGED_NAME = "global_plan.pdf"

DEFAULT_SORT_ORDER = "desc"  # Default to descending order         choices=["asc", "desc"],

DEFAULT_AUTO_MERGE = True
DEFAULT_AUTO_DELETE = False



def run_batch(input_dir: Path, output_dir: Path, header_left: str = "") -> None:
    cmd = [
        sys.executable,
        str(SKILL_DIR / "batch_process.py"),
        "-i",
        str(input_dir),
        "--intermediate-dir",
        str(output_dir),
    ]
    if header_left:
        cmd.extend(["--header-left", header_left])
    subprocess.run(cmd, check=True)


def run_merge(output_dir: Path, merged_path: Path, sort_order: str = "desc", header_left: str = "") -> None:
    cmd = [
        sys.executable,
        str(SKILL_DIR / "merge.py"),
        "-i",
        str(output_dir),
        "-o",
        str(merged_path),
        "--sort-order",
        sort_order,
    ]
    if header_left:
        cmd.extend(["--header-left", header_left])
    subprocess.run(cmd, check=True)


def delete_intermediate_pdfs(output_dir: Path, merged_path: Path) -> int:
    merged_resolved = merged_path.resolve()
    deleted = 0
    for pdf_path in output_dir.rglob("*.pdf"):
        if pdf_path.resolve() == merged_resolved:
            continue
        pdf_path.unlink()
        deleted += 1
    return deleted


def resolve_flag(default_value: bool, enable_flag: bool, disable_flag: bool) -> bool:
    if enable_flag:
        return True
    if disable_flag:
        return False
    return default_value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch convert Markdown and optionally merge/cleanup PDFs."
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
        "--intermediate-dir",
        help="Intermediate directory for individual PDFs (defaults to .temp_pdfs inside output)",
    )
    parser.add_argument(
        "--auto-merge",
        action="store_true",
        help="Merge all PDFs in the output directory",
    )
    parser.add_argument(
        "--no-auto-merge",
        action="store_true",
        help="Disable auto merge",
    )
    parser.add_argument(
        "--auto-delete",
        action="store_true",
        help="Delete intermediate PDFs after merging",
    )
    parser.add_argument(
        "--no-auto-delete",
        action="store_true",
        help="Disable auto delete",
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

    final_input = args.input or DEFAULT_INPUT_DIR
    final_output = args.output or DEFAULT_OUTPUT_DIR
    auto_merge = resolve_flag(DEFAULT_AUTO_MERGE, args.auto_merge, args.no_auto_merge)
    auto_delete = resolve_flag(DEFAULT_AUTO_DELETE, args.auto_delete, args.no_auto_delete)
    final_sort_order = args.sort_order or DEFAULT_SORT_ORDER

    if not final_input:
        parser.error("Input directory not specified. Use -i or set DEFAULT_INPUT_DIR.")
    if not final_output:
        parser.error("Output directory not specified. Use -o or set DEFAULT_OUTPUT_DIR.")

    final_input_dir = Path(final_input)
    final_output_dir = Path(final_output)
    
    # Resolve intermediate directory
    # Priority: CLI -> Script Default -> Error if missing
    if args.intermediate_dir:
        intermediate_dir = Path(args.intermediate_dir)
    elif DEFAULT_INTERMEDIATE_DIR:
        intermediate_dir = Path(DEFAULT_INTERMEDIATE_DIR)
    else:
        parser.error("Intermediate directory not specified. Use --intermediate-dir or set DEFAULT_INTERMEDIATE_DIR in the script.")

    if not final_input_dir.exists() or not final_input_dir.is_dir():
        parser.error(f"Input directory not found: {final_input_dir}")

    # Step 1: Batch convert to intermediate directory
    print(f"Phase 1: Converting Markdown to PDFs in {intermediate_dir}...")
    run_batch(final_input_dir, intermediate_dir, header_left=args.header_left)

    # Step 2: Merge if requested
    if auto_merge:
        # Determine merged path
        if DEFAULT_MERGED_NAME.startswith("/") or DEFAULT_MERGED_NAME.startswith("./"):
             merged_path = Path(DEFAULT_MERGED_NAME)
        else:
             merged_path = final_output_dir / DEFAULT_MERGED_NAME
        
        if merged_path.suffix.lower() != ".pdf":
            merged_path = merged_path.with_suffix(".pdf")

        print(f"Phase 2: Merging PDFs into {merged_path}...")
        run_merge(intermediate_dir, merged_path, final_sort_order, header_left=args.header_left)

        if auto_delete:
            deleted = delete_intermediate_pdfs(intermediate_dir, merged_path)
            print(f"Phase 3: Deleted {deleted} intermediate PDFs from {intermediate_dir}")
            
            # Clean up intermediate dir if empty
            try:
                if not any(intermediate_dir.iterdir()):
                    intermediate_dir.rmdir()
                    print(f"Cleaned up empty intermediate directory: {intermediate_dir}")
            except Exception:
                pass
    else:
        # If not merging, maybe move them to final output or just leave them
        # Current behavior: they stay in intermediate_dir (which might be the output dir if defaulting to it)
        # But wait, I changed default to .temp_pdfs. 
        # If auto_merge is false, user probably wants them in final_output.
        if not args.intermediate_dir:
            # Move from .temp_pdfs to final_output
            print(f"Moving PDFs from {intermediate_dir} to {final_output_dir}...")
            final_output_dir.mkdir(parents=True, exist_ok=True)
            for pdf_path in intermediate_dir.rglob("*.pdf"):
                rel = pdf_path.relative_to(intermediate_dir)
                dest = final_output_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                pdf_path.replace(dest)
            
            # Clean up
            try:
                # Simple cleanup of emptied dirs
                for d in sorted(intermediate_dir.rglob("*"), key=lambda x: len(str(x)), reverse=True):
                    if d.is_dir() and not any(d.iterdir()):
                        d.rmdir()
                if not any(intermediate_dir.iterdir()):
                    intermediate_dir.rmdir()
            except Exception:
                pass
        
        if auto_delete:
            print("[WARN] auto-delete ignored because auto-merge is disabled.")


if __name__ == "__main__":
    main()
