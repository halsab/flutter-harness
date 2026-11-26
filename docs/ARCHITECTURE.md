# Deterministic architecture

One task, one ordinary Git branch, one Build agent. OpenCode handles semantic work; Python CLI handles revision, candidate receipts, native verification, runtime evidence and approved PR delivery. No parallel workers, workspace manager or external controller. Original screenshot is optional when meaningful comparison is needed; required final evidence remains. Bounded recovery and diagnostics use observed state. Install/sync preserves unmanaged source. GitHub CI and owner approval remain independent safeguards; local guard is not a sandbox. No auto-merge.

## Engineering evolution

Prefer guarantees in domain types/APIs and existing analyzer/tests before custom checks, then scoped semantic review and concise instructions. Keep publication safeguards independent. Confirmed recurring defects are inputs to the smallest durable improvement, not automatic justification for a new agent, hook or document. See [engineering-evolution.md](engineering-evolution.md) for ownership and evaluation.

The installed Reporter sends only catalogued, schema-validated failure codes to central owner Issues. A separately enabled central Evolution workflow proposes regression-tested fixes; it does not inspect product repositories or modify installed Harness in place.
