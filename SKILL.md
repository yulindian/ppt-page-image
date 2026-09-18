---
name: ppt-page-image
description: Use when source material, lesson content, reports, outlines, screenshots, or a topic must become a reviewed image-based presentation PDF rather than an editable PPTX.
metadata:
  short-description: Create audited full-image PDF presentations
---

# PPT Page Image

Create a presentation whose pages are complete 16:9 images and whose final artifact is a verified PDF.

## Production Contract

- Generate every page as one complete image containing all visible text and visuals. A flattened composition assembled from separate layers does not qualify.
- Repair by regenerating the complete page. Never overlay text, patch a region, replace a crop, or switch to native PPT objects.
- Preserve locked copy, facts, page count, and user corrections. If fixed copy and fixed page count cannot remain readable together, stop and ask which constraint may change.
- Finish the planning package before final-page generation: `PPT内容大纲.txt`, `风格提示词.txt`, `字体说明.txt`, and a nonempty `fonts/` package.
- Deliver PDF, the three planning files, and `fonts/`. Add `images/` only for useful retained repair or source assets. Do not deliver PPTX unless separately requested.

**REQUIRED SUB-SKILL:** Use `imagegen` for style samples and all page images.

**REQUIRED SUB-SKILL:** Use `pdf` to inspect and verify the final PDF.

## Workflow

1. Read all materials and list active rules with `scripts/record_correction.py list-active --store references/learned-rules.json`. Read [intake and planning](references/intake-and-planning.md), assign source roles, resolve conflicts, lock exact copy, and define the ordered page list. For textbook lessons and themed class meetings, also evaluate relevant current cases and authentic-photo opportunities before layout planning.
2. Read [style and prompts](references/style-and-prompts.md). If no usable style reference or prompt exists, generate four materially different complete-page samples from the same representative content, recommend one, and stop for selection. Skip only when the user explicitly authorizes autonomous style choice.
3. After selection, record useful traits, rejected traits, and a style fingerprint. Treat composition as an optional layout family, not a deck-wide template.
4. Read [planning package](references/planning-package.md). Create the three planning files, package fonts, group all pages into layout families, and create `.work/project-state.json` from [project state](references/project-state.md). Run `scripts/validate_project.py` before generating final pages.
5. Read [full-page production](references/full-page-production.md). Generate and internally review up to five representative high-risk pages: cover, common-family mother page, densest page, special-structure page, and largest repeat-family mother page. Show a montage and stop for approval unless the user waived this gate.
6. Generate remaining pages. A candidate replaces the current page only after technical, copy, visual, and family checks pass. Keep process output under `.work/`.
7. Read [QA and delivery](references/qa-and-delivery.md). Audit pages, page families, and the whole-deck montage. Package only passing pages into a candidate PDF.
8. Render the candidate PDF back with `scripts/render_pdf.py`, inspect every rendered page and montage, then record inspection as `pass`. Promote the PDF only after this check.
9. Run `scripts/validate_delivery.py` with the matching render-back report. Clean process artifacts from the delivery folder and validate again before reporting completion.

## Project State

Track production in `.work/project-state.json`; do not deliver it. Use these states:

```text
INTAKE → STYLE_SAMPLING → STYLE_SELECTED → PLANNING_READY
→ PILOT_REVIEW → PILOT_APPROVED → FULL_PRODUCTION
→ QA → PDF_RENDER_CHECK → DELIVERY_READY
```

The state file records deck name, page count, every page's locked copy and prompt, font roles, page-family membership, mother pages, family invariants, and QA status. A content correction returns the project to `PLANNING_READY`; a visual repair returns it to the earliest affected production state.

For textbook and themed class-meeting decks, record accepted or rejected enrichment candidates: teaching relevance, verified facts, date, source, rights status, target pages, and whether an authentic photo is used as a generation reference. Current events and real photos are evidence, not decoration; omit them when they do not improve comprehension, transfer, discussion, or credibility.

## Page Families

Classify at least covers, section dividers, teaching activities, repeated exercises, and repeated case-analysis pages. Each family defines a mother page and shared title component, typography roles, palette roles, frame language, spacing rhythm, and answer or label placement.

Reuse a family when content structure and teaching action match. Change layout when repetition harms hierarchy, reading order, or deck rhythm. Same-level section pages share a title system while their content areas may vary. Same-block exercise pages share one worksheet family; place short answers, checks, and crosses directly in the intended blank or parentheses.

## Prompt And Visual Gates

Every page prompt must state:

- exact visible copy and font-role tokens;
- first, second, and third viewer focal points;
- content evidence and one-sentence design rationale;
- an element budget and purpose for every major element;
- layout family, reading order, and text-image relationship;
- a dedicated reading zone, text-free illustration zone, and calm title field when needed;
- page-specific negative constraints;
- that the output is one complete edge-to-edge 16:9 presentation page image.

Reject prompts or pages that rely on generic spectacle, template slogans, purposeless decoration, pseudo-writing, incidental labels, implausible details, busy title backgrounds, or supporting scenes that overpower the topic.

## Corrections And Retry Boundary

Read [learning and corrections](references/learning-and-corrections.md) whenever the user corrects content, style, layout, QA, or delivery. Record persistent rules with `scripts/record_correction.py`, update every affected planning artifact first, then regenerate complete affected pages.

Default correction scope is the named page. Expand to the complete family when the complaint concerns consistency. Keep unrelated approved pages unchanged.

For every failed generation, record a stable defect code, visible problem, suspected cause, changed planning or prompt condition, and result. Never retry an identical prompt for the same defect. Stop after three failures of the same defect and report permitted content or layout tradeoffs; never switch to compositing as a workaround.

## Delivery Commands

```powershell
python scripts/validate_project.py --state .work/project-state.json --project-dir <project-dir>
python scripts/images_to_pdf.py --slides-dir <slides-dir> --out .work/<name>.candidate.pdf --expected-pages <N>
python scripts/render_pdf.py --pdf .work/<name>.candidate.pdf --out-dir .work/render-back --expected-pages <N>
# Inspect every rendered page and montage, then rerun against the promoted PDF with an inspection record.
python scripts/render_pdf.py --pdf <delivery>/<name>.pdf --out-dir .work/render-back-final --expected-pages <N> --inspection pass --notes "Inspected every page and montage"
python scripts/validate_delivery.py --delivery-dir <delivery> --deck-name <name> --expected-pages <N> --render-report .work/render-back-final/render-back-report.json
```

Use quality 92–95 for dense text. Use `--mode lossless` when JPEG compression visibly damages text or thin lines.

## Final Response

Link the delivery folder, PDF, three planning files, `fonts/`, and optional `images/`. State the verified page count, confirm that every page is one complete image, and confirm PDF render-back inspection. State unresolved limitations honestly: packaged fonts are repair resources and visual targets, not proof that the image model rendered those exact fonts.
