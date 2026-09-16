import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PACKAGER = ROOT / "scripts" / "images_to_pdf.py"


def make_image(path: Path, color: tuple[int, int, int] = (200, 220, 240)) -> None:
    image = Image.new("RGB", (1600, 900), color)
    image.save(path)


class ImagesToPdfTests(unittest.TestCase):
    def run_packager(self, slides: Path, out: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PACKAGER),
                "--slides-dir",
                str(slides),
                "--out",
                str(out),
                *extra,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_rejects_numbering_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides = root / "slides"
            slides.mkdir()
            make_image(slides / "slide-01.png")
            make_image(slides / "slide-03.png", color=(120, 130, 140))
            result = self.run_packager(slides, root / ".work" / "candidate.pdf", "--expected-pages", "3")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing", result.stderr.lower())

    def test_rejects_expected_page_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides = root / "slides"
            slides.mkdir()
            make_image(slides / "slide-01.png")
            result = self.run_packager(slides, root / ".work" / "candidate.pdf", "--expected-pages", "2")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("page count", result.stderr.lower())

    def test_rejects_duplicate_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides = root / "slides"
            slides.mkdir()
            make_image(slides / "slide-01.png", color=(255, 0, 0))
            make_image(slides / "slide-02.png", color=(255, 0, 0))
            result = self.run_packager(slides, root / ".work" / "candidate.pdf", "--expected-pages", "2")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate", result.stderr.lower())

    def test_accepts_lossless_mode_for_valid_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slides = root / "slides"
            slides.mkdir()
            make_image(slides / "slide-01.png", color=(255, 0, 0))
            make_image(slides / "slide-02.png", color=(0, 255, 0))
            out = root / ".work" / "candidate.pdf"
            result = self.run_packager(slides, out, "--expected-pages", "2", "--mode", "lossless")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
