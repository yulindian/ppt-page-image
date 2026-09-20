# PPT Page Image First-Round Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate process artifacts from final delivery, generate the three planning documents from schema-v2 project state, enforce real production gates, and move mutable learned rules out of the Skill repository.

**Architecture:** A schema-v2 `project-state.json` in an external workspace is the only editable planning source. A deterministic renderer produces the three Chinese planning files, validators compare generated output and enforce gate evidence, and a promotion command builds a clean staged delivery before swapping it into place while preserving the previous managed delivery in workspace history.

**Tech Stack:** Python 3.11+, standard library, Pillow, PyMuPDF, `unittest`, UTF-8 text files.

**Spec:** `docs/superpowers/specs/2026-09-20-first-round-hardening-design.md`

## Global Constraints

- The final directory contains only the final PDF, three generated planning files, packaged fonts, and optional approved `images/` assets.
- Candidate pages, changed pages, prior pages, montages, OCR, render-back files, state files, and reports remain outside the final directory.
- `project-state.json` is the only editable planning authority for schema v2.
- Existing schema-v1 projects remain readable and report `legacy: true`; they cannot claim schema-v2 gate coverage.
- The promotion command never destroys unmanaged user files and preserves a previous managed delivery under workspace history.
- Every Python command documented for Windows uses `python -X utf8`.
- Production changes follow red-green-refactor; no production implementation is written before its failing test is observed.

## Review Focus

- A delivery target containing an unrelated DOCX must be rejected without moving or deleting that DOCX; Task 4 adds this test.
- A prior delivery must remain recoverable if the final directory swap fails; Task 4 adds rollback and history tests.
- A planning document with a one-character manual edit must fail validation; Task 2 adds an exact-content drift test.
- A page prompt containing locked copy but omitting its declared font role must fail the planning gate; Task 3 adds this test.
- A schema-v1 project must remain inspectable without being reported as schema-v2 compliant; Task 3 adds a legacy result test.

---

### Task 1: Move mutable correction rules to user state and promote core rules

**Files:**
- Modify: `scripts/record_correction.py`
- Modify: `references/learned-rules.json`
- Modify: `references/learning-and-corrections.md`
- Modify: `SKILL.md`
- Test: `tests/test_record_correction.py`

**Interfaces:**
- Produces: `default_store() -> pathlib.Path`
- Produces: `active_rules(data: dict) -> list[dict]`, returning only rules with status `active`
- Produces: CLI `--store` as optional; omitted value resolves to the user state store
- Consumes: `CODEX_HOME` when defined, otherwise `%USERPROFILE%/.codex`

- [ ] **Step 1: Write failing tests for the default store and promoted status**

Add tests equivalent to:

```python
def test_default_store_uses_codex_user_state(self):
    with patch.dict(os.environ, {"CODEX_HOME": str(self.root / "codex")}, clear=False):
        self.assertEqual(
            MODULE.default_store(),
            self.root / "codex" / "state" / "ppt-page-image" / "learned-rules.json",
        )

def test_list_active_omits_promoted_rules(self):
    self.store.write_text(json.dumps({
        "schema_version": 1,
        "rules": [
            {"id": "correction-0001", "status": "active"},
            {"id": "correction-0002", "status": "promoted"},
        ],
    }), encoding="utf-8")
    result = MODULE.list_active(argparse.Namespace(store=str(self.store)))
    self.assertEqual([item["id"] for item in result["rules"]], ["correction-0001"])
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -X utf8 -m unittest tests.test_record_correction -v
```

Expected: failure because `default_store` does not exist and `--store` is still required.

- [ ] **Step 3: Implement the user-state default and promoted status**

Implement:

```python
def default_store() -> Path:
    base = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
    return base / "state" / "ppt-page-image" / "learned-rules.json"
```

Make both subcommands use `default=str(default_store())`. Preserve `active_rules` as the single filter so `promoted` and `superseded` remain history but do not enter prompts.

- [ ] **Step 4: Promote existing core rules without deleting history**

Change active rules already represented in `SKILL.md` or references to `status: "promoted"` and add a `promoted_to` field naming the relevant document section. Keep superseded entries unchanged. The repository history file must contain zero active rules after this migration.

- [ ] **Step 5: Update correction documentation and Skill startup command**

Document the user-state default and replace the startup command with:

```powershell
python -X utf8 scripts/record_correction.py list-active
```

- [ ] **Step 6: Run focused and full tests**

Run:

