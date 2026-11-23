# Flutter Harness contributor instructions

The reusable Harness aims for quick, stable, high-quality autonomous Flutter delivery.

- One short feature request -> implementation -> minimal verification -> PR; no redundant technical approvals, worktree choice or repeated planning.
- Default GPT-6 Luna medium for build; per-session UI variant may override config. Reserve Sol/extra agents for genuinely complex work.
- Keep local changes safe; stage only task files, never auto-merge, force-push, publish or bypass permission denials. Never claim a feature delivered unless verify-pr.sh confirms its open PR contains the local HEAD.
- Default code gate: one check.sh standard (format, analyzer, fast unit/widget tests). Add focused Dart unit tests for business rules and persistence; widget tests only for meaningful stateful UI behavior. No tests for trivial labels/boilerplate or arbitrary coverage targets.
- Device/browser integration tests are optional and risk-triggered, not automatic for every feature. Prefer repeatable scripted assertions and exit statuses, not free-form AI screenshot interpretation. Run only relevant platforms.
- A hidden item under an active filter is not missing persisted data. Establish preconditions and verify state before classifying behavior as failed. Avoid repeated UI tool experiments.
- Build agent self-reviews its diff once. Independent read-only reviewer only for high-risk data/security/architecture/concurrency or explicit request; at most one targeted follow-up.
- Optional E2E not run is NOT RUN (not required), never a reason for mandatory Draft. Failed required checks and material unresolved issues keep Draft. Report actual checks honestly.
- CI stays lightweight; no hosted mobile/browser E2E added merely because local tools are unreliable.
