alter table public.simulations
  add column if not exists request_fingerprint text;

create index if not exists simulations_request_fingerprint_created_at_idx
  on public.simulations (request_fingerprint, created_at desc)
  where request_fingerprint is not null;
