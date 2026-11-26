# Production incident: location-selection delivery

The Vaqtpro task implemented location selection but did not deliver any commit/PR. The transcript showed repeated iOS captures after Android manifest, configuration and regression-test changes, six owner UI interactions, and review exhaustion. No full token export was supplied; elapsed intervals may overlap.

## Changes in this PR
- Separate full acceptance identity from task/platform visual inputs, with original capture provenance and fixture/script checks.
- Script interactions in Maestro/Playwright; reuse existing evidence before launch.
- Local checkpoint command and clean-candidate manifest preparation.
- Exact standard check reuse; targeted review with prior actual findings and per-file hashes; bounded two repair rounds.
- Explicitly owner-approved one-time review recovery and clean Draft backup, without acceptance or budget reset.

## Still to evaluate in the real Lab
- Device automation reliability, browser selectors, startup/fixture stability, and actual resource savings.
- Fine-grained per-state visual dependencies beyond the conservative platform scope; shared Dart changes still invalidate screenshots.
- Migrate or safely salvage an already-blocked app checkout separately; never overwrite its active dirty work.

Acceptance: regression suite and CI green, then repeat the same production scenario on a fresh task with no routine owner UI interaction and a verified delivery receipt. Compare local diagnostics and usage rather than inventing savings.

The pending-diff guard now enforces a local checkpoint at expensive standard/runtime boundaries for broad uncommitted source/test changes. Review instructions use bounded inspection of generated catalogs to avoid loading megabytes of data into model context.

## Full diagnostic follow-up

Sanitized archive: 4 exported sessions, 355 assistant messages, 469 tool calls, 785,746 uncached input tokens, 66,662 output tokens, 97,877 reasoning tokens and 38,318,720 cache-read tokens. The owner—not the Build agent—manually committed and pushed the work before exporting evidence. Do not treat that commit as autonomous delivery.

The local check now selects affected unit/widget files through Dart dependencies and records its task-base/last-success basis, exact candidate digest, selected tests, skipped steps, uncovered production paths, platform changes and fallback reasons. A failed run cannot advance the last successful basis. Dependency/global/uncertain changes can justify a full run; ordinary fixes do not. Full project PR CI is unchanged. The runtime build receipt uses platform-specific inputs independently of scenario edits; visual evidence retains its own original capture provenance. Native/device integration tests remain separate and must target the actual risk. Deterministic tests exercise incremental selection, failure and retry, runtime reuse and the full CI separation. The archived export is sanitized; exact individual tool arguments and provider costs are not available.

## CI overhead

The successful run 45827919712 on the previous PR head recorded a 1,675,187,314-byte SDK cache restore (~1598 MiB), plus a 24,366,832-byte pub cache. Flutter action setup occupied roughly 4m28s; the starter lifecycle itself took ~22s and the independent SDK-free job ~16s. The routine Harness CI now runs only the SDK-free checks, keeping `material-starter` as a conditional job for starter/product-template and product-policy changes in PRs or manual workflow dispatch. Avoid duplicate real-starter execution on post-merge pushes; manual dispatch is available for SDK/command contracts and direct starter changes on main. Application PR CI remains unchanged. This measures the old run, not a guaranteed future duration.
