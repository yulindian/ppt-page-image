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
- no watermark, QR code, logo, account, platform mark, signature, institution, or page number;
- style fingerprint and layout family remain consistent.

Any failure triggers complete-page regeneration.

## Whole-Deck QA

Inspect a montage for page count, order, palette drift, apparent type-size drift, family consistency, duplication, harmful monotony, unexplained changes, and all user corrections. Repeated composition is allowed when the pages share compatible structure, hierarchy, and teaching action. Repetition becomes a defect only when the layout does not fit the content, weakens hierarchy or reading order, or makes the teaching sequence meaningfully monotonous. Regenerate only pages with an actual layout problem; do not force whole-page regeneration merely to make the deck look more varied. A page that passes alone can still fail whole-deck consistency and must then be regenerated in full.

## Font Notes

Create `字体说明.txt` containing selection rationale, visual role mappings, display name, weight when known, fallback or similar style, page-by-page audience-facing mappings, prompt typography wording, and notice that image generation only approximates fonts.

Do not package font files or create a `fonts/` folder for this Skill's final delivery. Font names are style targets for prompting and documentation, not proof that the image model used local font files.

## PDF And Final Directory

Package only `PASS` images in natural filename order with `scripts/images_to_pdf.py`. Use quality 92-95 for dense Chinese, formulas, thin lines, or worksheets. Use original lossless pages when compression visibly reduces readability.

Then verify page count, render every PDF page back to an image, and inspect order, borders, crop, clarity, color, and text. Recheck first, last, densest, and regenerated pages at readable scale.

The delivery directory contains exactly:

```text
<PPT名称>/
|-- <PPT名称>.pdf
`-- 字体说明.txt
```

Keep samples, page images, prompts, manifests, OCR output, montages, compressed images, render checks, reports, fonts, and PPTX files in temporary storage. They may be shown during review but never enter this Skill's final delivery directory merely for convenience. A request to retain those artifacts is a separate deliverable outside the `ppt-page-image` contract. Run `scripts/validate_delivery.py`. Do not report completion unless validation passes and PDF render-back was inspected.
