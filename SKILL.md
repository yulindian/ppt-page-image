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

## Workflow

1. Read chat requirements and all supplied materials. Load active global correction rules from `references/learned-rules.json`.
2. Read [intake and planning](references/intake-and-planning.md). Assign material roles, resolve material conflicts, build the complete page list, and lock exact visible copy.
3. Read [style and prompts](references/style-and-prompts.md). When no usable style reference exists, or the user asks for style reference images, infer four suitable directions from the topic, audience, scenario, subject tone, content evidence, and density. Generate four materially different complete 16:9 samples, reject generic AI aesthetics before presenting them, recommend one, and stop for selection. Skip only when the user explicitly authorizes autonomous style choice without samples.
4. After selection, explain the useful traits, collect the user's feedback and rejected traits, then extract a style fingerprint. Keep palette roles, material, typography mood, image treatment, whitespace, and decoration density; do not turn the sample's composition into a deck-wide template.
5. Read [planning package](references/planning-package.md). Create and cross-check `PPT内容大纲.txt`, `风格提示词.txt`, and `字体说明.txt`; package selected fonts in `fonts/`, and prepare optional `images/`. For every page record its design rationale, content evidence, element budget, and generic AI traits to avoid. This stage is mandatory and happens before final-page generation.
6. Build the global prompt and every page prompt from the planning package. Each prompt carries exact copy, a content-driven layout, font-role wording from `字体说明.txt`, concrete subject and editorial references, the purpose of every major element, a restrained element budget, a dedicated reading zone, a text-free illustration zone, a calm title field when the main title is prominent, anti-AI-aesthetic constraints, and the complete-image statement. Reuse a proven layout family when it fits; do not force variation for its own sake.
7. Read [full-page production](references/full-page-production.md). Apply the pre-generation anti-AI gate before generation, then generate and internally audit the first five pages, or all pages when fewer than five. Create a montage and stop for approval. Continue directly only when the user explicitly requests full production without the first-five review.
8. Apply conversation corrections immediately. Read [learning and corrections](references/learning-and-corrections.md), classify scope conservatively, record persistent rules with `scripts/record_correction.py`, update every affected planning file, and regenerate every affected page in full.
9. Read [QA and delivery](references/qa-and-delivery.md). Run planning-package, font-package, asset, technical, OCR, visual, whole-deck, PDF, and delivery-folder checks. A page enters the PDF only after all applicable checks pass.
10. Package ordered pages with `scripts/images_to_pdf.py`. Render the PDF back to images and inspect it. Run `scripts/validate_delivery.py` before reporting completion.

## Stop Conditions

Stop and ask one concise question when materials conflict on content authority, audience, grade, edition, scope, or fixed page count. Stop after the four-style samples for selection and after the first-five montage for approval unless the corresponding gate was explicitly waived.

After three failed full-page generations for the same defect, stop and report the defect and possible content/layout tradeoffs. Do not switch to compositing, native text, PPTX, or local repair.

## Quick Reference

| Situation | Required action |
|---|---|
| No style prompt/reference, or user asks for references | Infer from topic and audience; show four distinct complete samples; recommend and stop for selection |
| Style reference supplied | Extract style fingerprint; do not copy layout or marks |
| Style selected | Record selection feedback and rejected traits before writing the planning package |
| Selected sample uses one composition | Keep its style; reuse that layout only where the page content fits it |
| Prompt-outline stage | Produce and cross-check all three planning `.txt` files before generating pages |
| Page looks generically "AI polished" | Strengthen content evidence, design rationale, element purpose, and restraint before generation |
| Illustration contains text-like detail | Regenerate with a dedicated text-free illustration zone |
| Prominent main title | Use a calm, clean background without writing, signs, or busy text-like detail |
| Chinese text is wrong | Regenerate the complete page |
| Text is too dense | Simplify layout or split only when permitted |
| User corrects one page | Page scope by default; regenerate affected page |
| User says “以后都要” | Record a global rule unless context clearly narrows it |
| Same defect fails three times | Stop and report; never change production route |
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
- Allowing incidental writing, labels, signs, book text, or screen text inside illustrations.
- Putting a prominent title over a busy background or text-like texture.
- Letting OCR replace visual inspection.
- Promoting a page correction into a global preference.
- Claiming exact font fidelity from an image model.
- Omitting the selected font files needed for later repair.
- Treating a font name as proof that the image model rendered that exact font.

## Final Response

Return links to the delivery folder, PDF, three planning files, `fonts/`, and optional `images/`; state the verified page count, confirm that all pages are complete images, and confirm that the PDF was rendered back and inspected. State unresolved limitations honestly, including that packaged fonts are repair resources and visual targets rather than proof of exact font rendering by the image model.
