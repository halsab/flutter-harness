# Candidate run — identical inputs

Read BRIEF.md and load .opencode/skills/product-design/SKILL.md. Inspect
references/README.md and both actual reference images (render the SVGs with
render.sh and use an image-capable read/vision tool). Do not read another
candidate's workspace, use outside examples, or ask the owner for approval.

Produce only these files in output/:
- concept-1.svg and concept-2.svg: two materially different screen designs,
  self-contained SVG, explicit width="390" height="844" viewBox="0 0 390 844".
  No remote assets/scripts, external fonts, logos or model identifiers.
- concept-1.png and concept-2.png: actual renders via render.sh. Visually
  inspect both. If image access fails, state BLOCKED rather than invent evidence.
- handoff.md: selected concept (1 or 2), brief comparison, rationale,
  interaction map covering every capability, considerations for empty/error
  states and implementation adaptations. At most 500 words. No invented
  functional test/quality claims. No implementation or PR.

Use one fresh build session at the selected model/effort, no subagents.
Spend effort on quality rather than tooling; at most one correction after
rendering. Do not install dependencies into the Flutter project. Stop after
these outputs, report observed limitations and elapsed time if available.
