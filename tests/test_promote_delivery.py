import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import images_to_pdf
import planning_documents
import promote_delivery
import render_pdf


class PromoteDeliveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        fixture = ROOT / "tests" / "fixtures" / "minimal-v2-state.json"
        self.state = json.loads(fixture.read_text(encoding="utf-8"))
        self.state["status"] = "DELIVERY_READY"
        fonts = self.workspace / "fonts"
        fonts.mkdir()
        (fonts / "NotoSansSC-Regular.otf").write_bytes(b"font")

        slides = self.workspace / "slides"
        slides.mkdir()
        self.slide = slides / "slide-1.png"
        Image.new("RGB", (1600, 900), "#f5ead7").save(self.slide)
        page = self.state["pages"][0]
        page["qa_status"] = "PASS"
        page["current_image"] = "slides/slide-1.png"
        page["image_sha256"] = hashlib.sha256(self.slide.read_bytes()).hexdigest()
        self.state["reviews"] = {
            "pilot": {"status": "pass", "pages": [1], "reviewed_pages": [1]},
            "families": {},
            "deck": {"status": "pass"},
            "render": {"status": "pass"},
        }
        self.state_path = self.workspace / "project-state.json"
        self.save_state()

        reports = self.workspace / "reports"
        reports.mkdir()
        self.pdf = reports / "课件.candidate.pdf"
        images_to_pdf.package([self.slide], self.pdf, 95, 1, "lossless")
        rendered = render_pdf.render(
            self.pdf,
            self.workspace / "render-back",
            1,
            1.0,
            "pass",
            "inspected",
        )
        self.render_report = Path(rendered["report"])
        self.delivery = self.root / "课件"

    def save_state(self) -> None:
        self.state_path.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        planning_documents.write_documents(self.state, self.workspace / "planning")

    def promote(self) -> dict:
        return promote_delivery.promote(
            self.state_path,
            self.workspace,
            self.pdf,
            self.delivery,
            self.render_report,
        )

    def test_promotes_only_managed_final_artifacts(self) -> None:
        process_names = {
            "candidates": "slide-1.new.png",
            "history": "slide-1.old.png",
            "montages": "cover.jpg",
            "ocr": "slide-1.txt",
        }
        for dirname, filename in process_names.items():
            folder = self.workspace / dirname
            folder.mkdir(exist_ok=True)
            (folder / filename).write_bytes(b"process")

        result = self.promote()

        self.assertEqual(
            {path.name for path in self.delivery.iterdir()},
            {"课件.pdf", "PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt", "fonts"},
        )
        delivered_names = {path.name for path in self.delivery.rglob("*")}
        for filename in process_names.values():
            self.assertNotIn(filename, delivered_names)
        self.assertEqual(result["delivery"], str(self.delivery))

    def test_rejects_target_with_unmanaged_docx_without_changing_it(self) -> None:
        self.delivery.mkdir()
        unrelated = self.delivery / "用户教案.docx"
        unrelated.write_bytes(b"user-owned")

        with self.assertRaisesRegex(ValueError, "unmanaged"):
            self.promote()

        self.assertEqual(unrelated.read_bytes(), b"user-owned")
        self.assertEqual({path.name for path in self.delivery.iterdir()}, {"用户教案.docx"})

    def test_rejects_delivery_directory_inside_workspace(self) -> None:
        delivery_inside_workspace = self.workspace / "final"
        with self.assertRaisesRegex(ValueError, "separate"):
            promote_delivery.promote(
                self.state_path,
                self.workspace,
                self.pdf,
                delivery_inside_workspace,
                self.render_report,
            )
        self.assertFalse(delivery_inside_workspace.exists())

    def test_moves_previous_managed_delivery_to_workspace_history(self) -> None:
        self.promote()
        previous_pdf = (self.delivery / "课件.pdf").read_bytes()

        self.promote()

        history = self.workspace / "history"
        saved = list(history.glob("delivery-*"))
        self.assertEqual(len(saved), 1)
        self.assertEqual((saved[0] / "课件.pdf").read_bytes(), previous_pdf)

    def test_restores_previous_delivery_when_final_rename_fails(self) -> None:
        self.promote()
        previous_pdf = (self.delivery / "课件.pdf").read_bytes()
        real_move = promote_delivery._move_path
        call_count = 0

        def fail_final_move(source: Path, target: Path) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise OSError("simulated final rename failure")
            real_move(source, target)

        with patch.object(promote_delivery, "_move_path", side_effect=fail_final_move):
            with self.assertRaisesRegex(OSError, "simulated final rename failure"):
                self.promote()

        self.assertEqual((self.delivery / "课件.pdf").read_bytes(), previous_pdf)


if __name__ == "__main__":
    unittest.main()
