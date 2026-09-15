#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import fitz

FONT_SUFFIXES = {".ttf", ".otf", ".ttc"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def validate(delivery_dir: Path, deck_name: str) -> dict:
    if not delivery_dir.is_dir():
        raise ValueError(f"Delivery directory not found: {delivery_dir}")

    required = {
        f"{deck_name}.pdf",
        "PPT内容大纲.txt",
        "风格提示词.txt",
        "字体说明.txt",
        "fonts",
    }
    allowed = required | {"images"}
    actual = {path.name for path in delivery_dir.iterdir()}
    unexpected = sorted(actual - allowed)
    missing = sorted(required - actual)
    if unexpected:
        raise ValueError(f"Unexpected delivery items: {', '.join(unexpected)}")
    if missing:
        raise ValueError(f"Missing delivery items: {', '.join(missing)}")

    pdf_path = delivery_dir / f"{deck_name}.pdf"
    if not pdf_path.is_file():
        raise ValueError("Expected PDF is not a file")

    for filename in ("PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt"):
        text_path = delivery_dir / filename
        if not text_path.is_file() or not text_path.read_text(encoding="utf-8").strip():
            raise ValueError(f"Required planning file is missing or empty: {filename}")

    fonts_dir = delivery_dir / "fonts"
    if not fonts_dir.is_dir():
        raise ValueError("fonts must be a directory")
    font_files = sorted(
        str(path.relative_to(delivery_dir))
        for path in fonts_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in FONT_SUFFIXES
    )
    if not font_files:
        raise ValueError("fonts is empty or contains no supported font files")

    images_dir = delivery_dir / "images"
    image_files = []
    if images_dir.exists():
        if not images_dir.is_dir():
            raise ValueError("images must be a directory when present")
        image_files = sorted(
            str(path.relative_to(delivery_dir))
            for path in images_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )
        if not image_files:
            raise ValueError("images is present but contains no supported image files")

    with fitz.open(pdf_path) as document:
        page_count = document.page_count
    if page_count < 1:
        raise ValueError("PDF has no pages")

    return {
        "pdf": str(pdf_path),
        "pages": page_count,
        "delivery_items": sorted(actual),
        "font_files": font_files,
        "image_files": image_files,
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
