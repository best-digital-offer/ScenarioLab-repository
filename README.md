# ScenarioLab

ScenarioLab is an independent decision-simulation SaaS with a Next.js frontend and a separate Python simulation worker. Its direction is inspired by the documented multi-stage MiroFish architecture, without copying upstream source files.

## Current architecture

1. **Seed graph:** Groq extracts a bounded set of entities and relationships from the user's scenario and context. This is currently a per-run local graph, not yet Zep GraphRAG.
2. **Agent profiles:** Groq creates distinct stakeholder personas and opening opinions grounded in the seed graph.
3. **Simulation environment:** CAMEL-OASIS creates a Twitter-like simulated environment; each agent posts an opening opinion and then performs model-driven actions for the requested rounds.
4. **Evidence extraction:** the worker inspects OASIS's SQLite output for recorded activity.
5. **ReportAgent pass:** a separate LLM request summarizes observed activity, separates evidence from assumptions, and returns structured findings.

## Requirements

- Node.js 20+ and npm for the frontend
- Python 3.11+ for the worker
- Groq API key (server-side only)
- Render or another persistent Python service host for the OASIS worker
- Supabase is prepared for a later authentication and report-persistence phase

## Local frontend setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_SIMULATION_BACKEND_URL` to the Python worker URL to use real OASIS simulation. If it is blank, the frontend currently falls back to the legacy single-call report endpoint; that fallback is not a multi-agent simulation.

## Local worker setup

```bash
cd backend
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
export LLM_API_KEY=your_groq_key
uvicorn main:app --host 0.0.0.0 --port 8000
```

Worker health endpoint: `GET /health`. Simulation endpoint: `POST /api/simulate`.

## Worker environment variables

- `LLM_API_KEY`: required Groq key
- `LLM_BASE_URL`: default `https://api.groq.com/openai/v1`
- `LLM_MODEL_NAME`: default `openai/gpt-oss-20b`
- `FRONTEND_ORIGIN`: allowed frontend origin(s), comma-separated

## Important current limits

- First worker milestone uses the OASIS Twitter-like environment only.
- Seed graph is generated locally per run; persistent Zep GraphRAG and long-term graph-memory updates are not yet implemented.
- No document upload/ingestion, parallel Reddit simulation, durable background job queue, or post-run agent chat yet.
- Worker currently uses a bounded synchronous request. Begin with 3 agents and 1 round; longer runs may exceed service request limits.
- Add durable jobs, user authentication, quotas, rate limits, and persistent artifacts before public production.
- The upstream MiroFish repository is AGPL-3.0. This worker is an original integration layer using CAMEL-OASIS, not a copy of MiroFish source files. Review dependency licenses and upstream notices before distribution.

## Project

Repository: https://github.com/best-digital-offer/ScenarioLab-repository  
Frontend: https://scenario-lab-repository.vercel.app/
