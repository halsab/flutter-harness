import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";
import { candidate, classify, publishing, standardCheck, finalVerdict, gateReason, registerQualityGate, reviewEffort, matchingReviewModel } from "../plugins/delivery-guard/quality.mjs";

test("risk detection follows actual repository changes, not routine UI wording", () => {
  assert.ok(classify(["lib/data/task_repository.dart"], "routine UI change").length);
  assert.ok(classify(["lib/features/tasks/task_list_screen.dart"], "Добавь возможность удалить все завершённые задачи").length);
  assert.equal(classify(["lib/features/tasks/task_list_screen.dart"], "Измени подпись").length, 0);
  assert.ok(classify(["test/widget_test.dart"], "", ["test/widget_test.dart: preserves records"]).length);
});
test("shared product UI and explicit redesign require review even at small sizes", () => {
  assert.ok(classify(["lib/design_system/theme.dart"],"change palette").length);
  assert.ok(classify(["lib/features/tasks/screens/tasks.dart"],"редизайн UI/UX").length);
  assert.equal(classify(["lib/features/tasks/screens/tasks.dart"],"fix typo").length,0);
  // PR #30 used natural Russian wording rather than the keyword "редизайн".
  const screen = ["lib/features/tasks/screens/tasks.dart"];
  assert.ok(classify(screen,"Переработай интерфейс приложения «Мои задачи», чтобы оно выглядело современно").some(r=>r.includes("material UI")));
  assert.ok(classify(screen,"Переделай экран задач").some(r=>r.includes("material UI")));
  assert.ok(classify(screen,"Создай новый экран истории").some(r=>r.includes("material UI")));
  assert.ok(classify(screen,"Rework the task list interface").some(r=>r.includes("material UI")));
  assert.equal(classify(screen,"Исправь сортировку задач").length,0);
  assert.equal(classify(["test/widget_test.dart"],"Переработай интерфейс").length,0);
  assert.ok(classify(["lib/app/bootstrap.dart"],"Move bootstrap").every(r=>!r.includes("material UI")));
});
test("review effort scales with diff size and risk, not the builder's choice", () => {
  assert.equal(reviewEffort({files:1,lines:20}),"medium");
  assert.equal(reviewEffort({files:3,lines:100}),"medium");
  assert.equal(reviewEffort({files:3,lines:101}),"high");
  assert.equal(reviewEffort({files:4,lines:20}),"high");
  assert.equal(reviewEffort({files:8,lines:400}),"high");
  assert.equal(reviewEffort({files:1,lines:401}),"high");
  assert.equal(reviewEffort({files:9,lines:20}),"high");
  assert.equal(reviewEffort({files:1,lines:8},["destructive operation"]),"high");
  assert.equal(matchingReviewModel({providerID:"openai",id:"gpt-6-luna",variant:"medium"},"high"),false);
  assert.equal(matchingReviewModel({providerID:"openai",id:"gpt-6-luna",variant:"xhigh"},"high"),true);
  assert.equal(matchingReviewModel({providerID:"openai",id:"gpt-6.2-sol",variant:"xhigh"},"high"),false);
});
test("only delivery commands and standard checks match", () => {
  for (const c of ["git push -u origin feature/a", "gh pr create --base app", "gh pr ready 1", "git status && git push"]) assert.ok(publishing(c), c);
  for (const c of ["git diff", "gh pr view 1", "flutter test"]) assert.equal(publishing(c), false);
  // Regression: the default mode is standard, just as in check.sh.
  for (const c of [
    "bash .flutter-harness/bin/check.sh .",
    "bash .flutter-harness/bin/check.sh . standard",
    "bash .flutter-harness/bin/check.sh . standard mobile-web",
    "bash .flutter-harness/bin/check.sh . standard mobile",
    "./.flutter-harness/bin/check.sh .",
  ]) assert.ok(standardCheck(c), c);
  for (const c of [
    "bash .flutter-harness/bin/check.sh",
    "bash .flutter-harness/bin/check.sh . quick",
    "bash .flutter-harness/bin/check.sh . quick mobile-web",
    "echo .flutter-harness/bin/check.sh . standard",
    "bash .flutter-harness/bin/check.sh . standard && echo done",
  ]) assert.equal(standardCheck(c), false, c);
});
test("review requires final exact PASS, not a build-agent claim or earlier PASS", () => {
  const m = text => ({ type: "assistant", content: [{type:"text", text}] });
  assert.ok(finalVerdict([m("No material issues.\nVERDICT: PASS")]));
  assert.equal(finalVerdict([m("VERDICT: PASS"),m("VERDICT: CHANGES_REQUIRED")]), false);
  assert.equal(finalVerdict([m("PASS")]), false);
  assert.equal(finalVerdict([m("VERDICT: PASS")],true),false);
  assert.equal(finalVerdict([m("VISUAL: CHANGES_REQUIRED\nVERDICT: PASS")],true),false);
  assert.ok(finalVerdict([m("Opened actual before/after images.\nVISUAL: PASS\nVERDICT: PASS")],true));
  assert.equal(finalVerdict([m("VISUAL: PASS\nVERDICT: PASS"),m("VERDICT: PASS")],true),false);
});
test("risk requires same-candidate checks and review; ordinary tasks do not", () => {
  const c = {digest:"a",reasons:["storage"]};
  assert.ok(gateReason(c,{passedDigest:"b"},true));
  assert.ok(gateReason(c,{passedDigest:"a"},false));
  assert.equal(gateReason(c,{passedDigest:"a"},true),"");
  assert.equal(gateReason({digest:"a",reasons:[]},{},false),"");
  assert.match(gateReason({digest:"a",reasons:[]},{lastCheckFailed:true},false),/previous standard check failed/);
});
async function fixture(t) {
  const root = await mkdtemp(join(tmpdir(),"harness-quality-"));
  t.after(() => rm(root,{recursive:true,force:true}));
  const git = (...args) => execFileSync("git",args,{cwd:root,stdio:"pipe"});
  git("init","-q","-b","app"); git("config","user.email","test@example.invalid"); git("config","user.name","Fixture");
  await mkdir(join(root,"lib/data"),{recursive:true});
  await mkdir(join(root,"test"),{recursive:true});
  await writeFile(join(root,"lib/data/task_repository.dart"),"void old() {}\n");
  await writeFile(join(root,"test/task_test.dart"),"test('existing', () {});\n");
  git("add","."); git("commit","-qm","base"); git("switch","-qc","feature/bulk");
  await writeFile(join(root,"lib/data/task_repository.dart"),"void deleteCompletedTasks() {}\n");
  return {root,git};
}
test("candidate is stable across commit, records removed failed-test name, and invalidates on edit", async t => {
  const {root,git}=await fixture(t);
  const path=join(root,"test/task_test.dart");
  await writeFile(path,"test('existing', () {});\ntest('keeps stored tasks unchanged', () {});\n");
  const failing=await candidate(root,"app","");
  await writeFile(path,"test('existing', () {});\n");
  const before=await candidate(root,"app","",failing.names);
  assert.equal(before.removed.length,1);
  assert.match(before.removed[0],/keeps stored tasks unchanged/);
  git("add","."); git("commit","-qm","feature");
  const after=await candidate(root,"app","",failing.names);
  assert.equal(after.digest,before.digest);
  assert.deepEqual(after.size,before.size);
  assert.equal(after.effort,"high");
  await writeFile(path,"test('replacement', () {});\n");
  assert.notEqual((await candidate(root,"app","")).digest,after.digest);
});
test("large untracked source counts toward review effort and stays stable after commit", async t => {
  const {root,git}=await fixture(t);
  await writeFile(join(root,"lib/new_feature.dart"),"// generated fixture line\n".repeat(401));
  const before=await candidate(root,"app","");
  assert.equal(before.effort,"high");
  assert.ok(before.reasons.includes("large change requires independent review"));
  git("add","."); git("commit","-qm","large change");
  const after=await candidate(root,"app","");
  assert.equal(after.effort,"high");
  assert.equal(after.digest,before.digest);
  assert.deepEqual(after.size,before.size);
});
test("mock V2 hooks deny risky push until real child PASS at required effort, then preserve ask; stale source blocks again", async t => {
  const {root,git}=await fixture(t);
  const values=new Map([["task/main",{active:true,request:"Удалить все завершённые задачи"}]]);
  const hooks={}; let child={parentID:"main",agent:"reviewer",outcome:"running",model:{providerID:"openai",id:"gpt-6-luna",variant:"medium"}};
  const ctx={
    storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v),remove:async k=>values.delete(k)},
    tool:{hook:async(n,f)=>hooks[n]=f},
    permission:{hook:async(n,f)=>hooks[n]=f},
    session:{get:async()=>child,context:async()=>[{type:"assistant",content:[{type:"text",text:"VERDICT: PASS"}]}]},
  };
  const q=await registerQualityGate(ctx,root,"app",id=>"task/"+id);
  const publish=async()=>{const e={sessionID:"main",action:"shell",resources:["git push -u origin feature/bulk"],effect:"ask"};await hooks.evaluate(e);return e;};
  assert.equal((await publish()).effect,"deny");
  await mkdir(join(root,".flutter-harness"),{recursive:true});
  await writeFile(join(root,".flutter-harness/product.json"),JSON.stringify({status:"active"}));
  const check={tool:"shell",sessionID:"main",id:"check",input:{command:"bash .flutter-harness/bin/check.sh ."}};
  await hooks["execute.before"](check);
  await hooks["execute.after"]({...check,status:"completed",result:{metadata:{exit:0},content:"PASS format\nPASS analyze\nPASS flutter-tests"}});
  assert.equal((await publish()).effect,"deny");
  assert.match(await q.reason("main"),/standard check/);
  await hooks["execute.before"](check);
  await hooks["execute.after"]({...check,status:"completed",result:{metadata:{exit:0},content:"PASS format\nPASS product\nPASS analyze\nPASS flutter-tests"}});
  assert.match(await q.reason("main"),/reviewer verdict/);
  const review={tool:"subagent",sessionID:"main",id:"review",input:{agent:"reviewer",prompt:"Review diff"}};
  await hooks["execute.before"](review);
  assert.match(review.input.prompt,/VERDICT: PASS/);
  assert.equal(review.input.model,"openai/gpt-6-luna#high");
  await hooks["execute.after"]({...review,status:"completed",result:{metadata:{sessionID:"child"}}});
  assert.equal((await publish()).effect,"deny");
  child={...child,outcome:"succeeded"};
  assert.equal((await publish()).effect,"deny", "Medium cannot satisfy a High review");
  child={...child,model:{...child.model,variant:"high"}};
  assert.equal(await q.reason("main"),"");
  assert.equal((await publish()).effect,"ask");
  // Committing identical content does not invalidate the successful default check or review.
  git("add","."); git("commit","-qm","reviewed change");
  assert.equal(await q.reason("main"),"");
  assert.equal((await publish()).effect,"ask");
  await writeFile(join(root,"lib/data/task_repository.dart"),"void deleteCompletedTasks() { throw StateError('bad'); }\n");
  assert.equal((await publish()).effect,"deny");
});

