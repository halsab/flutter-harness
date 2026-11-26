# Proportionate verification policy

The objective is sufficient evidence of the original request, not completion of a ritual. Choose the cheapest reliable proof. A small task has a small acceptance scope. Preserve the product standard, regression protection, owner approval, exact check receipts and independent full PR CI.

- Source-first: verify concrete source facts (text, colors, sizes, constraints, state, interactions) directly. Add focused behavioral tests where proof is insufficient or a material regression needs protection. For bugs establish the original failure or precise source proof. No quotas, no repeated full suites locally.
- Run one canonical impact check after implementation and again only for affected inputs after material fixes. Checkpoints preserve work; they do not imply acceptance and need not trigger checks.
- Self-review all original criteria. Independent code review for actual material risk or explicit request, with concrete findings and one targeted follow-up ordinarily. Routine styles and paths alone do not mandate visual review. The reviewer can verify corrections statically. Technical failure is not a product defect.
- Final runtime inspection only for material appearance/behavior that cheaper evidence cannot establish. Prefer one already-running affected target and hot reload where supported. No mandatory screenshots, theme matrix, baseline or automation for routine UI. Significant new UI needs an actual final inspection when necessary. Explicit automated acceptance uses capture-plan and exact receipts; specify only needed states/themes, scenarios for real interactions. Do not recapture before review or for source-verifiable corrections. Never claim stale evidence is current.
- Code review is independent of optional automated visual evidence. If explicitly required, that evidence is verified at final delivery, not as admission to code review.
- Use one normal Luna Medium Build. Reviewer Medium for focused changes, High for genuinely broad/critical risk. No automatic premium escalation, extra workers or repeated unchanged reviews.
- After sufficient local checks and review, create the owner-approved PR. Full CI is independent; do not claim CI PASS from local evidence. No automatic merge. Known material defects or missing required acceptance must not be presented as complete. If acceptance stalls, preserve local work and offer an owner-approved Draft PR with outstanding criteria. Never publish without permission.
- Use task-scoped diagnostic facts; compare actual outcomes, elapsed time, checks, reviews and exported token counters in the Lab. Do not infer cost savings from passing Harness unit tests.

See README for CLI operations and the recovery path.
