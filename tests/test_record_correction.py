import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORDER = ROOT / "scripts" / "record_correction.py"


def run_record(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RECORDER), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def add_rule(store: Path, rule: str, supersedes: str | None = None) -> subprocess.CompletedProcess[str]:
    args = [
        "add",
        "--store",
        str(store),
        "--scope",
        "global",
        "--source",
        rule,
        "--rule",
        rule,
        "--applies-to",
        "body pages",
    ]
    if supersedes:
        args.extend(["--supersedes", supersedes])
    return run_record(*args)


class RecordCorrectionTests(unittest.TestCase):
    def test_uses_user_state_store_when_store_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["CODEX_HOME"] = str(Path(tmp) / "codex")
            result = run_record(
                "add",
                "--scope",
                "global",
                "--source",
                "用户要求",
                "--rule",
                "正文使用浅色阅读区",
                "--applies-to",
                "body pages",
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            store = Path(env["CODEX_HOME"]) / "state" / "ppt-page-image" / "learned-rules.json"
            self.assertTrue(store.is_file())
            saved = json.loads(store.read_text(encoding="utf-8"))
            self.assertEqual(saved["rules"][0]["rule"], "正文使用浅色阅读区")

    def test_list_active_omits_promoted_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "rules.json"
            store.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "rules": [
                            {"id": "correction-0001", "status": "active"},
                            {"id": "correction-0002", "status": "promoted"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = run_record("list-active", "--store", str(store))
            self.assertEqual(result.returncode, 0, result.stderr)
            active = json.loads(result.stdout)
            self.assertEqual([rule["id"] for rule in active["rules"]], ["correction-0001"])

    def test_list_active_omits_superseded_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "rules.json"
            self.assertEqual(add_rule(store, "正文使用浅色阅读区").returncode, 0)
            self.assertEqual(add_rule(store, "正文使用独立阅读区", supersedes="correction-0001").returncode, 0)
            result = run_record("list-active", "--store", str(store))
            self.assertEqual(result.returncode, 0, result.stderr)
            active = json.loads(result.stdout)
            self.assertEqual([rule["id"] for rule in active["rules"]], ["correction-0002"])

    def test_rejects_duplicate_active_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "rules.json"
            self.assertEqual(add_rule(store, "正文使用浅色阅读区").returncode, 0)
            result = add_rule(store, "正文使用浅色阅读区")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
