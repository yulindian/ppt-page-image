#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_montage(images: list[Path], output: Path, thumb_width: int = 480) -> None:
    thumbs = []
    for index, path in enumerate(images, start=1):
        with Image.open(path) as image:
            thumb_height = round(image.height * thumb_width / image.width)
            thumb = image.convert("RGB").resize((thumb_width, thumb_height))
        canvas = Image.new("RGB", (thumb_width, thumb.height + 32), "white")
        canvas.paste(thumb, (0, 32))
        ImageDraw.Draw(canvas).text((12, 8), f"Page {index}", fill="black")
        thumbs.append(canvas)

    columns = min(4, len(thumbs))
    rows = math.ceil(len(thumbs) / columns)
    cell_width = max(image.width for image in thumbs)
    cell_height = max(image.height for image in thumbs)
    montage = Image.new("RGB", (columns * cell_width, rows * cell_height), "#d8d8d8")
    for index, image in enumerate(thumbs):
        montage.paste(image, ((index % columns) * cell_width, (index // columns) * cell_height))
        image.close()
    output.parent.mkdir(parents=True, exist_ok=True)
    montage.save(output, quality=92)
    montage.close()


def render(
    pdf_path: Path,
    output_dir: Path,
    expected_pages: int | None,
    scale: float,
    inspection: str,
    notes: str,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    page_sizes = []
    first_size = None
    with pymupdf.open(pdf_path) as document:
        if expected_pages is not None and document.page_count != expected_pages:
            raise ValueError(f"PDF page count mismatch: found {document.page_count}, expected {expected_pages}")
        if document.page_count < 1:
            raise ValueError("PDF has no pages")
        for index, page in enumerate(document, start=1):
            size = [round(page.rect.width, 3), round(page.rect.height, 3)]
            if abs(size[0] / size[1] - 16 / 9) > 0.002:
                raise ValueError(f"PDF page {index} is not 16:9: {size[0]}x{size[1]}")
            if first_size is None:
                first_size = size
            elif size != first_size:
                raise ValueError(f"PDF page size differs at page {index}: {size}, expected {first_size}")
            if page.get_text("text").strip():
                raise ValueError(f"PDF page {index} contains a text layer")
            if len(page.get_images(full=True)) != 1:
                raise ValueError(f"PDF page {index} must contain exactly one complete page image")
            page_sizes.append(size)
            output = output_dir / f"page-{index:03d}.png"
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
            pixmap.save(output)
            rendered.append(output)

    montage = output_dir / "montage.jpg"
    build_montage(rendered, montage)
    report = {
        "schema_version": 1,
        "pdf": str(pdf_path.resolve()),
        "pdf_sha256": file_sha256(pdf_path),
        "page_count": len(rendered),
        "page_sizes": page_sizes,
        "technical_pass": True,
        "rendered_pages": [str(path.resolve()) for path in rendered],
        "montage": str(montage.resolve()),
        "visual_inspection": {"status": inspection, "notes": notes},
    }
    report_path = output_dir / "render-back-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**report, "report": str(report_path.resolve())}


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a PDF to page images and create an auditable review report.")
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--scale", type=float, default=2.0)
    parser.add_argument("--inspection", choices=("pending", "pass", "fail"), default="pending")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    if args.scale <= 0:
        parser.error("--scale must be positive")
    try:
        result = render(
            Path(args.pdf),
            Path(args.out_dir),
            args.expected_pages,
            args.scale,
            args.inspection,
            args.notes,
        )
    except (OSError, ValueError, pymupdf.FileDataError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
