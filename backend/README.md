# ScenarioLab simulation worker

This Python service is a separate, OASIS-backed simulation worker for the ScenarioLab Next.js frontend.

## Architecture stages

1. Generate independent stakeholder profiles from the scenario using the configured OpenAI-compatible model.
2. Load the actual CAMEL-OASIS social simulation engine.
3. Seed opening opinions as simulated posts.
4. Run bounded OASIS agent-action rounds.
5. Read the OASIS SQLite activity database and send the observed evidence to a separate report-generation pass.

The service uses an original integration layer; it does not copy MiroFish source files. It is inspired by the public MiroFish workflow. This first worker milestone implements a Twitter-like simulated environment only. It does not yet implement Zep GraphRAG, source-document ingestion, Reddit parallel simulation, persistent job queues, or agent chat after completion.

## Environment variables

- `LLM_API_KEY`: required; Groq API key (server-side only)
- `LLM_BASE_URL`: default `https://api.groq.com/openai/v1`
- `LLM_MODEL_NAME`: default `openai/gpt-oss-20b`
- `FRONTEND_ORIGIN`: comma-separated allowed browser origins; default is the production ScenarioLab URL

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export LLM_API_KEY=your_groq_key
uvicorn main:app --host 0.0.0.0 --port 8000
```

Health endpoint: `GET /health`. Simulation endpoint: `POST /api/simulate`.

## Deployment notes

This worker runs long-lived Python dependencies and real model-driven agent actions. The first free-tier deployment may be slow or memory-constrained. Use small runs (3 agents, 1 round) for the first test. Never commit API keys. Before public production, add durable job storage, rate limits, authentication, quotas, and a persistent artifact store.
