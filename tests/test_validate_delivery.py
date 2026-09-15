import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_delivery.py"


class DeliveryContractTests(unittest.TestCase):
    def make_delivery(self, root: Path, include_images: bool = False) -> None:
        document = fitz.open()
        document.new_page(width=1600, height=900)
        document.save(root / "示例课件.pdf")
        (root / "PPT内容大纲.txt").write_text("第01页：封面", encoding="utf-8")
        (root / "风格提示词.txt").write_text("整页图片，图文分区", encoding="utf-8")
        (root / "字体说明.txt").write_text("标题：示例字体", encoding="utf-8")
        fonts = root / "fonts"
        fonts.mkdir()
        (fonts / "example.ttf").write_bytes(b"font-data")
        if include_images:
            images = root / "images"
            images.mkdir()
            (images / "slide-01.png").write_bytes(b"image-data")

    def validate(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--delivery-dir",
                str(root),
                "--deck-name",
                "示例课件",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_accepts_required_planning_files_fonts_and_optional_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_delivery(root, include_images=True)
            result = self.validate(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_accepts_delivery_without_optional_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_delivery(root)
            result = self.validate(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_missing_prompt_outline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_delivery(root)
            (root / "风格提示词.txt").unlink()
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing", result.stderr.lower())

    def test_rejects_empty_fonts_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_delivery(root)
            (root / "fonts" / "example.ttf").unlink()
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("font", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
