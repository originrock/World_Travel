#!/usr/bin/env python3
"""
Run batch Markdown conversion, optional merge, and optional cleanup.
"""

import argparse
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent

DEFAULT_INPUT_DIR = "/Users/originrock/dev/World_Travel/destinations"
DEFAULT_OUTPUT_DIR = "/Users/originrock/dev/World_Travel/destinations"
DEFAULT_AUTO_MERGE = True
DEFAULT_AUTO_DELETE = True
DEFAULT_MERGED_NAME = "/Users/originrock/dev/World_Travel"


def run_batch(input_dir: Path, output_dir: Path) -> None:
    cmd = [
        sys.executable,
        str(SKILL_DIR / "batch_process.py"),
        "-i",
        str(input_dir),
        "-o",
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)


def run_merge(output_dir: Path, merged_path: Path) -> None:
    cmd = [
        sys.executable,
        str(SKILL_DIR / "merge.py"),
        "-i",
        str(output_dir),
        "-o",
        str(merged_path),
    ]
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

    args = parser.parse_args()

    final_input = args.input or DEFAULT_INPUT_DIR
    final_output = args.output or DEFAULT_OUTPUT_DIR
    auto_merge = resolve_flag(DEFAULT_AUTO_MERGE, args.auto_merge, args.no_auto_merge)
    auto_delete = resolve_flag(DEFAULT_AUTO_DELETE, args.auto_delete, args.no_auto_delete)

    if not final_input:
        parser.error("Input directory not specified. Use -i or set DEFAULT_INPUT_DIR.")
    if not final_output:
        parser.error("Output directory not specified. Use -o or set DEFAULT_OUTPUT_DIR.")

    final_input_dir = Path(final_input)
    final_output_dir = Path(final_output)

    if not final_input_dir.exists() or not final_input_dir.is_dir():
        parser.error(f"Input directory not found: {final_input_dir}")

    run_batch(final_input_dir, final_output_dir)

    if auto_merge:
        merged_path = final_output_dir / DEFAULT_MERGED_NAME
        run_merge(final_output_dir, merged_path)

        if auto_delete:
            deleted = delete_intermediate_pdfs(final_output_dir, merged_path)
            print(f"Deleted {deleted} intermediate PDFs; kept {merged_path}")
    elif auto_delete:
        print("[WARN] auto-delete ignored because auto-merge is disabled.")


if __name__ == "__main__":
    main()
