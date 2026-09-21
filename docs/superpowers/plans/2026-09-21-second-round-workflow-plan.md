# PPT Page Image 第二轮工作流改造实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 Schema v2 的规范型工作流升级为 Schema v3 的可操作工作流，提供安全初始化、迁移、状态变更、审核失效、项目诊断、技术预检、Montage、来源追溯和带哈希清单的干净交付。

**Architecture:** `scripts/project_state.py` 是状态、路径、哈希、原子保存和审核失效的共享核心；每个 CLI 只承担一个明确职责。现有验证、策划和交付模块复用核心接口，v1/v2 继续可读，新项目和新操作使用 v3。

**Tech Stack:** Python 3.11+ 标准库、Pillow、PyMuPDF、`unittest`、JSON、PowerShell 命令示例。

**Spec:** `docs/superpowers/specs/2026-09-21-second-round-workflow-design.md`

## Global Constraints

- 每页仍是一张完整的 16:9 页面图片；不增加局部覆盖、拼贴或 PPTX 生产路径。
- 工作区与最终交付目录必须分离，过程文件不得进入最终交付。
- 所有写状态操作必须先验证、再原子替换；失败不得留下截断状态。
- 不自动删除用户文件，不覆盖含非托管文件的交付目录。
- OCR 是可选风险提示，不是文案正确性的自动裁决器。
- 新项目默认 Schema v3；v1/v2 保持读取和迁移能力。
- 所有 Python CLI 文档命令使用 `python -X utf8`。
- 每项生产代码必须先有一个观察到正确失败原因的测试。

## Review Focus

1. 中文、空格和大小写不同的 Windows 路径：Task 1、2、7 必须证明路径仍在工作区且不会误判合法路径。
2. 状态写入过程中发生替换失败：Task 1 必须证明原文件保持完整。
3. 页面图片原路径被符号链接引到工作区外：Task 1、3 必须拒绝登记和审核。
4. 旧审核记录状态为 pass、但输入哈希已变化：Task 3、6 必须使门禁失败。
5. 交付清单生成后文件被替换或增加：Task 7 必须使最终验证失败。

---

### Task 1: 共享项目状态核心与 Schema v3 基础验证

**Files:**
- Create: `scripts/project_state.py`
- Create: `tests/fixtures/minimal-v3-state.json`
- Create: `tests/test_project_state.py`
- Create: `tests/test_validate_project_v3.py`
- Modify: `scripts/planning_documents.py`
- Modify: `scripts/validate_project.py`
- Modify: `tests/test_generate_planning_files.py`
- Modify: `tests/test_validate_project_v2.py`

**Interfaces:**
- Produces: `load_state(path: Path) -> dict`, `save_state_atomic(path: Path, state: dict) -> None`, `file_sha256(path: Path) -> str`, `resolve_workspace_path(workspace: Path, relative: str, context: str) -> Path`, `append_audit(state: dict, action: str, target: str, reason: str, at: str | None = None) -> None`, `schema_version(state: dict) -> int`.
- Produces: `validate_v3_structure(data: dict, workspace: Path) -> tuple[list[dict], dict, list[str]]` and `validate_v3(state_path: Path, workspace: Path, gate: str) -> dict`.
- Consumes: existing Schema v2 field contracts and `planning_documents.render_documents`.

- [ ] **Step 1: Write the failing shared-core tests**

```python
class ProjectStateTests(unittest.TestCase):
    def test_atomic_save_preserves_unicode_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "含 空格" / "project-state.json"
            path.parent.mkdir()
            state = {"schema_version": 3, "deck": {"name": "让班级升温"}}
            project_state.save_state_atomic(path, state)
            self.assertEqual(project_state.load_state(path), state)

    def test_workspace_path_rejects_parent_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "work"
            workspace.mkdir()
            with self.assertRaisesRegex(ValueError, "inside workspace"):
                project_state.resolve_workspace_path(workspace, "../outside.png", "page image")

    def test_workspace_path_rejects_symlink_escape_when_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "work"
            outside = root / "outside"
            workspace.mkdir()
            outside.mkdir()
            try:
                (workspace / "linked").symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "inside workspace"):
                project_state.resolve_workspace_path(workspace, "linked/page.png", "page image")

    def test_failed_replace_leaves_original_state(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch("os.replace", side_effect=OSError("blocked")):
            path = Path(tmp) / "project-state.json"
            path.write_text('{"schema_version": 3, "marker": "old"}', encoding="utf-8")
            with self.assertRaises(OSError):
                project_state.save_state_atomic(path, {"schema_version": 3, "marker": "new"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["marker"], "old")
```

