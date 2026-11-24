# Design quality experiment v1 (not production policy)

Purpose: establish whether a specialized skill plus visual examples and
pre-implementation concept comparison improve visual quality; compare Luna
Medium with Sol Medium under identical conditions. This is an initial
exploratory trial, not a statistically conclusive model ranking. The
unsatisfactory Lab PR #25 remains an external negative baseline.
No changes to installer, runtime, delivery gates, CI or the Flutter app.

## Prepare

From the Harness checkout on this experiment branch:
```sh
bash experiments/design-quality/prepare.sh "$HOME/Desktop/harness-design-test"
```
Prerequisites: OpenCode authentication, installed Chrome, Python 3 and Node/npm.
A first `npx playwright` invocation may require network access. If unavailable,
report the rendering blocker. No app dependencies are modified.

## Run the same task twice

Open a fresh OpenCode build session in each isolated directory (A and B).
Select GPT-6 Luna Medium for one and GPT-6.2 Sol Medium for the other; record
the mapping privately. Check the actual model/variant in each session export.
Use exactly the same prompt in both:
> Read RUN.md and BRIEF.md and complete the design-only experiment.

Do not add design hints, use subagents, inspect the other run or change the
brief. Finish both runs before evaluation. Do not publish outputs to GitHub.
Each run produces two SVGs, two 390×844 PNGs and a short handoff. Record
elapsed wall time, reported tokens, tool count, model/effort and any blockers.
The browser rendering is visual concept evidence only.

## Judge

First calibrate the evaluator on the teaching pair and, if available, the
rejected PR #25 screenshots. The pair is illustrative, not a gold standard.
Use a fresh evaluation context, the brief and JUDGE.md; provide anonymous
concept images without model identifiers. Record visual ranking before
showing anonymous handoffs or revealing the model mapping. Ask the owner
for one final preference for calibration, not for approval during generation.
If both fail, improve the process rather than crown the lesser failure.
If useful, repeat on a held-out brief:
```sh
bash experiments/design-quality/prepare.sh "$HOME/Desktop/harness-design-holdout" transactions
```
For causal evidence later compare the winning model with and without the
skill/references on identical held-out briefs. Use more than one task and
repeat runs before adopting a routing rule. Evaluate real Flutter fidelity in
a separate experiment. Only then consider installing the skill and enforcing
a scoped design gate. Do not treat SVG scores as app acceptance.