```powershell
python -X utf8 -m unittest tests.test_record_correction -v
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```powershell
git add scripts/record_correction.py references/learned-rules.json references/learning-and-corrections.md SKILL.md tests/test_record_correction.py
git commit -m "feat: move ppt correction rules to user state"
```

### Task 2: Generate the three planning documents deterministically from schema v2

**Files:**
- Create: `scripts/planning_documents.py`
- Create: `scripts/generate_planning_files.py`
- Create: `tests/test_generate_planning_files.py`
- Create: `tests/fixtures/minimal-v2-state.json`

**Interfaces:**
- Produces: `render_documents(state: dict) -> dict[str, str]`
- Produces: `write_documents(state: dict, output_dir: Path) -> dict[str, Path]`
- Produces: CLI `generate_planning_files.py --state PATH --out-dir DIR`

- [ ] **Step 1: Add a complete minimal schema-v2 fixture**

The fixture contains one page and includes `deck`, `status`, `style`, one font role, one single-page family, one page with locked copy and full prompt, empty enrichment, review objects, and delivery name. Use the visible copy `让班级升温` and font role `F01` so assertions are deterministic.

- [ ] **Step 2: Write failing renderer tests**

Add:

```python
def test_render_documents_returns_exact_required_names(self):
    rendered = planning_documents.render_documents(self.state)
    self.assertEqual(
        set(rendered),
        {"PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt"},
    )

def test_render_documents_contains_locked_copy_prompt_and_font_mapping(self):
    rendered = planning_documents.render_documents(self.state)
    self.assertIn("让班级升温", rendered["PPT内容大纲.txt"])
    self.assertIn(self.state["pages"][0]["prompt"], rendered["风格提示词.txt"])
    self.assertIn("F01", rendered["字体说明.txt"])
    self.assertIn("NotoSansSC-Regular.otf", rendered["字体说明.txt"])

def test_write_documents_is_deterministic(self):
    first = planning_documents.write_documents(self.state, self.output)
    first_bytes = {name: path.read_bytes() for name, path in first.items()}
    second = planning_documents.write_documents(self.state, self.output)
    self.assertEqual(first_bytes, {name: path.read_bytes() for name, path in second.items()})
```

- [ ] **Step 3: Run the renderer tests and verify RED**

Run:

```powershell
python -X utf8 -m unittest tests.test_generate_planning_files -v
```

Expected: import failure because `planning_documents.py` does not exist.

- [ ] **Step 4: Implement deterministic rendering**

Implement pure rendering helpers that use fixed heading order, page order, family order from insertion order, UTF-8, `\n` newlines, and a final newline. Reject missing required sections with `ValueError`; do not invent content during rendering.

The CLI loads JSON using UTF-8, calls `write_documents`, and returns JSON listing output files and SHA-256 values.

- [ ] **Step 5: Run focused and full tests**

Run:

```powershell
python -X utf8 -m unittest tests.test_generate_planning_files -v
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```powershell
git add scripts/planning_documents.py scripts/generate_planning_files.py tests/test_generate_planning_files.py tests/fixtures/minimal-v2-state.json
git commit -m "feat: generate planning package from project state"
```

### Task 3: Enforce schema-v2 planning, pilot, production, and delivery gates

**Files:**
- Modify: `scripts/validate_project.py`
- Create: `tests/test_validate_project_v2.py`
- Modify: `references/project-state.md`
- Modify: `references/planning-package.md`

**Interfaces:**
- Produces: `validate_v2(state_path: Path, workspace: Path, gate: str) -> dict`
- Preserves: `validate(state_path: Path, project_dir: Path) -> dict` for schema v1
- Produces: CLI `--workspace PATH --gate planning|pilot|production|delivery`
- Preserves: CLI `--project-dir PATH` for schema v1 compatibility

- [ ] **Step 1: Write a failing test for exact planning-document comparison**

Generate documents from the fixture, change one character in `PPT内容大纲.txt`, and assert:

```python
with self.assertRaisesRegex(ValueError, "Planning file drift"):
    MODULE.validate_v2(self.state_path, self.workspace, "planning")
```

- [ ] **Step 2: Write failing tests for page prompt and font-role contracts**

Add separate tests that reject an empty locked-copy item, no page font roles, locked copy missing from the prompt, and `F01` missing from the prompt.

- [ ] **Step 3: Write failing tests for every gate**

Cover these cases:

```python
def test_planning_gate_requires_planning_ready(self): ...
def test_pilot_gate_requires_pilot_approval_and_page_evidence(self): ...
def test_production_gate_requires_current_image_for_every_page(self): ...
def test_delivery_gate_requires_page_family_deck_and_render_reviews(self): ...
```

Each test mutates only the relevant state field and asserts the specific error text.

- [ ] **Step 4: Write the schema-v1 legacy test**

Use the existing schema-v1 fixture and assert:

```python
result = MODULE.validate(self.state_path, self.project_dir)
self.assertTrue(result["legacy"])
self.assertEqual(result["schema_version"], 1)
```

- [ ] **Step 5: Run the v2 validator tests and verify RED**

Run:

```powershell
python -X utf8 -m unittest tests.test_validate_project_v2 -v
```

