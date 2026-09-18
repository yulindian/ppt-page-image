import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pymupdf
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_delivery.py"


class DeliveryContractTests(unittest.TestCase):
    def make_delivery(self, root: Path, include_images: bool = False) -> None:
        root.mkdir()
        source = root.parent / "page-source.png"
        Image.new("RGB", (1600, 900), "white").save(source)
        document = pymupdf.open()
        page = document.new_page(width=1600, height=900)
        page.insert_image(page.rect, filename=str(source))
        pdf_path = root / "示例课件.pdf"
        document.save(pdf_path)
        document.close()
        (root / "PPT内容大纲.txt").write_text("第01页：封面", encoding="utf-8")
        style_text = "整页图片，图文分区"
        if include_images:
            style_text += "\n素材登记：slide-01.png 用于第01页参考"
        (root / "风格提示词.txt").write_text(style_text, encoding="utf-8")
        (root / "字体说明.txt").write_text("标题：示例字体\n打包文件：example.ttf", encoding="utf-8")
        fonts = root / "fonts"
        fonts.mkdir()
        (fonts / "example.ttf").write_bytes(b"font-data")
        if include_images:
            images = root / "images"
            images.mkdir()
            (images / "slide-01.png").write_bytes(b"image-data")

        report = {
            "schema_version": 1,
            "pdf": str(pdf_path),
            "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
            "page_count": 1,
            "technical_pass": True,
            "visual_inspection": {"status": "pass", "notes": "test inspection"},
        }
        (root.parent / "render-report.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )

    def validate(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--delivery-dir",
                str(root),
                "--deck-name",
                "示例课件",
                "--render-report",
                str(root.parent / "render-report.json"),
                *extra,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_accepts_required_planning_files_fonts_and_optional_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root, include_images=True)
            result = self.validate(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_accepts_delivery_without_optional_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root)
            result = self.validate(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_missing_prompt_outline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root)
            (root / "风格提示词.txt").unlink()
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing", result.stderr.lower())

    def test_rejects_empty_fonts_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root)
            (root / "fonts" / "example.ttf").unlink()
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("font", result.stderr.lower())

    def test_rejects_expected_page_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root)
            result = self.validate(root, "--expected-pages", "2")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("page count", result.stderr.lower())

    def test_rejects_process_artifacts_in_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root)
            (root / ".work").mkdir()
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unexpected", result.stderr.lower())

    def test_rejects_old_version_files_in_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root)
            (root / "示例课件_v2.pdf").write_bytes(b"old")
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("old or process", result.stderr.lower())

    def test_rejects_unregistered_font_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root)
            (root / "字体说明.txt").write_text("标题：示例字体", encoding="utf-8")
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not registered", result.stderr.lower())

    def test_rejects_unregistered_image_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "delivery"
            self.make_delivery(root, include_images=True)
            (root / "风格提示词.txt").write_text("整页图片，图文分区", encoding="utf-8")
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not registered", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
