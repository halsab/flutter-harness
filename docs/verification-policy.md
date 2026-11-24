# Verification policy: speed with quality

Ordinary feature: one preflight diff/acceptance review to select the necessary tests, then one deterministic check.sh standard run (format, analyzer, flutter test). CI repeats fast code checks. Old tests passing cannot establish coverage of a newly added behavior.

Add tests only for important public behavior:
- Dart unit tests for validation, calculations, business decisions, persistence,
  serialization and significant error paths.
- Flutter widget tests for consequential UI state behavior (filtering, form
  validity, loading/errors); avoid fragile pixel/layout assertions.
- No tests for static labels, trivial framework wiring or every class/widget.
- Avoid duplicate scenarios at multiple levels and arbitrary coverage targets.

Integration/E2E is exceptional: use a small committed scripted scenario only
for high-risk OS/plugin boundaries, security/payment/data-loss workflows,
platform differences or explicit requests. One representative platform is
often enough. Do not require Android+iOS+Web for routine changes.

Before any UI scenario: normalize application state, select the correct tab or
filter, seed known data and assert the actual postcondition. In the task-filter
incident the newly created task was hidden under Completed; treating it as a
failed add was an agent inference error, not an app failure.

Machine-run checks return exit statuses and deterministic logs. Do not rely
on the agent's screenshot interpretation as a substitute for programmatic
assertions. One diagnostic and one changed attempt are enough for transient
device-input failures; then report the optional test blocked rather than
looping. An optional unrun E2E does not block a routine PR; a failed REQUIRED
risk-based gate does.

For product projects the standard runner also checks architecture and design-system conventions. Substantial new screens/redesigns require real visual inspection and the same independent reviewer, not an additional design agent or functional E2E suite. See templates/product/PRODUCT.md. Anticipate rejected writes before first review; use targeted checks during iteration, and run required reviewer and final check concurrently only when source is stable.

An independent reviewer is optional for isolated routine work, but use one focused pre-PR review for material cross-feature interactions (e.g. sorting+search+filter) and genuine high risks. It must check acceptance criteria and missing regression assertions, not aesthetics. Test/review overhead should not overwhelm
implementation.

Reviewer effort is adaptive: Luna Medium for <=100 lines and <=3 files, High for <=400 lines and <=8 files or risk flags, Extra High (xhigh) above either large-change threshold. Count source/test additions and deletions, not generated lockfiles. Large changes require independent review; isolated trivial changes still skip it. One reviewer per review stage; required review evidence must match the actual selected Luna variant and candidate. Tune thresholds from observed quality, time and token use.
