# ScenarioLab

ScenarioLab is an independent, lightweight decision-simulation SaaS. The existing Next.js frontend is preserved and now calls a Supabase Edge Function. Groq produces distinct fictional stakeholder perspectives, a short synthetic exchange, a compact seed graph, possible paths, and signals in one bounded model request.

## Current architecture

1. **Frontend:** Next.js on Vercel; the existing workspace and report UI are retained.
2. **Simulation endpoint:** Supabase Edge Function `scenariolab-simulate` (TypeScript/Deno); no Python worker or Render memory required.
3. **LLM:** Groq Chat Completions, default model `openai/gpt-oss-20b`; one model call per run to minimize cost.
4. **Persistence/job tracking:** `public.simulations` stores each run's scenario, status, model, report, timestamps, and a hashed request fingerprint. Status moves through `running`, `completed`, or `failed`.
5. **Basic abuse control:** up to five runs per hour per observed client IP fingerprint. This is a lightweight demo safeguard, not a complete production anti-abuse system.

## Required setup

### 1. Supabase Edge Function secret

In Supabase Dashboard, open **Project Settings / Edge Functions / Secrets** (or **Edge Functions → Secrets**) for project `zlxzhunkndeiotddppmf` and add:

- `GROQ_API_KEY` = your Groq API key

The function uses `openai/gpt-oss-20b` by default. You can optionally set `GROQ_MODEL` to another Groq-supported model. Do not commit the Groq key or put it in a `NEXT_PUBLIC_*` variable.

### 2. Vercel environment variables

Set these for the Vercel project and redeploy:

- `NEXT_PUBLIC_SUPABASE_URL=https://zlxzhunkndeiotddppmf.supabase.co`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` = the project's publishable key or legacy anon key (browser-safe key only)

The function is deployed at:

`https://zlxzhunkndeiotddppmf.supabase.co/functions/v1/scenariolab-simulate`

### 3. Database

The existing `public.simulations` table is reused. Migration `20261009065317_add_simulation_request_fingerprint.sql` adds the hashed fingerprint column and index; migration `20261009070000_allow_anonymous_simulation_jobs.sql` allows demo jobs without a signed-in user. Both changes have been applied to the linked Supabase project.

## Local frontend

```bash
npm install
cp .env.example .env.local
npm run dev
```

Use your Supabase project URL and public anon/publishable key in `.env.local`. Keep Groq credentials only in Supabase Edge Function secrets.

## Important limits

- This is a **lightweight LLM-generated simulation**, not CAMEL-OASIS, a real social-network environment, or the complete MiroFish/GraphRAG architecture.
- The model generates synthetic agent profiles, activity, a compact graph, and possible paths in a single call; it does not run independently acting agent processes.
- Likelihood labels are qualitative, not calibrated forecasts.
- The hourly IP fingerprint limit is only a basic safeguard. Before public production, add authentication, per-user quotas, stronger rate limiting, and monitoring.
- The upstream MiroFish repository is AGPL-3.0. ScenarioLab is an independent integration and does not copy MiroFish source files.

## Project

Repository: https://github.com/best-digital-offer/ScenarioLab-repository  
Frontend: https://scenario-lab-repository.vercel.app/
