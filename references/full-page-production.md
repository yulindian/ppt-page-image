# Full-Page Production

Read this before pilot or final-page generation.

## Pilot Gate

Generate up to five high-risk representatives, or the entire deck when it has fewer than five. Select without duplication:

1. cover or primary title page;
2. mother page of the most common body family;
3. densest copy page;
4. special structure such as process, comparison, case, map, quotation, or worksheet;
5. mother page of the largest or highest-risk repeat family.

Run page and family QA, create a montage, recommend changes, and stop for approval. Style selection approves visual direction; pilot approval confirms that the direction works with real content and family rules. Skip the pause only when explicitly authorized.

## Files And Promotion

Keep one current file and at most one candidate per page:

```text
slides/slide-07.png
.work/candidates/slide-07.new.png
.work/project-state.json
```

Keep OCR, montages, reports, and render-back output under `.work/`. Delete a failed candidate. Promote a passing candidate only after it opens, is uniform 16:9, matches locked copy, passes visual review, and fits its family. Do not create `v2`, `v3`, `旧版`, `修改版`, `final-final`, or backup variants.

## Pre-Generation Gate

Do not generate until the plan and prompt answer:

- What is noticed first, second, and third?
- Does the main task dominate supporting scenes and decoration?
- Why does this layout fit the content type, teaching action, hierarchy, and density?
- What source-grounded evidence makes the concept specific to this topic and audience?
- What is the one-sentence rationale?
- What is the element budget and purpose of each major element?
- Are people, objects, period details, and spatial relationships plausible?
- Are reading, illustration, decoration, and title zones explicit?
- Does the page inherit the correct family invariants without copying an unsuitable composition?
- Have filler copy and unjustified effects been removed?
- If a current case or authentic photo is used, is it verified, instructionally relevant, age-appropriate, rights-cleared, and protected from meaning-changing alteration?

Update the planning package when an answer is missing. Do not rely on final QA to rescue an underspecified prompt.

## Production Loop

For each page:

1. Load locked copy, page family, font roles, style fingerprint, prompt, active corrections, and previous defect history from project state.
2. Pass the pre-generation gate.
3. Generate one complete candidate page into `.work/candidates/`.
4. Run technical and copy checks, then inspect hierarchy, readability, content fidelity, subject plausibility, family consistency, and generic-AI traits.
   When an authentic photo is referenced, also compare identity, place, event context, and factual meaning against the source. Reject a page that turns documentary evidence into a fabricated scene.
5. Delete a failed candidate and record the defect. Promote only a page marked `PASS`.
6. Refresh the relevant family montage after an accepted page or repair.

Keep approved pages unchanged unless a later correction affects them. For a family defect, update the family prompt and regenerate the complete affected family.

## Defects And Retries

Use stable codes:

| Code | First adjustment |
|---|---|
| `TEXT_MISMATCH` | Simplify line structure, enlarge the reading zone, reduce visual competition |
| `TEXT_UNREADABLE` | Increase scale and contrast, simplify background and grouping |
| `EXTRA_TEXT` | Strengthen the text-free illustration zone; remove books, signs, screens, and packaging |
| `LAYOUT_OVERFLOW` | Rebalance groups or request a permitted split |
| `STYLE_DRIFT` | Reinforce fingerprint and family invariants |
| `IMAGE_DEFECT` | Simplify subjects, actions, and spatial relationships |
| `FULL_BLEED_FAILURE` | Restate edge-to-edge canvas and remove border-like framing |
| `DUPLICATE_PAGE` | Restore page-specific content evidence and goal |
| `CONTENT_MISMATCH` | Correct subject evidence and locked facts |
| `THEME_DEMOTED` | Reduce supporting area, contrast, faces, or detail |
| `SUPPORTING_SCENE_DOMINATES` | Reorder focal hierarchy and reposition the scene |
| `LAYOUT_MONOTONY` | Select a better content-driven family for affected pages |

Each retry records the visible problem, suspected cause, changed planning or prompt condition, and outcome. Change at least one relevant condition. Never rerun the same prompt for the same defect.

After three failed complete-page generations for the same defect, stop and report allowed tradeoffs such as simplifying optional copy, increasing reading space, or splitting a page when permitted. Do not use overlays, local repair, native text, compositing, or PPTX as a workaround.