- [ ] **Step 2: Run the shared-core tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_project_state -v`

Expected: import failure for missing `project_state` module.

- [ ] **Step 3: Implement the minimal shared core**

```python
def save_state_atomic(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise

def resolve_workspace_path(workspace: Path, relative: str, context: str) -> Path:
    root = workspace.resolve(strict=True)
    candidate = (root / relative).resolve(strict=False)
    if not candidate.is_relative_to(root):
        raise ValueError(f"{context} must stay inside workspace")
    return candidate
```

- [ ] **Step 4: Add the v3 fixture and failing validator tests**

Copy the complete v2 fixture to `minimal-v3-state.json`, set `schema_version` to `3`, and add these exact top-level values:

```json
"sources": [],
"audit_log": [],
"reviews": {
  "pilot": {"status": "pending", "pages": []},
  "pages": {},
  "families": {},
  "deck": {"status": "pending"},
  "render": {"status": "pending"}
},
"delivery": {"deck_name": "课件", "images": [], "manifest": "交付清单.json"}
```

Add:

```python
def test_accepts_complete_v3_planning_gate(self):
    workspace, state_path = self.make_v3_workspace()
    result = validate_project.validate_v3(state_path, workspace, "planning")
    self.assertEqual(result["schema_version"], 3)
    self.assertFalse(result["legacy"])

def test_v3_rejects_page_reference_to_unknown_source(self):
    workspace, state_path = self.make_v3_workspace()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["pages"][0]["source_refs"] = ["missing-source"]
    state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    with self.assertRaisesRegex(ValueError, "unknown source"):
        validate_project.validate_v3(state_path, workspace, "planning")
```

- [ ] **Step 5: Run v3 validator tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_validate_project_v3 -v`

Expected: module or attribute failure because `validate_v3` and its test module do not exist.

- [ ] **Step 6: Implement v3 planning support without duplicating v2 rendering**

Create `tests/test_validate_project_v3.py`. Refactor shared v2/v3 structural validation into helpers, require `sources`, `audit_log`, `reviews.pages`, `delivery.manifest`, validate unique source IDs and page `source_refs`, and allow `planning_documents.render_documents` for schema versions `{2, 3}`:

```python
def render_documents(state: dict) -> dict[str, str]:
    if state.get("schema_version") not in {2, 3}:
        raise ValueError("Planning documents require project-state schema_version 2 or 3")
    return {
        "PPT内容大纲.txt": _render_outline(state),
        "风格提示词.txt": _render_style(state),
        "字体说明.txt": _render_fonts(state),
    }
```

- [ ] **Step 7: Run focused and full tests**

Run: `python -X utf8 -m unittest tests.test_project_state tests.test_validate_project_v3 tests.test_generate_planning_files tests.test_validate_project_v2 -v`

Expected: all focused tests pass.

Run: `python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all existing and new tests pass.

- [ ] **Step 8: Commit Task 1**

```powershell
git add scripts/project_state.py scripts/planning_documents.py scripts/validate_project.py tests/fixtures/minimal-v3-state.json tests/test_project_state.py tests/test_validate_project_v3.py tests/test_generate_planning_files.py tests/test_validate_project_v2.py
git commit -m "feat: add schema v3 project state core"
```

---

### Task 2: 项目初始化与旧状态迁移

**Files:**
- Create: `scripts/init_project.py`
- Create: `scripts/migrate_project.py`
- Create: `tests/test_init_project.py`
- Create: `tests/test_migrate_project.py`
- Modify: `scripts/project_state.py`

**Interfaces:**
- Consumes: `save_state_atomic`, `load_state`, `append_audit` from Task 1.
- Produces: `initial_state(name: str, pages: int, audience: str, scenario: str) -> dict`, `initialize(workspace: Path, name: str, pages: int, audience: str, scenario: str) -> Path`, `migrate(data: dict) -> tuple[dict, list[str]]`, `migrate_file(source: Path, destination: Path, in_place: bool, workspace: Path | None) -> Path`.

- [ ] **Step 1: Write failing initialization tests**

```python
def test_initializes_unicode_workspace_with_26_page_placeholders(self):
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp) / "让班级 升温"
        state_path = init_project.initialize(workspace, "让班级升温", 26, "中小学生", "主题班会")
        state = project_state.load_state(state_path)
        self.assertEqual(state["schema_version"], 3)
        self.assertEqual([p["index"] for p in state["pages"]], list(range(1, 27)))
        self.assertEqual(state["status"], "INTAKE")
        self.assertEqual(
            {p.name for p in workspace.iterdir()},
            {"project-state.json", "planning", "fonts", "slides", "samples", "montages", "reports", "render-back", "history"},
        )

def test_refuses_nonempty_workspace(self):
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp) / "work"
        workspace.mkdir()
        (workspace / "用户文件.docx").write_bytes(b"keep")
        with self.assertRaisesRegex(ValueError, "empty"):
            init_project.initialize(workspace, "课件", 2, "中小学生", "主题班会")
        self.assertTrue((workspace / "用户文件.docx").is_file())
```

- [ ] **Step 2: Run initialization tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_init_project -v`

Expected: import failure for missing `init_project`.

- [ ] **Step 3: Implement initialization and CLI validation**

The CLI must reject `--pages < 1`, create directories only after all arguments validate, and print JSON containing `workspace`, `state`, `schema_version`, and `pages`.

