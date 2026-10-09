"""ScenarioLab's OASIS-backed simulation worker.

Architecture stages:
1) create independent stakeholder profiles with the configured OpenAI-compatible LLM
2) initialize an OASIS social simulation
3) seed each agent's opening position into the simulated feed
4) run bounded rounds of actual OASIS agent actions
5) inspect the simulation database and ask a separate report pass to analyze observed activity

This is an original integration layer inspired by the documented MiroFish workflow.
It does not copy MiroFish source files.
"""
from __future__ import annotations

import csv
import json
import os
import sqlite3
import tempfile
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="ScenarioLab Simulation Worker", version="0.2.0")
allowed_origins = [
    value.strip()
    for value in os.getenv(
        "FRONTEND_ORIGIN", "https://scenario-lab-repository.vercel.app"
    ).split(",")
    if value.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-ScenarioLab-Token"],
)

class SimulationRequest(BaseModel):
    scenario: str = Field(min_length=12, max_length=1200)
    context: str = Field(default="", max_length=5000)
    agents: int = Field(default=3, ge=3, le=5)
    rounds: int = Field(default=1, ge=1, le=2)

def config() -> tuple[str, str, str]:
    key = os.getenv("LLM_API_KEY", "")
    base = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    model = os.getenv("LLM_MODEL_NAME", "openai/gpt-oss-20b")
    if not key:
        raise HTTPException(status_code=503, detail="LLM_API_KEY is not configured on the simulation worker.")
    return key, base, model

async def llm_json(system: str, user: str, max_tokens: int = 1800) -> dict[str, Any]:
    key, base, model = config()
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "temperature": 0.35,
                    "max_tokens": max_tokens,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"LLM provider returned HTTP {response.status_code}. Check model access and worker logs.")
        payload = response.json()
        content = payload.get("choices", [{}])[0].get("message", {}).get("content")
        if not isinstance(content, str):
            raise ValueError("Provider returned no message content")
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Provider did not return a JSON object")
        return parsed
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {type(exc).__name__}") from exc


async def build_seed_graph(request: SimulationRequest) -> dict[str, Any]:
    """Extract a bounded entity/relationship graph from the supplied seed text."""
    data = await llm_json(
        "Extract a compact knowledge graph for a scenario simulation. Return only JSON with "
        "nodes (array of objects with id, label, type, description) and edges "
        "(array of objects with source, target, relation). Use only entities and relationships "
        "reasonably supported by the supplied scenario/context. Mark inferred items as inferred. "
        "Return 4-12 nodes and 3-20 edges. Do not invent external facts or statistics.",
        f"Scenario: {request.scenario}\\nContext/source material: {request.context or 'No additional context supplied.'}",
        max_tokens=1200,
    )
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise HTTPException(status_code=502, detail="The model did not return a valid seed graph.")
    clean_nodes = []
    known_ids = set()
    for index, node in enumerate(nodes[:12]):
        if not isinstance(node, dict):
            continue
        label = str(node.get("label") or "").strip()[:120]
        node_id = str(node.get("id") or f"entity_{index + 1}").strip()[:80]
        if not label or node_id in known_ids:
            continue
        known_ids.add(node_id)
        clean_nodes.append({
            "id": node_id,
            "label": label,
            "type": str(node.get("type") or "concept")[:80],
            "description": str(node.get("description") or "")[:500],
        })
    clean_edges = []
    for edge in edges[:20]:
        if not isinstance(edge, dict):
            continue
        source = str(edge.get("source") or "")
        target = str(edge.get("target") or "")
        relation = str(edge.get("relation") or "").strip()[:120]
        if source in known_ids and target in known_ids and source != target and relation:
            clean_edges.append({"source": source, "target": target, "relation": relation})
    if len(clean_nodes) < 3:
        raise HTTPException(status_code=502, detail="The seed graph contained too few valid entities.")
    return {"nodes": clean_nodes, "edges": clean_edges, "storage": "per-run in-memory graph", "graph_rag_enabled": False}

