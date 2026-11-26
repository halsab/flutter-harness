import test from "node:test";
import assert from "node:assert/strict";
import { registerResourceGuard } from "../plugins/delivery-guard/resources.mjs";
async function fixture() {
  const values=new Map([["task/main",{active:true,id:"first"}]]);
  const hooks={}, sessions=new Map([["main",{}],["nested",{parentID:"main"}]]);
  const ctx={storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v),remove:async k=>values.delete(k)},
    session:{get:async({sessionID})=>sessions.get(sessionID) || {}},
    tool:{hook:async(n,f)=>{hooks[n]=f;}}};
  let inputKey=0, ready=true;
  ctx.session.context=async({sessionID})=>[{type:"assistant",content:[{type:"text",text:"VERDICT: "+(sessions.get(sessionID).verdict || "CHANGES_REQUIRED")}]}];
  const guard=await registerResourceGuard(ctx,id=>"task/"+id,async()=>{if(!ready)throw Error("missing evidence");return {key:String(inputKey)};},async(e,input)=>{if(input.dispute)e.input.dispute=input.dispute;});
  let i=0;
  const call=async(agent,sessionID="main",model)=>{
    const e={tool:"subagent",sessionID,id:"call"+(++i),input:{agent,model}};
    await hooks["execute.before"](e);return e;
  };
  const finish=async(e,childID,outcome="succeeded")=>{
    sessions.set(childID,{parentID:"main",outcome});
    await hooks["execute.after"]({...e,status:"completed",result:{metadata:{sessionID:childID}}});
  };
  return {call,finish,guard,sessions,advance:()=>inputKey++,setReady:v=>ready=v,newTask:()=>values.set("task/main",{active:true,id:"second"})};
}
test("one advisor attempt is reserved even across concurrent requests", async()=>{
  const {call,guard}=await fixture();
  const out=await Promise.allSettled([call("advisor"),call("advisor")]);
  assert.equal(out.filter(x=>x.status==="fulfilled").length,1);
  assert.equal(out.find(x=>x.status==="fulfilled").value.input.model,"openai/gpt-6.2-sol#medium");
  await assert.rejects(call("advisor"),/wait for the current/);
  await guard.clear("main");
  await call("advisor");
});
test("sequential read-only consultations and no workers",async()=>{
  const {call,finish,guard}=await fixture();
  await assert.rejects(call("worker"),/one implementation agent/);
  await assert.rejects(call("general"),/one implementation agent/);
  await assert.rejects(call("advisor","nested"),/task parent/);
  await assert.rejects(call("reviewer","main","openai/gpt-6.2-sol#high"),/reserved/);
  const a=await call("architect");
  await assert.rejects(call("reviewer"),/wait for the current/);
  await finish(a,"a1","running");
  await assert.rejects(call("advisor"),/wait for the current/);
  assert.match(await guard.status("main"),/completion/);
});
test("two substantive reviews remain bounded",async()=>{
  const {call,finish,advance}=await fixture();
  await finish(await call("reviewer"),"r1");
  advance(); await finish(await call("reviewer"),"r2");
  advance(); await assert.rejects(call("reviewer"),/budget exhausted/);
});
test("missing evidence spends no review; changed evidence after BLOCKED allows bounded recovery",async()=>{
  const {call,finish,guard,sessions,advance,setReady}=await fixture();
  setReady(false); await assert.rejects(call("reviewer"),/missing evidence/);
  setReady(true); await finish(await call("reviewer"),"r1");
  sessions.get("r1").verdict="BLOCKED";
  await assert.rejects(call("reviewer"),/unchanged/);
  advance(); await finish(await call("reviewer"),"r2");
  advance(); await finish(await call("reviewer"),"r3");
  advance(); await assert.rejects(call("reviewer"),/budget exhausted/);
  assert.deepEqual(await guard.sessions("main"),["main","r1","r2","r3"]);
});

test("one unchanged-input adjudication carries actual findings, then stops or permits targeted repair",async()=>{
  const {call,finish,advance}=await fixture();
  await finish(await call("reviewer"),"r1");
  const second=await call("reviewer");
  assert.equal(second.input.dispute.childID,"r1");
  assert.match(second.input.dispute.report,/CHANGES_REQUIRED/);
  await finish(second,"r2");
  await assert.rejects(call("reviewer"),/unchanged/);
  advance(); await finish(await call("reviewer"),"r3");
  advance(); await assert.rejects(call("reviewer"),/budget exhausted/);
});

test("new task in same root starts fresh budgets",async()=>{
  const {call,finish,guard,newTask,advance}=await fixture();
  await finish(await call("advisor"),"a1");
  await finish(await call("reviewer"),"r1");
  advance(); await finish(await call("reviewer"),"r2");
  advance(); await assert.rejects(call("reviewer"),/budget exhausted/);
  await assert.rejects(call("advisor"),/budget exhausted/);
  newTask();
  assert.deepEqual(await guard.sessions("main"),["main"]);
  await finish(await call("advisor"),"a2");
  await finish(await call("reviewer"),"r3");
  assert.deepEqual(await guard.sessions("main"),["main","a2","r3"]);
});
