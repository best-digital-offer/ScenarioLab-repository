# ScenarioLab MVP — Product Requirements

## Goal
Help founders, product teams, marketers, and decision-makers explore plausible outcomes using distinct AI perspectives and an uncertainty-aware report.

## Primary workflow
1. User enters a scenario and relevant context.
2. User selects a bounded number of perspectives and reasoning rounds.
3. Server validates inputs and calls a server-configured OpenAI-compatible model.
4. The app validates structured output and displays scenario paths, qualitative likelihood labels, and observable signals.
5. Authenticated users will save and revisit reports in a later slice.

## MVP scope
- Responsive scenario setup and report workspace.
- Server-side model call, strict output validation, bounded usage, safe errors.
- Supabase-ready data model with per-user row-level security.

## Not in first slice
Full MiroFish GraphRAG graph building, OASIS social network simulation, thousands of agents, file ingestion, live social integrations, teams, billing, or calibrated forecasting.

## Acceptance criteria
- Invalid input rejected on server and client.
- Missing credentials return explicit setup error, never fabricated output.
- Provider errors/timeouts return safe messages.
- Output validates before display.
- Agent/round limits enforced server-side.
- RLS restricts simulation rows to their owner.

## Success metrics
Activation (first completed simulation), successful report rate, provider failure rate, 7-day repeat use, and average model cost per report.

## Risks
Outputs are scenario narratives, not guaranteed predictions. Usage controls are required before public launch. Review MiroFish license obligations before incorporating upstream code.