```python
def initialize(workspace: Path, name: str, pages: int, audience: str, scenario: str) -> Path:
    if pages < 1:
        raise ValueError("pages must be at least 1")
    if workspace.exists() and any(workspace.iterdir()):
        raise ValueError("workspace must be empty or absent")
    workspace.mkdir(parents=True, exist_ok=True)
    for folder in WORKSPACE_DIRS:
        (workspace / folder).mkdir()
    state_path = workspace / "project-state.json"
    save_state_atomic(state_path, initial_state(name, pages, audience, scenario))
    return state_path
```

- [ ] **Step 4: Write failing migration tests**

```python
def test_migrates_v2_without_fabricating_passed_page_reviews(self):
    source = json.loads(V2_FIXTURE.read_text(encoding="utf-8"))
    source["reviews"]["deck"] = {"status": "pass"}
    migrated, warnings = migrate_project.migrate(source)
    self.assertEqual(migrated["schema_version"], 3)
    self.assertEqual(migrated["reviews"]["pages"], {})
    self.assertEqual(migrated["reviews"]["deck"]["status"], "pending")
    self.assertIn("legacy review evidence was reset", warnings)

def test_in_place_migration_preserves_original_in_history(self):
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        source = workspace / "project-state.json"
        source.write_text(V2_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
        migrate_project.migrate_file(source, source, True, workspace)
        self.assertEqual(project_state.load_state(source)["schema_version"], 3)
        self.assertEqual(len(list((workspace / "history").glob("project-state-v2-*.json"))), 1)
```

- [ ] **Step 5: Run migration tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_migrate_project -v`

Expected: import failure for missing `migrate_project`.

- [ ] **Step 6: Implement v1/v2 to v3 migration**

The migrator copies known fields, initializes `sources`, `audit_log`, `reviews.pages`, and `delivery.manifest`, resets unprovable reviews to pending, caps migrated v1 status at `PLANNING_READY`, and writes warnings into `migration_warnings` and command output. A v3 input returns an equal deep copy with no warnings.

- [ ] **Step 7: Run focused and full tests**

Run: `python -X utf8 -m unittest tests.test_init_project tests.test_migrate_project -v`

Expected: all focused tests pass.

Run: `python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all tests pass.

- [ ] **Step 8: Commit Task 2**

```powershell
git add scripts/init_project.py scripts/migrate_project.py scripts/project_state.py tests/test_init_project.py tests/test_migrate_project.py
git commit -m "feat: initialize and migrate image deck projects"
```

---

### Task 3: 原子计划更新、状态推进和依赖审核失效

**Files:**
- Create: `scripts/update_project.py`
- Create: `tests/test_update_project.py`
- Modify: `scripts/project_state.py`
- Modify: `scripts/validate_project.py`

**Interfaces:**
- Consumes: Task 1 state core and v3 validation.
- Produces: `apply_plan(state_path: Path, workspace: Path, plan_path: Path, reason: str) -> dict`, `register_image(state_path: Path, workspace: Path, page_index: int, image: Path, reason: str) -> dict`, `content_changed(state_path: Path, workspace: Path, reason: str) -> dict`, `visual_changed(state_path: Path, workspace: Path, page_indices: set[int], reason: str) -> dict`, `set_status(state_path: Path, workspace: Path, target_status: str, reason: str) -> dict`, `invalidate_for_pages(state: dict, page_indices: set[int]) -> None`, `invalidate_all_reviews(state: dict) -> None`.

- [ ] **Step 1: Write failing invalidation tests**

```python
def test_registering_changed_image_invalidates_page_family_deck_and_render(self):
    workspace, state_path = self.make_reviewed_project()
    replacement = workspace / "slides" / "slide-1-new.png"
    Image.new("RGB", (1600, 900), "#123456").save(replacement)
    updated = update_project.register_image(state_path, workspace, 1, replacement, "标题位置调整")
    self.assertEqual(updated["pages"][0]["qa_status"], "PENDING")
    self.assertEqual(updated["reviews"]["pages"].get("1"), None)
    self.assertEqual(updated["reviews"]["families"]["cover"]["status"], "pending")
    self.assertEqual(updated["reviews"]["deck"]["status"], "pending")
    self.assertEqual(updated["reviews"]["render"]["status"], "pending")

def test_rejects_image_outside_workspace_even_through_relative_escape(self):
    workspace, state_path = self.make_reviewed_project()
    outside = workspace.parent / "outside.png"
    Image.new("RGB", (1600, 900)).save(outside)
    with self.assertRaisesRegex(ValueError, "inside workspace"):
        update_project.register_image(state_path, workspace, 1, outside, "replace")
```

- [ ] **Step 2: Run invalidation tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_update_project -v`

Expected: import failure for missing `update_project`.

- [ ] **Step 3: Implement image registration and invalidation**

```python
def invalidate_for_pages(state: dict, page_indices: set[int]) -> None:
    families = {p["family"] for p in state["pages"] if p["index"] in page_indices}
    for page in state["pages"]:
        if page["index"] in page_indices:
            page["qa_status"] = "PENDING"
            state["reviews"]["pages"].pop(str(page["index"]), None)
    for name in families:
        state["reviews"]["families"][name] = {"status": "pending"}
    state["reviews"]["deck"] = {"status": "pending"}
    state["reviews"]["render"] = {"status": "pending"}
