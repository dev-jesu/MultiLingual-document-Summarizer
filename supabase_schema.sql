-- 1. PROFILES
create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    full_name text not null,
    phone text,
    role text not null check (role in ('advocate', 'client')),
    avatar_url text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- 2. CASES
create table if not exists public.cases (
    id uuid primary key default gen_random_uuid(),
    case_number text not null,
    cnr_number text,
    case_type text,
    court_name text,
    court_level text,
    district text,
    state text,
    filing_date date,
    status text not null default 'active' check (status in ('active', 'pending', 'disposed', 'closed')),
    stage text,
    description text,
    created_by uuid not null references public.profiles(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- 3. CASE MEMBERS
create table if not exists public.case_members (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.cases(id) on delete cascade,
    user_id uuid not null references public.profiles(id) on delete cascade,
    role text not null check (role in ('owner', 'advocate', 'client')),
    created_at timestamptz not null default now(),
    unique(case_id, user_id)
);

-- 4. PARTIES
create table if not exists public.parties (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    party_type text check (party_type in ('individual', 'organization', 'government')),
    address text,
    contact text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- 5. CASE PARTIES
create table if not exists public.case_parties (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.cases(id) on delete cascade,
    party_id uuid not null references public.parties(id) on delete cascade,
    role text not null,
    created_at timestamptz not null default now(),
    unique(case_id, party_id)
);

-- 6. DOCUMENTS
create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.cases(id) on delete cascade,
    uploaded_by uuid not null references public.profiles(id),
    file_name text not null,
    storage_path text not null,
    file_type text not null,
    file_size bigint,
    document_type text,
    document_date date,
    description text,
    processing_status text not null default 'uploaded' check (processing_status in ('uploaded', 'processing', 'completed', 'failed')),
    extracted_text text,
    client_visible boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- 7. DOCUMENT CHUNKS
create table if not exists public.document_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references public.documents(id) on delete cascade,
    chunk_index integer not null,
    page_start integer,
    page_end integer,
    content text not null,
    estimated_tokens integer,
    created_at timestamptz not null default now(),
    unique(document_id, chunk_index)
);

-- 8. HEARINGS
create table if not exists public.hearings (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.cases(id) on delete cascade,
    hearing_date date not null,
    court_room text,
    purpose text,
    status text,
    outcome text,
    next_date date,
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- 9. NOTES
create table if not exists public.notes (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.cases(id) on delete cascade,
    created_by uuid not null references public.profiles(id),
    title text,
    content text not null,
    client_visible boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- 10. AI RUNS
create table if not exists public.ai_runs (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.cases(id) on delete cascade,
    document_id uuid references public.documents(id) on delete cascade,
    initiated_by uuid not null references public.profiles(id),
    operation text not null check (operation in ('summarization', 'translation', 'key_information', 'question_answering')),
    source_language text,
    target_language text,
    model text,
    status text not null default 'pending' check (status in ('pending', 'processing', 'completed', 'failed')),
    input_tokens integer,
    output_tokens integer,
    result text,
    client_visible boolean not null default false,
    created_at timestamptz not null default now(),
    completed_at timestamptz
);

-- 11. AI MESSAGES
create table if not exists public.ai_messages (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.cases(id) on delete cascade,
    document_id uuid references public.documents(id) on delete set null,
    user_id uuid not null references public.profiles(id),
    role text not null check (role in ('user', 'assistant')),
    content text not null,
    citations jsonb,
    client_visible boolean not null default false,
    created_at timestamptz not null default now()
);

-- 12. CASE INVITATIONS
create table if not exists public.case_invitations (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references public.cases(id) on delete cascade,
    email text not null,
    invited_role text not null default 'client' check (invited_role = 'client'),
    invited_by uuid not null references public.profiles(id),
    status text not null default 'pending' check (status in ('pending', 'accepted', 'expired', 'cancelled')),
    expires_at timestamptz,
    created_at timestamptz not null default now(),
    accepted_at timestamptz
);

-- INDEXES
create index if not exists idx_case_members_user_id on public.case_members(user_id);
create index if not exists idx_case_members_case_id on public.case_members(case_id);
create index if not exists idx_case_members_user_case on public.case_members(user_id, case_id);
create index if not exists idx_documents_case_id on public.documents(case_id);
create index if not exists idx_document_chunks_document_id on public.document_chunks(document_id);
create index if not exists idx_hearings_case_id on public.hearings(case_id);
create index if not exists idx_notes_case_id on public.notes(case_id);
create index if not exists idx_ai_runs_case_id on public.ai_runs(case_id);
create index if not exists idx_ai_messages_case_id on public.ai_messages(case_id);

-- ENABLE RLS
alter table public.profiles enable row level security;
alter table public.cases enable row level security;
alter table public.case_members enable row level security;
alter table public.parties enable row level security;
alter table public.case_parties enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.hearings enable row level security;
alter table public.notes enable row level security;
alter table public.ai_runs enable row level security;
alter table public.ai_messages enable row level security;
alter table public.case_invitations enable row level security;

-- ROW LEVEL SECURITY POLICIES

-- Profiles: users can see their own profile. For others, they might need to see members of their case.
-- We keep it simple: users can see profiles of users they share a case with, or their own.
create policy "Users can view their own profile" on public.profiles for select using (auth.uid() = id);

-- Cases: User must be a member of the case to view it.
create policy "Case members can view case" on public.cases for select
using (
    exists (
        select 1 from public.case_members 
        where case_members.case_id = cases.id and case_members.user_id = auth.uid()
    )
);

create policy "Advocates can insert cases" on public.cases for insert
with check (
    auth.uid() = created_by
    and exists (select 1 from public.profiles where id = auth.uid() and role = 'advocate')
);

create policy "Owner/advocate can update cases" on public.cases for update
using (
    exists (
        select 1 from public.case_members 
        where case_members.case_id = cases.id and case_members.user_id = auth.uid() and role in ('owner', 'advocate')
    )
);

-- Case Members: Users can see members of their own cases.
create policy "Case members can view other members" on public.case_members for select
using (
    exists (
        select 1 from public.case_members as my_cases
        where my_cases.case_id = case_members.case_id and my_cases.user_id = auth.uid()
    )
);

create policy "Advocates can insert case members" on public.case_members for insert
with check (
    exists (
        select 1 from public.case_members as my_cases
        where my_cases.case_id = case_members.case_id and my_cases.user_id = auth.uid() and my_cases.role in ('owner', 'advocate')
    )
    or
    (user_id = auth.uid()) -- for initial creation of the case owner
);

-- Parties: Anyone in the case can see parties.
create policy "Case members can view case parties" on public.case_parties for select
using (
    exists (
        select 1 from public.case_members
        where case_members.case_id = case_parties.case_id and case_members.user_id = auth.uid()
    )
);

-- Documents: 
-- Advocates can see all documents in their cases.
-- Clients can only see client_visible documents in their cases.
create policy "Advocates can view all documents in case" on public.documents for select
using (
    exists (
        select 1 from public.case_members
        where case_members.case_id = documents.case_id and case_members.user_id = auth.uid() and case_members.role in ('owner', 'advocate')
    )
);

create policy "Clients can view visible documents" on public.documents for select
using (
    client_visible = true 
    and exists (
        select 1 from public.case_members
        where case_members.case_id = documents.case_id and case_members.user_id = auth.uid()
    )
);

-- Notes: Same logic as documents
create policy "Advocates can view all notes in case" on public.notes for select
using (
    exists (
        select 1 from public.case_members
        where case_members.case_id = notes.case_id and case_members.user_id = auth.uid() and case_members.role in ('owner', 'advocate')
    )
);

create policy "Clients can view visible notes" on public.notes for select
using (
    client_visible = true 
    and exists (
        select 1 from public.case_members
        where case_members.case_id = notes.case_id and case_members.user_id = auth.uid()
    )
);

-- AI Runs: Same logic
create policy "Advocates can view all ai runs in case" on public.ai_runs for select
using (
    exists (
        select 1 from public.case_members
        where case_members.case_id = ai_runs.case_id and case_members.user_id = auth.uid() and case_members.role in ('owner', 'advocate')
    )
);

create policy "Clients can view visible ai runs" on public.ai_runs for select
using (
    client_visible = true 
    and exists (
        select 1 from public.case_members
        where case_members.case_id = ai_runs.case_id and case_members.user_id = auth.uid()
    )
);

-- Hearings: Anyone in the case can see hearings
create policy "Case members can view hearings" on public.hearings for select
using (
    exists (
        select 1 from public.case_members
        where case_members.case_id = hearings.case_id and case_members.user_id = auth.uid()
    )
);

-- Document chunks
create policy "Case members can view document chunks" on public.document_chunks for select
using (
    exists (
        select 1 from public.documents 
        where documents.id = document_chunks.document_id 
        and (
            documents.client_visible = true or 
            exists (
                select 1 from public.case_members
                where case_members.case_id = documents.case_id and case_members.user_id = auth.uid() and case_members.role in ('owner', 'advocate')
            )
        )
    )
);
