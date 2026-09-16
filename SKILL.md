---
name: ppt-page-image
description: Use when turning source content, reports, lesson materials, outlines, screenshots, or a topic into a planned and audited image-based presentation package with content outline, style prompts, font resources, complete generated pages, and a final PDF.
metadata:
  short-description: Create audited full-image PDF presentations
---

# PPT Page Image

Create the complete presentation workflow from content to PDF. Every final page is one integrated 16:9 image containing all visible text and visuals.

## Non-Negotiable Contract

- Generate each final page as one complete image. Do not assemble a background, text, illustration, chart, or decoration after generation.
- A flattened composite is still a composite and does not satisfy this contract.
- Repair every failed page by regenerating the whole page. Never overlay corrected text, replace a crop, patch a region, or reuse a blank background.
- Complete the planning package before page production: `PPT内容大纲.txt`, `风格提示词.txt`, and `字体说明.txt` are mandatory production inputs and final deliverables.
- Deliver `<PPT名称>.pdf`, the three planning files, and a nonempty `fonts/` package. Include `images/` only when retained source or repair assets are useful. Do not deliver PPTX unless the user separately requests it.
- Preserve exact required copy and user-fixed facts. Do not change wording, page count, or production route to hide generation problems.

## Required Skills

- **REQUIRED SUB-SKILL:** Use `imagegen` for four-style samples and every final page.
- **REQUIRED SUB-SKILL:** Use `pdf` to inspect, render back, and verify the final PDF.

## Model Role Guidance

Use the strongest available planning model for intake, family planning, prompt architecture, QA reasoning, and final judgment. Prefer `gpt-5.6-sol` with high reasoning when available. Use lighter models only for bounded prompt drafting, inventory, or mechanical review. Generate and edit raster pages through `imagegen`; do not describe image creation as being performed by `gpt-5.5` or any other text model, and do not hard-code near-retirement models into the workflow.

## Workflow