```

Image registration stores a workspace-relative POSIX path and a SHA-256 calculated after path containment checks. It does not copy arbitrary outside files into the workspace.

- [ ] **Step 4: Write failing plan and status transition tests**

```python
def test_apply_plan_is_all_or_nothing(self):
    workspace, state_path = self.make_planning_project()
    before = state_path.read_bytes()
    invalid_plan = workspace / "invalid-plan.json"
    invalid_plan.write_text('{"pages": []}', encoding="utf-8")
    with self.assertRaises(ValueError):
        update_project.apply_plan(state_path, workspace, invalid_plan, "刷新大纲")
    self.assertEqual(state_path.read_bytes(), before)

def test_apply_plan_rolls_back_state_and_planning_when_replace_fails(self):
    workspace, state_path = self.make_planning_project()
    before_state = state_path.read_bytes()
    before_planning = {p.name: p.read_bytes() for p in (workspace / "planning").iterdir()}
    plan_path = self.write_valid_changed_plan(workspace)
    real_replace = os.replace
    calls = 0
    def fail_second_replace(source, target):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("blocked")
        return real_replace(source, target)
    with mock.patch("update_project.os.replace", side_effect=fail_second_replace):
        with self.assertRaises(OSError):
            update_project.apply_plan(state_path, workspace, plan_path, "刷新大纲")
    self.assertEqual(state_path.read_bytes(), before_state)
    self.assertEqual({p.name: p.read_bytes() for p in (workspace / "planning").iterdir()}, before_planning)

def test_content_change_resets_planning_and_all_reviews(self):
    workspace, state_path = self.make_reviewed_project()
    state = update_project.content_changed(state_path, workspace, "调整第三部分活动")
    self.assertEqual(state["status"], "PLANNING_READY")
    self.assertEqual(state["reviews"]["pages"], {})
    self.assertEqual(state["reviews"]["pilot"]["status"], "pending")

def test_set_status_cannot_skip_failed_target_gate(self):
    workspace, state_path = self.make_planning_project(status="STYLE_SELECTED")
    with self.assertRaisesRegex(ValueError, "planning"):
        update_project.set_status(state_path, workspace, "PLANNING_READY", "策划完成")
```

- [ ] **Step 5: Run transition tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_update_project -v`

Expected: failures for missing transition functions.

- [ ] **Step 6: Implement apply-plan, content/visual change and legal status transitions**

`apply_plan` accepts only `deck`, `style`, `fonts`, `sources`, `enrichment`, `families`, and `pages`; preserves operational fields; validates a deep-copied candidate; stages the candidate state and all three planning files in a sibling temporary directory; then replaces the managed files as one recoverable transaction. If any replacement fails, restore every original state/planning file before raising. `set_status` validates target-gate evidence while temporarily evaluating the candidate target status, and only then persists it.

- [ ] **Step 7: Run focused and full tests**

Run: `python -X utf8 -m unittest tests.test_update_project tests.test_validate_project_v3 -v`

Expected: all focused tests pass.

Run: `python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all tests pass.

- [ ] **Step 8: Commit Task 3**

```powershell
git add scripts/update_project.py scripts/project_state.py scripts/validate_project.py tests/test_update_project.py
git commit -m "feat: manage project transitions and review invalidation"
```

---

### Task 4: 一键项目诊断

**Files:**
- Create: `scripts/project_check.py`
- Create: `tests/test_project_check.py`
- Modify: `scripts/validate_project.py`

**Interfaces:**
- Consumes: `validate_v3`, gate constants, state loading.
- Produces: `check_project(state_path: Path, workspace: Path) -> dict` with `schema_version`, `status`, `last_passed_gate`, `blocking_items`, `next_action`, and `next_command`.

- [ ] **Step 1: Write failing diagnosis tests**

```python
def test_reports_planning_as_next_action_for_new_project(self):
    workspace, state_path = self.make_initialized_project()
    result = project_check.check_project(state_path, workspace)
    self.assertEqual(result["last_passed_gate"], None)
    self.assertEqual(result["next_action"], "complete_planning")
    self.assertTrue(any("style" in item or "font" in item for item in result["blocking_items"]))
    self.assertIn("generate_planning_files.py", result["next_command"])

def test_returns_exit_one_for_blocked_and_two_for_invalid_input(self):
    self.assertEqual(self.run_cli(self.initialized_state).returncode, 1)
    self.assertEqual(self.run_cli(self.workspace / "missing.json").returncode, 2)

def test_delivery_ready_project_reports_no_next_command(self):
    workspace, state_path = self.make_delivery_ready_project()
    result = project_check.check_project(state_path, workspace)
    self.assertEqual(result["last_passed_gate"], "delivery")
    self.assertEqual(result["blocking_items"], [])
    self.assertIsNone(result["next_command"])
```

- [ ] **Step 2: Run diagnosis tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_project_check -v`

Expected: import failure for missing `project_check`.

- [ ] **Step 3: Implement deterministic gate diagnosis**

