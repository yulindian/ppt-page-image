#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import fitz

FONT_SUFFIXES = {".ttf", ".otf", ".ttc"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
STALE_NAME_TOKENS = ("v2", "v3", "旧版", "修改版", "final-final", "candidate", "backup", "备份")
PROCESS_ITEM_NAMES = {".work", "slides", "preview", "previews", "render", "renders", "ocr", "montage", "montages", "reports"}


def has_stale_or_process_name(path: Path) -> bool:
    lowered = path.name.lower()
    return path.name in PROCESS_ITEM_NAMES or any(token in lowered for token in STALE_NAME_TOKENS)


def validate(delivery_dir: Path, deck_name: str, expected_pages: int | None = None) -> dict:
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
    stale = sorted(path.name for path in delivery_dir.iterdir() if has_stale_or_process_name(path))
    if stale:
        raise ValueError(f"Unexpected old or process delivery items are not allowed: {', '.join(stale)}")
    unexpected = sorted(actual - allowed)
    missing = sorted(required - actual)
    if unexpected:
        raise ValueError(f"Unexpected delivery items: {', '.join(unexpected)}")
    if missing:
        raise ValueError(f"Missing delivery items: {', '.join(missing)}")

    pdf_path = delivery_dir / f"{deck_name}.pdf"
    if not pdf_path.is_file():
        raise ValueError("Expected PDF is not a file")

    planning_texts = {}
    for filename in ("PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt"):
        text_path = delivery_dir / filename
        text = text_path.read_text(encoding="utf-8") if text_path.is_file() else ""
        if not text.strip():
            raise ValueError(f"Required planning file is missing or empty: {filename}")
        planning_texts[filename] = text

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
    font_notes = planning_texts["字体说明.txt"]
    for font_file in font_files:
        font_name = Path(font_file).name
        if font_name not in font_notes and font_file.replace("\\", "/") not in font_notes:
            raise ValueError(f"Font file is not registered in 字体说明.txt: {font_file}")

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
        style_notes = planning_texts["风格提示词.txt"]
        for image_file in image_files:
            image_name = Path(image_file).name
            if image_name not in style_notes and image_file.replace("\\", "/") not in style_notes:
                raise ValueError(f"Image asset is not registered in 风格提示词.txt: {image_file}")

    with fitz.open(pdf_path) as document:
        page_count = document.page_count
    if page_count < 1:
        raise ValueError("PDF has no pages")
    if expected_pages is not None and page_count != expected_pages:
        raise ValueError(f"PDF page count mismatch: found {page_count}, expected {expected_pages}")

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
    parser.add_argument("--expected-pages", type=int)
    args = parser.parse_args()
    if args.expected_pages is not None and args.expected_pages < 1:
        parser.error("--expected-pages must be at least 1")
    try:
        result = validate(Path(args.delivery_dir), args.deck_name, args.expected_pages)
    except (OSError, UnicodeError, ValueError, fitz.FileDataError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
