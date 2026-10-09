# ScenarioLab — Multi-Agent Simulation Product Requirements

## Product goal
Build a scenario-simulation SaaS in which distinct agents have individual profiles, publish opinions, interact in a simulated environment, and produce findings from recorded simulation activity. This is not intended to be a one-prompt report generator.

## Target architecture
1. Scenario/context seed input.
2. Entity and relationship extraction into a seed graph.
3. Distinct stakeholder profile generation grounded in the graph.
4. A real multi-agent simulation environment (CAMEL-OASIS initially) where agents publish opening opinions and perform model-driven actions over bounded rounds.
5. Activity extraction from the simulation database.
6. A separate ReportAgent pass that summarizes observed behavior and clearly separates evidence, assumptions, and hypotheses.
7. Later: persistent GraphRAG memory, document ingestion, parallel platform simulations, agent interviews, and interactive follow-up.

## Current implementation milestone
- Next.js/React frontend remains on Vercel.
- Python worker in `backend/` provides `GET /health` and `POST /api/simulate`.
- Worker uses Groq through an OpenAI-compatible endpoint.
- Seed graph is extracted per run and is currently local/ephemeral; it is not yet Zep GraphRAG.
- CAMEL-OASIS runs a Twitter-like environment and stores its run database in a temporary workspace.
- Frontend can call the worker directly using `NEXT_PUBLIC_SIMULATION_BACKEND_URL`.
- The previous single-call endpoint remains as a fallback until the worker is deployed and configured.

## Next implementation milestones
1. Deploy and verify the Python worker, beginning with 3 agents and 1 round.
2. Verify that OASIS produces recorded activity and that the report references observed output rather than invented evidence.
3. Add persistent job state and artifacts; add Zep GraphRAG/temporal memory after selecting/configuring the graph provider.
4. Add Supabase authentication and report persistence.
5. Add Saved Reports, deletion, rate limits, usage accounting, and monitoring.
6. Add source-document ingestion, richer graph visualization, optional Reddit simulation, and agent follow-up conversations.

## Quality and safety requirements
- Never fabricate numerical evidence or present qualitative likelihood labels as calibrated probabilities.
- Distinguish simulated events from real-world facts.
- Reject malformed input and cap agent/round counts.
- Keep API keys server-side; never expose Groq secrets to the browser.
- Keep simulation costs and rate limits visible before public launch.
- Review licenses for all upstream dependencies, especially AGPL-3.0 obligations if MiroFish source is ever reused.

## Initial bounds
- 3–5 agents
- 1–2 simulation rounds
- Groq `openai/gpt-oss-20b` default, configurable by environment variables