Evaluate gates in order without mutating state. Collect the first failing gate's stable error messages and map it to one of `complete_planning`, `review_pilot`, `finish_production`, or `finish_delivery_review`. CLI writes one JSON object; return `0` only when the current next action is executable without unresolved blockers, `1` for project blockers, and `2` for invalid input/environment.

- [ ] **Step 4: Run focused and full tests**

Run: `python -X utf8 -m unittest tests.test_project_check -v`

Expected: all focused tests pass.

Run: `python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all tests pass.

- [ ] **Step 5: Commit Task 4**

```powershell
git add scripts/project_check.py scripts/validate_project.py tests/test_project_check.py
git commit -m "feat: diagnose project readiness and next actions"
```

---

### Task 5: 页面技术预检与 Montage 证据

**Files:**
- Create: `scripts/preflight_images.py`
- Create: `scripts/build_montage.py`
- Create: `tests/test_preflight_images.py`
- Create: `tests/test_build_montage.py`
- Modify: `scripts/project_state.py`

**Interfaces:**
- Consumes: state loading, path resolution, SHA-256.
- Produces: `inspect_pages(state: dict, workspace: Path, min_width: int = 1600, min_height: int = 900, edge_threshold: int = 250, ocr: Callable[[Path], str] | None = None) -> dict`.
- Produces: `build_family_montage(state: dict, workspace: Path, family: str, columns: int = 4) -> dict`, `build_deck_montage(state: dict, workspace: Path, columns: int = 4) -> dict`.

- [ ] **Step 1: Write failing preflight tests**

```python
def test_detects_duplicate_low_resolution_and_white_edge(self):
    workspace, state = self.make_three_page_workspace()
    Image.new("RGB", (800, 450), "white").save(workspace / "slides" / "slide-1.png")
    shutil.copy2(workspace / "slides" / "slide-1.png", workspace / "slides" / "slide-2.png")
    Image.new("RGB", (1600, 900), "#123456").save(workspace / "slides" / "slide-3.png")
    report = preflight_images.inspect_pages(state, workspace)
    codes = {issue["code"] for issue in report["issues"]}
    self.assertTrue({"LOW_RESOLUTION", "DUPLICATE_PAGE", "WHITE_EDGE"}.issubset(codes))

def test_ocr_unavailable_is_reported_not_passed(self):
    workspace, state = self.make_one_page_workspace()
    report = preflight_images.inspect_pages(state, workspace, ocr=None)
    self.assertEqual(report["ocr"]["status"], "unavailable")
    self.assertNotEqual(report["ocr"]["status"], "pass")
```

- [ ] **Step 2: Run preflight tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_preflight_images -v`

Expected: import failure for missing `preflight_images`.

- [ ] **Step 3: Implement deterministic image preflight**

Use Pillow to verify opening, dimensions, ratio tolerance of `0.002`, alpha/white edges, entropy-based near-blank detection, byte-independent pixel digest for exact duplicates, numbering and registered hashes. JSON report includes thresholds and per-page issues. Exit `0` when no technical issues, `1` when issues exist, `2` on invalid input.

- [ ] **Step 4: Write failing Montage tests**

```python
def test_family_montage_records_member_and_output_hashes(self):
    workspace, state = self.make_family_workspace()
    result = build_montage.build_family_montage(state, workspace, "activity", columns=2)
    report = json.loads(Path(result["report"]).read_text(encoding="utf-8"))
    self.assertEqual(report["member_pages"], [1, 2])
    self.assertEqual(set(report["member_hashes"]), {"1", "2"})
    self.assertEqual(report["montage_sha256"], project_state.file_sha256(Path(result["montage"])))

def test_rejects_unknown_family_and_missing_member_image(self):
    workspace, state = self.make_family_workspace()
    with self.assertRaisesRegex(ValueError, "unknown family"):
        build_montage.build_family_montage(state, workspace, "missing")
    (workspace / state["pages"][0]["current_image"]).unlink()
    with self.assertRaisesRegex(ValueError, "not found"):
        build_montage.build_family_montage(state, workspace, "activity")
```

- [ ] **Step 5: Run Montage tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_build_montage -v`

Expected: import failure for missing `build_montage`.

- [ ] **Step 6: Implement family and deck Montage generation**

Create thumbnail cells with page-number captions outside the page image, save under `montages/families/<safe-name>.png` or `montages/deck.png`, and write a sibling `.json` report. Sanitize output filenames while preserving the original family name in the report.

- [ ] **Step 7: Run focused and full tests**

Run: `python -X utf8 -m unittest tests.test_preflight_images tests.test_build_montage -v`

Expected: all focused tests pass.

Run: `python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all tests pass.

- [ ] **Step 8: Commit Task 5**

```powershell
git add scripts/preflight_images.py scripts/build_montage.py scripts/project_state.py tests/test_preflight_images.py tests/test_build_montage.py
git commit -m "feat: preflight pages and build auditable montages"
```

---

### Task 6: 结构化审核登记与 v3 门禁绑定

**Files:**
- Modify: `scripts/update_project.py`
- Modify: `scripts/validate_project.py`
- Create: `tests/test_review_evidence_v3.py`
- Modify: `tests/test_update_project.py`

