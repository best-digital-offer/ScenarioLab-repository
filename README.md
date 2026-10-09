# ScenarioLab MVP

ScenarioLab is a decision-simulation SaaS starter inspired by multi-agent simulation workflows. It is an independent MVP shell, not a rebranded MiroFish distribution and not a reproduction of MiroFish's full GraphRAG/OASIS pipeline.

## Requirements
- Node.js 20+ and npm
- A dedicated Supabase project (migration included)
- An OpenAI-compatible model API key for live reports

## Local setup
```bash
npm install
cp .env.example .env.local
# Fill in environment variables
npm run dev
```
Open http://localhost:3000.

Without `LLM_API_KEY`, the simulation endpoint returns a setup error rather than inventing a result. Keep this key server-side only.

## Database
Review `supabase/migrations/0001_initial.sql` and apply it only to a dedicated ScenarioLab Supabase project. Do not run it blindly against an existing production database.

## Deployment
Connect this repository to Vercel and set environment variables for each environment. Authentication and persistence UI wiring, usage quotas, rate limiting, and end-to-end tests remain required before a public launch.

## MiroFish relationship
This starter does not bundle upstream MiroFish code. A full integration requires a separate worker and a review of the upstream AGPL-3.0 license and operational dependencies.
