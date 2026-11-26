# Deterministic architecture

One task, one ordinary Git branch, one Build agent. OpenCode handles semantic work; Python CLI handles revision, candidate receipts, native verification, runtime evidence and approved PR delivery. No parallel workers, workspace manager or external controller. Source-first verification; independent code review precedes explicitly selected final automated runtime evidence. Routine UI fixes require no screenshots. Checkpoints preserve work, verified drafts park incomplete tasks, and explicit resume starts fresh acceptance. Bounded recovery and task-window diagnostics use observed state. Install/sync preserves unmanaged source. GitHub CI and owner approval remain independent safeguards; local guard is not a sandbox. No auto-merge.

## Engineering evolution

Prefer guarantees in domain types/APIs and existing analyzer/tests before custom checks, then scoped semantic review and concise instructions. Keep publication safeguards independent. Confirmed recurring defects are inputs to the smallest durable improvement, not automatic justification for a new agent, hook or document. See [engineering-evolution.md](engineering-evolution.md) for ownership and evaluation.

The installed Reporter sends only catalogued, schema-validated failure codes to central owner Issues. On-demand maintenance in the normal local OpenCode session proposes regression-tested fixes from accumulated Issues. No cloud repair workflow, separate credentials, product-repository scanning or in-place self-modification.
