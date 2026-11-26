# Production incident: location-selection delivery

The Vaqtpro task implemented location selection but did not deliver any commit/PR. The transcript showed repeated iOS captures after Android manifest, configuration and regression-test changes, six owner UI interactions, and review exhaustion. No full token export was supplied; elapsed intervals may overlap.

## Changes in this PR
- Separate full acceptance identity from task/platform visual inputs, with original capture provenance and fixture/script checks.
- Script interactions in Maestro/Playwright; reuse existing evidence before launch.
- Local checkpoint command and clean-candidate manifest preparation.
- Exact standard check reuse; targeted review with prior actual findings and per-file hashes; bounded two repair rounds.

## Still to evaluate in the real Lab
- Device automation reliability, browser selectors, startup/fixture stability, and actual resource savings.
- Fine-grained per-state visual dependencies beyond the conservative platform scope; shared Dart changes still invalidate screenshots.
- Explicit owner-authorized recovery/draft-only publication after exhaustion; no automatic bypass or false completion in this PR.
- Migrate or safely salvage an already-blocked app checkout separately; never overwrite its active dirty work.

Acceptance: regression suite and CI green, then repeat the same production scenario on a fresh task with no routine owner UI interaction and a verified delivery receipt. Compare local diagnostics and usage rather than inventing savings.
