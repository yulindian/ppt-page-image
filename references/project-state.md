# Project State

Create `.work/project-state.json` after style selection and keep it current through delivery. It is the machine-readable production source; the three planning text files remain the human-readable deliverables.

## Minimal Shape

```json
{
  "schema_version": 1,
  "deck": {"name": "课件名", "expected_pages": 2},
  "status": "PLANNING_READY",
  "families": {
    "cover": {
      "mother_page": 1,
      "pages": [1],
      "invariants": ["主题第一视觉层级", "元信息为小字"]
    },
    "body": {
      "mother_page": 2,
      "pages": [2],
      "invariants": ["统一标题组件", "独立阅读区"],
      "component_specifications": [
        {
          "name": "body_title",
          "applies_to": [2],
          "fixed": ["左上定位", "深蓝标题", "统一字号与基线"],
          "variable": ["标题文案"],
          "forbidden": ["渐变", "阴影", "另加编号徽章"]
        }
      ]
    }
  },
  "fonts": [
    {"role": "F01", "packaged_filename": "Title.ttf"},
    {"role": "F02", "packaged_filename": "Body.ttf"}
  ],
  "enrichment": [
    {
      "type": "authentic_photo",
      "status": "accepted",
      "teaching_purpose": "why it improves the lesson",
      "source": "URL or provenance",
      "verified_date": "YYYY-MM-DD",
      "rights_status": "user_supplied, official, public_domain, licensed, or restricted",
      "target_pages": [2],
      "fidelity_constraints": ["facts and documentary meaning must not change"]
    }
  ],
  "pages": [
    {
      "index": 1,
      "title": "封面",
      "visible_copy": ["课程标题"],
      "family": "cover",
      "font_roles": ["F01"],
      "prompt": "包含锁定文案的完整页面提示词",
      "qa_status": "PENDING"
    }
  ]
}
```

## Rules

- `expected_pages` equals the length of `pages`; indices are continuous from 1.
- Every page belongs to exactly one family.
- Every family names a mother page within its page list and at least one invariant.
- Every family with two or more pages defines `component_specifications`. Each specification has a stable `name`, `applies_to` covering every family page, and nonempty `fixed`, `variable`, and `forbidden` lists. Single-page families are exempt.
- `visible_copy` contains every locked audience-facing string; every item must appear verbatim in that page's prompt.
- Use no more than seven font roles. Each page references only declared roles, and every role names its packaged font file.
- Update state and affected planning files before regeneration.
- For textbook and themed class-meeting decks, record evaluated current-case and authentic-photo candidates, including rejected items when the rejection prevents a likely future mistake. Accepted items require teaching purpose, verified source/date, rights status, target pages, and fidelity constraints.
- Run `scripts/validate_project.py` at `PLANNING_READY`, after accepted corrections, and before full production.

The validator checks planning files, packaged font files, structure, component specifications, and cross-references. It does not replace editorial or visual review.
