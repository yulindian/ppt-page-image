# Planning Package

Create this package after style selection and before final-page generation. It is both the production source of truth and part of the final delivery.

## Required Order

1. Finalize the ordered page list and lock exact visible copy.
2. Record the selected style, the user's feedback, useful traits, and rejected traits.
3. Inspect available local fonts and choose repairable font roles.
4. Write and cross-check the three planning files and `.work/project-state.json`.
5. Package selected fonts and any useful retained images.
6. Generate pages only after the package is internally consistent.

## PPT内容大纲.txt

Start with PPT name, audience, scenario, language, page count, source authority, content scope, style selection, and important assumptions. For every page record:

- page index, page type, communication or teaching goal;
- exact title and exact visible copy;
- required facts and source notes;
- accepted hotspot or real-world case with date, verified source, teaching purpose, and target wording when applicable;
- content evidence: specific people, objects, places, actions, era details, quotations, diagrams, or material traits that justify the visual concept;
- design rationale: one concise reason why this hierarchy, layout, imagery, and density serve the page's teaching or communication goal;
- element budget: one focal element, the minimum supporting elements, and the decoration limit;
- layout family, reading order, and density risk;
- separate text, illustration, and decoration zones;
- visual subject and image-text relationship;
- authentic-photo asset, fidelity requirement, permitted treatment, and documentary constraints when applicable;
- title and body font-role tokens that map to `字体说明.txt`;
- page-specific negative constraints.
- generic AI traits to avoid on this page, including irrelevant glow, gradient spectacle, floating cards, decorative icons, sticker clutter, template-like slogans, and implausible details.

## 风格提示词.txt

Include:

- selected style summary, user feedback, useful traits, and rejected traits;
- palette roles, material, image treatment, whitespace, decoration density, and permitted variation;
- typography direction with explicit references to the roles in `字体说明.txt`;
- layout families and the rules for reusing them without fixing one composition globally;
- illustration/text separation and the quiet-background rule for prominent titles;
- asset inventory for every retained item in `images/`, including source, purpose, and page use;
- for current cases and authentic photos: verification date, source URL or provenance, rights status, teaching rationale, fidelity requirement, and forbidden alterations;
- one reusable global prompt;
- a page-generation prompt outline for every page;
- the anti-AI-aesthetic rules, including content evidence, design rationale, element budget, element-purpose statements, and banned generic AI traits;
- global negative constraints and prompt self-checks.

Every page-generation prompt outline must carry the exact copy, font-role wording, layout and reading order, content evidence, design rationale, element budget, the purpose of every major visual element, separate text and text-free illustration zones, visual subject, page-specific negatives, and the complete-page generation statement.

## 字体说明.txt

Create this file before image generation so typography guides the prompts instead of being documented after the fact. Include:

- font-selection rationale and local font inspection result;
- display name, weight, local source path, packaged filename, and fallback for each selected font;
- role mappings for cover title, section title, body, quotation, annotation, English, pinyin, numerals, and formulas as applicable;
- page-by-page or line-by-line mapping for all audience-facing text;
- visible typography wording used in prompts, such as stroke character, width, contrast, spacing, and alignment;
- licensing or redistribution notes and repair guidance;
- notice that the image model approximates the requested typography.

Use no more than seven tracked font roles. Add a decorative role only when it materially improves hierarchy and has a packageable local font or realistic editable substitute.

## fonts/

The folder is mandatory and nonempty. Package selected, locally available `.ttf`, `.otf`, or `.ttc` files when redistribution is permitted. Replace unavailable or nonredistributable choices with a suitable packageable font and update all three planning files. Packaged fonts support later repair and are visual targets; they do not prove that the image model loaded the exact font.

## images/

This folder is optional. Use it only for concrete source images, selected style samples, references, or retained full-page images that materially help later repair. When present it must be nonempty, and every item must be listed in `风格提示词.txt` with source, role, and page use.

When an authentic photograph is used in generation, retain it in `images/` when rights permit and register its provenance, rights status, teaching purpose, target page, and fidelity constraints. If redistribution is not permitted, do not package the file; record the source and limitation instead.

## Cross-Check

Before generation and after every accepted correction, verify that page count, page titles, exact copy, style choices, font-role tokens, packaged filenames, asset names, and per-page prompts agree across all three files. Update the planning package before regenerating affected pages.

`PPT内容大纲.txt` is the human-readable authority for page order, page count, exact audience-facing copy, and page families. `风格提示词.txt` and `字体说明.txt` must derive from it. Mirror those invariants in `.work/project-state.json` using [project state](project-state.md), run `scripts/validate_project.py`, and do not deliver the state file.