**Interfaces:**
- Consumes: page hashes, Montage reports, render-back report, preflight report.
- Produces: `record_page_review(state_path: Path, workspace: Path, page_index: int, status: str, checks: dict[str, bool], notes: str) -> dict`.
- Produces: `record_family_review(state_path: Path, workspace: Path, family: str, status: str, montage_report: Path, checks: dict[str, bool], notes: str) -> dict`.
- Produces: `record_deck_review(state_path: Path, workspace: Path, status: str, montage_report: Path, checks: dict[str, bool], notes: str) -> dict`.
- Produces: `record_render_review(state_path: Path, workspace: Path, pdf: Path, render_report: Path, checks: dict[str, bool], notes: str) -> dict`.

- [ ] **Step 1: Write failing structured-review tests**

```python
def test_page_pass_requires_all_checks_and_current_hash(self):
    workspace, state_path = self.make_production_project()
    checks = {name: True for name in ("copy", "hierarchy", "crop", "clarity", "pseudo_text", "style")}
    state = update_project.record_page_review(state_path, workspace, 1, "pass", checks, "人工检查完成")
    review = state["reviews"]["pages"]["1"]
    self.assertEqual(review["image_sha256"], state["pages"][0]["image_sha256"])
    self.assertEqual(state["pages"][0]["qa_status"], "PASS")
    checks["copy"] = False
    with self.assertRaisesRegex(ValueError, "all required checks"):
        update_project.record_page_review(state_path, workspace, 1, "pass", checks, "")

def test_family_gate_rejects_montage_with_stale_member_hash(self):
    workspace, state_path = self.make_reviewed_family_project()
    state = project_state.load_state(state_path)
    state["reviews"]["families"]["activity"]["member_hashes"]["1"] = "stale"
    project_state.save_state_atomic(state_path, state)
    with self.assertRaisesRegex(ValueError, "member hashes"):
        validate_project.validate_v3(state_path, workspace, "delivery")

def test_render_pass_requires_matching_pdf_and_render_page_hashes(self):
    workspace, state_path, pdf, report = self.make_rendered_project()
    payload = json.loads(report.read_text(encoding="utf-8"))
    payload["pdf_sha256"] = "stale"
    report.write_text(json.dumps(payload), encoding="utf-8")
    with self.assertRaisesRegex(ValueError, "PDF hash"):
        update_project.record_render_review(state_path, workspace, pdf, report, self.render_checks(), "checked")
```

- [ ] **Step 2: Run review tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_review_evidence_v3 -v`

Expected: missing review functions or v3 evidence checks.

- [ ] **Step 3: Implement review recorders**

Every pass record stores `status`, complete named checks, notes, `reviewed_at`, and exact input hashes. Family and deck reviews must consume current Montage JSON; render review must consume the current PDF and `render-back-report.json`. A fail record may omit complete positive checks but never advances QA status.

- [ ] **Step 4: Strengthen v3 gates**

Planning uses structural evidence; pilot requires passing current page-review hashes for the declared pilot pages; production requires every current image and at least reviewed page evidence; delivery requires every page pass, all repeated families pass with current Montage/member hashes, deck pass with current Montage/member hashes, and render pass with current PDF/render hashes.

- [ ] **Step 5: Run focused and full tests**

Run: `python -X utf8 -m unittest tests.test_review_evidence_v3 tests.test_update_project tests.test_validate_project_v3 -v`

Expected: all focused tests pass.

Run: `python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all tests pass.

- [ ] **Step 6: Commit Task 6**

```powershell
git add scripts/update_project.py scripts/validate_project.py tests/test_review_evidence_v3.py tests/test_update_project.py
git commit -m "feat: bind structured reviews to current artifacts"
```

---

### Task 7: 来源追溯与带哈希交付清单

**Files:**
- Modify: `scripts/planning_documents.py`
- Modify: `scripts/validate_project.py`
- Modify: `scripts/promote_delivery.py`
- Modify: `scripts/validate_delivery.py`
- Create: `tests/test_delivery_manifest.py`
- Modify: `tests/test_promote_delivery.py`
- Modify: `tests/test_validate_delivery.py`

**Interfaces:**
- Consumes: v3 `sources`, page `source_refs`, registered fonts/images, passing render report.
- Produces: `build_manifest(stage: Path, deck_name: str, page_count: int, render_pdf_sha256: str) -> dict`, `write_manifest(stage: Path, manifest: dict) -> Path`, and manifest-aware `validate_delivery.validate(delivery_dir: Path, deck_name: str, expected_pages: int | None, render_report: Path) -> dict`.

- [ ] **Step 1: Write failing source validation tests**

```python
def test_local_source_hash_must_match_and_accepted_enrichment_must_reference_source(self):
    workspace, state_path = self.make_v3_workspace()
    source = workspace / "sources" / "案例.txt"
    source.parent.mkdir()
    source.write_text("事实", encoding="utf-8")
    state = project_state.load_state(state_path)
    state["sources"] = [{
        "id": "S01", "type": "local_file", "path": "sources/案例.txt",
        "sha256": "stale", "acquired_date": "2026-09-21", "rights_status": "user_supplied", "notes": ""
    }]
    state["enrichment"] = [{"status": "accepted", "type": "case", "source_refs": []}]
    project_state.save_state_atomic(state_path, state)
    with self.assertRaisesRegex(ValueError, "source hash"):
        validate_project.validate_v3(state_path, workspace, "planning")
```

