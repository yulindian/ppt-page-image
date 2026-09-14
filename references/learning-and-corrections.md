# Learning And Corrections

Read this whenever the user corrects content, style, layout, prompting, QA, or delivery behavior.

## Meaning And Scope

Learning means persistent, auditable rules. It does not train model weights and does not silently rewrite `SKILL.md`.

- `page`: one named page or range;
- `project`: the current presentation;
- `global`: future `ppt-page-image` projects.

Infer conservatively. An explicit page number such as “第7页” is page scope unless the user separately names a broader target. A trailing phrase such as “以后别再犯” means remember the correction at its already established scope; it does not broaden a page rule into a project or global rule. “这套后面都要” is project scope. “以后所有课件都要” is global scope. When scope remains ambiguous, use project scope and state that choice; never promote a temporary correction globally.

## Apply A Correction

1. preserve the original correction text;
2. translate it into one clear positive rule and optional avoid clause;
3. choose page, project, or global scope;
4. record it with `scripts/record_correction.py`;
5. apply it immediately to the affected prompt;
6. regenerate the affected page in full;
7. inspect accepted family pages for the same issue;
8. keep unrelated approved pages unchanged.

Global rules live in `references/learned-rules.json`. Project rules live in temporary project storage and are not delivered. Read active global rules at the beginning of every task.

Example:

```powershell
python scripts/record_correction.py add --store references/learned-rules.json --scope global --source "以后正文不要使用复杂场景压字" --rule "正文使用独立浅色阅读区" --applies-to "body pages" --avoid "dense copy over scenery"
```

## Supersession And Conflicts

Never delete history. When a new rule replaces an old rule, pass `--supersedes <id>`; the script marks the old rule `superseded` and appends the new active rule.

Priority is latest explicit chat instruction, active project rule, active global rule, then defaults. If a global rule conflicts with the current request, follow the current request and record a project exception. Ask only when two current requirements cannot both be satisfied.

Core instructions change only when the user explicitly asks to solidify a correction into the Skill. Ordinary learning updates the rule store.
