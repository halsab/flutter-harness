# Flutter Harness contributor instructions

This repository contains the reusable harness, not the user's Flutter application.

- Default product workflow: one concise design checkpoint only when material decisions require it, then plan/implement/test/review/PR without asking the user to approve a second technical plan.
- Preserve the upstream Superpowers project unchanged. Its mandatory interactive approvals are incompatible with the autonomous default; it is available only as a separately opted-in interactive workflow.
- The default model is GPT-6 Luna medium. GPT-6.2 Sol medium is for complex architecture or hard diagnosis, not routine calls. Prefer one Luna medium final reviewer pass; avoid repeated full reviews.
- Work on a feature branch in the current checkout by default. Preserve unrelated local edits; never reset, stash, commit or stage them without authorization.
- Prefer official Flutter/Dart tools, targeted tests and deterministic scripts. Use Maestro for Android/iOS mobile scenarios and Playwright for Web. Do not loop on incompatible Maestro Web semantics.
- Never claim a test, iOS Simulator run, build, UI observation or model-cost reduction without evidence. Report PASS / FAIL / BLOCKED / SKIPPED separately.
- After an agreed feature is implemented, attempt push + PR by default. Respect the interactive push permission; report BLOCKED if denied. The owner alone merges PRs or approves changed golden screenshots.
- No destructive Git operations, force pushes, releases, production secrets or permission bypass. MCP and shell permissions are guardrails, not a sandbox.
- Keep session usage reports local and sanitized; do not commit private conversation exports. This repo is separate from https://github.com/halsab/flutter-harness-lab.
