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
  assert.match(first.prompt,/Do not dispatch another reviewer/);
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

test("delivery failures preserve cause and only retry known transient failures", () => {
  const result={current:{...base,branch:"feature/test"},reasons:["Delivery incomplete"]};
  const q={phase:"work",issue:"",check:"passed",digest:"a"};
  const error={code:"PR_URL_MISMATCH",stage:"delivery-pushed",message:"Unexpected PR URL",retryable:false};
  const stop=recovery({attempts:0},{...result,deliveryError:error},q);
  assert.equal(stop.stop,true);
  assert.equal(stop.terminal,true);
  assert.match(stop.reason,/PR_URL_MISMATCH at delivery-pushed/);
  const transient={...error,code:"PR_CREATE_TRANSIENT",retryable:true};
  const first=recovery({attempts:0},{...result,deliveryError:transient},q);
  assert.equal(first.stop,false);
  assert.match(first.prompt,/Preserve the existing delivery.json/);
  const last=recovery({attempts:1,lastRecovery:first.fingerprint},{...result,deliveryError:transient},q);
  assert.equal(last.stop,true);
  assert.match(last.reason,/PR_CREATE_TRANSIENT/);
  assert.equal(recovery({attempts:0},{...result,deliveryError:error},{...q,phase:"check",check:"failed"}).stop,false);
});
test("clean committed candidate with missing manifest must not invent acceptance flags", () => {
  const result={current:{...base,branch:"feature/test"},reasons:["Delivery incomplete"]};
  const q={phase:"manifest",issue:"manifest missing",check:"passed",digest:"a"};
  const stop=recovery({attempts:0},result,q);
  assert.equal(stop.stop,true);
  assert.match(stop.reason,/restore the original manifest/);
  assert.equal(recovery({attempts:0},{...result,current:{...result.current,status:" M lib/main.dart"}},q).stop,false);
});


test("verified delivery closes task without idle; same OpenCode session receives a fresh generation",async()=>{
  const {taskLifecycle}=await import("../plugins/delivery-guard/lifecycle.mjs");
  const values=new Map(),records=[],archives=[],clears=[];
  let current={head:"a",branch:"app",status:"",digest:"base"}, receipt=null;
  const ctx={storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v)},
    session:{synthetic:async()=>{throw Error("unexpected recovery");}}};
  const deps={assertRevision:async()=>{},snapshot:async()=>current,
    completion:async()=>receipt, deliveryIdentity:async()=>({branch:"feature/one",digest:"candidate",checked_at:11}),
    quality:{clear:async(id,t)=>clears.push(t.id),status:async()=>({issue:"",phase:"work"})},
    resources:{clear:async()=>{},status:async()=>""},
    record:async(id,stage)=>records.push(stage),saveSessions:async()=>{},archive:async t=>archives.push(t.id),
    inspect:async()=>({active:true,passed:false,current,reasons:["not delivered"]}),lastBegin:async()=>null};
  const life=taskLifecycle(ctx,deps), prompt=text=>life.prompt({sessionID:"root",prompt:{text}});
  const task=()=>values.get("task/root");
  await prompt("Добавь функцию");const first=task().id;
  const delivery={tool:"shell",sessionID:"root",id:"deliver-one",input:{command:"python3 .flutter-harness/bin/harness.py deliver"}};
  await life.authorize(delivery,task());
  receipt={status:"PASS",branch:"feature/one",head:"b",digest:"old",checked_at:11,delivered_at:Math.floor(Date.now()/1000)};
  await life.delivered({...delivery,status:"completed",result:{metadata:{exit:0}}});
  await prompt("Продолжи задачу");assert.equal(task().id,first);
  receipt={...receipt,digest:"candidate"};
  current={branch:"feature/one",head:"b",status:"",digest:"candidate"};
  await life.delivered({...delivery,status:"completed",result:{metadata:{exit:0}}});
  assert.equal(task().active,false);
  assert.deepEqual(archives,[first]);assert.deepEqual(clears,[first]);
  await prompt("Исправь другую ошибку");
  assert.notEqual(task().id,first);assert.equal(task().lastCompletedBranch,"feature/one");
  assert.equal(task().attempts,0);assert.equal(task().request,"Исправь другую ошибку");
  await life.delivered({...delivery,status:"completed",result:{metadata:{exit:0}}});
  assert.equal(task().active,true);assert.equal(records.filter(x=>x==="task-complete").length,1);
});

test("next prompt reconciles interrupted completion, but preserves unfinished budgets",async()=>{
  const {taskLifecycle}=await import("../plugins/delivery-guard/lifecycle.mjs");
  const values=new Map();let receipt=null;
  const ctx={storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v)},session:{synthetic:async()=>{}}};
  const life=taskLifecycle(ctx,{assertRevision:async()=>{},snapshot:async()=>base,completion:async()=>receipt,
    deliveryIdentity:async()=>({branch:"feature/one",digest:"candidate",checked_at:1}),
    quality:{clear:async()=>{}},resources:{clear:async()=>{},status:async()=>""},record:async()=>{},saveSessions:async()=>{},archive:async()=>{},lastBegin:async()=>({stage:"begin"})});
  const prompt=()=>life.prompt({sessionID:"root",prompt:{text:"Добавь функцию"}});
  const task=()=>values.get("task/root");
  await prompt();const first=task().id;
  values.set("task/root",{...task(),attempts:2});
  await prompt();assert.equal(task().id,first);assert.equal(task().attempts,2);
  await life.authorize({sessionID:"root",id:"deliver"},task());
  receipt={status:"PASS",branch:"feature/one",digest:"candidate",head:"new",checked_at:1,delivered_at:Math.floor(Date.now()/1000)};
  await prompt();assert.notEqual(task().id,first);assert.equal(task().attempts,0);
});

