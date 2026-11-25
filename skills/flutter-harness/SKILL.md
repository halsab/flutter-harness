---
name: flutter-harness
description: Focused verification guidance for unusual Flutter delivery risks; not needed for routine work.
---

# Flutter Harness — exceptional verification

AGENTS.md is the ordinary workflow. Do not load another skill for a task
already covered there. Use direct CLI and existing scripts; trust actual
exit status and evidence, not a model's declaration.

Read only the relevant canonical guide, if not already in context:
- Foundation, architecture or material UI: .flutter-harness/PRODUCT.md.
- Material behavior: .flutter-harness/templates/product/BEHAVIOR.md.
- Substantial visual work: .flutter-harness/templates/product/DESIGN.md.
- Complex planning, delegation, recovery: .flutter-harness/templates/product/ORCHESTRATION.md.

## Risk-specific verification

For persistent-data writes, seed storage, reject only the write, reload and
assert retained records. A widget fake that only throws is not a replacement
for a meaningful storage regression test. Verify sorting in supported orders,
ties when relevant, selected state and interaction with other controls;
assert saved data is unchanged when the operation is presentation-only.

For required runtime E2E, seed known state and use executable assertions.
For Web use the compiled preview and Playwright. A server READY or build PASS
is not UI PASS. For transient device/input problems allow one diagnostic and
one changed attempt; report BLOCKED if unresolved.

For required independent review provide the original request, contract,
whole task diff, tests and actual runtime captures for material UI changes.
Reviewer uses separate permitted Git commands and the read tool; no chained
shell commands. A failed or incomplete review is not PASS. Follow the
plugin's actual variant, same-candidate evidence and attempt limits.
After a material correction run affected checks and one final confirmation;
at most one targeted re-review. Preserve permission and delivery gates.

The scripts and plugin enforce only their implemented predicates, not
semantic correctness. Keep product/visual judgment with the agent and owner.
