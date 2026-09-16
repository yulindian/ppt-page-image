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

## Representative Pilot Gate

Generate up to five representative high-risk pages, or the whole deck when it has fewer than five. Select the pilot set in this order, without duplicating a page that satisfies multiple roles:

1. cover or primary title page;
2. mother page for the most common body family;
3. densest copy page;
4. special structure page such as process, comparison, case, map, long quotation, or worksheet;
5. mother page for the largest repeated family or highest consistency-risk family.

Run internal QA, create a montage, recommend needed fixes, then stop for approval. “继续” approves the next stage without changing approved pages. If the user explicitly authorizes full production without this pause, produce the whole deck but retain all QA gates.

The four-style and pilot gates are separate: style selection approves direction; pilot approval validates application to real content and family rules.

## State And Candidate Files

Keep one current version and at most one candidate for each page, planning file, and PDF. Use this structure during production:

```text
slides/slide-07.png
.work/candidates/slide-07.new.png
.work/project-state.json
```

The current file remains in place until the candidate opens, is 16:9, passes copy and visual checks, and is accepted. Delete failed candidates immediately. Promote a passing candidate with an atomic replacement on the same volume. Do not create `v2`, `v3`, `旧版`, `修改版`, `final-final`, backup copies, or parallel process products.

Put OCR output, montages, render-back pages, QA reports, and temporary manifests under `.work/`. Final delivery cannot include `.work/` or any process artifact.

## Pre-Generation Anti-AI Gate

Before sending any page prompt to the image model, reject it unless all answers are explicit:

- From a viewer's first glance, what should be noticed first, second, and third?
- Does the main theme, key message, question, or reading task clearly dominate over supporting scenes and decoration?
- Is this page's layout chosen because of its content type, teaching action, hierarchy, and density, rather than because the selected style sample or previous page used that geometry?
- If the page uses text plus side illustration, why is that structure necessary here, and how will nearby pages avoid mechanical repetition?
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
2. pass the pre-generation gate, then generate one complete candidate page under `.work/candidates/` with a dedicated reading zone, a text-free illustration zone, and a calm title field when applicable;
3. run technical, OCR, and visual checks on the candidate;
4. delete the candidate when any check fails;
5. mark `PASS` and promote the candidate only when every check passes;
6. refresh the family montage after accepted repairs.

Keep approved pages unchanged unless a later correction affects them. For a family defect, correct the family prompt and regenerate every affected page in full.

For a viewer-perspective failure, record a stable reason such as `THEME_DEMOTED`, `SUPPORTING_SCENE_DOMINATES`, or `LAYOUT_MONOTONY`, update the planning package with the corrected focal order and layout family, then regenerate affected pages in full. Do not keep a page simply because the text is readable when the viewing experience or deck rhythm is wrong.

## Retry Boundary

Record stable codes: `TEXT_MISMATCH`, `TEXT_UNREADABLE`, `EXTRA_TEXT`, `LAYOUT_OVERFLOW`, `STYLE_DRIFT`, `IMAGE_DEFECT`, `FULL_BLEED_FAILURE`, `DUPLICATE_PAGE`, `CONTENT_MISMATCH`, `THEME_DEMOTED`, `SUPPORTING_SCENE_DOMINATES`, and `LAYOUT_MONOTONY`.

Each retry must record the visible failure, suspected cause, changed planning or prompt condition, and result. Change at least one relevant condition before retrying: reading-zone size, copy density, visual complexity, title field, text-image relationship, family invariant, or page-specific negative constraint. Never rerun the same prompt for the same defect just to gamble on a better sample.

After three failed full-page generations for the same defect, stop. Report the failure and permitted tradeoffs such as simplifying optional copy, increasing reading space, or splitting a page when allowed. Never propose or adopt overlay text, local compositing, PPTX, or native objects.

## Rationalization Guard

| Temptation | Required response |
|---|---|
| “The final file is still one image.” | Flattening layers does not make generation compliant. |
| “Chinese is more accurate with native text.” | Regenerate the complete page and enforce the retry boundary. |
| “Only this small region is wrong.” | The whole page is the repair unit. |
| “A fixed background improves consistency.” | Use the style fingerprint and family prompts. |
| “The deadline is tight.” | Preserve required style and QA gates unless explicitly waived. |
| “Keep the old one just in case.” | Keep it only until the candidate passes, then replace it; do not deliver old versions. |
