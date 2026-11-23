import test from "node:test";
import assert from "node:assert/strict";
import { taskIntent, changed, decide } from "../plugins/delivery-guard/guard.mjs";
const base = { head: "abc", branch: "app", status: "" };
test("detects feature intent without treating a question as work", () => {
  assert.equal(taskIntent("Добавь счётчик задач"), true);
  assert.equal(taskIntent("Как устроен Flutter?"), false);
});
test("the aborted counter run is incomplete", () => {
  const result = decide(base, { ...base, status: " M lib/main.dart" }, true, false, "No PR");
  assert.equal(result.passed, false);
  assert.equal(result.reasons.length, 3);
});
test("complete pushed feature with PR passes", () => {
  assert.equal(decide(base, { head: "def", branch: "feature/counter", status: "" }, true, true, "").passed, true);
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
