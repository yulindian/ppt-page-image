# Project State

Schema v2 uses the external workspace `project-state.json` as the only editable planning authority. Generate the three human-readable planning files from it; never maintain four independent copies of the same plan.

## Required Top-Level Shape

```json
{
  "schema_version": 2,
  "deck": {
    "name": "课件名",
    "expected_pages": 2,
    "audience": "中小学生",
    "scenario": "主题班会",
    "language": "简体中文",
    "source_authority": "用户提供材料",
    "content_scope": "本次课件范围",
    "assumptions": []
  },
  "status": "PLANNING_READY",
  "style": {
    "summary": "选定风格",
    "user_feedback": "用户确认与调整",
    "useful_traits": ["保留特征"],
    "rejected_traits": ["拒绝特征"],
    "fingerprint": "色彩、材质、图像和留白指纹",
    "palette_roles": {"background": "暖米白", "primary": "深蓝"},
    "material": "纸张质感",
    "image_treatment": "自然手绘",
    "whitespace": "充足",
    "decoration_density": "低",
    "permitted_variation": ["内容区随教学动作变化"],
    "typography_direction": "清晰且可修复",
    "global_prompt": "完整全局提示词",
    "global_negatives": ["水印", "伪文字"]
  },
  "fonts": [],
  "enrichment": [],
  "families": {},
  "pages": [],
  "reviews": {
    "pilot": {"status": "pending", "pages": []},
    "families": {},
    "deck": {"status": "pending"},
    "render": {"status": "pending"}
  },
  "delivery": {"deck_name": "课件名", "images": []}
}
```

## Fonts

Each font entry requires:

```json
{
  "role": "F01",
  "display_name": "Noto Sans SC",
  "weight": "Regular",
  "source_path": "C:/Windows/Fonts/NotoSansSC-Regular.otf",
  "packaged_filename": "NotoSansSC-Regular.otf",
  "fallback": "Microsoft YaHei",
  "visual_traits": "清晰无衬线、字面开阔",
  "license_status": "redistributable"
}
```

Use no more than seven unique roles. `packaged_filename` is a plain `.ttf`, `.otf`, or `.ttc` filename and must exist under workspace `fonts/`.

## Families

Every page belongs to exactly one family. Each family has `mother_page`, `pages`, and nonempty `invariants`. A family with two or more pages also has `component_specifications`; every specification contains `name`, `applies_to`, and nonempty `fixed`, `variable`, and `forbidden` lists.

## Pages

Every page requires:

- `index`, `type`, `goal`, `title`, `family`, and `density_risk`;
- nonempty `visible_copy`; no empty string is allowed;
- `required_facts`, `source_notes`, and `content_evidence` lists;
- `design_rationale` and `element_budget` with `focal`, `supporting`, and `decoration_limit`;
- `reading_order`, `zones`, `visual_subject`, and `image_text_relationship`;
- nonempty declared `font_roles` and `negative_constraints`;
- a complete `prompt` containing every locked-copy item and every declared font-role token;
- `qa_status` from `PENDING`, `REVIEWED`, `PASS`, or `FAIL`;
- a `defects` list.

After a page is accepted for production it also has:

```json
{
  "current_image": "slides/slide-1.png",
  "image_sha256": "sha256 of the current approved page"
}
```

The path must remain inside the workspace and the hash must match the current file.

## Reviews And Gates

Run:

```powershell
python -X utf8 scripts/validate_project.py --state <workspace>/project-state.json --workspace <workspace> --gate planning
python -X utf8 scripts/validate_project.py --state <workspace>/project-state.json --workspace <workspace> --gate pilot
python -X utf8 scripts/validate_project.py --state <workspace>/project-state.json --workspace <workspace> --gate production
python -X utf8 scripts/validate_project.py --state <workspace>/project-state.json --workspace <workspace> --gate delivery
```

- `planning` requires `PLANNING_READY` or later, exact generated planning files, valid fonts, complete pages, and valid prompts.
- `pilot` requires `PILOT_APPROVED` or later and `reviews.pilot` with `status: pass`, a nonempty page list, and the same `reviewed_pages` list.
- `production` requires `FULL_PRODUCTION` or later, the pilot evidence, current page images, matching hashes, and page QA of `PASS` or `REVIEWED`.
- `delivery` requires `DELIVERY_READY`, every page `PASS`, every repeated-family review `pass` with hashes matching current members, and passing whole-deck and render reviews.

A content correction returns the state to `PLANNING_READY`. A visual correction returns it to the earliest affected production status and invalidates downstream review evidence.

## Schema v1 Compatibility

Schema-v1 projects remain readable with:

```powershell
python -X utf8 scripts/validate_project.py --state <state> --project-dir <legacy-project-dir>
```

Their result contains `"schema_version": 1` and `"legacy": true`. This preserves inspection of old projects but does not claim schema-v2 planning, pilot, production, or delivery-gate coverage.
