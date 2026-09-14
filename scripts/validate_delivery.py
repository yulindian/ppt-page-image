#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import fitz


def validate(delivery_dir: Path, deck_name: str) -> dict:
    if not delivery_dir.is_dir():
        raise ValueError(f"Delivery directory not found: {delivery_dir}")

    expected = {f"{deck_name}.pdf", "字体说明.txt"}
    actual = {path.name for path in delivery_dir.iterdir()}
    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    if unexpected:
        raise ValueError(f"Unexpected delivery items: {', '.join(unexpected)}")
    if missing:
        raise ValueError(f"Missing delivery items: {', '.join(missing)}")

    pdf_path = delivery_dir / f"{deck_name}.pdf"
    font_notes = delivery_dir / "字体说明.txt"
    if not pdf_path.is_file():
        raise ValueError("Expected PDF is not a file")
    if not font_notes.is_file() or not font_notes.read_text(encoding="utf-8").strip():
        raise ValueError("Font instructions are missing or empty")

    with fitz.open(pdf_path) as document:
        page_count = document.page_count
    if page_count < 1:
        raise ValueError("PDF has no pages")

    return {
        "pdf": str(pdf_path),
        "pages": page_count,
        "delivery_items": sorted(actual),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the ppt-page-image delivery contract.")
    parser.add_argument("--delivery-dir", required=True)
    parser.add_argument("--deck-name", required=True)
    args = parser.parse_args()
    try:
        result = validate(Path(args.delivery_dir), args.deck_name)
    except (OSError, UnicodeError, ValueError, fitz.FileDataError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
