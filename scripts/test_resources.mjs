import test from "node:test";
import assert from "node:assert/strict";
import { registerResourceGuard } from "../plugins/delivery-guard/resources.mjs";
async function fixture() {
  const values=new Map([["task/main",{active:true}]]);
  let hook;
  const ctx={storage:{get:async k=>values.get(k),set:async(k,v)=>values.set(k,v),remove:async k=>values.delete(k)},
    session:{get:async({sessionID})=>sessionID==="child"?{parentID:"main"}:{}},
    tool:{hook:async(n,f)=>{hook=f;}}};
  const guard=await registerResourceGuard(ctx,id=>"task/"+id);
  const call=async(agent,sessionID="main",model)=>{const e={tool:"subagent",sessionID,input:{agent,model}};await hook(e);return e;};
  return {call,guard,values};
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
test("two reviewer attempts; no change to normal workers",async()=>{
  const {call}=await fixture();
  await call("reviewer");await call("reviewer");
  await assert.rejects(call("reviewer"),/budget exhausted/);
  for(let i=0;i<5;i++)await call("worker");
});
test("no nested advisor or explicit Sol implementation in tracked task",async()=>{
  const {call}=await fixture();
  await assert.rejects(call("advisor","child"),/task parent/);
  await assert.rejects(call("worker","main","openai/gpt-6.2-sol#high"),/reserved/);
  await call("worker","main","openai/gpt-6-luna#low");
});
