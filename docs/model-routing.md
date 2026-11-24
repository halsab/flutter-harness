# OpenCode model routing, autonomy and usage

Flutter Harness implements a **short-request → one product checkpoint (when
needed) → implementation/tests/review → PR** workflow. A design approval also
approves routine technical planning and execution within that design. A second
plan signoff, choosing subagent/worktree strategy, or manually requesting a PR
is not part of the default experience.

| Work | Agent | Model | Reasoning |
| --- | --- | --- | --- |
| Default implementation and tooling | `build` | GPT-6 Luna | medium |
| Focused independent final diff review | `reviewer` | GPT-6 Luna | medium |
| Codebase search when beneficial | `explore` | GPT-6 Luna | low |
| Routine delegated work | `general` | GPT-6 Luna | medium |
| Complex architecture or hard diagnosis | `architect` | GPT-6 Luna | medium |
| Explicit manual planning | `plan` | GPT-6 Luna | medium |
| Title, summary, compaction | maintenance agents | GPT-6 Luna | low |

No default role routes to Sol or another premium model. Explicit user model
selection remains possible; do not switch automatically. The autonomous
default does not force an architect consultation or
independent reviewer for simple features. The implementer checks the diff once,
and the standard deterministic Flutter tests/analyzer supply ordinary
verification. Call a fresh read-only Luna reviewer only for material security,
privacy, data migration, architecture or concurrency risk, or explicit request.
If called, supply requirements and the complete task diff, ask for concrete
failure scenarios and do at most one targeted recheck for an important fix.
Never run a repetitive review/fix loop.

If the read-only reviewer is needed, use separate whitelisted git status,
git merge-base and git diff calls, with literal SHAs, and read files via read.
Denials or unavailable changes make review OPEN. Avoid expanding shell access.
Explore/architect subagents are optional for genuinely unfamiliar or complex
problems, not default steps. A simple UI filter does not justify specialist
delegation or high-reasoning escalation.

## Interactive design versus autonomous delivery

Superpowers is a separate, optional **interactive** workflow. It is not
loaded by the default profile, because the first lab trial showed mandatory
design, writing-plans and execution-choice gates. Do not circumvent those
requirements when the owner explicitly opts into Superpowers. The default
project skill instead encodes a lean TDD-style process and a single design
checkpoint. In OpenCode V2, `skill` deny permissions hide the named
interactive skills if installed globally.

Superpowers may also be installed globally. Plugin lists from multiple
OpenCode configuration sources can be merged; after installing the new
profile, inspect `opencode debug config` and verify the effective plugin
and skill set in a **new session**. Static CI cannot demonstrate that a
previously running session has unloaded the old plugin.

## Tools, testing and context budget

Default on ordinary features: run check.sh standard once after implementation,
covering format, analyze and fast Dart unit/widget tests. Add tests only for
important logic and stateful observable behavior. Routine changes do not
require device/browser E2E or a separate reviewer.

Only when concrete risk demands it, run the smallest executable integration
scenario on relevant platform(s); never automatically all Android/iOS/Web.
Use test assertions and runner exit statuses rather than agent visual opinions.
For Web Playwright, the optional web-preview.py serves a built app locally.
Do not confuse build/server READY with a UI PASS.

Establish known initial state and validate results before diagnosing UI
failures. In the third trial the newly added active task was hidden behind
the Completed filter. Repeating clipboard/input tools was unnecessary.
If UI input fails, allow one focused diagnosis and one changed attempt,
then report BLOCKED without long retry loops.

The former verify-e2e.py helper is optional for explicitly requested
all-platform tests; no verification.json is required for ordinary PRs.
Optional E2E NOT RUN is not a blocker. Failed required high-risk checks
or unresolved material review findings require Draft PRs.

Keep MCP discovery bounded, skip whole-project searches for small changes,
and avoid repeated full-codebase reviews. Usage limits are preferences, not
hard enforced model caps. Inspect real session exports to measure overhead.
See docs/verification-policy.md for the risk matrix.

## GitHub and authorization

Use a feature branch in the checkout, preserve unrelated local edits, stage
only task files. Finish a normal feature by pushing the branch and creating a
PR into `app` (lab) or the documented integration branch. Do not treat a
local commit as finished delivery. An OpenCode permission prompt for
`git push`, external directories or `gh api` is not optional. Request
approval, honor denials, report BLOCKED when required and **never auto-merge**.
GitHub rulesets remain the server-side protection. Never update accepted
golden baselines without the owner's explicit decision.

## Model authentication

Use OpenCode's OpenAI **Sign in with ChatGPT** option for eligible subscription
access rather than supplying an API key unintentionally. Select the default
`build` agent in a new session; switching agents in an old session may not
switch the selected model variant. Run `opencode models` and
`opencode debug config`, and confirm actual calls in sanitized exports.
ChatGPT subscription allowances and potential provider limits still apply.

References:
- https://opencode.ai/docs/agents
- https://opencode.ai/docs/permissions
- https://opencode.ai/docs/skills
- https://opencode.ai/docs/mcp-servers
