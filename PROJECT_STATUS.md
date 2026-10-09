# Project Status

## Confirmed
- Repository: `best-digital-offer/ScenarioLab-repository`, branch `main`.
- Frontend: https://scenario-lab-repository.vercel.app/
- User confirmed the latest frontend build succeeded and a real Groq-generated report was returned.
- Groq API defaults: `https://api.groq.com/openai/v1`, model `openai/gpt-oss-20b`.
- Supabase project schema was prepared earlier for a later persistence phase.

## Committed architecture changes
- Added `backend/main.py`: Python API worker that extracts a seed graph, generates independent agent profiles, runs CAMEL-OASIS in a Twitter-like environment, extracts activity from OASIS SQLite output, and runs a separate report-generation pass.
- Added `backend/requirements.txt` with FastAPI, CAMEL-OASIS, and CAMEL-AI dependencies.
- Added `backend/README.md` with worker setup and environment requirements.
- Updated frontend to call `NEXT_PUBLIC_SIMULATION_BACKEND_URL` when configured and to display the seed graph, agent profiles/opening opinions, and recorded activity.
- Updated the root README and PRD to reflect the real multi-stage simulation goal.

## Not yet verified
- Python dependency installation and worker build have not yet been run.
- The OASIS worker has not yet been deployed.
- No end-to-end OASIS run has been verified in the live site.
- Seed graph is per-run and ephemeral, not Zep GraphRAG; no persistent temporal graph memory yet.
- Only the Twitter-like OASIS environment is implemented in this first worker milestone.
- Supabase authentication/persistence UI is not yet wired.

## Next
1. Deploy the Python worker to Render or another persistent Python host.
2. Configure the worker's server-side `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME`, and allowed frontend origin.
3. Set Vercel `NEXT_PUBLIC_SIMULATION_BACKEND_URL` to the worker URL and redeploy the frontend.
4. Test a small run (3 agents, 1 round); verify OASIS activity, latency, and report evidence.
5. Add persistent job handling and Zep GraphRAG/temporal memory.
6. Only after the simulation engine is verified, add Supabase authentication and Saved Reports.

## Architecture decisions
- Keep ScenarioLab independent from QueueTurn and SameWindow.
- Use Vercel for the frontend and a separate Python worker for OASIS.
- Start with small simulations to control Groq cost and hosting constraints.
- Do not copy MiroFish source files. Its upstream repository is AGPL-3.0; review license obligations before any direct reuse.
