# Project Status

## Done
- Confirmed the connected GitHub, Supabase, and Vercel accounts.
- Published ScenarioLab Next.js/TypeScript application scaffold, simulation API, SQL migration, PRD, environment template, and setup documentation to GitHub.
- Verified the repository is `best-digital-offer/ScenarioLab-repository` on `main`.

## In progress
- Connecting a Vercel project; project creation through the connected Vercel integration returned HTTP 403 Forbidden.
- Selecting a dedicated Supabase project and organization; no new database has been created yet.

## Next
1. Resolve Vercel project-creation permissions or create/link the project in the Vercel dashboard.
2. Confirm the Supabase organization and create a dedicated ScenarioLab project, then review/apply the migration.
3. Configure provider secrets in Vercel (never commit secrets).
4. Add Supabase authentication and report persistence.
5. Add rate limits, usage ledger, end-to-end tests, accessibility checks, and monitoring.
6. Consider a dedicated Python multi-agent worker for deeper MiroFish/OASIS-style simulation.

## Open questions
- Confirm that the existing Supabase organization `yxyixddhnnrcuwuvzyki` is the intended organization for ScenarioLab.
- Initial niche: product launches, marketing/public opinion, or general business decisions.
- Billing provider and plan limits.

## Decisions
- Repository: `best-digital-offer/ScenarioLab-repository`.
- Keep ScenarioLab separate from QueueTurn and SameWindow.
- Bound initial runs to 3–5 perspectives and 1–2 rounds.
- Do not copy MiroFish wholesale; assess AGPL obligations before integration.

## Verification
- GitHub writes completed for the app scaffold, simulation API, schema migration, and docs.
- No production build, live model call, database migration, or deployment has been verified yet.
- Vercel project creation attempt failed with 403 Forbidden; no project was created by that attempt.