- [ ] **Step 2: Run source tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_validate_project_v3.ProjectStateV3Tests.test_local_source_hash_must_match_and_accepted_enrichment_must_reference_source -v`

Expected: current validator does not reject the stale source hash or lacks the test.

- [ ] **Step 3: Implement source validation and planning rendering**

Require unique source IDs. Local files must remain inside workspace and match SHA-256. URL sources require `url`, `acquired_date`, and `rights_status`; no network request occurs during validation. Render source IDs and page usage in `PPT内容大纲.txt` and `风格提示词.txt` without exposing unrelated absolute paths.

- [ ] **Step 4: Write failing manifest tests**

```python
def test_promoted_v3_delivery_contains_complete_manifest(self):
    workspace, state_path, pdf, report, delivery = self.make_ready_delivery()
    promote_delivery.promote(state_path, workspace, pdf, delivery, report)
    manifest = json.loads((delivery / "交付清单.json").read_text(encoding="utf-8"))
    self.assertEqual(manifest["schema_version"], 1)
    self.assertEqual(manifest["deck"]["pages"], 1)
    self.assertEqual(
        {item["path"] for item in manifest["files"]},
        {"课件.pdf", "PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt", "fonts/NotoSansSC-Regular.otf"},
    )

def test_manifest_validation_rejects_replaced_and_extra_files(self):
    delivery, report = self.make_promoted_delivery()
    (delivery / "PPT内容大纲.txt").write_text("被替换", encoding="utf-8")
    with self.assertRaisesRegex(ValueError, "manifest hash"):
        validate_delivery.validate(delivery, "课件", 1, report)
    delivery, report = self.make_promoted_delivery()
    (delivery / "旧稿.png").write_bytes(b"old")
    with self.assertRaisesRegex(ValueError, "Unexpected delivery items"):
        validate_delivery.validate(delivery, "课件", 1, report)
```

- [ ] **Step 5: Run manifest tests and verify RED**

Run: `python -X utf8 -m unittest tests.test_delivery_manifest -v`

Expected: delivery lacks `交付清单.json` and validation does not verify its file hashes.

- [ ] **Step 6: Implement manifest staging and verification**

Generate the manifest after all managed files are in the sibling staging directory and before final validation. Each item records POSIX relative path, byte length, and SHA-256. The manifest does not list itself. For v3, the root allowlist includes the manifest and validation requires it; preserve the current v2 delivery contract so existing deliveries remain valid.

- [ ] **Step 7: Run focused and full tests**

Run: `python -X utf8 -m unittest tests.test_delivery_manifest tests.test_promote_delivery tests.test_validate_delivery tests.test_validate_project_v3 -v`

Expected: all focused tests pass.

Run: `python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all tests pass.

- [ ] **Step 8: Commit Task 7**

```powershell
git add scripts/planning_documents.py scripts/validate_project.py scripts/promote_delivery.py scripts/validate_delivery.py tests/test_delivery_manifest.py tests/test_promote_delivery.py tests/test_validate_delivery.py tests/test_validate_project_v3.py
git commit -m "feat: trace sources and verify delivery manifests"
```

---

### Task 8: Skill 瘦身、可执行行为回归与真实项目兼容演练

**Files:**
- Modify: `SKILL.md`
- Modify: `references/project-state.md`
- Modify: `references/intake-and-planning.md`
- Modify: `references/full-page-production.md`
- Modify: `references/qa-and-delivery.md`
- Modify: `references/learning-and-corrections.md`
- Modify: `tests/behavior-scenarios.md`
- Create: `tests/test_second_round_end_to_end.py`
- Modify: `agents/openai.yaml` only if the existing description no longer matches the final capability.

**Interfaces:**
- Consumes: every CLI and v3 contract from Tasks 1–7.
- Produces: concise routing-oriented `SKILL.md`, authoritative reference documentation, and an executable end-to-end workflow test.

- [ ] **Step 1: Write the failing end-to-end behavior test before editing Skill text**

