# Style And Prompt Contract

Read this before generating style samples or final pages.

## Four-Style Gate

Trigger when neither a usable style prompt nor a usable style reference image exists, and whenever the user explicitly asks for style reference images. Waive it only when the user explicitly says to skip four-style selection and authorizes autonomous style choice.

Infer the four directions from the presentation topic, audience age and preferences, use scenario, subject character, content tone, density, and output context. Do not offer generic trends detached from the material.

Use one representative page and the same minimal real copy for all four samples. Generate four complete 16:9 page images that differ materially in composition, palette, material, typography mood, image treatment, whitespace, and visual density. Do not submit four color variants.

Evaluate topic fit, audience fit, readability, text capacity, multi-page extensibility, consistency potential, generation stability, and correction cost. Recommend the strongest direction, explain tradeoffs briefly, display all four, and stop. After selection, explain which visual traits are useful, collect the user's feedback and rejected traits, and record them before prompt planning begins.

Before presenting samples, reject any direction that still looks like a generic AI poster: interchangeable subject matter, vague luxury or dreamy styling, excessive glow or gradients, floating-card clutter, decorative icons without meaning, pseudo-writing, implausible objects, or a composition that would work unchanged after replacing the title with an unrelated topic.

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

## Viewer-Perspective Hierarchy Gate

Before accepting a style sample, planning package, first-five montage, or final deck, inspect it as a real viewer would. Ask what the eye notices first, second, and third. The page fails when the supporting illustration area, side scene, decoration, or repeated composition competes with or steals attention from the main title, key teaching point, question, or reading task.

For title-heavy pages, especially covers and section pages, the topic must dominate the first glance. Supporting scenes should frame, contextualize, or lead toward the topic; they must not occupy so much contrast, detail, face count, or color weight that the viewer studies the side illustration before understanding the lesson theme. Reduce the supporting area, simplify it, move it below, soften contrast, or choose a different layout family when the theme is visually demoted.

For a deck sequence, do not judge pages only one by one. View the montage as a learner moving through the lesson. A sequence fails when most pages resolve into the same "text block plus side illustration" pattern, even if each page is individually readable. Repeated left-text/right-image layouts are allowed only when the page types genuinely share the same structure and teaching action; otherwise choose content-specific alternatives such as centered title with surrounding evidence, top question with bottom scenarios, full-width reading field with margin vignettes, route map, comparison grid, classroom board, worksheet sheet, or scene-first page with a small controlled caption.

When a generated page reveals a layout failure, treat it as self-iteration evidence. Name the failure in the project notes, update the planning package and page prompt before regenerating, and inspect related pages for the same pattern. Do not merely ask the image model for "more variety"; specify the new hierarchy, focal order, and content-driven layout so the next generation starts smarter than the failed one.

## Anti-AI-Aesthetic Prompting

Reduce generic AI aesthetics before generation, not only during QA:

1. **Start from content evidence.** Name specific source-grounded subjects, objects, actions, relationships, era details, materials, quotations, or diagram logic. Do not invent a generic decorative scene merely to fill space.
2. **State the design rationale.** Explain in one sentence why the selected hierarchy, layout, image treatment, and density serve this page's teaching or communication goal.
3. **Set an element budget.** Prefer one focal subject, only the supporting elements needed for comprehension, and restrained decoration. Empty space is intentional and does not need to be filled.
4. **Assign every major element a purpose.** Each illustration, icon, line, texture, badge, or color block must support meaning, grouping, navigation, emphasis, or atmosphere grounded in the content. Remove elements with no stated purpose.
5. **Use concrete design references.** Describe an applicable editorial, textbook, archival, museum-label, field-guide, classroom-material, or children's-book visual language. Avoid relying on vague requests such as premium, dreamy, cinematic, magical, sophisticated, or highly polished.
6. **Use source-specific copy.** Preserve locked teaching language and remove template-like filler such as generic journey, exploration, discovery, future, or inspiration slogans unless the source or user requires it.
7. **Control finish.** Prefer coherent print-like materials, restrained lighting, limited effects, and believable depth. Avoid generic AI aesthetics such as purple-blue spectacle gradients, neon rim light, glossy floating cards, excessive rounded panels, sticker/icon scatter, sparkles, bokeh, or ornamental detail everywhere unless specifically justified.
8. **Demand plausible subject details.** Specify age, period, setting, clothing, object structure, spatial relationships, and recurring-character continuity when relevant. Do not add fake authenticity through deliberate damage or random imperfection.

