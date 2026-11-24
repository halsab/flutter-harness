# Large-task orchestration

Use for genuinely broad or coupled work, not a new mandatory ritual.
Ordinary small fixes/features stay in the Medium build session.

## Roles and lifecycle

The Medium build agent is the sole coordinator and delivery owner. Fetch and
verify the integration base before edits; preserve unrelated work. For complex
work call the read-only architect (Luna High) once with original intent,
current behavior/contract, relevant code, tests, and constraints. Ask it to
trace actual dependencies, callers, consumers, data ownership, state
transitions, side effects, failure paths and compatibility. It returns
proposed product rules, affected boundaries and a dependency graph, not
code or a file-based checklist alone. High effort is more reasoning, not
a larger context window. Parent resolves omissions and freezes the compact
behavior contract. Consult again only for material newly discovered risk,
not as a second default planning round. No automatic Sol.

Split by independently verifiable outcome and stable interfaces, not by an
arbitrary line count or one agent per file. Include expected input/output,
preserved behavior, dependencies, exact reads/writes, and observable
acceptance. Keep migrations, schema/API changes and shared foundations
sequential; settle interface contracts before dispatching consumers.
For a significant visual change establish the intended design before
delegating its implementation. A slice must be small enough for a worker
to understand and check without rereading the entire project.

## Durable plan

Parent writes one branch/task-specific local manifest under
.flutter-harness/work/ (ignored, not a committed product spec). Keep it
through interruption/compaction; on resume reconcile it with actual
Git diff, child sessions and check evidence. Do not reuse a stale plan
for a different base or silently mark unknown work complete.

Example plan.json (illustrative paths, replace with actual project paths):

    {
      "schema": 1,
      "goal": "Group and sort tasks without changing storage",
      "tasks": [
        {
          "id": "projection",
          "goal": "Implement pure grouping/sort per frozen contract",
          "depends_on": [],
          "reads": ["lib/features/tasks/models/task_item.dart"],
          "writes": ["lib/features/tasks/models/task_list_view.dart"],
          "acceptance": ["Grouped A-Z/Z-A; stable ties; no storage mutation"],
          "status": "pending"
        },
        {
          "id": "sort-control",
          "goal": "Present selected criterion using the frozen interface",
          "depends_on": [],
          "reads": [],
          "writes": ["lib/features/tasks/widgets/sort_control.dart"],
          "acceptance": ["Selected criterion and direction are visible"],
          "status": "pending"
        },
        {
          "id": "integration",
          "goal": "Connect projection and controls; test their interaction",
          "depends_on": ["projection", "sort-control"],
          "reads": ["lib/features/tasks/models/task_list_view.dart", "lib/features/tasks/widgets/sort_control.dart"],
          "writes": ["lib/features/tasks/screens/task_list_screen.dart", "test/widget_test.dart"],
          "acceptance": ["Order/filter/query/grouping interaction passes targeted tests"],
          "status": "pending"
        }
      ]
    }

Use explicit concrete file paths for all material read/write conflicts.
Use dependencies for semantic coupling even with no overlapping files.
Only the parent edits the manifest and shared contracts.
Commands (from project root):

    python3 .flutter-harness/bin/task-plan.py check PATH/plan.json
    python3 .flutter-harness/bin/task-plan.py ready PATH/plan.json
    python3 .flutter-harness/bin/task-plan.py complete PATH/plan.json

ready lists at most two compatible pending task IDs with done prerequisites,
respecting running tasks. It checks declared paths only, not actual tool
permissions or semantic independence. Do not treat it as an execution sandbox.
Before dispatch mark selected slices running; after the actual final result,
inspect changes and run the smallest meaningful checks; mark done with a
nonempty evidence note only if accepted. Otherwise mark failed, repair and
return to pending (revalidate the graph if affected boundaries change).
Parent can execute a ready slice directly. If a slice has no work to do,
explain and amend the plan rather than invent evidence.

## Dispatch and integration

Worker (Luna Low) is for a simple stable-contract code/test slice. Give it
the slice goal, exact owned files, prerequisite decisions, interfaces,
acceptance examples, forbidden scope and relevant paths. It edits only
assigned files and returns changed paths, outcome, possible regressions,
and suggested targeted checks. Worker has no shell; parent runs checks
and owns dependency installs, shared build cache, simulator/browser, Git
operations, contract amendments and tests requiring shared resources.
Keep consequential data/state/security/complex work with the Medium parent.

At most two workers concurrently, only if contracts are frozen and all
read/write dependencies and ownership are known. Shared reads are fine;
read/write or write/write conflicts are not. Use sequential execution
when uncertain. This first version uses one checkout with instructed file
ownership, not enforced per-worker edit locks or automatic worktree merges.
Inspect actual diffs; unexpected writes/conflicts mean stop parallel
dispatch and reconcile without overwriting unrelated changes. Do not launch
competing Flutter commands, edit manifests or lockfiles concurrently.
Read-only investigation can overlap independent work when it cannot see
unstable intermediate contracts.

OpenCode V2 supports child sessions with fresh context and background
execution. Retain returned session IDs and wait for actual completion,
not the initial tool acknowledgement or a partial report. Do not send
the final user answer while children are running. Do not ask the user to
switch agents, choose parallel vs sequential, or copy results. After each
accepted slice select the next ready wave. Resume from the manifest after
compaction. If there is no ready work and unresolved failure, diagnose
the root cause and make a changed attempt rather than repeat the same
prompt. Use bounded recovery; no premium escalation. Report INCOMPLETE
if still unresolved, preserving progress.

Finally check complete, integrate and review cross-slice behavior against
the original request/contract, including states and side effects spanning
slices. Run existing final standard and risk-based independent review
once on the actual integrated candidate (and bounded recheck if needed).
One task branch and one PR, only parent publishes; never auto-merge.
Do not call every local child or intermediate check a delivered feature.

## Measure before increasing concurrency

Capture actual models/variants, total parent+child input/output/reasoning
tokens, elapsed time, number of slices, failed attempts and material
defects. Parallel execution may save wall time while increasing tokens.
Two workers is an initial limit, not a proven optimum or provider quota.
Do not widen until a live trial demonstrates benefit. The plan checker
does not force dispatch, wait or completion at the OpenCode runtime level;
that enforcement can be considered after the workflow is tested.
