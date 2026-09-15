# Full-Page Production

Read this before generating review or final pages.

## Definition

A compliant page is generated as one complete image in one page-generation operation. All visible text and visuals are already present in that output.

These do not comply, even when flattened later:

- generated background plus programmatic or native text;
- separately generated person, illustration, chart, title, or decoration;
- crop replacement, inpainting, local redraw, text-region patch, or overlay;
- fixed background with only the middle content replaced;
- an image-only PPTX exported to PDF as a substitute for direct PDF packaging.

Use supplied images as model references when appropriate, never as post-generation pieces.

## First-Five Gate

Generate the first five planned pages, or the whole deck when it has fewer than five. Cover the cover, a typical body page, the densest page, and a special structure when available.

Run internal QA, create a montage, recommend needed fixes, then stop for approval. “继续” approves the next stage without changing approved pages. If the user explicitly authorizes full production without this pause, produce the whole deck but retain all QA gates.

The four-style and first-five gates are separate: style selection approves direction; first-five approval validates application to real content.

## Pre-Generation Anti-AI Gate

Before sending any page prompt to the image model, reject it unless all answers are explicit:

- What specific content evidence makes this visual concept belong to this topic and audience?
- What is the one-sentence design rationale for its hierarchy, layout, imagery, and density?
- What is the element budget, and what communication purpose does every major element serve?
- Has template-like copy or generic motivational filler been removed unless it is locked source text?
- Has unnecessary decoration been removed, including unjustified glow, gradients, floating cards, stickers, icons, sparkles, and ornamental texture?
- Are people, objects, period details, spatial relationships, and recurring subjects plausible and consistent?
- Does the prompt request plausible subject details rather than vague beauty, luxury, cinematic polish, or dreaminess?
- Are typography, reading zone, text-free illustration zone, and title field described concretely?

Revise the plan and prompt before generation when any answer is missing. Do not rely on final QA to repair an under-specified concept.

## Production Loop

For each page:

1. load locked copy, style fingerprint, layout family, font-role mapping, page prompt outline, anti-AI rationale, element budget, and active corrections;
2. pass the pre-generation gate, then generate one complete page with a dedicated reading zone, a text-free illustration zone, and a calm title field when applicable;
3. run technical, OCR, and visual checks;
4. mark `PASS` only when every check passes;
5. regenerate the whole page when any check fails;
6. refresh the montage after accepted repairs.

Keep approved pages unchanged unless a later correction affects them. For a family defect, correct the family prompt and regenerate every affected page in full.

## Retry Boundary

Record stable codes: `TEXT_MISMATCH`, `TEXT_UNREADABLE`, `EXTRA_TEXT`, `LAYOUT_OVERFLOW`, `STYLE_DRIFT`, `IMAGE_DEFECT`, `FULL_BLEED_FAILURE`, `DUPLICATE_PAGE`, and `CONTENT_MISMATCH`.

After three failed full-page generations for the same defect, stop. Report the failure and permitted tradeoffs such as simplifying optional copy, increasing reading space, or splitting a page when allowed. Never propose or adopt overlay text, local compositing, PPTX, or native objects.

## Rationalization Guard

| Temptation | Required response |
|---|---|
| “The final file is still one image.” | Flattening layers does not make generation compliant. |
| “Chinese is more accurate with native text.” | Regenerate the complete page and enforce the retry boundary. |
| “Only this small region is wrong.” | The whole page is the repair unit. |
| “A fixed background improves consistency.” | Use the style fingerprint and family prompts. |
| “The deadline is tight.” | Preserve required style and QA gates unless explicitly waived. |