```python
def test_26_page_project_change_and_repromotion_keeps_delivery_clean(self):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        workspace = root / "过程 工作区" / "让班级升温"
        state_path = init_project.initialize(workspace, "让班级升温", 26, "中小学生", "主题班会")
        self.populate_complete_plan(workspace, state_path)
        self.create_and_register_pages(workspace, state_path, 26)
        self.review_pilot_pages(workspace, state_path, [1, 2, 3, 4, 5])
        self.review_all_pages_families_and_deck(workspace, state_path)
        pdf, render_report = self.package_and_review(workspace, state_path)
        delivery = root / "最终 交付" / "让班级升温"
        promote_delivery.promote(state_path, workspace, pdf, delivery, render_report)

        changed = workspace / "slides" / "slide-3-revised.png"
        Image.new("RGB", (1600, 900), "#345678").save(changed)
        update_project.register_image(state_path, workspace, 3, changed, "用户要求调整第三页")
        with self.assertRaises(ValueError):
            validate_project.validate_v3(state_path, workspace, "delivery")
        self.reapprove_changed_dependencies(workspace, state_path, 3)
        pdf, render_report = self.package_and_review(workspace, state_path)
        promote_delivery.promote(state_path, workspace, pdf, delivery, render_report)

        self.assertEqual(len(list(delivery.glob("*.pdf"))), 1)
        self.assertTrue((delivery / "交付清单.json").is_file())
        self.assertFalse(any("旧" in p.name or "revised" in p.name for p in delivery.rglob("*")))
        validate_delivery.validate(delivery, "让班级升温", 26, render_report)
```

- [ ] **Step 2: Run the scenario and verify RED**

Run: `python -X utf8 -m unittest tests.test_second_round_end_to_end -v`

Expected: failure until all Task 1–7 interfaces and helpers are integrated; if it unexpectedly passes, deliberately alter the expected manifest filename to prove the assertion detects a regression, restore it, then continue.

- [ ] **Step 3: Rewrite `SKILL.md` as a concise router**

The final entrypoint must contain only:

1. trigger and full-image production contract;
2. required `imagegen` and `pdf` sub-skills;
3. v3 command-oriented workflow with explicit user approval stops;
4. correction and retry boundary;
5. final delivery contract;
6. links saying exactly when to read each reference.

Remove duplicated field lists and long checklists already enforced by scripts or owned by references. Keep the description trigger-only:

```yaml
description: Use when source material, lesson content, reports, outlines, screenshots, or a topic must become a reviewed image-based presentation PDF rather than an editable PPTX.
```

- [ ] **Step 4: Update references as single authorities**

Document exact v3 shapes and commands in `project-state.md`; initialization and source roles in `intake-and-planning.md`; image registration, preflight and Montage in `full-page-production.md`; structured review, manifest and promotion in `qa-and-delivery.md`; automatic invalidation and audit records in `learning-and-corrections.md`. Delete v2 instructions only where v3 supersedes new-project behavior; preserve a clearly labeled compatibility section.

- [ ] **Step 5: Turn behavior scenarios into an executable mapping**

Keep `tests/behavior-scenarios.md` as a short index where every scenario names its executable test, for example:

```markdown
| Scenario | Executable regression |
|---|---|
| 用户指定前五页试做 | `test_26_page_project_change_and_repromotion_keeps_delivery_clean` |
| 单页修改使下游审核失效 | `test_registering_changed_image_invalidates_page_family_deck_and_render` |
| 最终目录不保留旧稿 | `test_manifest_validation_rejects_replaced_and_extra_files` |
```

- [ ] **Step 6: Run the executable behavior test and full verification**

Run: `python -X utf8 -m unittest tests.test_second_round_end_to_end -v`

Expected: the 26-page scenario passes.

Run: `python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: all tests pass.

Run: `python -X utf8 C:\Users\yulin\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\yulin\.codex\skills\ppt-page-image`

Expected: `Skill is valid!`

Run: `python -X utf8 -m compileall -q scripts`

Expected: exit code `0` with no output.

Run: `git diff --check`

Expected: exit code `0` with no output.

- [ ] **Step 7: Perform a non-destructive compatibility rehearsal**

Locate the current《让班级升温》workspace by finding its `project-state.json` without modifying files. Copy only that state and its registered process assets into a newly created temporary directory outside the delivery folder. Run migration, planning generation and `project_check.py`. Do not generate new images and do not invoke promotion against the original delivery. Record the resolved source path, commands, migration warnings and check result under the plan's ignored execution workspace. If no such state file exists, record that factual absence and run the same rehearsal from an untouched copy of `tests/fixtures/minimal-v2-state.json`; this fallback verifies compatibility without pretending the historical project had machine-readable state.

Expected: original source and delivery directories have unchanged file counts and hashes; the temporary migrated project is v3 and reports truthful blockers rather than fabricated review passes.

- [ ] **Step 8: Commit Task 8**

```powershell
git add SKILL.md agents/openai.yaml references/project-state.md references/intake-and-planning.md references/full-page-production.md references/qa-and-delivery.md references/learning-and-corrections.md tests/behavior-scenarios.md tests/test_second_round_end_to_end.py
git commit -m "docs: adopt schema v3 image deck workflow"
```

---

## Final Verification And Review

1. Run the entire unittest suite and record the exact count.
2. Run Skill quick validation, `compileall`, and `git diff --check`.
3. Compare every acceptance criterion in the design spec against a test or rehearsal result.
4. Generate a whole-branch review package from the merge base through HEAD.
5. Because subagent delegation is not authorized in this session, read the standard code-reviewer instructions and conduct a separate self-review; explicitly report that this is weaker than an independent reviewer.
6. Fix Critical and Important findings in one RED→GREEN pass; ledger Minor findings without silently expanding scope.
7. Keep the completed feature branch and worktree until the user chooses whether to merge, push, retain, or discard it.
