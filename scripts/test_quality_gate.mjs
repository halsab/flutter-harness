import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";
import { candidate, classify, publishing, standardCheck, finalVerdict, gateReason, registerQualityGate } from "../plugins/delivery-guard/quality.mjs";

test("risk detection follows actual repository changes, not routine UI wording", () => {
  assert.ok(classify(["lib/data/task_repository.dart"], "routine UI change").length);
  assert.ok(classify(["lib/features/tasks/task_list_screen.dart"], "Добавь возможность удалить все завершённые задачи").length);
  assert.equal(classify(["lib/features/tasks/task_list_screen.dart"], "Измени подпись").length, 0);
  assert.ok(classify(["test/widget_test.dart"], "", ["test/widget_test.dart: preserves records"]).length);
});
test("only delivery commands and standard checks match", () => {
  for (const c of ["git push -u origin feature/a", "gh pr create --base app", "gh pr ready 1", "git status && git push"]) assert.ok(publishing(c), c);
  for (const c of ["git diff", "gh pr view 1", "flutter test"]) assert.equal(publishing(c), false);
  assert.ok(standardCheck("bash .flutter-harness/bin/check.sh . standard mobile-web"));
  assert.equal(standardCheck("bash .flutter-harness/bin/check.sh . quick"), false);
});
test("review requires final exact PASS, not a build-agent claim or earlier PASS", () => {
  const m = text => ({ type: "assistant", content: [{type:"text", text}] });
  assert.ok(finalVerdict([m("No material issues.\nVERDICT: PASS")]));
  assert.equal(finalVerdict([m("VERDICT: PASS"),m("VERDICT: CHANGES_REQUIRED")]), false);
  assert.equal(finalVerdict([m("PASS")]), false);
});
test("risk requires same-candidate checks and review; ordinary tasks do not", () => {
  const c = {digest:"a",reasons:["storage"]};
  assert.ok(gateReason(c,{passedDigest:"b"},true));
  assert.ok(gateReason(c,{passedDigest:"a"},false));
  assert.equal(gateReason(c,{passedDigest:"a"},true),"");
  assert.equal(gateReason({digest:"a",reasons:[]},{},false),"");
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
  await writeFile(path,"test('replacement', () {});\n");
  assert.notEqual((await candidate(root,"app","")).digest,after.digest);
});
test("mock V2 hooks deny risky push until real child PASS, then preserve ask; stale source blocks again", async t => {
  const {root}=await fixture(t);
  const values=new Map([["task/main",{active:true,request:"Удалить все завершённые задачи"}]]);
  const hooks={}; let child={parentID:"main",agent:"reviewer",outcome:"running"};
  const ctx={
    storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v),remove:async k=>values.delete(k)},
    tool:{hook:async(n,f)=>hooks[n]=f},
    permission:{hook:async(n,f)=>hooks[n]=f},
    session:{get:async()=>child,context:async()=>[{type:"assistant",content:[{type:"text",text:"VERDICT: PASS"}]}]},
  };
  const q=await registerQualityGate(ctx,root,"app",id=>"task/"+id);
  const publish=async()=>{const e={sessionID:"main",action:"shell",resources:["git push -u origin feature/bulk"],effect:"ask"};await hooks.evaluate(e);return e;};
  assert.equal((await publish()).effect,"deny");
  const check={tool:"shell",sessionID:"main",id:"check",input:{command:"bash .flutter-harness/bin/check.sh . standard mobile-web"}};
  await hooks["execute.before"](check);
  await hooks["execute.after"]({...check,status:"completed",result:{metadata:{exit:0},content:"PASS format\nPASS analyze\nPASS flutter-tests"}});
  assert.equal((await publish()).effect,"deny");
  const review={tool:"subagent",sessionID:"main",id:"review",input:{agent:"reviewer",prompt:"Review diff"}};
  await hooks["execute.before"](review);
  assert.match(review.input.prompt,/VERDICT: PASS/);
  await hooks["execute.after"]({...review,status:"completed",result:{metadata:{sessionID:"child"}}});
  assert.equal((await publish()).effect,"deny");
  child={...child,outcome:"succeeded"};
  assert.equal(await q.reason("main"),"");
  assert.equal((await publish()).effect,"ask");
  await writeFile(join(root,"lib/data/task_repository.dart"),"void deleteCompletedTasks() { throw StateError('bad'); }\n");
  assert.equal((await publish()).effect,"deny");
});
