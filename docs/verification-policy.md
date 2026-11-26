# Verification policy

Ordinary application changes require one successful CLI check on the exact
candidate, then delivery. Check runs dependency resolution, formatting,
product conventions, analyzer and fast Flutter tests. CI independently
checks formatting without rewriting files. Use focused unit/widget tests
for material changed behavior and error paths; no test quotas or duplicate
all-platform scenarios. A green old suite is not proof of new behavior. For a bug, reproduce the original failure (or establish a precise static proof), fix the cause and verify the original scenario; retain material executable regression protection.

Risk-based review covers interacting behavior, persistent/destructive
operations, native/platform configuration, security, large diffs and
substantial UI; the semantic flag in delivery.json supplements the lexical
classifier. Required review is a real read-only child session with actual
model/variant, matching candidate and final VERDICT: PASS. For visual risk,
also require scoped current runtime planned screen/interaction light/dark capture receipts before dispatch, and bind review to the exact evidence digest plus VISUAL: PASS
immediately before VERDICT: PASS. Read PRODUCT/DESIGN for actual UX criteria.
Screenshots do not prove interaction correctness.

Each blocking review finding names a violated requirement/invariant, source or runtime location, reachable scenario, expected/actual result, impact and evidence. A read-only reviewer may prove a defect statically, cite existing execution/capture evidence, or hand the smallest reproduction to Build; it must not claim execution it did not perform. Unconfirmed hypotheses and preferences are not blocking defects. Missing required evidence remains BLOCKED. Do not introduce an additional reviewer or a rigid finding parser; semantic quality stays with the existing reviewer and parent.

For critical native/browser acceptance use one relevant executable scenario.
Declare required_e2e in delivery.json; CLI e2e runs actual tools on the
launched candidate and writes a digest-bound result. Optional tests not
needed are NOT RUN. Failed/missing required evidence stops delivery; no
fabricated report, no hidden fallback, no auto-merge. A material correction
requires fresh affected checks and targeted independent recheck; up to two substantive repair rounds are available. A technical BLOCKED/ERROR may permit one extra bounded dispatch; unchanged evidence cannot be re-reviewed merely by asking again.

The standard gate requires current evidence even for routine changes.
The classifier is conservative and lexical, not semantic understanding.
Local receipt provenance is not an adversarial security boundary.

Default visual runtime is one pinned target selected by CLI launch auto in iOS → Android → Web order. Additional platform builds/E2E require actual affected platform risk or release scope. Significant layout changes test representative compact, medium, expanded sizes and resize/state preservation with actual feature widget tests; use real wide runtime evidence when materially affected, not a mandatory three-platform matrix. Small changes stay scoped.

The fast standard runner stops at the first failed step; Flutter uses --fail-fast, a 45s default per-test timeout and a 180s suite watchdog. Explicitly set HARNESS_TEST_SUITE_TIMEOUT for larger known suites (1–1800s), not to hide a hanging test. A single canonical check may run per checkout. Failed checks retain reports and a bounded local log tail; diagnostics remain available without a session export. A supplied baseline must match task.json's original digest. Do not compare against historical captures when baseline is unavailable.

Use `diagnostics --local` for immediate local evidence without any OpenCode export. The standard diagnostics command persists local facts before attempting usage export.

For focused UI and new screens omit baseline. Capture the original actual screen explicitly before edits only when comparison matters; use its exact task digest. Batch capture reuses task-scoped platform runtime input digest/device/theme/fixture/script-hash receipts; --refresh LABEL forces both themes of one changed state. The full delivery/check/review digest remains exact. Test-only Dart files and other platform trees are excluded from the visual input digest in the standard layout unless referenced in pubspec; unknown files, shared Dart, assets, configuration and scripts remain inputs. Capture receipts retain their original candidate digest. Interaction evidence must use a scripted scenario on every platform. Run visual-evidence before relaunching after a fix; use capture-plan only for missing affected states. Do not ask owners to operate routine UI. One fresh read-only adjudication is available for a first CHANGES_REQUIRED on unchanged evidence; it must explicitly resolve every prior finding and return ADJUDICATION: RESOLVED plus the normal required PASS. Confirmed defects still require repair; no third unchanged-input review. The production quality gate reads the CLI's current standard receipt rather than relying on text alone.

The CLI checks that no canonical check holds the checkout check lock before accepting a current PASS receipt for review or delivery.

Task isolation: the OpenCode conversation may span successive tasks. A task generation owns reviewer/consultation/recovery budgets, requirements and pending tool evidence. Successful canonical delivery is reconciled against the exact local completion receipt immediately and on the next prompt if the idle hook was interrupted. An unfinished or blocked task retains its limits. A subsequent task requires a fresh canonical begin and feature branch; archived receipts are diagnostic only. Session usage exports remain cumulative for the parent conversation, not per-task token measurements.

Local checkpoint commits save coherent tested slices, without approval, push or acceptance. The final check/review considers the complete task diff, including every local commit. Clean checkpointed work may prepare its first delivery manifest; once publication starts its original manifest is preserved.
