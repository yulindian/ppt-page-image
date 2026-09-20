import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import pymupdf
from PIL import Image


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_delivery = load_module("validate_delivery", "validate_delivery.py")
images_to_pdf = load_module("images_to_pdf", "images_to_pdf.py")
render_pdf = load_module("render_pdf", "render_pdf.py")


def make_image_pdf(path: Path, size=(1600, 900)) -> None:
    image_path = path.with_suffix(".png")
    Image.new("RGB", size, "white").save(image_path)
    document = pymupdf.open()
    page = document.new_page(width=size[0], height=size[1])
    page.insert_image(page.rect, filename=str(image_path))
    document.save(path)
    document.close()
    image_path.unlink()


def make_delivery(root: Path, deck_name="Demo") -> Path:
    delivery = root / deck_name
    delivery.mkdir()
    make_image_pdf(delivery / f"{deck_name}.pdf")
    (delivery / "PPT内容大纲.txt").write_text("第1页：封面\n", encoding="utf-8")
    (delivery / "风格提示词.txt").write_text("全局提示词\n", encoding="utf-8")
    (delivery / "字体说明.txt").write_text("DemoFont.ttf\n", encoding="utf-8")
    fonts = delivery / "fonts"
    fonts.mkdir()
    (fonts / "DemoFont.ttf").write_bytes(b"font-placeholder")
    return delivery


