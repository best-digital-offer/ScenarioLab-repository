import { NextResponse } from 'next/server';
import { z } from 'zod';
export const runtime = 'nodejs';
export const maxDuration = 60;
const inputSchema=z.object({scenario:z.string().trim().min(12).max(1200),context:z.string().trim().max(5000).default(''),agents:z.number().int().min(3).max(5),rounds:z.number().int().min(1).max(2)});
const reportSchema=z.object({title:z.string().min(1).max(160),summary:z.string().min(20).max(5000),scenarios:z.array(z.object({name:z.string().min(1).max(160),likelihood:z.string().min(1).max(80),detail:z.string().min(1).max(2000)})).min(2).max(4),signals:z.array(z.string().min(1).max(300)).min(2).max(8),caveat:z.string().min(1).max(1000)});
export async function POST(request:Request){
 let parsed:z.infer<typeof inputSchema>;
 try{parsed=inputSchema.parse(await request.json())}catch{return NextResponse.json({error:'Check the scenario text and simulation settings, then try again.'},{status:400})}
 const maxAgents=Math.min(5,Math.max(3,Number(process.env.MAX_SIMULATION_AGENTS||5)));const maxRounds=Math.min(2,Math.max(1,Number(process.env.MAX_SIMULATION_ROUNDS||2)));
 if(parsed.agents>maxAgents||parsed.rounds>maxRounds)return NextResponse.json({error:'This simulation exceeds the configured usage limit.'},{status:400});
 const apiKey=process.env.LLM_API_KEY;const baseUrl=process.env.LLM_BASE_URL||'https://api.openai.com/v1';const model=process.env.LLM_MODEL_NAME||'gpt-4o-mini';
 if(!apiKey){
  if(process.env.SIMULATION_DEMO_MODE==='true'){
   const report={title:'Demo report: '+parsed.scenario.slice(0,110),summary:'This is a deterministic demonstration report generated without an AI provider. It shows the expected report structure for the scenario you entered; it is not a genuine model analysis or a prediction.',scenarios:[
    {name:'Favorable adoption',likelihood:'Plausible path',detail:'Some customers accept the change because they see enough value, communicate the benefits clearly, and remain engaged. Validate this with a small pilot before acting.'},
    {name:'Mixed response',likelihood:'Plausible path',detail:'A portion of customers accepts the change while price-sensitive or uncertain customers delay, downgrade, or ask for alternatives. Segment feedback instead of relying on one overall metric.'},
    {name:'Adverse reaction',likelihood:'Risk path',detail:'Customers perceive the change as poor value and consider leaving. Prepare a clear explanation, support responses, and a rollback or mitigation threshold.'}
   ],signals:['Trial-to-paid conversion changes versus baseline','Cancellation and downgrade requests by customer segment','Support-ticket volume and sentiment after the change','Customer interviews explaining perceived value'],caveat:'Demo mode only: these generic examples are not tailored AI findings, verified facts, or calibrated probabilities.'};
   return NextResponse.json({report,meta:{model:'demo-mode-no-ai',agents:parsed.agents,rounds:parsed.rounds,generatedAt:new Date().toISOString(),calibratedForecast:false,demo:true}},{headers:{'Cache-Control':'no-store'}});
  }
  return NextResponse.json({error:'Live simulation is not configured. Add LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL_NAME, or enable SIMULATION_DEMO_MODE=true for a clearly labeled demo.'},{status:503});
 }
 const system=`You are a cautious scenario-analysis facilitator. Use ${parsed.agents} distinct stakeholder perspectives over ${parsed.rounds} reasoning round(s). Distinguish assumptions from evidence, include downside paths, and do not invent external facts. Likelihood labels must be qualitative, never calibrated percentages. Return ONLY JSON: {"title":string,"summary":string,"scenarios":[{"name":string,"likelihood":string,"detail":string}],"signals":[string],"caveat":string}. Include 2-4 paths and 2-8 observable signals. Explain uncertainty.`;
 try{const response=await fetch(`${baseUrl.replace(/\\/$/,'')}/chat/completions`,{method:'POST',headers:{Authorization:`Bearer ${apiKey}`,'Content-Type':'application/json'},body:JSON.stringify({model,temperature:.45,max_tokens:1800,response_format:{type:'json_object'},messages:[{role:'system',content:system},{role:'user',content:`Scenario: ${parsed.scenario}\\n\\nBackground and assumptions: ${parsed.context||'No extra context supplied.'}\\n\\nAnalyze this scenario from multiple perspectives and output the JSON report.`}]}),signal:AbortSignal.timeout(50000)});
 if(!response.ok)return NextResponse.json({error:response.status===429?'Model provider rate limit reached. Wait and retry.':response.status>=500?'Model provider temporarily unavailable.':'Model provider rejected the request. Check server-side configuration.'},{status:response.status===429?429:502});
 const body=await response.json();const content=body?.choices?.[0]?.message?.content;if(typeof content!=='string')throw new Error('invalid response');const report=reportSchema.parse(JSON.parse(content));return NextResponse.json({report,meta:{model,agents:parsed.agents,rounds:parsed.rounds,generatedAt:new Date().toISOString(),calibratedForecast:false}},{headers:{'Cache-Control':'no-store'}});
 }catch(e){const msg=e instanceof Error?e.message:'';const timeout=msg.toLowerCase().includes('timeout');return NextResponse.json({error:timeout?'Simulation timed out. Try fewer perspectives or shorter scenario.':'Simulation could not produce a valid report. Retry with a clearer scenario.'},{status:timeout?504:502})}
}