Expected: failures because schema v2 and `--gate` are unsupported.

- [ ] **Step 6: Implement schema-v2 structural validation**

Validate required deck/style/font/family/page/review/delivery fields, fixed enum values, continuous indices, family membership, component specifications, font file suffixes and paths, nonempty copy strings, prompt copy inclusion, prompt font-role inclusion, and deterministic planning-file equality.

Use gate rank:

```python
STATUS_ORDER = {
    "INTAKE": 0,
    "STYLE_SAMPLING": 1,
    "STYLE_SELECTED": 2,
    "PLANNING_READY": 3,
    "PILOT_REVIEW": 4,
    "PILOT_APPROVED": 5,
    "FULL_PRODUCTION": 6,
    "QA": 7,
    "PDF_RENDER_CHECK": 8,
    "DELIVERY_READY": 9,
}
```

Gate evidence must be checked independently of status rank so a manually advanced status cannot bypass missing reviews.

- [ ] **Step 7: Implement gate-specific evidence checks**

- Planning: generated files match, fonts exist, pages and prompts are complete.
- Pilot: `reviews.pilot.status == "pass"`, reviewed page list is nonempty and matches declared pilot pages.
- Production: every page has `qa_status` in `PASS|REVIEWED` and an existing `current_image` whose SHA-256 matches `image_sha256`.
- Delivery: every page is `PASS`, every repeated family review is `pass` and matches current member hashes, whole-deck review is `pass`, and render review is `pass`.

- [ ] **Step 8: Update schema documentation with a complete v2 example**

Document every required field and the v1 compatibility boundary. Replace claims that the old validator checks cross-file content with the exact v2 behavior.

- [ ] **Step 9: Run focused and full tests**

Run:

```powershell
python -X utf8 -m unittest tests.test_validate_project_v2 -v
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 10: Commit**

```powershell
git add scripts/validate_project.py tests/test_validate_project_v2.py references/project-state.md references/planning-package.md
git commit -m "feat: enforce project state production gates"
```

### Task 4: Promote only managed final artifacts through a staged delivery

**Files:**
- Create: `scripts/promote_delivery.py`
- Create: `tests/test_promote_delivery.py`
- Modify: `scripts/validate_delivery.py`
- Modify: `tests/test_validate_delivery.py`

**Interfaces:**
- Produces: `promote(state_path: Path, workspace: Path, pdf_path: Path, delivery_dir: Path, render_report: Path) -> dict`
- Produces: CLI arguments from the approved design
- Consumes: `validate_project.validate_v2(..., gate="delivery")`
- Consumes: `validate_delivery.validate(...)`

- [ ] **Step 1: Write a failing clean-promotion test**

Create a complete temporary v2 workspace containing final planning files, one font, current slide, candidate PDF, and matching render report. Add process files under `candidates/`, `history/`, `montages/`, `ocr/`, and `render-back/`. Assert the promoted directory contains exactly:

```python
{
    "课件.pdf",
    "PPT内容大纲.txt",
    "风格提示词.txt",
    "字体说明.txt",
    "fonts",
}
```

Assert no process file basename appears recursively in the delivery.

- [ ] **Step 2: Write failing safety and recovery tests**

Add:

```python
def test_rejects_target_with_unmanaged_docx_without_changing_it(self): ...
def test_moves_previous_managed_delivery_to_workspace_history(self): ...
def test_restores_previous_delivery_when_final_rename_fails(self): ...
```

The rollback test patches only the final rename operation and verifies the original delivery bytes remain unchanged.

- [ ] **Step 3: Run promotion tests and verify RED**

Run:

```powershell
python -X utf8 -m unittest tests.test_promote_delivery -v
```

Expected: import failure because `promote_delivery.py` does not exist.

- [ ] **Step 4: Implement staging and managed-file detection**

Build a sibling staging directory with `tempfile.mkdtemp(dir=delivery_dir.parent)`. Copy only PDF, generated planning documents, state-registered fonts, and state-registered deliverable images. Reject an existing target containing names outside the validator's allowed managed set before any move.

- [ ] **Step 5: Validate staging and implement recoverable swap**

Run the delivery validator on staging. Move an existing managed delivery to `<workspace>/history/delivery-<UTC timestamp>/`, rename staging to the final name, and restore the old directory if the final rename fails. Never delete the history copy automatically.

- [ ] **Step 6: Strengthen final-directory process-artifact rejection**

Add recursive rejection for `candidates`, `history`, `render-back`, `project-state.json`, `slide-*.png`, and filenames containing `old`, `previous`, `修改前`, `调整前`, `候选`, or `过程`. Keep checks case-insensitive for Latin text.

- [ ] **Step 7: Run focused and full tests**

Run:

```powershell
python -X utf8 -m unittest tests.test_promote_delivery tests.test_validate_delivery -v
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
```

Expected: all tests pass and the temporary final directory has no process artifacts.

- [ ] **Step 8: Commit**

```powershell
git add scripts/promote_delivery.py scripts/validate_delivery.py tests/test_promote_delivery.py tests/test_validate_delivery.py
git commit -m "feat: promote clean recoverable image deck deliveries"
```

### Task 5: Update the Skill workflow and consolidate test discovery

**Files:**
- Modify: `SKILL.md`
- Modify: `references/full-page-production.md`
- Modify: `references/qa-and-delivery.md`
- Modify: `references/intake-and-planning.md`
- Move: `scripts/tests/test_skill_scripts.py` to `tests/test_skill_scripts.py`
- Delete: `scripts/tests/test_skill_scripts.py`

**Interfaces:**
- Documents: external workspace and final-directory separation
- Documents: generate → validate gate → produce → promote sequence
- Documents: explicit user-selected pilot pages take priority over heuristic representatives

- [ ] **Step 1: Move the remaining script test suite into top-level discovery**

Move the file without changing test behavior, update its repository-root calculation, and run:

```powershell
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
```

Expected: the combined suite discovers every previous top-level and script test exactly once.

- [ ] **Step 2: Rewrite the workflow around the external workspace**

Replace project-root planning instructions with:

1. create external workspace;
2. edit schema-v2 state;
3. generate planning documents under workspace `planning/`;
4. pass the appropriate gate;
5. generate and revise only inside workspace;
6. promote through `promote_delivery.py`;
7. validate the final directory.

- [ ] **Step 3: Add the process-artifact invariant**

State explicitly in `SKILL.md`, production, and delivery references that every changed page, rejected page, prior page, candidate, montage, OCR file, render-back, report, and state file is a process artifact. None may enter or remain in the final directory.

- [ ] **Step 4: Resolve pilot-selection precedence**

Document that an explicit user request such as “先做前五页” selects pages 1–5. The high-risk representative heuristic applies only when the user did not specify page numbers.

- [ ] **Step 5: Update every command to UTF-8-safe invocation**

Use `python -X utf8` for generation, validation, packaging, rendering, rule recording, and promotion commands.

- [ ] **Step 6: Run documentation contract and full tests**

Run:

```powershell
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
python -X utf8 C:\Users\yulin\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\yulin\.codex\skills\ppt-page-image
```

Expected: all tests pass and quick validation prints `Skill is valid!`.

- [ ] **Step 7: Commit**

```powershell
git add SKILL.md references scripts/tests tests/test_skill_scripts.py
git commit -m "docs: adopt clean workspace and delivery workflow"
```

### Task 6: End-to-end first-round acceptance

**Files:**
- Create: `tests/test_first_round_end_to_end.py`
- Modify only if the new end-to-end test exposes a defect: the owning production file and its focused test

**Interfaces:**
- Exercises: state → planning generation → planning gate → delivery gate → staged promotion → final validation

- [ ] **Step 1: Write the failing end-to-end acceptance test**

Build a one-page v2 project, generate its planning files, create the approved page and PDF, populate all required review hashes, promote it, and assert:

```python
self.assertEqual(
    {path.name for path in self.delivery.iterdir()},
    {"课件.pdf", "PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt", "fonts"},
)
self.assertFalse(any(path.name.startswith("slide-") for path in self.delivery.rglob("*")))
self.assertFalse(any(path.name == "project-state.json" for path in self.delivery.rglob("*")))
self.assertTrue((self.workspace / "history").exists())
```

- [ ] **Step 2: Run the acceptance test and verify RED if any integration is missing**

Run:

```powershell
python -X utf8 -m unittest tests.test_first_round_end_to_end -v
```

Expected before final integration: failure naming the missing boundary or evidence field. If it passes immediately because earlier tasks fully covered the flow, temporarily change one expected managed item to prove the test can fail, restore it, and rerun.

- [ ] **Step 3: Implement only the missing integration behavior**

Make the smallest change in the owning script. Do not loosen delivery validation or copy process artifacts to satisfy the test.

- [ ] **Step 4: Run all verification commands fresh**

Run:

```powershell
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
python -X utf8 C:\Users\yulin\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\yulin\.codex\skills\ppt-page-image
git diff --check
git status --short
```

Expected: zero failed tests, `Skill is valid!`, no whitespace errors, and only the planned acceptance changes remain before commit.

- [ ] **Step 5: Re-read the approved design and verify every requirement**

Confirm explicitly that the implementation covers directory separation, single-source planning generation, schema-v2 gates, schema-v1 legacy reporting, clean recoverable promotion, user-state correction rules, and the no-process-artifacts final-directory invariant.

- [ ] **Step 6: Commit**

```powershell
git add tests/test_first_round_end_to_end.py
git add scripts SKILL.md references tests
git commit -m "test: verify clean image deck workflow end to end"
```
