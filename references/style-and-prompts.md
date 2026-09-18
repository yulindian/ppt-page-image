# Style And Prompts

Read this before style samples or final-page prompts.

## Four-Style Gate

Use this gate when neither a usable style prompt nor reference image exists, or when the user asks for style references. Waive it only with explicit authorization for autonomous style choice.

Choose one representative page with real, moderate-density copy. Generate four complete 16:9 samples using the same copy. They must differ materially in composition, palette, material, typography mood, image treatment, whitespace, and density—not merely color.

Derive directions from topic, audience, scenario, subject tone, content evidence, density, and output context. Reject generic AI-poster directions before presenting them. Compare topic fit, audience fit, readability, text capacity, multi-page extensibility, family consistency, generation stability, and repair cost. Recommend one and stop for selection.

After selection, record useful traits, user feedback, and rejected traits before planning final pages.

## Style Fingerprint And Layout Families

The fingerprint fixes palette roles, material, typography mood, image treatment, whitespace, decoration density, allowed variation, and rejected traits. It does not fix page geometry.

Choose each page layout from:

1. communication or teaching action;
2. copy density and hierarchy;
3. reading order and text-image relationship;
4. a compatible reusable layout family;
5. the shared style fingerprint.

Reuse a good family when structure and teaching action match. Change it only when it no longer serves content, hierarchy, reading order, or deck rhythm. Same-level section pages share one title system while their content areas may vary. Same-block exercise and case pages share their family invariants.

## Viewer-Perspective Gate

For every sample, pilot page, and final page, identify what the viewer notices first, second, and third. The title, question, key message, or reading task must precede supporting scenes and decoration.

Reduce or reposition supporting imagery when it steals attention through size, contrast, detail, faces, or color. A readable page still fails if the topic is visually demoted.

Review the montage as a sequence. Repeated composition is acceptable within a genuine family; it is a defect when most unrelated pages become the same text-plus-side-image pattern. Unexplained variation is also a defect inside one family.

## Anti-Generic Design Recipe

Every page concept includes:

- concrete source-grounded people, objects, actions, places, era details, quotations, or diagram logic;
- one sentence explaining why hierarchy, layout, imagery, and density serve the page goal;
- one focal element, only necessary supporting elements, and a clear decoration limit;
- a communication purpose for each major element;
- a specific editorial, textbook, archival, museum-label, field-guide, classroom-material, or children's-book language when relevant;
- plausible subject details and continuity;
- source-specific copy without generic motivational filler.

For accepted real-world cases or photographs, name the factual source, date/context, teaching purpose, and required visual fidelity. Keep documentary subjects natural and credible; do not beautify, dramatize, relocate, de-age, merge, or invent people and events in ways that change meaning. Use a real photograph because the lesson benefits from evidence, not to make every page photographic.

Remove unjustified spectacle: glow, neon rims, purple-blue gradients, glossy floating cards, excessive panels, stickers, icons, sparkles, bokeh, ornamental texture, fake authenticity, or implausible objects.

## Prompt Architecture

Read `字体说明.txt` first. Translate each font role into visible qualities such as stroke character, width, weight, contrast, spacing, alignment, and mood. Font names are repair targets; the image model may only approximate them.

Store all prompts in `风格提示词.txt` before final generation using three layers:

- **global:** theme, audience, 16:9 full-bleed format, fingerprint, typography, allowed families, active corrections, and global negatives;
- **family:** title component, typography roles, palette roles, frame language, spacing rhythm, answer or label placement, and allowed variation;
- **page:** index, goal, exact copy, focal order, content evidence, rationale, element budget, layout, reading order, subject details, and page negatives.

When a page uses an authentic photograph, its page layer also identifies the registered asset, what must remain recognizable, what transformations are permitted, and which documentary alterations are forbidden.

Every page prompt states that its layout is content-driven rather than inherited automatically from a sample or preceding page. It ends with this meaning:

```text
Create one complete edge-to-edge 16:9 presentation page image. Render the background, layout, exact title, exact body copy, illustrations, labels, and decorations together. Do not output separate layers, isolated assets, a blank background, or a page intended for later text overlay or compositing.
```

## Text And Readability

- Put locked copy in a dedicated high-contrast reading zone.
- Keep illustration zones free of incidental writing, labels, numbers, signs, posters, book text, screens, boards, packaging, and pseudo-writing. Put required labels in the controlled reading zone.
- Place prominent titles on calm fields without writing, dense objects, busy patterns, or text-like texture.
- Use short lines, clear grouping, large text, and restrained decoration for generated Chinese.
- Do not scatter dense copy through speech bubbles, stickers, windows, boards, characters, or scenery.
- Forbid watermarks, QR codes, logos, page numbers, account names, platform marks, bylines, signatures, and institutions unless locked source content explicitly requires them.
- Forbid unused borders, crop marks, blank underline placeholders, clipping, collisions, edge crowding, low contrast, and unfilled canvas.

When copy is too dense, enlarge the reading zone, simplify grouping and decoration, or split only when allowed. Never solve density with tiny text or post-generation overlays.
