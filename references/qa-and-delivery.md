# QA And Delivery

Read this before a review gate and before final delivery.

## Page QA

Technical checks: the image opens, is uniform 16:9, nonblank, full-canvas, correctly ordered, not duplicated, and sufficiently clear. Reject white/gray/transparent borders and crop marks.

OCR/copy checks: compare OCR with locked copy, then inspect visually. Check titles, body, punctuation, numbers, English, pinyin, formulas, options, and answers. Reject missing, extra, garbled, meaning-changing, or incidental text. OCR assists; it never replaces visual review.

Visual checks:

- clear reading order and hierarchy;
- readable size, contrast, margins, and spacing;
- no clipping, overlap, edge crowding, or placeholder;
- distinct reading, image, and decoration zones;
- no busy scene behind dense copy;
- no malformed subject or unintended text;
- illustration zones are text-free unless exact lesson content requires a controlled label;
- a prominent main title sits on a calm field without writing, signs, busy text-like texture, or dense object competition;
- no watermark, QR code, logo, account, platform mark, signature, institution, or page number;
- style fingerprint and layout family remain consistent.

Any failure triggers complete-page regeneration.

## Whole-Deck QA

Inspect a montage for page count, order, palette drift, apparent type-size drift, family consistency, duplication, harmful monotony, unexplained changes, and all user corrections. Repeated composition is allowed when the pages share compatible structure, hierarchy, and teaching action. Repetition becomes a defect only when the layout does not fit the content, weakens hierarchy or reading order, or makes the teaching sequence meaningfully monotonous. Regenerate only pages with an actual layout problem; do not force whole-page regeneration merely to make the deck look more varied. A page that passes alone can still fail whole-deck consistency and must then be regenerated in full.

## Planning Package QA

Confirm that `PPT内容大纲.txt`, `风格提示词.txt`, and `字体说明.txt` exist and are nonempty before final-page production and again before delivery. Cross-check page count, order, exact copy, selected-style feedback, font-role tokens, packaged filenames, image asset names, and every page prompt. A correction is incomplete until the affected planning files are updated.

## Font Notes And Package

Create `字体说明.txt` before generation. Include selection rationale, local inspection result, display name, weight, source path, packaged filename, fallback, page-by-page or line-by-line audience-facing mappings, prompt typography wording, licensing notes, repair guidance, and notice that image generation only approximates fonts.

Package a nonempty `fonts/` folder containing the selected locally available `.ttf`, `.otf`, or `.ttc` files when redistribution is permitted. Replace unavailable or nonredistributable fonts with packageable alternatives and update the notes and prompts. Font files are repair resources and visual targets, not proof that the image model used them exactly.

## PDF And Final Directory

Package only `PASS` images in natural filename order with `scripts/images_to_pdf.py`. Use quality 92-95 for dense Chinese, formulas, thin lines, or worksheets. Use original lossless pages when compression visibly reduces readability.

Then verify page count, render every PDF page back to an image, and inspect order, borders, crop, clarity, color, and text. Recheck first, last, densest, and regenerated pages at readable scale.

The delivery directory contains:

```text
<PPT名称>/
|-- <PPT名称>.pdf
|-- PPT内容大纲.txt
|-- 风格提示词.txt
|-- 字体说明.txt
|-- fonts/
`-- images/                  optional; only when useful repair/source assets exist
```

When `images/` exists, it must be nonempty and every file must be listed in `风格提示词.txt` with its source, role, and page use. Keep unselected samples, transient page images, manifests, OCR output, montages, compressed images, render checks, reports, and PPTX files in temporary storage. Run `scripts/validate_delivery.py`. Do not report completion unless validation passes and PDF render-back was inspected.
