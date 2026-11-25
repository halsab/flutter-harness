import test from "node:test";
import assert from "node:assert/strict";
import { taskIntent, changed, decide, recovery } from "../plugins/delivery-guard/guard.mjs";
const base = { head: "abc", branch: "app", status: "" };
test("detects feature intent without treating a question as work", () => {
  assert.equal(taskIntent("Добавь счётчик задач"), true);
  assert.equal(taskIntent("Улучши поиск"), true);
  assert.equal(taskIntent("Как устроен Flutter?"), false);
});
test("the aborted counter run is incomplete", () => {
  const result = decide(base, { ...base, status: " M lib/main.dart" }, true, false, "No PR");
  assert.equal(result.passed, false);
  assert.equal(result.reasons.length, 3);
});
test("REGRESSION: initially dirty task committed to a clean PR is complete", () => {
  const initiallyDirty = { head: "abc", branch: "app", status: " M lib/main.dart" };
  const delivered = { head: "def", branch: "feature/counter", status: "" };
  const result = decide(initiallyDirty, delivered, true, true, "PASS PR");
  assert.equal(result.passed, true);
  assert.deepEqual(result.reasons, []);
});
test("unchanged unrelated preexisting modifications do not block a valid PR", () => {
  const initiallyDirty = { head: "abc", branch: "app", status: "?? private-notes.txt" };
  const delivered = { head: "def", branch: "feature/counter", status: "?? private-notes.txt" };
  assert.equal(decide(initiallyDirty, delivered, true, true, "PASS PR").passed, true);
});
test("a dirty worktree with newly changed files still blocks delivery", () => {
  const initiallyDirty = { head: "abc", branch: "app", status: " M notes.txt" };
  const incomplete = { head: "def", branch: "feature/counter",
    status: " M notes.txt\n M lib/main.dart" };
  const result = decide(initiallyDirty, incomplete, true, true, "PASS PR");
  assert.equal(result.passed, false);
  assert.ok(result.reasons.some(reason => reason.includes("uncommitted")));
});
test("initially dirty and still dirty after a different edit is not completed", () => {
  const initiallyDirty = { head: "abc", branch: "app", status: " M lib/main.dart" };
  const incomplete = { head: "def", branch: "feature/counter", status: " M test/widget_test.dart" };
  assert.equal(decide(initiallyDirty, incomplete, true, true, "PASS PR").passed, false);
});
test("complete pushed feature with PR passes", () => {
  assert.equal(decide(base, { head: "def", branch: "feature/counter", status: "" }, true, true, "").passed, true);
});
test("a remote PR alone cannot complete a task without local evidence", () => {
  const delivered = {head:"def",branch:"feature/search",status:""};
  const result = decide(base,delivered,true,false,"Missing delivery-result.json");
  assert.equal(result.passed,false);
  assert.match(result.reasons.join(";"),/Missing delivery-result/);
});
test("a chat without edits does not require PR", () => {
  assert.equal(decide(base, base, false, false, "").active, false);
});
test("no-op feature request must not silently end", () => {
  assert.equal(decide(base, base, true, false, "").passed, false);
});
test("existing PR does not hide uncommitted work", () => {
  assert.equal(decide(base, { head: "def", branch: "feature/counter", status: " M lib/main.dart" }, true, true, "").passed, false);
});
test("feature branch change counts as activity", () => {
  assert.equal(changed(base, { ...base, branch: "feature/new" }), true);
});

test("recovery repairs checks before publication and stops without progress", () => {
  const result={current:base,reasons:["PR missing"]};
  const evidence={phase:"check",issue:"check failed",check:"failed",digest:"a"};
  const first=recovery({attempts:0},result,evidence);
  assert.equal(first.stop,false);
  assert.match(first.prompt,/earliest failed/);
  assert.equal(recovery({attempts:1,lastRecovery:first.fingerprint},result,evidence).stop,true);
  const changed={...evidence,digest:"b"};
  assert.equal(recovery({attempts:1,lastRecovery:first.fingerprint},result,changed).stop,false);
  assert.equal(recovery({attempts:2},result,changed).stop,true);
});
test("review or delivery recovery reuses existing successful checks", () => {
  const result={current:base,reasons:["PR missing"]};
  const q={phase:"review",issue:"review missing",check:"passed",digest:"a"};
  assert.match(recovery({attempts:0},result,q).prompt,/Reuse the successful standard evidence/);
  assert.match(recovery({attempts:0},result,{...q,phase:"work",issue:""}).prompt,/do not repeat builds/);
});

test("visual progress participates in recovery; exhausted budget stops immediately",()=>{
  const result={current:base,reasons:["incomplete"]};
  const q={phase:"visual",issue:"missing",digest:"a",check:"passed",visualDigest:"one"};
  const first=recovery({attempts:0},result,q);
  assert.match(first.prompt,/Do not dispatch a reviewer/);
  assert.equal(recovery({attempts:1,lastRecovery:first.fingerprint},result,{...q,visualDigest:"two"}).stop,false);
  assert.equal(recovery({attempts:0},result,{...q,phase:"blocked"}).stop,true);
});

test("Build-only hook scope follows the live selected agent and excludes children", async () => {
  const {buildOnly} = await import("../plugins/delivery-guard/scope.mjs");
  const sessions = new Map();
  const hooks = new Map();
  const domain = name => ({hook: async (event, callback) => hooks.set(name + "/" + event, callback)});
  const raw = {
    session: {...domain("session"), get: async ({sessionID}) => sessions.get(sessionID)},
    tool: domain("tool"),
    permission: domain("permission"),
  };
  const ctx = buildOnly(raw);
  let calls = 0;
  const handler = async event => { calls++; event.handled = true; };
  for (const name of ["prompt","context","experimental.idle"]) await ctx.session.hook(name, handler);
  for (const name of ["execute.before","execute.after"]) await ctx.tool.hook(name, handler);
  await ctx.permission.hook("evaluate", handler);
  const fire = async (expected) => {
    for (const [name, hook] of hooks) {
      const event = {sessionID:"s", tool:"subagent", action:"shell", effect:"allow"};
      await hook(event);
      assert.equal(Boolean(event.handled), expected, name);
      assert.equal(event.effect, "allow");
    }
  };
  for (const agent of ["plan", "ask", "review", "reviewer", "custom", undefined]) {
    sessions.set("s",{agent});
    await fire(false);
  }
  sessions.set("s",{agent:"build",parentID:"other"});
  await fire(false);
  assert.equal(calls,0);
  sessions.set("s",{agent:"build"});
  await fire(true);
  assert.equal(calls,6);
  // A previously active Build session may be switched to a conversational agent.
  sessions.set("s",{agent:"plan"});
  await fire(false);
  assert.equal(calls,6);
  sessions.set("s",{agent:"build"});
  await fire(true);
  assert.equal(calls,12);
  const conflicting = {sessionID:"s",agent:"review"};
  await hooks.get("session/context")(conflicting);
  assert.equal(conflicting.handled,undefined);
  const read = {sessionID:"s",tool:"read"};
  await hooks.get("tool/execute.before")(read);
  assert.equal(read.handled,undefined);
});
