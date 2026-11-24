---
name: product-design
description: Design materially new screens and flows as a product designer, with visual alternatives and evidence-based critique before implementation.
---

# Product design (experimental v1)

Design an experience, not a collection of widgets. First read the product brief,
existing product policy and relevant visual references. The user owns product
intent; do not invent a brand, feature, navigation destination, data or marketing
message. Make ordinary design decisions autonomously.

## Understand the job

Identify the primary user job, the information needed to perform it, common
actions and rare actions. Decide which actions deserve persistent visibility,
which can be contextual, and how users discover and return from them. Preserve
every requested capability. Do not confuse preserved capability with a
permanently visible control. Prefer explicit, accessible alternatives to
gesture-only actions. Think about populated, empty, error, long-content,
keyboard and loading states where relevant.

## Visual direction

Inspect actual images of two or three relevant existing product/reference
screens when available. Extract concrete patterns and explain their suitability
to this task. Use the supplied annotated visual examples as practice, not as
a template or a catalog of universally correct layouts. Respect the project's
platform profile, design tokens and established identity. Do not invent
new colors or use web conventions indiscriminately on native mobile.

- Establish a clear focal point and reading order. In a working utility,
  the primary content should not compete with decorations or unrelated summaries.
- Use a coherent grid, alignment, spacing rhythm, and typography. Use weight,
  size, grouping and contrast with intention; prefer legible labels to ornamental
  microcopy. Reserve strong accent for meaningful actions or information.
- A surface, divider, section, card, icon or label must earn its space.
  Avoid duplicate labels, gratuitous hero blocks, generic slogans, nested
  cards, excessive outlines, chips and decorative statistics. These patterns
  are not banned: justify them when the user's job benefits.
- Preserve readable density, touch targets (44 logical px for iOS and 48
  for Material), text scaling and contrast. Do not trade discoverability,
  accessibility or clarity for a visually empty screen.
- Optimize for the actual content, not one short sample. Show realistic varied
  lengths, statuses and ordinary data. Adapt structure to available space and
  platform rather than stretching a mobile composition on desktop.

## Explore and select

Before changing application source for a significant redesign, make two
materially distinct visual concepts, not merely palette or radius variations.
Use the same content and constraints for comparison. Render both at the
target viewport and inspect the actual images. Compare them against the brief,
existing screen (when supplied), and relevant references. Pick one and explain
the key trade-off in a few sentences. If neither works, revise the stronger
direction once. Stop rather than claim an unobserved or unsatisfactory PASS.

The selected visual artifact and short interaction map are the handoff:
where each required action lives, primary/secondary hierarchy, states and
platform/width adaptations. A static concept is not evidence of working
behavior, accessibility, responsive implementation or native theme support.
For production changes, compare actual rendered implementation with the
selected design; keep ordinary engineering checks separate.

In the experiment use local, self-contained SVG concepts only. Do not modify
product source, build Flutter, use a second application stack, or publish a PR.
The experimental brief controls exactly what to produce.
