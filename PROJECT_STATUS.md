# Project Status

## Done
- Confirmed connected GitHub, Supabase, and Vercel accounts.
- Created the initial ScenarioLab app scaffold and migration in the working package.
- Selected Next.js App Router + TypeScript, Supabase, and Vercel.

## In progress
- Publishing source files to the connected GitHub repository.
- Provisioning dedicated Supabase and Vercel resources.

## Next
1. Verify deployment build.
2. Add Supabase auth and report persistence.
3. Configure provider secrets in Vercel (never commit secrets).
4. Add rate limits, usage ledger, end-to-end tests, and monitoring.
5. Decide whether to integrate a dedicated Python multi-agent worker.

## Open questions
- Initial niche: product launches, marketing/public opinion, or general business decisions.
- Billing provider and plan limits.

## Decisions
- Repository: best-digital-offer/ScenarioLab-repository.
- Keep ScenarioLab separate from QueueTurn and SameWindow.
- Bound first-run scenarios to 3–5 perspectives and 1–2 rounds.
- Do not copy MiroFish wholesale; assess license before integration.

## Verification
- Repository existence verified through connected GitHub.
- Source files are being added. Build and live model call are not yet verified.
