#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image


SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg"}


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


def validate_images(files: list[Path]) -> tuple[int, int]:
    if not files:
        raise ValueError("No slide images found")
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


def package(files: list[Path], output: Path, quality: int) -> None:
    validate_images(files)
    output.parent.mkdir(parents=True, exist_ok=True)
    pages = []
    try:
        for path in files:
            with Image.open(path) as image:
                pages.append(image.convert("RGB"))
            print(path.name)
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
    args = parser.parse_args()
    if not 1 <= args.quality <= 100:
        parser.error("--quality must be between 1 and 100")

    try:
        files = collect_images(Path(args.slides_dir))
        package(files, Path(args.out), args.quality)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({"output": args.out, "pages": len(files), "quality": args.quality}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