async def generate_profiles(request: SimulationRequest, graph: dict[str, Any]) -> list[dict[str, Any]]:
    data = await llm_json(
        "Create distinct fictional stakeholder profiles for a bounded social simulation. "
        "Return only JSON with key profiles: an array. Each profile must have name, username, "
        "role, bio, persona, opening_opinion, stance, and interests. Make opinions genuinely "
        "different and grounded only in the supplied scenario/context. Do not invent statistics.",
        f"Create exactly {request.agents} profiles for this scenario:\n{request.scenario}\n\n"
        f"Context and assumptions:\n{request.context or 'No additional context supplied.'}\n\n"
        "Ensure roles differ (for example, loyal customer, price-sensitive customer, product lead, "
        "finance lead, competitor-aware buyer as appropriate). Each opening_opinion should be a "
        "short first-person statement suitable for an initial simulated social post.",
        max_tokens=1800,
    )
    profiles = data.get("profiles")
    if not isinstance(profiles, list) or len(profiles) < request.agents:
        raise HTTPException(status_code=502, detail="The model did not return enough valid agent profiles.")
    normalized = []
    for index, item in enumerate(profiles[:request.agents]):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or f"Stakeholder {index + 1}")[:100]
        username = "".join(ch for ch in str(item.get("username") or f"stakeholder_{index + 1}") if ch.isalnum() or ch == "_")[:30]
        normalized.append({
            "user_id": index,
            "username": username or f"stakeholder_{index + 1}",
            "name": name,
            "role": str(item.get("role") or "Stakeholder")[:120],
            "bio": str(item.get("bio") or item.get("role") or "Scenario participant")[:500],
            "persona": str(item.get("persona") or item.get("bio") or item.get("role") or "Scenario participant")[:1200],
            "opening_opinion": str(item.get("opening_opinion") or "I need more information before taking a position.")[:1000],
            "stance": str(item.get("stance") or "uncertain")[:80],
            "interests": item.get("interests", []) if isinstance(item.get("interests", []), list) else [],
        })
    if len(normalized) != request.agents:
        raise HTTPException(status_code=502, detail="Some generated agent profiles were invalid.")
    return normalized

