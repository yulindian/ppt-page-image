# Planning Package

Create this package after style selection and before final-page generation. It is both the production source of truth and part of the final delivery.

## Required Order

1. Finalize the ordered page list and lock exact visible copy.
2. Record the selected style, the user's feedback, useful traits, and rejected traits.
3. Inspect available local fonts and choose repairable font roles.
4. Write and cross-check the three planning files.
5. Package selected fonts and any useful retained images.
6. Generate pages only after the package is internally consistent.

## PPT内容大纲.txt

Start with PPT name, audience, scenario, language, page count, source authority, content scope, style selection, and important assumptions. For every page record:

- page index, page type, communication or teaching goal;
- exact title and exact visible copy;
- required facts and source notes;
- layout family, reading order, and density risk;
- separate text, illustration, and decoration zones;
- visual subject and image-text relationship;
- title and body font-role tokens that map to `字体说明.txt`;
- page-specific negative constraints.

## 风格提示词.txt

Include:

- selected style summary, user feedback, useful traits, and rejected traits;
- palette roles, material, image treatment, whitespace, decoration density, and permitted variation;
- typography direction with explicit references to the roles in `字体说明.txt`;
- layout families and the rules for reusing them without fixing one composition globally;
- illustration/text separation and the quiet-background rule for prominent titles;
- asset inventory for every retained item in `images/`, including source, purpose, and page use;
- one reusable global prompt;
- a page-generation prompt outline for every page;
- global negative constraints and prompt self-checks.

Every page-generation prompt outline must carry the exact copy, font-role wording, layout and reading order, separate text and text-free illustration zones, visual subject, page-specific negatives, and the complete-page generation statement.

## 字体说明.txt

Create this file before image generation so typography guides the prompts instead of being documented after the fact. Include:

- font-selection rationale and local font inspection result;
- display name, weight, local source path, packaged filename, and fallback for each selected font;
- role mappings for cover title, section title, body, quotation, annotation, English, pinyin, numerals, and formulas as applicable;
- page-by-page or line-by-line mapping for all audience-facing text;
- visible typography wording used in prompts, such as stroke character, width, contrast, spacing, and alignment;
- licensing or redistribution notes and repair guidance;
- notice that the image model approximates the requested typography.

## fonts/

The folder is mandatory and nonempty. Package selected, locally available `.ttf`, `.otf`, or `.ttc` files when redistribution is permitted. Replace unavailable or nonredistributable choices with a suitable packageable font and update all three planning files. Packaged fonts support later repair and are visual targets; they do not prove that the image model loaded the exact font.

## images/

This folder is optional. Use it only for concrete source images, selected style samples, references, or retained full-page images that materially help later repair. When present it must be nonempty, and every item must be listed in `风格提示词.txt` with source, role, and page use.

## Cross-Check

Before generation and after every accepted correction, verify that page count, page titles, exact copy, style choices, font-role tokens, packaged filenames, asset names, and per-page prompts agree across all three files. Update the planning package before regenerating affected pages.
