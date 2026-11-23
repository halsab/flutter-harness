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
| Complex architecture or hard diagnosis | `architect` | GPT-6.2 Sol | medium |
| Explicit manual planning | `plan` | GPT-6.2 Sol | medium |
| Title, summary, compaction | maintenance agents | GPT-6 Luna | low |

The autonomous default does **not** force an architect consultation for
simple CRUD features. Use `reviewer` once with a fresh subagent context: pass
requirements and changed code, without the author's self-assessment. Request
concrete failing scenarios and evidence, not a numerical score or generic
style complaints. `build` fixes confirmed important issues and can request
**one targeted recheck** of a high-risk correction. Do not start a five-round
review loop by default. Scope the review to the full task diff against the
integration branch's merge base, plus task-related uncommitted and untracked
files; `git diff HEAD` alone misses earlier task commits. Require a location,
realistic failure scenario, impact and evidence for every accepted finding.
Mark review OPEN if material findings or relevant failed checks remain; do not
mislabel a blocked platform test as a pass. Reviewer shell is deliberately
read-only: run `git status --short`, `git merge-base app HEAD`, and
`git diff --no-ext-diff <literal-base-sha>` as **separate** calls; use
`read` to inspect files rather than `cat`. Chaining with `&&`, `;`
or `$(...)` matches neither the safe whitelist nor the review contract.
If any relevant diff/new file is inaccessible, report review **OPEN**, not
PASSED. Do not grant `shell *` to workaround denied commands.

For large unfamiliar codebases, use one read-only `explore` (Luna low) request
for a concise map of file paths, key symbols, callers and relevant tests. The
implementer verifies cited code. Skip this delegation for small/focused tasks.

This adapts the useful independent-review principle from
[Loop Code Review](https://github.com/di-sukharev/loop-code-review-skill)
without installing its repeated reviewer/fixer loop. The original skill's
up-to-five rounds and strong high-effort model for stored-data changes would
increase usage and conflict with our read-only reviewer. The related
[Code Scout](https://github.com/di-sukharev/code-scout-skill) is helpful only
when locating code in a large/unfamiliar repository; for a tiny Flutter app,
one extra subagent can cost more than it saves. The author's
[Orchestration](https://github.com/di-sukharev/orchestration-skill) and
[Refactoring](https://github.com/di-sukharev/refactoring-skill) use expensive
multi-agent loops and remain optional.

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

## Tools and context budget

- Discover Android and iOS devices first (`flutter devices`, Maestro device listing;
  on macOS check `xcrun simctl list devices booted`). A booted iOS Simulator
  must receive a Maestro UI scenario for any relevant mobile feature even if
  the Android flow already passed. If unavailable, document iOS BLOCKED and
  the concrete reason; an iOS build is separate evidence. Use **Playwright**
  for Flutter Web. Do not spend dozens of attempts trying Maestro Web text
  selectors or unsupported keyboard commands.
- Assert the **exact expected persisted result** after relaunch. If a typing
  operation accidentally duplicates a suffix, fix the input action and rerun;
  never replace an expected value with the observed wrong value to make a test pass.
- Report separate Android/iOS/Web statuses, target IDs, key assertions and
  evidence. Distinguish a successful build, UI test and unavailable platform.
- Chrome DevTools MCP remains configured but `disabled: true` by default.
  Enable it temporarily only when Playwright cannot diagnose a browser bug.
- For a repeated failing tool command, stop after two attempts at the same
  approach, inspect a small diagnostic and change strategy or report a blocker.
- Minimize large search outputs, repeated config dumps, simultaneous MCP
  discovery, long plans and unnecessary full-codebase reviews. The model
  processes tool outputs in context. The MCP server itself is not necessarily
  a separate paid LLM call.
- These are **soft usage preferences**, not token, money or call caps. A
  cheaper model can also spend more total tokens if it loops; compare
  observed results rather than assuming exact savings.

Use the stdlib-only session reporter in the harness repository:

```bash
opencode session export SESSION_ID --sanitize > /tmp/parent.json
python3 scripts/session-usage.py /tmp/parent.json /tmp/child.json
```

Include exports of child sessions to account for delegated models. The
report lists raw input/output/reasoning/cache counters, calls to tools, and
agent/model variants. It is not a monetary bill or an exact context-window
cost. Keep exports out of git. Individual invocations and reasoning efforts
must be checked in actual session exports; static config tests only verify
declared defaults. A GUI-selected OpenCode variant can persist per session;
the second lab trial's `build` export used Luna **high** despite a project
default of **medium**. Confirm the displayed variant in a **new** interactive
session before testing. Do not attribute High usage to the Harness default
without checking the active session.

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
