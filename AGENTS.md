# Flutter Harness contributor instructions

The reusable Harness aims for quick, stable, high-quality autonomous Flutter delivery.

- One short feature request -> implementation -> minimal verification -> PR; no redundant technical approvals, worktree choice or repeated planning.
- Default GPT-6 Luna medium for build; per-session UI variant may override config. Reserve Sol/extra agents for genuinely complex work.
- Keep local changes safe; stage only task files, never auto-merge, force-push, publish or bypass permission denials. Never claim a feature delivered unless verify-pr.sh confirms its open PR contains the local HEAD.
- Default code gate: one check.sh standard (format, analyzer, fast unit/widget tests). Add focused Dart unit tests for business rules and persistence; widget tests only for meaningful stateful UI behavior. No tests for trivial labels/boilerplate or arbitrary coverage targets.
- Device/browser integration tests are optional and risk-triggered, not automatic for every feature. Prefer repeatable scripted assertions and exit statuses, not free-form AI screenshot interpretation. Run only relevant platforms.
- A hidden item under an active filter is not missing persisted data. Establish preconditions and verify state before classifying behavior as failed. Avoid repeated UI tool experiments.
- Before the one standard check and PR, inspect the full task diff once and map meaningful new behavior to existing/new tests; green OLD tests do not prove a new sorting/filtering rule. Add one focused test for any material untested branch, not a test for each widget. Use one bounded independent read-only reviewer for multi-feature state interactions (sort+search+filter), high-risk data/security/architecture/concurrency or explicit request; skip it for isolated trivial edits. No reviewer loops.
- Optional E2E not run is NOT RUN (not required), never a reason for mandatory Draft. Failed required checks and material unresolved issues keep Draft. Report actual checks honestly.
- Keep main.dart focused on app bootstrap for growing apps; put screen and state transformations in a feature folder without introducing state-management packages gratuitously. Refactor existing monoliths separately rather than grow them indefinitely.
- Persistent-data mutations, bulk deletion and tests removed after a failed run require actual standard-check and independent reviewer evidence on the same candidate before publication. Never delete a meaningful failing acceptance test to turn CI green. Fix formatting before a standard run.
- Select reviewer Luna Medium/High/Extra High (xhigh) from actual diff size; risk-flagged changes use at least High and large changes require review. One reviewer, no repeated tier escalation. Verify actual child model/effort for required review.
- CI stays lightweight; no hosted mobile/browser E2E added merely because local tools are unreliable.
