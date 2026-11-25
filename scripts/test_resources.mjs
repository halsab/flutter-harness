import test from "node:test";
import assert from "node:assert/strict";
import { registerResourceGuard } from "../plugins/delivery-guard/resources.mjs";
async function fixture() {
  const values=new Map([["task/main",{active:true}]]);
  const hooks={}, sessions=new Map([["main",{}],["nested",{parentID:"main"}]]);
  const ctx={storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v),remove:async k=>values.delete(k)},
    session:{get:async({sessionID})=>sessions.get(sessionID) || {}},
    tool:{hook:async(n,f)=>{hooks[n]=f;}}};
  const guard=await registerResourceGuard(ctx,id=>"task/"+id);
  let i=0;
  const call=async(agent,sessionID="main",model)=>{
    const e={tool:"subagent",sessionID,id:"call"+(++i),input:{agent,model}};
    await hooks["execute.before"](e);return e;
  };
  const finish=async(e,childID,outcome="succeeded")=>{
    sessions.set(childID,{parentID:"main",outcome});
    await hooks["execute.after"]({...e,status:"completed",result:{metadata:{sessionID:childID}}});
  };
  return {call,finish,guard,sessions};
}
test("one advisor attempt is reserved even across concurrent requests", async()=>{
  const {call,guard}=await fixture();
  const out=await Promise.allSettled([call("advisor"),call("advisor")]);
  assert.equal(out.filter(x=>x.status==="fulfilled").length,1);
  assert.equal(out.find(x=>x.status==="fulfilled").value.input.model,"openai/gpt-6.2-sol#medium");
  await assert.rejects(call("advisor"),/budget exhausted/);
  await guard.clear("main");
  await call("advisor");
});
test("two reviewer attempts; actual workers bounded and tracked",async()=>{
  const {call,finish,guard,sessions}=await fixture();
  await finish(await call("reviewer"),"r1");
  await finish(await call("reviewer"),"r2");
  await assert.rejects(call("reviewer"),/budget exhausted/);
  const a=await call("worker"),b=await call("worker");
  await assert.rejects(call("worker"),/two active workers/);
  assert.match(await guard.status("main"),/dispatch/);
  await finish(a,"w1","running");
  await finish(b,"w2");
  assert.match(await guard.status("main"),/completion/);
  sessions.get("w1").outcome="succeeded";
  assert.equal(await guard.status("main"),"");
  assert.deepEqual(await guard.sessions("main"),["main","r1","r2","w1","w2"]);
});
test("no nested advisor or explicit Sol implementation in tracked task",async()=>{
  const {call}=await fixture();
  await assert.rejects(call("advisor","nested"),/task parent/);
  await assert.rejects(call("worker","main","openai/gpt-6.2-sol#high"),/reserved/);
  await call("worker","main","openai/gpt-6-luna#low");
});
