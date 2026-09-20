import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import planning_documents


SPEC = importlib.util.spec_from_file_location("validate_project_v2_module", SCRIPTS / "validate_project.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ProjectStateV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name) / "workspace"
        self.workspace.mkdir()
        fixture = ROOT / "tests" / "fixtures" / "minimal-v2-state.json"
        self.state = json.loads(fixture.read_text(encoding="utf-8"))
        fonts = self.workspace / "fonts"
        fonts.mkdir()
        (fonts / "NotoSansSC-Regular.otf").write_bytes(b"font")
        self.state_path = self.workspace / "project-state.json"
        self.save_state()

    def save_state(self, generate_planning: bool = True) -> None:
        self.state_path.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if generate_planning:
            planning_documents.write_documents(self.state, self.workspace / "planning")

    def test_accepts_complete_planning_gate(self) -> None:
        result = MODULE.validate_v2(self.state_path, self.workspace, "planning")
        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(result["gate"], "planning")
        self.assertFalse(result["legacy"])

    def test_rejects_manual_planning_file_drift(self) -> None:
        outline = self.workspace / "planning" / "PPT内容大纲.txt"
        outline.write_text(outline.read_text(encoding="utf-8") + "人工改动\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Planning file drift"):
            MODULE.validate_v2(self.state_path, self.workspace, "planning")

    def test_rejects_empty_locked_copy_item(self) -> None:
        self.state["pages"][0]["visible_copy"].append("")
        self.save_state()
        with self.assertRaisesRegex(ValueError, "empty locked copy"):
            MODULE.validate_v2(self.state_path, self.workspace, "planning")

    def test_rejects_page_without_font_roles(self) -> None:
        self.state["pages"][0]["font_roles"] = []
        self.save_state()
        with self.assertRaisesRegex(ValueError, "at least one font role"):
            MODULE.validate_v2(self.state_path, self.workspace, "planning")

    def test_rejects_locked_copy_missing_from_prompt(self) -> None:
        self.state["pages"][0]["prompt"] = self.state["pages"][0]["prompt"].replace("让班级升温", "班会主题")
        self.save_state()
        with self.assertRaisesRegex(ValueError, "missing locked copy"):
            MODULE.validate_v2(self.state_path, self.workspace, "planning")

    def test_rejects_font_role_missing_from_prompt(self) -> None:
        self.state["pages"][0]["prompt"] = self.state["pages"][0]["prompt"].replace("F01", "标题字体")
        self.save_state()
        with self.assertRaisesRegex(ValueError, "missing font role"):
            MODULE.validate_v2(self.state_path, self.workspace, "planning")

    def test_planning_gate_requires_planning_ready_status(self) -> None:
        self.state["status"] = "INTAKE"
        self.save_state()
        with self.assertRaisesRegex(ValueError, "planning gate requires status"):
            MODULE.validate_v2(self.state_path, self.workspace, "planning")

    def test_pilot_gate_requires_passed_review_evidence(self) -> None:
        self.state["status"] = "PILOT_APPROVED"
        self.save_state()
        with self.assertRaisesRegex(ValueError, "pilot review evidence"):
            MODULE.validate_v2(self.state_path, self.workspace, "pilot")

    def test_production_gate_requires_current_image_for_every_page(self) -> None:
        self.state["status"] = "FULL_PRODUCTION"
        self.state["pages"][0]["qa_status"] = "PASS"
        self.state["reviews"]["pilot"] = {"status": "pass", "pages": [1], "reviewed_pages": [1]}
        self.save_state()
        with self.assertRaisesRegex(ValueError, "current_image"):
            MODULE.validate_v2(self.state_path, self.workspace, "production")

    def test_delivery_gate_requires_deck_and_render_reviews(self) -> None:
        image = self.workspace / "slides" / "slide-1.png"
        image.parent.mkdir()
        image.write_bytes(b"approved page")
        self.state["status"] = "DELIVERY_READY"
        page = self.state["pages"][0]
        page["qa_status"] = "PASS"
        page["current_image"] = "slides/slide-1.png"
        page["image_sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
        self.state["reviews"]["pilot"] = {"status": "pass", "pages": [1], "reviewed_pages": [1]}
        self.save_state()
        with self.assertRaisesRegex(ValueError, "whole-deck review"):
            MODULE.validate_v2(self.state_path, self.workspace, "delivery")

    def test_schema_v1_result_is_explicitly_legacy(self) -> None:
        project = Path(self.temporary.name) / "legacy"
        project.mkdir()
        for filename in ("PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt"):
            (project / filename).write_text("内容", encoding="utf-8")
        (project / "fonts").mkdir()
        (project / "fonts" / "Body.ttf").write_bytes(b"font")
        legacy = {
            "schema_version": 1,
            "deck": {"name": "旧课件", "expected_pages": 1},
            "status": "PLANNING_READY",
            "families": {"cover": {"mother_page": 1, "pages": [1], "invariants": ["主题突出"]}},
            "fonts": [{"role": "F01", "packaged_filename": "Body.ttf"}],
            "pages": [{
                "index": 1,
                "title": "封面",
                "visible_copy": ["旧课件"],
                "family": "cover",
                "font_roles": ["F01"],
                "prompt": "旧课件 F01",
                "qa_status": "PENDING",
            }],
        }
        state_path = project / "project-state.json"
        state_path.write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")
        result = MODULE.validate(state_path, project)
        self.assertTrue(result["legacy"])
        self.assertEqual(result["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