The goal is not to make the page rough. The goal is to make every visible decision feel necessary, specific to the content, and consistent with a human editorial point of view.

## Prompt Shape

Before writing final prompts, read `字体说明.txt`. Convert each font role into visible typography language covering stroke character, width, weight, contrast, spacing, alignment, and mood. Font names are visual targets and repair references; the image model may only approximate them.

Store the global prompt and the full page-generation prompt outline for every page in `风格提示词.txt` before generating any final page. This mandatory prompt-outline stage follows [planning package](planning-package.md).

The global prompt states theme, audience, 16:9 full-bleed format, style invariants, typography direction, permitted layout families, active corrections, and global negative constraints. It must explicitly say that the reference composition is an optional layout family rather than a mandatory template. Build prompts with a three-layer structure: global prompt, family prompt, and page-specific differences. Store the final full prompt for each page so QA can trace it back to the planning package.

Every page prompt contains:

1. page index, type, and communication goal;
2. exact title and exact visible copy;
3. layout family and explicit text-image relationship;
4. title/body hierarchy and typography description;
5. subject, scene, actions, and mood;
6. fixed family traits and permitted variation;
7. page-specific negative constraints;
8. complete-page generation statement.

It also names the viewer's first-glance focal order, the content evidence, design rationale, element budget, purpose of each major visual element, plausible subject details, and the generic AI traits forbidden on that page. For each page, state why the chosen layout is not merely inherited from the style sample or previous page.

Always include this meaning:

```text
Create one complete 16:9 presentation page image, edge to edge. Render the background, layout, exact title, exact body copy, illustrations, labels, and decorations together in the generated image. Do not output a blank background, separate layers, isolated assets, or a page intended for later text overlay or compositing.
```

## Readability And Negative Constraints

Every body page names the relationship chosen for that page, such as left text/right image, top text/bottom image, question area/separate illustration, grid/separate explanation, or calm pale reading area with surrounding scene. Reuse a relationship when it continues to fit; do not default to one merely because it appeared in the selected sample.

Keep approved page copy in a dedicated reading zone and keep the illustration zone text-free whenever the subject does not require text. Explicitly forbid writing, labels, numbers, signs, posters, book-page text, screen UI, board writing, badges, tickets, packaging copy, and pseudo-writing inside illustrations. If a required short label belongs to the lesson content, place it in the controlled reading zone instead of embedding it casually in scenery.

When the main title is prominent, reserve a calm, high-contrast title field. The background behind it must avoid complex writing, signs, posters, dense objects, busy patterns, and text-like texture. Dense copy must never be scattered through speech bubbles, stickers, windows, boards, characters, or scenery.

- No watermark, QR code, logo, page number, account name, platform mark, byline, signature, institution name, or copyright corner.
- No pseudo-writing, garbled text, incidental labels, decorative paragraphs, or fake chart values.
- No incidental writing or text-like marks inside illustration zones.
- No complex writing, signage, dense objects, or busy text-like texture behind a prominent main title.
- No unused border, white edge, gray frame, transparent edge, crop mark, or unfilled canvas.
- No blank underline placeholder unless explicitly requested.
- No all-over collage of copy, stickers, speech bubbles, labels, answer boxes, characters, and scenery.
- No collision, clipping, edge crowding, unreadable contrast, or complex texture behind dense copy.

For generated Chinese, use large high-contrast text, short lines, clear groups, simple reading zones, and restrained decoration. Font file names are visual targets only; never claim the image model loaded a local font.
