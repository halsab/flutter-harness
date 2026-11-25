# Verification policy

Ordinary application changes require one successful CLI check on the exact
candidate, then delivery. Check runs dependency resolution, formatting,
product conventions, analyzer and fast Flutter tests. CI independently
checks formatting without rewriting files. Use focused unit/widget tests
for material changed behavior and error paths; no test quotas or duplicate
all-platform scenarios. A green old suite is not proof of new behavior.

Risk-based review covers interacting behavior, persistent/destructive
operations, native/platform configuration, security, large diffs and
substantial UI; the semantic flag in delivery.json supplements the lexical
classifier. Required review is a real read-only child session with actual
model/variant, matching candidate and final VERDICT: PASS. For visual risk,
also require current candidate light/dark capture receipts and VISUAL: PASS
immediately before VERDICT: PASS. Read PRODUCT/DESIGN for actual UX criteria.
Screenshots do not prove interaction correctness.

For critical native/browser acceptance use one relevant executable scenario.
Declare required_e2e in delivery.json; CLI e2e runs actual tools on the
launched candidate and writes a digest-bound result. Optional tests not
needed are NOT RUN. Failed/missing required evidence stops delivery; no
fabricated report, no hidden fallback, no auto-merge. A material correction
requires fresh affected checks and at most one targeted independent recheck.

The standard gate requires current evidence even for routine changes.
The classifier is conservative and lexical, not semantic understanding.
Local receipt provenance is not an adversarial security boundary.
