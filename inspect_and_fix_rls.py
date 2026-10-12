import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL").replace(":6543/", ":5432/")
if "?" not in url:
    url += "?sslmode=require"

conn = psycopg2.connect(url)
conn.autocommit = True
cur = conn.cursor()

print("Current policies on profiles:")
cur.execute("SELECT policyname, qual FROM pg_policies WHERE tablename = 'profiles';")
for p in cur.fetchall():
    print(" -", p[0], "-->", p[1])

print("\nFixing RLS recursion on profiles and other tables...")

sql_fix = """
-- 1. Create SECURITY DEFINER function to check admin status without recursion
CREATE OR REPLACE FUNCTION public.is_admin(_user_id uuid)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
STABLE
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = _user_id AND role = 'admin'
  );
$$;

-- 2. Drop the recursive policy on profiles
DROP POLICY IF EXISTS "Admin can view all profiles" ON public.profiles;

-- 3. Allow users to view their own profile OR admin can view all profiles
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can view their own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT
USING (
  auth.uid() = id OR public.is_admin(auth.uid())
);

-- 4. Update the remaining admin policies to use public.is_admin(auth.uid())
DROP POLICY IF EXISTS "Admin can view all cases" ON public.cases;
CREATE POLICY "Admin can view all cases" ON public.cases FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can insert cases" ON public.cases;
CREATE POLICY "Admin can insert cases" ON public.cases FOR INSERT
WITH CHECK (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can update cases" ON public.cases;
CREATE POLICY "Admin can update cases" ON public.cases FOR UPDATE
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all case members" ON public.case_members;
CREATE POLICY "Admin can view all case members" ON public.case_members FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can insert case members" ON public.case_members;
CREATE POLICY "Admin can insert case members" ON public.case_members FOR INSERT
WITH CHECK (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can delete case members" ON public.case_members;
CREATE POLICY "Admin can delete case members" ON public.case_members FOR DELETE
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all documents" ON public.documents;
CREATE POLICY "Admin can view all documents" ON public.documents FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can insert documents" ON public.documents;
CREATE POLICY "Admin can insert documents" ON public.documents FOR INSERT
WITH CHECK (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can update documents" ON public.documents;
CREATE POLICY "Admin can update documents" ON public.documents FOR UPDATE
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can delete documents" ON public.documents;
CREATE POLICY "Admin can delete documents" ON public.documents FOR DELETE
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all document chunks" ON public.document_chunks;
CREATE POLICY "Admin can view all document chunks" ON public.document_chunks FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can insert document chunks" ON public.document_chunks;
CREATE POLICY "Admin can insert document chunks" ON public.document_chunks FOR INSERT
WITH CHECK (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all ai runs" ON public.ai_runs;
CREATE POLICY "Admin can view all ai runs" ON public.ai_runs FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can insert ai runs" ON public.ai_runs;
CREATE POLICY "Admin can insert ai runs" ON public.ai_runs FOR INSERT
WITH CHECK (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can update ai runs" ON public.ai_runs;
CREATE POLICY "Admin can update ai runs" ON public.ai_runs FOR UPDATE
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all ai messages" ON public.ai_messages;
CREATE POLICY "Admin can view all ai messages" ON public.ai_messages FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all hearings" ON public.hearings;
CREATE POLICY "Admin can view all hearings" ON public.hearings FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all notes" ON public.notes;
CREATE POLICY "Admin can view all notes" ON public.notes FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all parties" ON public.parties;
CREATE POLICY "Admin can view all parties" ON public.parties FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all case parties" ON public.case_parties;
CREATE POLICY "Admin can view all case parties" ON public.case_parties FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can view all invitations" ON public.case_invitations;
CREATE POLICY "Admin can view all invitations" ON public.case_invitations FOR SELECT
USING (public.is_admin(auth.uid()));

DROP POLICY IF EXISTS "Admin can insert invitations" ON public.case_invitations;
CREATE POLICY "Admin can insert invitations" ON public.case_invitations FOR INSERT
WITH CHECK (public.is_admin(auth.uid()));
"""

cur.execute(sql_fix)
print("\n[OK] RLS security definer fix applied successfully!")

cur.close()
conn.close()
