# Behavior Scenarios

## Topic And Audience Style Gate

No usable style image is supplied and the user asks for reference styles.
Expected behavior: infer four materially different 16:9 sample directions from
the topic, audience, scenario, subject tone, and content density; recommend one
and stop for selection. After selection, explain useful traits, record feedback
and rejected traits, then create the planning package before final images.

## Planning Package Is Mandatory

The user selects a style sample and asks the agent to start making images
immediately. Expected behavior: first create and cross-check `PPT内容大纲.txt`,
`风格提示词.txt`, and `字体说明.txt`; then use their exact page copy, style
fingerprint, font-role wording, and image constraints during generation.

## Illustration Text Separation

A page prompt includes exact teaching copy plus an illustration of a street,
classroom, book, sign, and screen. Expected behavior: keep approved copy in a
dedicated reading zone and make the illustration text-free, removing or avoiding
signs, posters, book-page writing, screen UI, labels, and pseudo-writing unless a
specific label is required by the lesson.

## Quiet Title Background

A cover needs a prominent main title. Expected behavior: reserve a calm,
high-contrast title field and keep the background behind it free of complex
objects, incidental text, text-like texture, signs, posters, and busy patterns.

## Font Visual Target And Repair Package

The image model cannot guarantee a local font identity. Expected behavior:
inspect available fonts, map every audience-facing line to a font role in
`字体说明.txt`, translate those roles into every page prompt, state that the
rendering is an approximation, and package every actually used locatable font
file in `fonts/` for later repair.

## Layout Family Reuse

The selected sample uses a left-right composition, and several later pages have
different content structures. Expected behavior: preserve the visual style but
choose each layout from content needs. Reuse a good layout family on compatible
pages; do not make it the global template and do not force variation merely
because a composition repeats.

## Anti-AI Controls Begin Before Generation

The requested topic could easily become a generic polished AI poster. Expected
behavior: derive each page's visual concept from specific content evidence and
audience context; record a design rationale and element budget; reject
template-like copy, purposeless decoration, generic glow/gradient/card effects,
and implausible subject details before generation. The page prompt names the
purpose of every major visual element and uses concrete editorial or classroom
references instead of vague requests for a "premium" or "dreamy" look.
