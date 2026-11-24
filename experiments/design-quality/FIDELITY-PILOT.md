# Flutter design-fidelity pilot (experiment, not production policy)

Goal: test whether Luna Medium can faithfully implement the owner's chosen
Sol task concept without losing existing functionality or data. This is a
controlled handoff experiment, not another free-form redesign or a test of
fully autonomous design selection. Use normal installed Harness engineering
checks and delivery guard. Do not install this experimental document as a
production policy or modify the Harness in the lab branch.

## Input and preflight

Start a fresh task from the clean, current lab `app` integration branch.
Fetch origin app and verify local HEAD equals origin/app before branching.
Do not reset, overwrite unrelated work, or start from PR #25. Create a fresh
feature branch; do not update or merge #25.

Read the installed flutter-harness skill, current .flutter-harness/PRODUCT.md,
product.json and actual source/tests. The local directory
.flutter-harness/previews/design-pilot contains this document as PILOT.md,
the selected Sol concept as reference.png and its handoff as handoff.md.
Actually inspect the PNG with an image-capable tool before implementation.
If it cannot be inspected, stop this pilot as BLOCKED; do not improvise an
unrelated design. The reference is a static iOS light concept, not a runtime
capture. Never treat it as implementation evidence.

## Owner-approved design and deliberate amendments

Implement the selected grouped, content-first design: recognizable
«Мои задачи» title, unfinished count, header add action, status filter,
clear active/completed groups, aligned compact readable task rows with
completion control and contextual actions, sorting and contextual cleanup.
Use the current Adaptive profile (native iOS blue and semantic surfaces;
Material 3 Ocean Blue on Android/Web, system light/dark). Use actual platform
controls and a single shared feature architecture; do not force iOS pixels
on Material or desktop. Use reference proportions, rhythm and hierarchy,
not a screenshot as a background or fixed coordinates.

Owner amendment: iOS search is initially collapsed, revealed by pulling
down at the top in the native style, and collapses as the list is scrolled
when search is inactive. Keep an accessible explicit search entry as a
non-gesture alternative (e.g. navigation action if necessary). Do not hide
or clear active query/focused search merely because the list scrolls;
clear/cancel and return to the list must be predictable. Verify the actual
SDK's supported Cupertino patterns rather than inventing APIs. Document
any necessary native-pattern limitation. Android/Web may use suitable
platform-native search affordances. Do not display duplicate search entries
without purpose.

No hero, marketing text, renamed product, extra statistics, dates, fields,
new navigation destinations or new dependencies without a demonstrated
need. Preserve content priority, all existing capabilities, storage key,
serialized records, identity, mutations, rejection handling and concurrency.
Implement the actual current product foundation and activate it only after
integration; never disable its checks or substitute a second web stack.

## Resolve handoff ambiguity using the existing product contract

The existing repository and tests are the authority for persistence and
behavior, not speculative details in the design handoff. The following
decisions apply only to this pilot:

- Default All view presents active/completed groups while preserving
  relative stored order within each group. Grouping is presentation only;
  do not reorder stored records. This intentionally changes the visual
  ordering of a mixed-status default list. For alphabetical sorting in All,
  preserve the existing global case-insensitive sort, using a unified list
  if needed. Single-status scopes preserve existing matching and sorting.
  Count all active tasks regardless of current query/filter.
- Duplicate is a distinct active same-title record appended to storage,
  exactly as existing tests specify, including a completed source.
  Add, duplicate and reopen can be excluded by the current view; provide
  feedback and a clear way to show the result without silently mutating
  the user's filter or sorting.
- Prefer single-delete confirmation in this pilot rather than introduce
  a new persistence-level undo/restore operation. Retain confirmation
  for bulk deletion; state that it deletes all completed tasks and show
  the count. Hide bulk cleanup when no completed tasks exist, during
  active-only scope, or during an active query. Provide a clear way to
  return to All and clear the query. Keep rename/add validation and
  failed input retry; failed writes retain actual saved state.

Preserve important existing assertions (including persistence failures).
Adjust obsolete widget finders/interaction sequences for the changed UI
without weakening behavior checks. Add only focused coverage for material
new behavior, such as group/sort interaction and search disclosure or
creation recovery. Standard check and one required independent code review
on the final candidate; one focused recheck if necessary. The reviewer
must treat material product hierarchy and reference fidelity as legitimate
defects, not dismiss them as cosmetic preferences. Do not introduce
mandatory E2E suites, goldens, blanket tests or additional review loops.

## Runtime evidence and delivery

Use the actual implementation on local simulator/browser, not SVGs or
Ahem test renders, for visual evidence. Obtain screenshots from the final
candidate with representative comparable data. The six reference titles
and completion states are in the concept/handoff (four active, two
completed). Use an isolated debug preview fixture invoking the same real
screen and design system if necessary; never wipe the owner's stored
tasks or ship sample data in normal launch. A preview fixture does not
prove real persistence; repository tests still must pass.

Capture in a separate output directory under .flutter-harness/previews:
- iOS light populated, search collapsed and revealed.
- iOS dark populated.
- Material mobile light and dark populated (Android if available).
- Material desktop web populated at a representative wide viewport.
- Representative changed empty state when practical.

Use shared comparable sample content; label viewport, theme, actual
platform, candidate commit, and any fixture. Capture after material
fixes affecting the image, not from a stale build. Inspect actual
images side by side with the selected reference and evaluate fidelity
of hierarchy, typography, alignment, density, state/discoverability and
platform adaptation. Do not assert working gestures/accessibility from
static screenshots; test meaningful behavior separately. If a required
runtime capture is unavailable, report BLOCKED; avoid repeated tool
experiments and false PASS. Use the existing bounded verification policy.
No default device E2E.

Open a new PR into app only when required existing delivery evidence
allows it; prefer a draft for the pilot pending owner evaluation.
Do not merge or bypass delivery guard. If blocked, report the specific
blocker, current branch and evidence rather than claim completion.
Attach/identify final screenshot paths and verification evidence in the
PR, explicitly separating code review, actual visual inspection and
pending external fidelity acceptance. Report which checks were actually
run. Include elapsed time and model/effort if observed. The experiment
owner will compare the actual screens against the selected concept
independently before integration of any new design workflow.

Stop once the bounded implementation/delivery is complete. No further
product-design round, no extra model comparison and no new Harness
infrastructure during this pilot.
