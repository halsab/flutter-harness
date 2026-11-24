# Initial design-only experiment results

Reported wall time (OpenCode final build summaries, not token exports):

| Brief | Luna Medium | Sol Medium |
| --- | --- | --- |
| Tasks | 2m 32s | 2m 44s |
| Transaction history | 2m 29s | 2m 32s |

Both authors produced two rendered 390×844 SVG concepts in each case,
selected concept 1, and supplied a written interaction map. The owner
preferred Sol's task concept 1 with the iOS search field hidden initially,
revealed by pull-down, and collapsing on scroll when search is inactive.
Do not turn this preference into a universal prohibition on persistent
search: choose based on user job and platform. Preserve active queries,
accessibility and discoverability when implementing that behavior.

Observations from non-blind review of supplied PNGs and handoffs:
- Both task redesigns remove the old decorative hero, focus on tasks,
  retain a visible add action, and move secondary row actions into menus.
- Sol's task handoff addresses combined filter/sort/grouping and a task
  created outside the current view. These are proposed behaviors, not
  tested functionality. Do not change existing persistence semantics.
- Luna's finance concept 1 duplicates the search entry and makes the
  date filter ambiguous; both finance concepts add invented category-like
  labels not present in the brief.
- Sol's finance concept 1 presents date/type/search/sort controls clearly.
  Its handoff covers combined filters, invalid date range, return to
  scroll position, and long amount/merchant adaptation.
- Sol Medium is the provisional designer candidate, with Luna Medium
  retained as implementer. The time difference is small.

Limitations: two list-oriented briefs, no repeated trials, no randomized
model routing, no skill-free control, no actual Flutter implementation,
no independent blinded assessment yet, and no verified session token
exports. Do not infer universal design superiority, causal effect of the
skill alone, or production readiness.

Next: run an independent evaluator on the existing concepts and the actual
legacy screenshot using prepare-judge.sh and JUDGE-RUN.md. Then pilot
the owner-preferred task design in Flutter, retaining existing data and
functionality. Separate design quality, implementation fidelity and
engineering acceptance; no new production delivery guard until tested.

## Independent evaluator trial

One fresh Sol Medium session reported 1m 44s wall time, all 11 PNGs
inspected, and no blocker. The two user-supplied reports record an image-only
assessment before the interaction-map audit. The author mapping was concealed
within the judge workspace: tasks X = Luna, Y = Sol; finance X = Sol, Y = Luna.

| Brief | Luna 1 | Luna 2 | Sol 1 | Sol 2 | Recommended |
| --- | --- | --- | --- | --- | --- |
| Tasks | acceptable | acceptable | acceptable | acceptable | Sol 1 |
| Finance | changes required | changes required | acceptable | acceptable | Sol 1 |

The evaluator preferred the content-first teaching example while identifying
its redundant subtitles and the weaker example's useful affordances. It
identified the legacy task screen's hierarchy and scope problems (no
separate absolute legacy verdict was recorded). It rejected both Luna
finance concepts for invented data and interaction/discoverability defects;
reading the handoffs did not overturn those verdicts. The task winner
matches the owner's preference, with the owner's search behavior amendment
still to be implemented. The audit identifies real ambiguities involving
default ordering, duplicate placement, destructive actions, and accessibility.

This is promising initial evidence, not validation of the evaluator across
products. The same model family judged its own anonymous outputs, only one
judge run was performed, no score threshold is calibrated, and neither
functionality nor implementation fidelity was established. No gate should
treat an ordinal score or ACCEPTABLE_CONCEPT as implementation acceptance.

Next experiment: FIDELITY-PILOT.md. Pilot Luna implementation of the selected
Sol task concept on a fresh branch from current lab app. Keep PR #25 as the
negative control, do not merge it or use its code as a starting point.
