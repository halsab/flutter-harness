# Flutter Harness contributor instructions

This repository contains the reusable harness, not the user's Flutter application.

- Default product workflow: one concise design checkpoint only when material decisions require it, then plan/implement/test/review/PR without asking the user to approve a second technical plan.
- Preserve the upstream Superpowers project unchanged. Its mandatory interactive approvals are incompatible with the autonomous default; it is available only as a separately opted-in interactive workflow.
- The configured default model is GPT-6 Luna medium, but the OpenCode UI may retain a session-specific High override; verify the active session variant and audit actual usage rather than trusting config alone. GPT-6.2 Sol medium is for complex architecture or hard diagnosis, not routine calls. Prefer one Luna medium final reviewer pass with concrete scenarios and evidence; allow at most one targeted recheck. Use Luna-low explore only for broad unfamiliar-code search.
- Work on a feature branch in the current checkout by default. Preserve unrelated local edits; never reset, stash, commit or stage them without authorization.
- Prefer official Flutter/Dart tools, targeted tests and deterministic scripts. Discover Android/iOS devices; if an iOS Simulator is booted, run Maestro on it as well as Android (iOS build alone is insufficient). Use Playwright for Web with the deterministic built Web preview, not a Chrome debug-service run. Run all platform E2E tests independently, record actual tool evidence, and use verify-e2e.py; if any platform is incomplete, create only a DRAFT PR. Check exact post-action values without adapting assertions to unexpected text. Do not loop on incompatible Maestro Web semantics.
- The read-only reviewer must obtain the complete task diff; run separate allowed Git status / merge-base / diff commands, not chained shells, and use read for files. Permission-denied or missing diff coverage means review OPEN, not PASSED.
- Never claim a test, iOS Simulator run, build, UI observation or model-cost reduction without evidence. Report PASS / FAIL / BLOCKED / SKIPPED separately for Android, iOS and Web.
- After an agreed feature is implemented, attempt push + PR by default. Respect the interactive push permission; report BLOCKED if denied. The owner alone merges PRs or approves changed golden screenshots.
- No destructive Git operations, force pushes, releases, production secrets or permission bypass. MCP and shell permissions are guardrails, not a sandbox.
- Keep session usage reports local and sanitized; do not commit private conversation exports. This repo is separate from https://github.com/halsab/flutter-harness-lab.
