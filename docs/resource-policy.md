# Resource policy (initial tuning)

The goal is accepted behavior per total usage, not the shortest answer or
fewest calls at any cost. Do not replace required evidence with model claims.
Use the existing session-usage.py on parent and every child export. Report
elapsed wall time, raw input/output/reasoning/cache counters by role and
variant, tool calls, retries and accepted/unresolved defects. Counters may
overlap; they are not subscription balances, prices or provider billing.

| Work | Default |
| --- | --- |
| Parent implementation/integration | Luna Medium |
| Complex plan or hard diagnosis | Luna High when needed |
| Small independent stable-contract worker | Luna Low; at most two declared running |
| Optional compact architectural decision | Sol Medium; one attempted advisor call |
| Required independent review | Luna Medium or High; at most two attempts |

Large diff still requires review; automatic xhigh is removed provisionally,
not a claim that High is equivalent. Use complete integrated diff, original
request, behavior contract and meaningful evidence. Avoid unrelated source
dumps, duplicate reviewer context and repeated platform builds.

The plugin counts attempts before the supported subagent tool dispatch,
forces advisor to Sol Medium and rejects explicit Sol overrides on other
roles in the tracked task. Failed attempts consume budget; counters survive
automatic continuations in the same root session. A new root session is
not linked automatically. The before-hook rejection and actual model
routing must be validated in the installed OpenCode version. These are
workflow guardrails, not a sandbox or a provider-enforced token limit.
No automatic model invocation is made by the resource guard.

A check failure remains a failure until actual current-candidate evidence
passes. Recovery is phase-aware and stops early if the source/check/PR
fingerprint is unchanged. It never authorizes push or bypasses the quality
gate. The behavior specification under docs/product is part of the
candidate hash, so edits cannot silently reuse stale review evidence.
External errors, no-progress cases and exhausted attempts remain visible.
Do not invent a hard token quota from unavailable subscription telemetry.

Compare live trials with actual user-visible acceptance, not CI alone.
Keep changes provisional until measured on the installed environment.
