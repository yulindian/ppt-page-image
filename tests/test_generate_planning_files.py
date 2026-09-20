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


class PlanningDocumentTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "minimal-v2-state.json"
        self.state = json.loads(fixture.read_text(encoding="utf-8"))

    def test_render_documents_returns_exact_required_names(self) -> None:
        rendered = planning_documents.render_documents(self.state)
        self.assertEqual(
            set(rendered),
            {"PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt"},
        )

    def test_render_documents_contains_locked_copy_prompt_and_font_mapping(self) -> None:
        rendered = planning_documents.render_documents(self.state)
        self.assertIn("让班级升温", rendered["PPT内容大纲.txt"])
        self.assertIn(self.state["pages"][0]["prompt"], rendered["风格提示词.txt"])
        self.assertIn("F01", rendered["字体说明.txt"])
        self.assertIn("NotoSansSC-Regular.otf", rendered["字体说明.txt"])

    def test_write_documents_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            first = planning_documents.write_documents(self.state, output)
            first_bytes = {name: path.read_bytes() for name, path in first.items()}
            second = planning_documents.write_documents(self.state, output)
            self.assertEqual(first_bytes, {name: path.read_bytes() for name, path in second.items()})

    def test_renders_structured_enrichment_without_crashing(self) -> None:
        self.state["enrichment"] = [
            {
                "type": "authentic_photo",
                "status": "accepted",
                "source": "https://example.edu/photo",
                "verified_date": "2026-09-20",
                "rights_status": "official",
                "teaching_purpose": "呈现真实课堂协作",
                "target_pages": [1],
                "fidelity_constraints": ["不得改变人物关系"],
            }
        ]
        rendered = planning_documents.render_documents(self.state)
        self.assertIn("https://example.edu/photo", rendered["风格提示词.txt"])
        self.assertIn("不得改变人物关系", rendered["风格提示词.txt"])


if __name__ == "__main__":
    unittest.main()