test("changing a behavior contract invalidates evidence without inflating source effort", async t => {
  const {root}=await fixture(t);
  await mkdir(join(root,"docs/product"),{recursive:true});
  const before=await candidate(root,"app","");
  await writeFile(join(root,"docs/product/tasks.md"),"Sort within groups.");
  const after=await candidate(root,"app","");
  assert.notEqual(after.digest,before.digest);
  assert.deepEqual(after.size,before.size);
});

test("explicit redesign cannot publish on a generic reviewer PASS", async t => {
  const {root,git}=await fixture(t);
  await mkdir(join(root,"lib/features/tasks/screens"),{recursive:true});
  await writeFile(join(root,"lib/features/tasks/screens/tasks.dart"),"// visual change\n");
  const values=new Map([["task/main",{active:true,request:"Переработай интерфейс приложения"}]]);
  const hooks={};
  let verdict="VERDICT: PASS";
  const ctx={
    storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v),remove:async k=>values.delete(k)},
    tool:{hook:async(n,f)=>hooks[n]=f},
    permission:{hook:async(n,f)=>hooks[n]=f},
    session:{
      get:async()=>({parentID:"main",agent:"reviewer",outcome:"succeeded",model:{providerID:"openai",id:"gpt-6-luna",variant:"high"}}),
      context:async()=>[{type:"assistant",content:[{type:"text",text:verdict}]}],
    },
  };
  const q=await registerQualityGate(ctx,root,"app",id=>"task/"+id);
  const check={tool:"shell",sessionID:"main",id:"check",input:{command:"bash .flutter-harness/bin/check.sh ."}};
  await hooks["execute.before"](check);
  await hooks["execute.after"]({...check,status:"completed",result:{metadata:{exit:0},content:"PASS format\nPASS analyze\nPASS flutter-tests"}});
  const review={tool:"subagent",sessionID:"main",id:"review",input:{agent:"reviewer",prompt:"Review"}};
  await hooks["execute.before"](review);
  assert.match(review.input.prompt,/VISUAL: PASS/);
  await hooks["execute.after"]({...review,status:"completed",result:{metadata:{sessionID:"child"}}});
  assert.match(await q.reason("main"),/reviewer verdict/);
  verdict="VISUAL: PASS\nVERDICT: PASS";
  assert.equal(await q.reason("main"),"");
  git("add","."); git("commit","-qm","visual change");
  assert.equal(await q.reason("main"),"");
  await writeFile(join(root,"lib/features/tasks/screens/tasks.dart"),"// changed again\n");
  assert.match(await q.reason("main"),/standard check/);
});
