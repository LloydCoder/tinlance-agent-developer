export interface WorkflowStep{readonly id:string;readonly capability:string;readonly dependsOn:readonly string[];readonly approval?:string;readonly evidence:readonly string[];readonly consequential?:boolean;readonly timeoutMs?:number;readonly maxAttempts?:number;}
export interface Workflow{readonly name:string;readonly version:string;readonly steps:readonly WorkflowStep[];}
export interface CompiledWorkflow{readonly name:string;readonly version:string;readonly order:readonly string[];readonly steps:readonly WorkflowStep[];}
const safeName=/^[a-z][a-z0-9.-]{2,127}$/;const semver=/^\d+\.\d+\.\d+$/;
const rank=(id:string)=>id.localeCompare(id);
function freezeStep(step:WorkflowStep):WorkflowStep{return Object.freeze({...step,dependsOn:Object.freeze([...step.dependsOn].sort()),evidence:Object.freeze([...step.evidence])});}
export function compileWorkflow(workflow:Workflow):CompiledWorkflow{
 const errors=validateWorkflow(workflow);if(errors.length)throw new Error(errors.join("; "));
 const steps=[...workflow.steps].map(freezeStep).sort((a,b)=>rank(a.id)-rank(b.id));
 const byId=new Map(steps.map(s=>[s.id,s]));const state=new Map<string,number>();const order:string[]=[];
 function visit(id:string){const current=state.get(id)||0;if(current===1)throw new Error("workflow dependency cycle");if(current===2)return;const step=byId.get(id);if(!step)throw new Error("missing workflow dependency: "+id);state.set(id,1);for(const dep of [...step.dependsOn].sort())visit(dep);state.set(id,2);order.push(id);}
 const ready=steps.map(s=>s.id);for(const id of ready)visit(id);
 return Object.freeze({name:workflow.name,version:workflow.version,order:Object.freeze(order),steps:Object.freeze(steps)});
}
export function validateWorkflow(workflow:Workflow):readonly string[]{
 const e:string[]=[];
 if(!safeName.test(workflow.name)||!semver.test(workflow.version))e.push("workflow identity is invalid");
 if(!Array.isArray(workflow.steps)||workflow.steps.length===0)e.push("workflow must contain at least one step");
 const ids=new Set<string>();
 for(const s of workflow.steps){
  if(!safeName.test(s.id)||!s.capability)e.push("step identity and capability are required");
  if(ids.has(s.id))e.push("duplicate workflow step id: "+s.id);ids.add(s.id);
  if(s.dependsOn.includes(s.id))e.push("step cannot depend on itself: "+s.id);
  if(new Set(s.dependsOn).size!==s.dependsOn.length)e.push("duplicate dependency in step: "+s.id);
  if(s.consequential&&!s.approval)e.push("consequential step requires an approval declaration: "+s.id);
  if(s.timeoutMs!==undefined&&(!Number.isInteger(s.timeoutMs)||s.timeoutMs<=0))e.push("timeoutMs must be a positive integer: "+s.id);
  if(s.maxAttempts!==undefined&&(!Number.isInteger(s.maxAttempts)||s.maxAttempts<1))e.push("maxAttempts must be a positive integer: "+s.id);
 }
 for(const s of workflow.steps)for(const dep of s.dependsOn)if(!ids.has(dep))e.push("missing workflow dependency: "+dep);
 return Object.freeze(e);
}
