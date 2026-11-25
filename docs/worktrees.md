# Task worktrees

Owner runs workspace.py from primary project checkout after installing and merging the same Harness revision into integration. Close other OpenCode sessions using the same simulators first.

Single and Parallel use the same mechanism. Maximum three registered worktrees per repository. Create in priority order: first free ready iOS, Android, Web slot (one per platform across this OS user's Harness projects). Web only in mobile-web. Use --only for platform-specific tasks. Reservations persist until merged cleanup. No automatic device boot, reset or lease stealing.

```sh
python3 .flutter-harness/bin/workspace.py create profile
python3 .flutter-harness/bin/workspace.py create auth
python3 .flutter-harness/bin/workspace.py create localization
```
In three separate terminals from primary checkout, run workspace.py run NAME and submit the real task. The wrapper uses the exact working directory and holds a session lock. Guard uses current Git working-copy root, not shared canonical project root. If OpenCode location differs, fail closed. Do not use a desktop worktree picker until local compatibility is verified.

Each agent executes existing begin/check/runtime/review/deliver on assigned branch and device. Source, ignored receipts, build outputs and Web ports are separate. Native CLI operations honor platform leases and short operation locks. External/manual tools and older Harness installations are not isolated by these workflow guards. Use isolated test accounts/fixtures and backend namespaces. Dependencies are sequential; do not run incompatible shared navigation/schema/dependency changes without agreed contracts.

Close TUIs after delivery. No merge during batch development.
```sh
python3 .flutter-harness/bin/workspace.py verify-batch profile auth localization
python3 .flutter-harness/bin/workspace.py next
```
The first command verifies exact open PR heads against local delivery receipts, then merges cumulative prefixes in a temporary detached worktree and runs canonical CI on each. No pushes or remote merges. Conflict or test failure stops with a log and task name. Resolve in task worktree, repeat acceptance and delivery; then revalidate. No automatic semantic conflict resolution.

The next command checks PR states/heads and actual base tree against verified prefix. Merge returned PR manually (squash or merge commit, with exact head and green GitHub checks), then run next again. Base/head/order drift invalidates the batch. Strict branch protection may require update and CI; never bypass it. Merge Queue optional later.

After merge and closing TUI:
```sh
python3 .flutter-harness/bin/workspace.py clean profile
```
Cleanup requires exact delivered head merged, clean worktree, no live wrapper and correct slot. Git worktree remove without force; branch/history retained. Git may refuse removal if ignored files remain. Preserve work; no automatic destructive cleanup. Interrupted creation or stale reservations require explicit owner inspection. Never steal a live slot.

Compatibility is limited to tested trees and test coverage. Local automated tests do not prove actual OpenCode bindings or three simultaneous runtime environments. First real batch verifies those; single-task fallback if needed.