def make_render_report(pdf_path: Path, report_path: Path, status="pass") -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "pdf": str(pdf_path),
                "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
                "page_count": 1,
                "technical_pass": True,
                "visual_inspection": {"status": status, "notes": "inspected"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


class DeliveryValidationTests(unittest.TestCase):
    def test_accepts_image_only_16_9_pdf_with_matching_review_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            delivery = make_delivery(root)
            report = root / ".work" / "render-back-report.json"
            make_render_report(delivery / "Demo.pdf", report)

            result = validate_delivery.validate(delivery, "Demo", 1, report)

            self.assertEqual(result["pages"], 1)
            self.assertTrue(result["render_back_verified"])

    def test_rejects_pdf_with_non_16_9_page(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            delivery = make_delivery(root)
            make_image_pdf(delivery / "Demo.pdf", size=(1000, 1000))
            report = root / ".work" / "render-back-report.json"
            make_render_report(delivery / "Demo.pdf", report)

            with self.assertRaisesRegex(ValueError, "16:9"):
                validate_delivery.validate(delivery, "Demo", 1, report)

    def test_rejects_pending_visual_inspection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            delivery = make_delivery(root)
            report = root / ".work" / "render-back-report.json"
            make_render_report(delivery / "Demo.pdf", report, status="pending")

            with self.assertRaisesRegex(ValueError, "visual inspection"):
                validate_delivery.validate(delivery, "Demo", 1, report)

    def test_rejects_report_for_a_different_pdf(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            delivery = make_delivery(root)
            report = root / ".work" / "render-back-report.json"
            make_render_report(delivery / "Demo.pdf", report)
            with (delivery / "Demo.pdf").open("ab") as handle:
                handle.write(b"changed")

            with self.assertRaisesRegex(ValueError, "does not match"):
                validate_delivery.validate(delivery, "Demo", 1, report)

    def test_rejects_pdf_text_layer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            delivery = make_delivery(root)
            pdf_path = delivery / "Demo.pdf"
            with pymupdf.open(pdf_path) as document:
                page = document[0]
                page.insert_text((50, 50), "native text")
                updated = root / "updated.pdf"
                document.save(updated)
            pdf_path.write_bytes(updated.read_bytes())
            report = root / ".work" / "render-back-report.json"
            make_render_report(pdf_path, report)

            with self.assertRaisesRegex(ValueError, "text layer"):
                validate_delivery.validate(delivery, "Demo", 1, report)


class PdfPackagingTests(unittest.TestCase):
    def test_lossless_mode_preserves_png_encoding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            slides = root / "slides"
            slides.mkdir()
            source = slides / "slide-1.png"
            Image.new("RGB", (1600, 900), "#335577").save(source)
            output = root / "deck.pdf"

            images_to_pdf.package([source], output, 95, 1, "lossless")

            with pymupdf.open(output) as document:
                images = document[0].get_images(full=True)
                self.assertEqual(len(images), 1)
                extracted = document.extract_image(images[0][0])
                self.assertEqual(extracted["ext"], "png")

    def test_render_pdf_creates_pages_montage_and_hash_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pdf_path = root / "Demo.pdf"
            make_image_pdf(pdf_path)

            result = render_pdf.render(pdf_path, root / "rendered", 1, 1.0, "pass", "checked")

            self.assertTrue((root / "rendered" / "page-001.png").is_file())
            self.assertTrue((root / "rendered" / "montage.jpg").is_file())
            self.assertEqual(result["pdf_sha256"], hashlib.sha256(pdf_path.read_bytes()).hexdigest())
            self.assertEqual(result["visual_inspection"]["status"], "pass")

    def test_end_to_end_package_render_and_delivery_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            delivery = make_delivery(root)
            slides = root / "slides"
            slides.mkdir()
            source = slides / "slide-1.png"
            Image.new("RGB", (1600, 900), "#f4eee2").save(source)
            pdf_path = delivery / "Demo.pdf"

            images_to_pdf.package([source], pdf_path, 95, 1, "lossless")
            rendered = render_pdf.render(
                pdf_path,
                root / ".work" / "render-back-final",
                1,
                1.0,
                "pass",
                "inspected",
            )
            result = validate_delivery.validate(delivery, "Demo", 1, Path(rendered["report"]))

            self.assertTrue(result["render_back_verified"])


class ProjectStateValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validate_project = load_module("validate_project", "validate_project.py")

    def write_project(self, root: Path, font_roles=None):
        for name in ("PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt"):
            (root / name).write_text("已规划\n", encoding="utf-8")
        fonts_dir = root / "fonts"
        fonts_dir.mkdir()
        state = {
            "schema_version": 1,
            "deck": {"name": "Demo", "expected_pages": 2},
            "status": "PLANNING_READY",
            "families": {
                "cover": {"mother_page": 1, "pages": [1], "invariants": ["主题优先"]},
                "body": {"mother_page": 2, "pages": [2], "invariants": ["标题系统"]},
            },
            "pages": [
                {
                    "index": 1,
                    "title": "封面",
                    "visible_copy": ["课程标题"],
                    "family": "cover",
                    "font_roles": ["F01"],
                    "prompt": "整页生成：课程标题",
                    "qa_status": "PENDING",
                },
                {
                    "index": 2,
                    "title": "正文",
                    "visible_copy": ["正文内容"],
                    "family": "body",
                    "font_roles": ["F02"],
                    "prompt": "整页生成：正文内容",
                    "qa_status": "PENDING",
                },
            ],
            "fonts": font_roles or [
                {"role": "F01", "packaged_filename": "Title.ttf"},
                {"role": "F02", "packaged_filename": "Body.ttf"},
            ],
        }
        state_path = root / ".work" / "project-state.json"
        state_path.parent.mkdir()
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        for font in state["fonts"]:
            (fonts_dir / font["packaged_filename"]).write_bytes(b"font-placeholder")
        return state_path

    def test_accepts_consistent_project_state(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_path = self.write_project(root)
            result = self.validate_project.validate(state_path, root)
            self.assertEqual(result["pages"], 2)
            self.assertEqual(result["font_roles"], 2)

    def test_rejects_more_than_seven_font_roles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            roles = [
                {"role": f"F{i:02d}", "packaged_filename": f"Font{i}.ttf"}
                for i in range(1, 9)
            ]
            state_path = self.write_project(root, roles)
            with self.assertRaisesRegex(ValueError, "7 font roles"):
                self.validate_project.validate(state_path, root)

    def test_rejects_missing_packaged_font_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_path = self.write_project(root)
            (root / "fonts" / "Body.ttf").unlink()

            with self.assertRaisesRegex(ValueError, "Packaged font file is missing"):
                self.validate_project.validate(state_path, root)

    def test_rejects_missing_planning_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_path = self.write_project(root)
            (root / "风格提示词.txt").unlink()

            with self.assertRaisesRegex(ValueError, "Required planning file is missing or empty"):
                self.validate_project.validate(state_path, root)

    def test_rejects_accepted_enrichment_without_source_and_rights(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_path = self.write_project(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["enrichment"] = [
                {
                    "type": "authentic_photo",
                    "status": "accepted",
                    "teaching_purpose": "show the real setting",
                    "target_pages": [2],
                }
            ]
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "source.*rights_status"):
                self.validate_project.validate(state_path, root)

    def test_rejects_repeated_family_without_component_specifications(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_path = self.write_project(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["families"] = {
                "body": {
                    "mother_page": 1,
                    "pages": [1, 2],
                    "invariants": ["统一标题系统"],
                }
            }
            for page in state["pages"]:
                page["family"] = "body"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "component_specifications"):
                self.validate_project.validate(state_path, root)

    def test_accepts_repeated_family_with_verifiable_component_specifications(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_path = self.write_project(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["families"] = {
                "body": {
                    "mother_page": 1,
                    "pages": [1, 2],
                    "invariants": ["统一标题系统"],
                    "component_specifications": [
                        {
                            "name": "section_title",
                            "applies_to": [1, 2],
                            "fixed": [
                                "top-left position",
                                "navy title color",
                                "same baseline and spacing",
                            ],
                            "variable": ["section number", "title copy"],
                            "forbidden": ["gradient", "shadow", "separate number badge"],
                        }
                    ],
                }
            }
            for page in state["pages"]:
                page["family"] = "body"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

            result = self.validate_project.validate(state_path, root)
            self.assertEqual(result["families"], 1)


if __name__ == "__main__":
    unittest.main()