1. Read chat requirements and all supplied materials. Load active global correction rules from `references/learned-rules.json`.
2. Read [intake and planning](references/intake-and-planning.md). Assign material roles, resolve material conflicts, build the complete page list, and lock exact visible copy.
3. Read [style and prompts](references/style-and-prompts.md). When no usable style reference exists, or the user asks for style reference images, infer four suitable directions from the topic, audience, scenario, subject tone, content evidence, and density. Generate four materially different complete 16:9 samples, reject generic AI aesthetics before presenting them, recommend one, and stop for selection. Skip only when the user explicitly authorizes autonomous style choice without samples.
4. After selection, explain the useful traits, collect the user's feedback and rejected traits, then extract a style fingerprint. Keep palette roles, material, typography mood, image treatment, whitespace, and decoration density; do not turn the sample's composition into a deck-wide template.
5. Read [planning package](references/planning-package.md). Create and cross-check `PPT内容大纲.txt`, `风格提示词.txt`, and `字体说明.txt`; package selected fonts in `fonts/`, and prepare optional `images/`. For every page record its design rationale, content evidence, element budget, and generic AI traits to avoid. This stage is mandatory and happens before final-page generation.
6. Build the global prompt and every page prompt from the planning package. Each prompt carries exact copy, a content-driven layout, font-role wording from `字体说明.txt`, concrete subject and editorial references, the purpose of every major element, a restrained element budget, a dedicated reading zone, a text-free illustration zone, a calm title field when the main title is prominent, anti-AI-aesthetic constraints, and the complete-image statement. Reuse a proven layout family when it fits; do not force variation for its own sake. For same-family pages such as exercise sets, repeated teaching segments, or similarly structured activity pages, keep the title treatment, title scale, frame language, spacing rhythm, and answer placement consistent unless the content genuinely requires a different structure. For same-level teaching section or chapter-navigation pages, keep one title component system across the set: section label treatment, main-title scale, placement, decorative rules, and title-to-content spacing should match, while the content area may vary by teaching action. For lesson covers, separate metadata from the lesson title: put edition/year, grade/book, unit, lesson, and period in a deliberate hierarchy, with low-importance curriculum metadata as a small one-line annotation and the current lesson/period title as the visual focus.
7. Before generating related pages, group the page list into reusable template families. At minimum classify covers, chapter/section dividers, teaching activities, same-format exercises, and same-format case-analysis pages. Record the family name and shared layout rules in `PPT内容大纲.txt`, then make every page prompt in that family inherit the same title component, typography roles, color roles, frame/card language, spacing rhythm, and answer/label placement. This family pass is required whenever the user comments that pages are the same structure, same level, same style, or should be similar.
8. Read [full-page production](references/full-page-production.md). Apply the pre-generation anti-AI gate before generation, then generate and internally audit up to five representative high-risk pages: cover, common-family mother page, densest page, special-structure page, and largest repeat-family page. Create a montage and stop for approval. Continue directly only when the user explicitly requests full production without the pilot review.
9. Maintain one current version and at most one candidate per page, planning file, or PDF. Put candidates, OCR, montages, render-back output, reports, and project state under `.work/`. Failed candidates are deleted; passing candidates replace the current file only after checks pass. Do not create `v2`, `v3`, `旧版`, `修改版`, `final-final`, backup, or parallel process-product files.
10. Apply conversation corrections immediately. Read [learning and corrections](references/learning-and-corrections.md), classify scope conservatively, record persistent rules with `scripts/record_correction.py`, update every affected planning file, and regenerate every affected page in full. When the user flags inconsistency across same-block pages, expand the repair scope to the whole page family rather than only the shown page; choose one mother page or template family, lock its shared layout invariants, and regenerate all affected pages against those invariants.
11. Read [QA and delivery](references/qa-and-delivery.md). Run planning-package, font-package, asset, technical, OCR, visual, whole-deck, PDF, and delivery-folder checks. A page enters the PDF only after all applicable checks pass. Include a family-consistency audit for grouped pages: compare related pages side by side for title hierarchy, font mood, color roles, card sizes, answer placement, and overall rhythm before packaging. After repairing a same-block inconsistency, make a side-by-side montage or PDF render-back montage of the affected page family before delivery.
12. Package ordered pages with `scripts/images_to_pdf.py --expected-pages <N>` into a candidate PDF under `.work/`. Render the candidate PDF back to images and inspect it. Promote it to the final PDF only after checks pass, then run `scripts/validate_delivery.py --expected-pages <N>` before reporting completion.

## Stop Conditions

Stop and ask one concise question when materials conflict on content authority, audience, grade, edition, scope, or fixed page count. Stop after the four-style samples for selection and after the representative pilot montage for approval unless the corresponding gate was explicitly waived.

Each failed generation must produce information: record the defect code, visible problem, suspected cause, changed planning or prompt condition, and result. Do not retry an identical prompt for the same defect. After three failed full-page generations for the same defect, stop and report the defect and possible content/layout tradeoffs. Do not switch to compositing, native text, PPTX, or local repair.

## Quick Reference

