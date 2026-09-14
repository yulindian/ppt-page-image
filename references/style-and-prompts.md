# Style And Prompt Contract

Read this before generating style samples or final pages.

## Four-Style Gate

Trigger when neither a usable style prompt nor a usable style reference image exists. Waive it only when the user explicitly says to skip four-style selection and authorizes autonomous style choice.

Use one representative page and the same minimal real copy for all four samples. Generate four complete 16:9 page images that differ materially in composition, palette, material, typography mood, image treatment, whitespace, and visual density. Do not submit four color variants.

Evaluate topic fit, audience fit, readability, text capacity, multi-page extensibility, consistency potential, generation stability, and correction cost. Recommend the strongest direction, explain tradeoffs briefly, display all four, and stop.

## Style Fingerprint

After selection, record palette roles, background/material, title/body typography mood, image treatment, whitespace, decoration density, allowed variation, and rejected traits. These are style invariants.

Use the selected image as a reference, not a template. Do not copy pixel geometry, exact object placement, unique characters, source text, errors, marks, watermarks, platform UI, page numbers, or distinctive protected layout. Never reuse it as a blank background.

## Style And Layout Separation

The selected sample primarily answers **how the deck looks**, not **where every page must put its content**. Its left-right split, centered hero, grid, or other page geometry may be reused as one layout family when later content has the same structural needs, but it is not the automatic global default.

For every page, choose layout in this order:

1. identify the page type and teaching or communication action;
2. measure copy density and hierarchy;
3. decide the required text-image relationship and reading order;
4. select the layout that best serves those needs, reusing a proven layout family when it remains a strong fit;
5. apply the shared style invariants to that layout.

Examples of content-driven structures include an immersive or centered cover, a path for sequential goals, a full-width grid for vocabulary, a scene map for locations, a top-bottom structure for background information, a balanced comparison for contrasts, and a spacious reading field for quotations. These are examples, not fixed mappings.

Across the page plan, assign a layout family to every page before generation. Intentionally reuse good layout families for pages with compatible structure, hierarchy, and teaching action. Repetition alone is not a defect. Change a repeated layout only when it no longer fits the content, weakens hierarchy or reading order, or makes the teaching sequence meaningfully monotonous. Consistency comes from both the style fingerprint and well-managed layout families.

## Prompt Shape

The global prompt states theme, audience, 16:9 full-bleed format, style invariants, typography direction, permitted layout families, active corrections, and global negative constraints. It must explicitly say that the reference composition is an optional layout family rather than a mandatory template.

Every page prompt contains:

1. page index, type, and communication goal;
2. exact title and exact visible copy;
3. layout family and explicit text-image relationship;
4. title/body hierarchy and typography description;
5. subject, scene, actions, and mood;
6. fixed family traits and permitted variation;
7. page-specific negative constraints;
8. complete-page generation statement.

Always include this meaning:

```text
Create one complete 16:9 presentation page image, edge to edge. Render the background, layout, exact title, exact body copy, illustrations, labels, and decorations together in the generated image. Do not output a blank background, separate layers, isolated assets, or a page intended for later text overlay or compositing.
```

## Readability And Negative Constraints

Every body page names the relationship chosen for that page, such as left text/right image, top text/bottom image, question area/separate illustration, grid/separate explanation, or calm pale reading area with surrounding scene. Reuse a relationship when it continues to fit; do not default to one merely because it appeared in the selected sample. Dense copy must not be scattered through signs, speech bubbles, stickers, windows, boards, characters, or scenery.

- No watermark, QR code, logo, page number, account name, platform mark, byline, signature, institution name, or copyright corner.
- No pseudo-writing, garbled text, incidental labels, decorative paragraphs, or fake chart values.
- No unused border, white edge, gray frame, transparent edge, crop mark, or unfilled canvas.
- No blank underline placeholder unless explicitly requested.
- No all-over collage of copy, stickers, speech bubbles, labels, answer boxes, characters, and scenery.
- No collision, clipping, edge crowding, unreadable contrast, or complex texture behind dense copy.

For generated Chinese, use large high-contrast text, short lines, clear groups, simple reading zones, and restrained decoration. Font file names are visual targets only; never claim the image model loaded a local font.