test("read-only conversation does not require delivery, but a begun or recovering task cannot reset",async()=>{
  const {taskLifecycle}=await import("../plugins/delivery-guard/lifecycle.mjs");
  const values=new Map();let begin=null,waiting="",continuations=0;
  const ctx={storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v)},
    session:{synthetic:async()=>{continuations++;}}};
  const life=taskLifecycle(ctx,{assertRevision:async()=>{},snapshot:async()=>base,
    completion:async()=>null,quality:{clear:async()=>{},status:async()=>({phase:"check",issue:"missing",check:"missing"})},
    resources:{clear:async()=>{},status:async()=>waiting},record:async()=>{},saveSessions:async()=>{},archive:async()=>{},
    inspect:async()=>({active:false,passed:true,current:base,reasons:[]}),lastBegin:async()=>begin});
  const prompt=()=>life.prompt({sessionID:"root",prompt:{text:"Как устроен Flutter?"}});
  const idle=()=>life.idle({sessionID:"root"});
  const task=()=>values.get("task/root");
  await prompt();waiting="child running";await idle();assert.equal(task().active,true);
  waiting="";await idle();assert.equal(task().active,false);assert.equal(continuations,0);
  await prompt();begin={stage:"begin"};const id=task().id;
  await idle();assert.equal(task().active,true);assert.equal(task().attempts,1);
  begin=null;await prompt();assert.equal(task().id,id);
  await idle();assert.equal(task().active,true);assert.equal(task().finalReminder,true);
  const count=continuations;await idle();assert.equal(continuations,count);
});

 test("clean local checkpoints may prepare a first delivery manifest",()=>{
  const result={current:{status:""},publicationStarted:false,reasons:["Delivery incomplete"]};
  const next=recovery({attempts:0},result,{phase:"manifest",issue:"manifest missing",check:"passed",digest:"a"});
  assert.equal(next.stop,false);
  assert.match(next.prompt,/prepare-delivery/);
});

test("Plan to Build: no-start recovery never enters check gate, retires failed start and permits explicit retry",async()=>{
  const {taskLifecycle}=await import("../plugins/delivery-guard/lifecycle.mjs");
  const values=new Map(),records=[],reminders=[];
  let current={...base,digest:"unchanged"},begin=null;
  const ctx={storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v)},
    session:{synthetic:async e=>reminders.push(e.text)}};
  const life=taskLifecycle(ctx,{assertRevision:async()=>{},snapshot:async()=>current,
    completion:async()=>null,lastBegin:async()=>begin,
    inspect:async()=>({active:true,passed:false,current,reasons:["No task change"]}),
    quality:{clear:async()=>{},status:async()=>{throw Error("must not enter check gate before begin");}},
    resources:{clear:async()=>{},status:async()=>"",sessions:async id=>[id]},
    record:async(id,stage)=>records.push(stage),saveSessions:async()=>{}});
  const prompt=()=>life.prompt({sessionID:"root",prompt:{text:"реализуй"}});
  const idle=()=>life.idle({sessionID:"root"});
  const task=()=>values.get("task/root");
  await prompt();const first=task().id;
  await idle();assert.equal(reminders.length,1);assert.match(reminders[0],/root Build implementation agent/);
  assert.match(reminders[0],/canonical begin/);
  await idle();assert.equal(task().active,false);assert.equal(task().outcome,"NOT_STARTED");
  assert.ok(records.includes("task-not-started"));assert.ok(!records.includes("task-complete"));
  assert.equal(reminders.length,1);
  await prompt();assert.notEqual(task().id,first);assert.equal(task().attempts,0);
  // A legacy no-start task already exhausted its idle budget.
  const second=task().id;
  values.set("task/root",{...task(),attempts:2});
  await prompt();assert.notEqual(task().id,second);assert.equal(task().attempts,0);
  // A genuinely begun task must retain its generation and budget.
  begin={stage:"begin"};
  const third=task().id;
  values.set("task/root",{...task(),attempts:2});
  await prompt();assert.equal(task().id,third);assert.equal(task().attempts,2);
});


test("verified draft parks without PASS and permits a new task",async()=>{
  const {taskLifecycle}=await import("../plugins/delivery-guard/lifecycle.mjs");
  const values=new Map(),records=[];
  const snap={head:"a",branch:"feature/parked",status:"",digest:"candidate"};
  let draft=null;
  const ctx={storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v)},session:{synthetic:async()=>{}}};
  const life=taskLifecycle(ctx,{assertRevision:async()=>{},snapshot:async()=>snap,completion:async()=>null,draftCompletion:async()=>draft,
    quality:{clear:async()=>{}},resources:{clear:async()=>{},status:async()=>""},
    record:async(id,stage)=>records.push(stage),saveSessions:async()=>{},archive:async()=>{},lastBegin:async()=>({stage:"begin"})});
  const prompt=()=>life.prompt({sessionID:"root",prompt:{text:"реализуй"}});
  const task=()=>values.get("task/root");
  await prompt();const old=task().id;
  await life.authorizeDraft({sessionID:"root",id:"draft"},task());
  draft={...snap,status:"DRAFT_SAVED",saved_at:Date.now()};
  await life.delivered({tool:"shell",sessionID:"root",id:"draft",status:"completed",result:{metadata:{exit:0}}});
  assert.equal(task().active,false);
  assert.equal(task().outcome,"DRAFT_SAVED");
  assert.ok(records.includes("task-parked"));
  assert.ok(!records.includes("task-complete"));
  await prompt();assert.notEqual(task().id,old);
  assert.equal(task().lastParkedBranch,"feature/parked");
});
