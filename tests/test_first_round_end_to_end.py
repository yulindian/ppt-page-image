import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import images_to_pdf
import planning_documents
import promote_delivery
import render_pdf
import validate_project


class FirstRoundEndToEndTests(unittest.TestCase):
    def test_state_to_clean_recoverable_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / ".ppt-page-image-work" / "class-warmth"
            workspace.mkdir(parents=True)
            fixture = ROOT / "tests" / "fixtures" / "minimal-v2-state.json"
            state = json.loads(fixture.read_text(encoding="utf-8"))
            state["status"] = "DELIVERY_READY"

            fonts = workspace / "fonts"
            fonts.mkdir()
            (fonts / "NotoSansSC-Regular.otf").write_bytes(b"font")
            slides = workspace / "slides"
            slides.mkdir()
            slide = slides / "slide-1.png"
            Image.new("RGB", (1600, 900), "#f0e2ca").save(slide)
            page = state["pages"][0]
            page["qa_status"] = "PASS"
            page["current_image"] = "slides/slide-1.png"
            page["image_sha256"] = hashlib.sha256(slide.read_bytes()).hexdigest()
            state["reviews"] = {
                "pilot": {"status": "pass", "pages": [1], "reviewed_pages": [1]},
                "families": {},
                "deck": {"status": "pass"},
                "render": {"status": "pass"},
            }
            state_path = workspace / "project-state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
            planning_documents.write_documents(state, workspace / "planning")
            self.assertEqual(validate_project.validate_v2(state_path, workspace, "planning")["gate"], "planning")

            for dirname in ("candidates", "montages", "ocr"):
                process = workspace / dirname
                process.mkdir()
                (process / "过程文件.txt").write_text("process", encoding="utf-8")
            reports = workspace / "reports"
            reports.mkdir()
            pdf = reports / "课件.candidate.pdf"
            images_to_pdf.package([slide], pdf, 95, 1, "lossless")
            rendered = render_pdf.render(pdf, workspace / "render-back", 1, 1.0, "pass", "inspected")

            delivery = root / "课件"
            promote_delivery.promote(state_path, workspace, pdf, delivery, Path(rendered["report"]))
            promote_delivery.promote(state_path, workspace, pdf, delivery, Path(rendered["report"]))

            self.assertEqual(
                {path.name for path in delivery.iterdir()},
                {"课件.pdf", "PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt", "fonts"},
            )
            self.assertFalse(any(path.name == "project-state.json" for path in delivery.rglob("*")))
            self.assertFalse(any(path.name.startswith("slide-") for path in delivery.rglob("*")))
            self.assertEqual(len(list((workspace / "history").glob("delivery-*"))), 1)


if __name__ == "__main__":
    unittest.main()
