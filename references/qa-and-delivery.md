# QA And Delivery

Read this before a review gate and final delivery.

## Page QA

### Technical

- Opens successfully; uniform 16:9 dimensions; full canvas; sufficient clarity.
- Correct page number and filename; not blank or duplicated.
- No white, gray, or transparent edge, crop mark, or unintended border.

### Copy

Compare OCR with locked copy, then inspect visually. Check title, body, punctuation, numbers, English, pinyin, formulas, options, and answers. Reject missing, extra, garbled, meaning-changing, or incidental text. OCR assists; it never replaces visual inspection.

### Visual

- The title, question, key message, or reading task leads the first glance.
- Supporting scenes and decoration do not steal attention.
- Reading order, hierarchy, size, contrast, spacing, and margins are clear.
- Reading, image, decoration, and title zones remain distinct.
- Dense copy does not sit on busy scenery; a prominent title has a calm field.
- Illustration zones contain no incidental or pseudo-writing.
- Subjects are plausible; nothing is malformed, clipped, colliding, or crowded.
- Current cases match their verified dated source and remain relevant to the teaching goal.
- Referenced authentic photographs preserve recognizable subject, place, and factual meaning; no generated alteration creates false documentary evidence.
- Style fingerprint and family invariants are intact.
- Same-level section pages share one title system while their content layouts may vary.
- Same-block exercises share a worksheet family; short answers appear in their intended blank or parentheses.
- Every major element has a communication purpose; the page does not depend on generic spectacle or filler copy.
- No watermark, QR code, logo, account, platform mark, signature, institution, or page number unless locked content requires it.

Any failure requires complete-page regeneration.

## Family And Whole-Deck QA

Every repeated family must have a current montage containing all its pages in order. Inspect it component by component against the planning specifications: fixed traits must match, differences must appear in the permitted-variable list, and forbidden drift must be absent. A changed family page invalidates the earlier family review and requires a new montage and full-family inspection.

After all families pass, create the whole-deck montage and check page count and order, focal hierarchy, palette and type-size drift, duplication, harmful monotony, generic AI traits, and every user correction. PDF packaging is blocked while any repeated family lacks a current passing montage review.

Repetition is valid when pages share structure and teaching action. It fails when it harms content fit, hierarchy, reading order, or deck rhythm. Variation fails when related pages lose their shared title, frame, spacing, palette, or answer logic. A page that passes alone may still fail its family or the complete sequence.

## Planning And Font QA

Before pilot generation, after accepted corrections, and before delivery:

1. confirm the three planning files are complete and nonempty;
2. confirm page order, locked copy, prompts, families, component specifications, and font tokens agree;
3. confirm every registered font file exists in `fonts/` and run `scripts/validate_project.py`; any failure blocks generation;
4. confirm `fonts/` contains every registered, redistributable `.ttf`, `.otf`, or `.ttc` file;
5. confirm no more than seven font roles are used and each has a realistic repair substitute.
6. for enrichment assets, confirm relevance, verification date, provenance, rights status, target page, and fidelity constraints are recorded.

Packaged fonts support later repair and provide visual targets. They do not prove that the image model used the exact fonts.

## PDF And Render-Back

Package only `PASS` images in natural filename order:

```powershell
python scripts/images_to_pdf.py --slides-dir <slides-dir> --out .work/<name>.candidate.pdf --expected-pages <N> --quality 95
```

Use `--mode lossless` when JPEG compression visibly damages dense Chinese, formulas, or thin lines. This mode preserves the source image encoding instead of recompressing PNG pages as JPEG.

Render every candidate page back to an image:

```powershell
python scripts/render_pdf.py --pdf .work/<name>.candidate.pdf --out-dir .work/render-back --expected-pages <N>
```

Inspect every rendered page and the montage for order, borders, crop, clarity, color, and text. Recheck the first, last, densest, and every regenerated page at readable scale. Promote only after this passes. Render the promoted final PDF again and record the actual review:

```powershell
python scripts/render_pdf.py --pdf <delivery>/<name>.pdf --out-dir .work/render-back-final --expected-pages <N> --inspection pass --notes "Inspected every page and montage"
```

The report contains the final PDF hash. Any later PDF change invalidates it.

## Delivery

```text
<name>/
|-- <name>.pdf
|-- PPT内容大纲.txt
|-- 风格提示词.txt
|-- 字体说明.txt
|-- fonts/
`-- images/                  optional
```

When `images/` exists, it must be nonempty and every asset must be registered in `风格提示词.txt` with source, role, and page use. Keep samples, slides, candidates, OCR, montages, reports, render output, state, PPTX, and old versions outside the delivery folder.

Validate the clean directory against the matching render-back report:

```powershell
python scripts/validate_delivery.py --delivery-dir <delivery> --deck-name <name> --expected-pages <N> --render-report .work/render-back-final/render-back-report.json
```

The validator checks required files, registered assets, PDF page count and 16:9 size, one image per page, absence of a text layer, and a passing hash-matched render-back report. Do not report completion unless it passes.