| Situation | Required action |
|---|---|
| No style prompt/reference, or user asks for references | Infer from topic and audience; show four distinct complete samples; recommend and stop for selection |
| Style reference supplied | Extract style fingerprint; do not copy layout or marks |
| Style selected | Record selection feedback and rejected traits before writing the planning package |
| Selected sample uses one composition | Keep its style; reuse that layout only where the page content fits it |
| Lesson cover with edition/unit/lesson/period metadata | Put edition/year first, then unit, lesson, and period in order; keep metadata as a small annotation and make the current lesson or period title dominant |
| Same-family exercise or activity pages | Keep title style, title size, frame style, spacing rhythm, and answer placement consistent |
| Choice, fill-in, judgment, or short-answer pages in one exercise set | Use one worksheet family: same title component, body font mood, body color, option spacing, margins, and answer color logic |
| Same-format case-analysis pages | Use one case-analysis family: same title position/scale, illustration-to-text proportion, panel style, card count, card colors, label treatment, and line spacing |
| Same-level teaching section pages | Unify the section-title component and hierarchy; vary only the content area according to teaching action |
| User says pages are “同一种结构/同一层次/排版相近/风格相近” | Update the planning outline to define the shared family rules, then regenerate every affected page in full |
| User reports same-block pages still look different | Repair the complete related page family: pick a mother page, lock layout invariants, regenerate all affected pages, and inspect them in one montage |
| Exercise answers fit in blanks or parentheses | Put answers directly in the blank or parentheses, including check/cross marks, instead of using a detached answer strip |
| Prompt-outline stage | Produce and cross-check all three planning `.txt` files before generating pages |
| Page looks generically "AI polished" | Strengthen content evidence, design rationale, element purpose, and restraint before generation |
| Illustration contains text-like detail | Regenerate with a dedicated text-free illustration zone |
| Prominent main title | Use a calm, clean background without writing, signs, or busy text-like detail |
| Chinese text is wrong | Regenerate the complete page |
| Text is too dense | Simplify layout or split only when permitted |
| User corrects one page | Page scope by default; regenerate affected page |
| User says “以后都要” | Record a global rule unless context clearly narrows it |
| Same defect fails three times | Stop and report; never change production route |
| Making a newer version | Generate one candidate under `.work/`; delete it if it fails, or promote it over the current file if it passes |
| Temporary review output | Keep it under `.work/`; remove it before final delivery |
| Planning and QA model choice | Prefer `gpt-5.6-sol` high for architecture and judgment; use `imagegen` for actual raster generation |
| Final delivery | PDF + three planning files + nonempty `fonts/` + optional useful `images/` |

## Common Mistakes

- Treating “最终是一张图” as permission to build it from layers.
- Skipping four style samples because the deadline is tight.
- Skipping the prompt-outline stage and improvising prompts page by page.
- Using vague style words such as premium, dreamy, cinematic, or sophisticated without content-specific design evidence.
- Adding glow, gradients, floating cards, stickers, icons, or characters without a communication purpose.
- Keeping template-like filler copy such as “开启探索之旅” when it is not required source text.
- Using a selected sample as a fixed background.
- Turning the selected sample's composition into the deck-wide default without checking whether each page's content fits it.
- Over-diversifying pages that belong to the same exercise set, lesson segment, or repeated activity structure.
- Making same-level section pages look like unrelated templates, or over-correcting by forcing their entire content layouts to be identical.
- Treating choice questions, judgment questions, and case-analysis questions as unrelated designs when they are part of the same exercise block.
- Letting one page in a family use a different brush title, font mood, body color, or card rhythm because it was generated in a separate pass.
- Fixing only the screenshot page after a same-block consistency complaint, instead of repairing and comparing the complete related page family.
- Giving cover metadata the same visual weight as the lesson/period title, or stacking low-importance metadata as multiple prominent subtitle lines.
- Using separate answer bars when the exercise format has blanks or parentheses intended to hold the answer.
- Allowing incidental writing, labels, signs, book text, or screen text inside illustrations.
- Putting a prominent title over a busy background or text-like texture.
- Letting OCR replace visual inspection.
- Promoting a page correction into a global preference.
- Claiming exact font fidelity from an image model.
- Omitting the selected font files needed for later repair.
- Treating a font name as proof that the image model rendered that exact font.

## Final Response

Return links to the delivery folder, PDF, three planning files, `fonts/`, and optional `images/`; state the verified page count, confirm that all pages are complete images, and confirm that the PDF was rendered back and inspected. State unresolved limitations honestly, including that packaged fonts are repair resources and visual targets rather than proof of exact font rendering by the image model.
