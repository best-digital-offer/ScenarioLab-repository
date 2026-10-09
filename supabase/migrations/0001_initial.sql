-- ScenarioLab MVP schema. Apply only to a dedicated project after review.
create extension if not exists pgcrypto;
create table if not exists public.simulations (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 title text not null check (char_length(title) between 1 and 160),
 scenario text not null check (char_length(scenario) between 12 and 1200),
 context text not null default '' check (char_length(context)<=5000),
 status text not null default 'completed' check (status in ('queued','running','completed','failed')),
 agent_count smallint not null check (agent_count between 3 and 5),
 reasoning_rounds smallint not null check (reasoning_rounds between 1 and 2),
 report jsonb,
 model_name text,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create index if not exists simulations_user_created_idx on public.simulations(user_id,created_at desc);
alter table public.simulations enable row level security;
create policy "Users can read their own simulations" on public.simulations for select to authenticated using(auth.uid()=user_id);
create policy "Users can create their own simulations" on public.simulations for insert to authenticated with check(auth.uid()=user_id);
create policy "Users can update their own simulations" on public.simulations for update to authenticated using(auth.uid()=user_id) with check(auth.uid()=user_id);
create policy "Users can delete their own simulations" on public.simulations for delete to authenticated using(auth.uid()=user_id);
create or replace function public.set_updated_at() returns trigger language plpgsql as $$ begin new.updated_at=now(); return new; end; $$;
drop trigger if exists simulations_updated_at on public.simulations;
create trigger simulations_updated_at before update on public.simulations for each row execute function public.set_updated_at();
