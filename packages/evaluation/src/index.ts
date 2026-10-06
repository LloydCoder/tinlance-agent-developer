export interface EvaluationMetrics{readonly correctness:number;readonly safety:number;readonly policyCompliance:number;readonly authorizationCompliance:number;readonly evidenceQuality:number;readonly reliability:number;}
export type EvaluationMetricKey=keyof EvaluationMetrics;
export type EvaluationGateKey=keyof EvaluationGates;
export interface EvaluationGates{readonly correctness:number;readonly safety:number;readonly policyCompliance:number;readonly authorizationCompliance:number;readonly evidenceQuality:number;}
export interface EvaluationCaseResult{readonly id:string;readonly metrics:EvaluationMetrics;readonly passed:boolean;readonly failures:readonly string[];}
export interface EvaluationRun{readonly target:string;readonly targetDigest:string;readonly suite:string;readonly suiteVersion:string;readonly cases:readonly EvaluationCaseResult[];readonly modelVersion:string;readonly harnessVersion:string;readonly toolVersions:Readonly<Record<string,string>>;readonly environment:Readonly<Record<string,string>>;readonly seed?:string;readonly evaluatedAt:string;}
export interface EvaluationReceipt{readonly receiptVersion:"1";readonly target:string;readonly targetDigest:string;readonly suite:string;readonly suiteVersion:string;readonly caseCount:number;readonly passedCases:number;readonly metrics:EvaluationMetrics;readonly gates:EvaluationGates;readonly passed:boolean;readonly failures:readonly string[];readonly modelVersion:string;readonly harnessVersion:string;readonly toolVersions:Readonly<Record<string,string>>;readonly environment:Readonly<Record<string,string>>;readonly seed?:string;readonly evaluatedAt:string;}
const metricKeys:readonly EvaluationMetricKey[]=["correctness","safety","policyCompliance","authorizationCompliance","evidenceQuality","reliability"];
function assertScore(value:number,label:string){if(!Number.isFinite(value)||value<0||value>1)throw new Error(label+" must be between 0 and 1");}
function validateCase(result:EvaluationCaseResult){if(!result.id.trim())throw new Error("evaluation case id is required");for(const key of metricKeys)assertScore(result.metrics[key],"case metric "+key);}
function aggregate(cases:readonly EvaluationCaseResult[]):EvaluationMetrics{
 const totals={correctness:0,safety:0,policyCompliance:0,authorizationCompliance:0,evidenceQuality:0,reliability:0};
 for(const result of cases)for(const key of metricKeys)totals[key]+=result.metrics[key];
 return Object.freeze({correctness:totals.correctness/cases.length,safety:totals.safety/cases.length,policyCompliance:totals.policyCompliance/cases.length,authorizationCompliance:totals.authorizationCompliance/cases.length,evidenceQuality:totals.evidenceQuality/cases.length,reliability:totals.reliability/cases.length});
}
export function evaluateRun(run:EvaluationRun,gates:EvaluationGates):EvaluationReceipt{
 if(!run.target.trim()||!run.targetDigest.trim()||!run.suite.trim()||!run.suiteVersion.trim())throw new Error("evaluation identity is required");
 if(!Array.isArray(run.cases)||run.cases.length===0)throw new Error("evaluation run requires at least one case");
 const ids=new Set<string>();for(const result of run.cases){validateCase(result);if(ids.has(result.id))throw new Error("duplicate evaluation case id: "+result.id);ids.add(result.id);}
 for(const key of Object.keys(gates) as EvaluationGateKey[])assertScore(gates[key],"gate "+key);
 const metrics=aggregate(run.cases);const failures=run.cases.flatMap(result=>result.failures.map(f=>result.id+": "+f));
 const passed=Object.keys(gates).every(key=>metrics[key as EvaluationGateKey]>=(gates[key as EvaluationGateKey]));
 return Object.freeze({receiptVersion:"1" as const,target:run.target,targetDigest:run.targetDigest,suite:run.suite,suiteVersion:run.suiteVersion,caseCount:run.cases.length,passedCases:run.cases.filter(c=>c.passed).length,metrics,gates:Object.freeze({...gates}),passed,failures:Object.freeze(failures),modelVersion:run.modelVersion,harnessVersion:run.harnessVersion,toolVersions:Object.freeze({...run.toolVersions}),environment:Object.freeze({...run.environment}),seed:run.seed,evaluatedAt:run.evaluatedAt});
}
export function assertEvaluation(receipt:EvaluationReceipt){if(!receipt.passed)throw new Error("evaluation gates failed");if(receipt.caseCount<1||receipt.passedCases>receipt.caseCount)throw new Error("invalid evaluation receipt");return receipt;}
