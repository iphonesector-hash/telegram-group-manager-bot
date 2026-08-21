-- iSectorLand unified bot database
-- This schema is consumed by SQLAlchemy over the Supabase Postgres connection.

create table if not exists public.users (
  id bigint primary key,
  username text,
  first_name text,
  coins bigint not null default 0,
  bank_balance bigint not null default 0,
  loan_balance bigint not null default 0,
  xp bigint not null default 0,
  level integer not null default 1,
  message_count bigint not null default 0,
  last_daily_claim timestamp,
  vip_until timestamp,
  is_admin boolean not null default false,
  joined_at timestamp not null default now()
);

create table if not exists public.groups (
  id bigint primary key,
  title text,
  lock_links boolean not null default false,
  lock_usernames boolean not null default false,
  lock_forward boolean not null default false,
  lock_photos boolean not null default false,
  lock_videos boolean not null default false,
  lock_files boolean not null default false,
  lock_stickers boolean not null default false,
  lock_gifs boolean not null default false,
  lock_voice boolean not null default false,
  lock_contacts boolean not null default false,
  welcome_enabled boolean not null default true,
  welcome_text text not null default 'خوش اومدی به گروه 🌟\nلطفاً قوانین رو رعایت کن.',
  rules text,
  rules_enabled boolean not null default true,
  antispam_enabled boolean not null default true,
  antispam_limit integer not null default 5,
  economy_enabled boolean not null default true,
  ai_enabled boolean not null default true,
  prevent_bots boolean not null default false,
  new_member_limit boolean not null default false,
  approval_mode boolean not null default false,
  activity_logging boolean not null default true,
  is_active boolean not null default true,
  joined_at timestamp not null default now()
);

create table if not exists public.warnings (
  id bigserial primary key,
  user_id bigint references public.users(id) on delete cascade,
  group_id bigint references public.groups(id) on delete cascade,
  reason text not null default 'بدون دلیل',
  warned_by bigint,
  created_at timestamp not null default now()
);

create table if not exists public.mutes (
  id bigserial primary key,
  user_id bigint references public.users(id) on delete cascade,
  group_id bigint references public.groups(id) on delete cascade,
  until timestamp,
  created_at timestamp not null default now()
);

create table if not exists public.purchases (
  id bigserial primary key,
  user_id bigint not null references public.users(id) on delete cascade,
  item_id text not null,
  amount bigint not null default 0,
  telegram_payment_charge_id text unique,
  status text not null default 'completed',
  created_at timestamp not null default now()
);

create index if not exists idx_users_coins on public.users(coins desc);
create index if not exists idx_users_activity on public.users(message_count desc);
create index if not exists idx_warnings_group_user on public.warnings(group_id, user_id);
create index if not exists idx_mutes_group_user on public.mutes(group_id, user_id);
create index if not exists idx_purchases_user on public.purchases(user_id, created_at desc);

-- No public Data API access is needed for these tables. The Vercel bot connects directly to Postgres.
alter table public.users enable row level security;
alter table public.groups enable row level security;
alter table public.warnings enable row level security;
alter table public.mutes enable row level security;
alter table public.purchases enable row level security;

revoke all on public.users, public.groups, public.warnings, public.mutes, public.purchases from anon, authenticated;
