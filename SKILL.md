---
name: ppt-page-image
description: Use when turning source content, reports, lesson materials, outlines, screenshots, or a topic into a polished image-based PPT delivered as PDF, especially when every page must be one complete generated image and the workflow needs style selection, prompt design, correction learning, and strict QA.
metadata:
  short-description: Create audited full-image PDF presentations
---

# PPT Page Image

Create the complete presentation workflow from content to PDF. Every final page is one integrated 16:9 image containing all visible text and visuals.

## Non-Negotiable Contract

- Generate each final page as one complete image. Do not assemble a background, text, illustration, chart, or decoration after generation.
- A flattened composite is still a composite and does not satisfy this contract.
- Repair every failed page by regenerating the whole page. Never overlay corrected text, replace a crop, patch a region, or reuse a blank background.
- Deliver only `<PPT名称>.pdf` and `字体说明.txt`. Do not include a `fonts/` folder or packaged font files. Convenience review requests may expose temporary previews in conversation but do not add PNG, prompts, reports, fonts, or PPTX to this Skill's final delivery. Treat a request for those files as a separate out-of-scope deliverable.
- Preserve exact required copy and user-fixed facts. Do not change wording, page count, or production route to hide generation problems.

## Required Skills

- **REQUIRED SUB-SKILL:** Use `imagegen` for four-style samples and every final page.
- **REQUIRED SUB-SKILL:** Use `pdf` to inspect, render back, and verify the final PDF.

## Workflow

1. Read chat requirements and all supplied materials. Load active global correction rules from `references/learned-rules.json`.
2. Read [intake and planning](references/intake-and-planning.md). Assign material roles, resolve material conflicts, build the complete page list, and lock exact visible copy.
3. Read [style and prompts](references/style-and-prompts.md). If no usable style prompt or style reference exists, generate four materially different complete 16:9 style samples, recommend one, and stop for selection. A request to hurry or avoid pauses does not waive this gate. Skip only when the user explicitly authorizes skipping the four-style selection.
4. Extract a style fingerprint from the selected sample or supplied reference. Separate style invariants from layout: keep palette roles, material, typography mood, image treatment, whitespace, and decoration density; do not carry the sample's composition or text-image split into the global style fingerprint.
5. Build the global prompt and every page prompt before final generation. Choose each page layout from its page type, teaching or communication action, information density, hierarchy, and text-image relationship before applying the style fingerprint. Reuse a proven layout family when multiple pages have compatible content structures; do not force variation for its own sake. Each page prompt includes exact copy, the chosen content-driven layout, typography direction, subject, negative constraints, and the complete-image statement.
6. Read [full-page production](references/full-page-production.md). Generate and internally audit the first five pages, or all pages when fewer than five, then create a montage and stop for approval. Continue directly only when the user explicitly requests full production without the first-five review.
7. Apply conversation corrections immediately. Read [learning and corrections](references/learning-and-corrections.md), classify scope conservatively, record persistent rules with `scripts/record_correction.py`, and regenerate every affected page in full.
8. Read [QA and delivery](references/qa-and-delivery.md). Run technical, OCR, visual, whole-deck, PDF, and delivery-folder checks. A page enters the PDF only after all applicable checks pass.
9. Package ordered pages with `scripts/images_to_pdf.py`. Render the PDF back to images and inspect it. Run `scripts/validate_delivery.py` before reporting completion.

## Stop Conditions

Stop and ask one concise question when materials conflict on content authority, audience, grade, edition, scope, or fixed page count. Stop after the four-style samples for selection and after the first-five montage for approval unless the corresponding gate was explicitly waived.

After three failed full-page generations for the same defect, stop and report the defect and possible content/layout tradeoffs. Do not switch to compositing, native text, PPTX, or local repair.

## Quick Reference

| Situation | Required action |
|---|---|
| No style prompt/reference | Four distinct complete style samples, recommendation, user selection |
| Style reference supplied | Extract style fingerprint; do not copy layout or marks |
| Selected sample uses one composition | Keep its style; reuse that layout only where the page content fits it |
| Chinese text is wrong | Regenerate the complete page |
| Text is too dense | Simplify layout or split only when permitted |
| User corrects one page | Page scope by default; regenerate affected page |
| User says “以后都要” | Record a global rule unless context clearly narrows it |
| Same defect fails three times | Stop and report; never change production route |
| Final delivery | PDF + `字体说明.txt` only |

## Common Mistakes

- Treating “最终是一张图” as permission to build it from layers.
- Skipping four style samples because the deadline is tight.
- Using a selected sample as a fixed background.
- Turning the selected sample's composition into the deck-wide default without checking whether each page's content fits it.
- Letting OCR replace visual inspection.
- Promoting a page correction into a global preference.
- Claiming exact font fidelity from an image model.
- Leaving PNG pages, prompts, previews, reports, or PPTX beside the final PDF.
- Treating “为了方便检查” as permission to expand the final delivery folder.

## Final Response

Return the delivery folder and PDF path, verified page count, confirmation that all pages are complete images, confirmation that the PDF was rendered back and inspected, and confirmation that no font package was delivered. State unresolved limitations honestly.
