#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import pymupdf
from PIL import Image


SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg"}
SLIDE_RE = re.compile(r"^slide-(\d+)\.(png|jpe?g)$", re.IGNORECASE)


def natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def collect_images(slides_dir: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in slides_dir.iterdir()
            if path.is_file()
            and path.name.lower().startswith("slide-")
            and path.suffix.lower() in SUPPORTED_SUFFIXES
        ),
        key=natural_key,
    )


def slide_number(path: Path) -> int:
    match = SLIDE_RE.fullmatch(path.name)
    if not match:
        raise ValueError(f"Invalid slide filename: {path.name}")
    return int(match.group(1))


def validate_sequence(files: list[Path], expected_pages: int | None) -> None:
    numbers = [slide_number(path) for path in files]
    expected_count = expected_pages or len(files)
    expected = list(range(1, expected_count + 1))
    if numbers != expected:
        missing = sorted(set(expected) - set(numbers))
        detail = f"; missing pages: {missing}" if missing else ""
        raise ValueError(f"Page count or slide numbering mismatch{detail}; got {numbers}, expected {expected}")
    if len(files) != expected_count:
        raise ValueError(f"Page count mismatch: found {len(files)}, expected {expected_count}")


def image_digest(path: Path) -> str:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        return hashlib.sha256(rgb.tobytes()).hexdigest()


def validate_duplicates(files: list[Path]) -> None:
    seen = {}
    for path in files:
        digest = image_digest(path)
        if digest in seen:
            raise ValueError(f"Duplicate page image: {path.name} matches {seen[digest]}")
        seen[digest] = path.name


def validate_images(files: list[Path], expected_pages: int | None) -> tuple[int, int]:
    if not files:
        raise ValueError("No slide images found")
    validate_sequence(files, expected_pages)
    validate_duplicates(files)
    expected = None
    for path in files:
        with Image.open(path) as image:
            size = image.size
        if abs(size[0] / size[1] - 16 / 9) > 0.002:
            raise ValueError(f"Not 16:9: {path.name} ({size[0]}x{size[1]})")
        if expected is None:
            expected = size
        elif size != expected:
            raise ValueError(f"Image dimensions differ: {path.name} is {size}, expected {expected}")
    return expected


def package(files: list[Path], output: Path, quality: int, expected_pages: int | None, mode: str) -> None:
    validate_images(files, expected_pages)
    output.parent.mkdir(parents=True, exist_ok=True)
    for path in files:
        print(path.name)

    if mode == "lossless":
        document = pymupdf.open()
        try:
            for path in files:
                page = document.new_page(width=960, height=540)
                page.insert_image(page.rect, filename=str(path), keep_proportion=False)
            document.save(output, deflate=True)
        finally:
            document.close()
        return

    pages = []
    try:
        for path in files:
            with Image.open(path) as image:
                pages.append(image.convert("RGB"))
        pages[0].save(
            output,
            format="PDF",
            save_all=True,
            append_images=pages[1:],
            quality=quality,
            subsampling=0,
            resolution=150.0,
        )
    finally:
        for page in pages:
            page.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Package complete 16:9 slide images into a PDF.")
    parser.add_argument("--slides-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--quality", type=int, default=95)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--mode", choices=("jpeg", "lossless"), default="jpeg")
    args = parser.parse_args()
    if not 1 <= args.quality <= 100:
        parser.error("--quality must be between 1 and 100")
    if args.expected_pages is not None and args.expected_pages < 1:
        parser.error("--expected-pages must be at least 1")

    try:
        files = collect_images(Path(args.slides_dir))
        package(files, Path(args.out), args.quality, args.expected_pages, args.mode)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({"output": args.out, "pages": len(files), "quality": args.quality, "mode": args.mode}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
