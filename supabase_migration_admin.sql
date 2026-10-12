-- ============================================================
-- MIGRATION: Add Admin Role & RLS Policies
-- ============================================================

-- 1. Update profiles role constraint to include 'admin'
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_role_check;
ALTER TABLE public.profiles ADD CONSTRAINT profiles_role_check
  CHECK (role IN ('admin', 'advocate', 'client'));

-- 2. Admin can view ALL profiles
CREATE POLICY "Admin can view all profiles" ON public.profiles FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles AS p WHERE p.id = auth.uid() AND p.role = 'admin')
);

-- 3. Admin can view ALL cases
CREATE POLICY "Admin can view all cases" ON public.cases FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 4. Admin can insert cases
CREATE POLICY "Admin can insert cases" ON public.cases FOR INSERT
WITH CHECK (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 5. Admin can update cases
CREATE POLICY "Admin can update cases" ON public.cases FOR UPDATE
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 6. Admin can view all case_members
CREATE POLICY "Admin can view all case members" ON public.case_members FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 7. Admin can insert case_members (enroll advocates/clients)
CREATE POLICY "Admin can insert case members" ON public.case_members FOR INSERT
WITH CHECK (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 8. Admin can delete case_members (remove enrollment)
CREATE POLICY "Admin can delete case members" ON public.case_members FOR DELETE
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 9. Admin can view all documents
CREATE POLICY "Admin can view all documents" ON public.documents FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 10. Admin can insert documents (allocate to cases)
CREATE POLICY "Admin can insert documents" ON public.documents FOR INSERT
WITH CHECK (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 11. Admin can update documents
CREATE POLICY "Admin can update documents" ON public.documents FOR UPDATE
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 12. Admin can delete documents
CREATE POLICY "Admin can delete documents" ON public.documents FOR DELETE
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 13. Admin can view all document chunks
CREATE POLICY "Admin can view all document chunks" ON public.document_chunks FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 14. Admin can insert document chunks
CREATE POLICY "Admin can insert document chunks" ON public.document_chunks FOR INSERT
WITH CHECK (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 15. Admin can view all AI runs
CREATE POLICY "Admin can view all ai runs" ON public.ai_runs FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 16. Admin can insert AI runs
CREATE POLICY "Admin can insert ai runs" ON public.ai_runs FOR INSERT
WITH CHECK (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 17. Admin can update AI runs
CREATE POLICY "Admin can update ai runs" ON public.ai_runs FOR UPDATE
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 18. Admin can view all AI messages
CREATE POLICY "Admin can view all ai messages" ON public.ai_messages FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 19. Admin can view all hearings
CREATE POLICY "Admin can view all hearings" ON public.hearings FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 20. Admin can view all notes
CREATE POLICY "Admin can view all notes" ON public.notes FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 21. Admin can manage parties
CREATE POLICY "Admin can view all parties" ON public.parties FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

CREATE POLICY "Admin can view all case parties" ON public.case_parties FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- 22. Admin can manage invitations
CREATE POLICY "Admin can view all invitations" ON public.case_invitations FOR SELECT
USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

CREATE POLICY "Admin can insert invitations" ON public.case_invitations FOR INSERT
WITH CHECK (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);
