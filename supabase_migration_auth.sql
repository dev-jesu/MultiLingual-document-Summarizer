-- ============================================================
-- Authentication Migration
-- Run this in the Supabase SQL Editor AFTER the base schema.
-- ============================================================

-- 1. Extend profiles.role to include 'admin'
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_role_check;
ALTER TABLE public.profiles ADD CONSTRAINT profiles_role_check
  CHECK (role IN ('admin', 'advocate', 'client'));

-- 2. Add invitation_token to case_invitations for secure accept links
ALTER TABLE public.case_invitations
  ADD COLUMN IF NOT EXISTS invitation_token uuid DEFAULT gen_random_uuid() UNIQUE;

-- 3. RLS policies for case_invitations

-- Advocates can view invitations for cases they own/advocate
CREATE POLICY "Advocates can view case invitations"
  ON public.case_invitations FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.case_members
      WHERE case_members.case_id = case_invitations.case_id
        AND case_members.user_id = auth.uid()
        AND case_members.role IN ('owner', 'advocate')
    )
  );

-- Advocates can create invitations for cases they own/advocate
CREATE POLICY "Advocates can create case invitations"
  ON public.case_invitations FOR INSERT
  WITH CHECK (
    invited_by = auth.uid()
    AND EXISTS (
      SELECT 1 FROM public.case_members
      WHERE case_members.case_id = case_invitations.case_id
        AND case_members.user_id = auth.uid()
        AND case_members.role IN ('owner', 'advocate')
    )
  );

-- Advocates can update (cancel) invitations they created
CREATE POLICY "Advocates can update their invitations"
  ON public.case_invitations FOR UPDATE
  USING (
    invited_by = auth.uid()
  );

-- 4. Admin policies for profiles (admin can see all profiles)
CREATE POLICY "Admin can view all profiles"
  ON public.profiles FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles AS p
      WHERE p.id = auth.uid() AND p.role = 'admin'
    )
  );

-- Users can see profiles of users they share a case with
CREATE POLICY "Users can view case-mate profiles"
  ON public.profiles FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.case_members cm1
      JOIN public.case_members cm2 ON cm1.case_id = cm2.case_id
      WHERE cm1.user_id = auth.uid() AND cm2.user_id = profiles.id
    )
  );

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- 5. INSERT policies for documents (advocates can upload)
CREATE POLICY "Advocates can insert documents"
  ON public.documents FOR INSERT
  WITH CHECK (
    uploaded_by = auth.uid()
    AND EXISTS (
      SELECT 1 FROM public.case_members
      WHERE case_members.case_id = documents.case_id
        AND case_members.user_id = auth.uid()
        AND case_members.role IN ('owner', 'advocate')
    )
  );

-- 6. INSERT policies for notes
CREATE POLICY "Advocates can insert notes"
  ON public.notes FOR INSERT
  WITH CHECK (
    created_by = auth.uid()
    AND EXISTS (
      SELECT 1 FROM public.case_members
      WHERE case_members.case_id = notes.case_id
        AND case_members.user_id = auth.uid()
        AND case_members.role IN ('owner', 'advocate')
    )
  );

-- 7. INSERT policies for ai_runs
CREATE POLICY "Advocates can insert ai_runs"
  ON public.ai_runs FOR INSERT
  WITH CHECK (
    initiated_by = auth.uid()
    AND EXISTS (
      SELECT 1 FROM public.case_members
      WHERE case_members.case_id = ai_runs.case_id
        AND case_members.user_id = auth.uid()
        AND case_members.role IN ('owner', 'advocate')
    )
  );

-- 8. Admin can view all cases
CREATE POLICY "Admin can view all cases"
  ON public.cases FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
    )
  );

-- 9. Profiles INSERT policy (for service-role creating profiles for new users)
CREATE POLICY "Service role can insert profiles"
  ON public.profiles FOR INSERT
  WITH CHECK (true);