def extract_activity(db_path: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read OASIS's own SQLite simulation output, without assuming a fixed schema."""
    tables: list[dict[str, Any]] = []
    activity: list[dict[str, Any]] = []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        names = [
            row["name"] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        ]
        for table in names:
            safe_table = table.replace('"', '""')
            try:
                rows = conn.execute(f'SELECT * FROM "{safe_table}" LIMIT 30').fetchall()
            except sqlite3.Error:
                continue
            samples = []
            for row in rows:
                record = {key: row[key] for key in row.keys()}
                samples.append(record)
                lowered = {str(key).lower(): value for key, value in record.items()}
                content = next((lowered[k] for k in ("content", "text", "post_content", "body", "caption") if isinstance(lowered.get(k), str) and lowered[k].strip()), None)
                if content:
                    activity.append({
                        "table": table,
                        "agent": next((str(lowered[k]) for k in ("agent_name", "username", "user_name", "author", "name") if lowered.get(k) is not None), "Simulation agent"),
                        "action": next((str(lowered[k]) for k in ("action_type", "action", "type") if lowered.get(k) is not None), "post"),
                        "content": str(content)[:1500],
                        "round": next((lowered[k] for k in ("round_num", "round", "step") if lowered.get(k) is not None), None),
                    })
            if samples:
                tables.append({"table": table, "rows": samples[:10]})
    return activity[:50], tables

@app.get("/health")
async def health():
    return {"ok": True, "engine": "camel-oasis", "version": "0.2.0"}

@app.post("/api/simulate")
async def simulate(request: SimulationRequest):
    """Run a small real OASIS social simulation and analyze its recorded output."""
    key, base, model_name = config()
    seed_graph = await build_seed_graph(request)
    profiles = await generate_profiles(request, seed_graph)

    try:
        # OASIS is loaded lazily so /health can still diagnose a deployment with missing dependencies.
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType
        import oasis
        from oasis import ActionType, LLMAction, ManualAction, generate_twitter_agent_graph
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"OASIS dependencies are unavailable: {type(exc).__name__}. Check backend build logs.") from exc

    with tempfile.TemporaryDirectory(prefix="scenariolab-") as work:
        root = Path(work)
        profile_path = root / "twitter_profiles.csv"
        db_path = root / "simulation.db"
        with profile_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "user_id", "username", "name", "bio", "persona",
                "friend_count", "follower_count", "statuses_count", "created_at"
            ])
            writer.writeheader()
            for profile in profiles:
                writer.writerow({
                    "user_id": profile["user_id"],
                    "username": profile["username"],
                    "name": profile["name"],
                    "bio": profile["bio"],
                    "persona": profile["persona"],
                    "friend_count": 30 + profile["user_id"] * 7,
                    "follower_count": 50 + profile["user_id"] * 13,
                    "statuses_count": 10,
                    "created_at": "2026-01-01",
                })

        os.environ["OPENAI_API_KEY"] = key
        os.environ["OPENAI_API_BASE_URL"] = base
        try:
            model = ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=model_name)
            agent_graph = await generate_twitter_agent_graph(
                profile_path=str(profile_path),
                model=model,
                available_actions=[
                    ActionType.CREATE_POST, ActionType.LIKE_POST, ActionType.REPOST,
                    ActionType.FOLLOW, ActionType.DO_NOTHING, ActionType.QUOTE_POST,
                ],
            )
            env = oasis.make(
                agent_graph=agent_graph,
                platform=oasis.DefaultPlatformType.TWITTER,
                database_path=str(db_path),
                semaphore=min(8, request.agents + 2),
            )
            await env.reset()
            agents = [agent_graph.get_agent(i) for i in range(request.agents)]
            opening_actions = {
                agent: ManualAction(
                    action_type=ActionType.CREATE_POST,
                    action_args={"content": f"{profiles[index]['name']} ({profiles[index]['role']}): {profiles[index]['opening_opinion']}"},
                )
                for index, agent in enumerate(agents)
            }
            await env.step(opening_actions)
            for _round in range(request.rounds):
                await env.step({agent: LLMAction() for agent in agents})
            close = getattr(env, "close", None)
            if close:
                result = close()
                if hasattr(result, "__await__"):
                    await result
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"OASIS simulation failed: {type(exc).__name__}. Check model compatibility and worker logs.") from exc

        activity, db_tables = extract_activity(str(db_path))
        evidence = {
            "scenario": request.scenario,
            "context": request.context,
            "agent_profiles": profiles,
            "recorded_activity": activity,
            "database_samples": db_tables,
            "activity_rows_found": len(activity),
        }
        report_data = await llm_json(
            "You are the report analyst for a completed multi-agent simulation. "
            "Use the supplied profiles and recorded simulation database evidence. "
            "Do not invent statistics or claim an event happened unless the evidence supports it. "
            "Clearly separate observed simulation activity from interpretation and assumptions. "
            "Return JSON with title, summary, scenarios (2-4 objects with name, likelihood, detail), "
            "signals (2-8 strings), caveat. Likelihood is qualitative, not a calibrated probability. "
            "Mention if recorded activity is sparse.",
            json.dumps(evidence, ensure_ascii=False)[:18000],
            max_tokens=1800,
        )
        report_data["agent_profiles"] = profiles
        report_data["activity"] = activity
        report_data["knowledge_graph"] = seed_graph
        report_data["simulation"] = {
            "engine": "camel-oasis",
            "platform": "twitter-like simulated environment",
            "agents_requested": request.agents,
            "rounds_requested": request.rounds,
            "recorded_activity_count": len(activity),
            "model": model_name,
        }
        return {"report": report_data, "meta": {"engine": "camel-oasis", "model": model_name, "agents": request.agents, "rounds": request.rounds, "demo": False, "recorded_activity_count": len(activity)}}
