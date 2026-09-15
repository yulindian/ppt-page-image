import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AntiAiContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_style_prompt_contract_prevents_generic_ai_aesthetics(self) -> None:
        text = self.read("references/style-and-prompts.md")
        self.assertIn("Anti-AI-Aesthetic Prompting", text)
        self.assertIn("design rationale", text)
        self.assertIn("generic AI aesthetics", text)
        self.assertIn("element budget", text)
        self.assertIn("content evidence", text)

    def test_planning_package_records_page_specific_design_reasoning(self) -> None:
        text = self.read("references/planning-package.md")
        self.assertIn("design rationale", text)
        self.assertIn("content evidence", text)
        self.assertIn("element budget", text)
        self.assertIn("generic AI traits", text)

    def test_production_has_pre_generation_anti_ai_gate(self) -> None:
        text = self.read("references/full-page-production.md")
        self.assertIn("Pre-Generation Anti-AI Gate", text)
        self.assertIn("template-like copy", text)
        self.assertIn("unnecessary decoration", text)
        self.assertIn("plausible subject details", text)

    def test_main_workflow_applies_anti_ai_controls_before_generation(self) -> None:
        text = self.read("SKILL.md")
        self.assertIn("anti-AI-aesthetic", text)
        self.assertIn("before generation", text)


if __name__ == "__main__":
    unittest.main()
