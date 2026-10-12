import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL").replace(":6543/", ":5432/")
if "?" not in url:
    url += "?sslmode=require"

conn = psycopg2.connect(url)
cur = conn.cursor()

sql = """
CREATE OR REPLACE FUNCTION public.is_case_member(_case_id uuid, _user_id uuid)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
STABLE
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.case_members
    WHERE case_id = _case_id AND user_id = _user_id
  );
$$;

DROP POLICY IF EXISTS "Case members can view other members" ON public.case_members;
CREATE POLICY "Case members can view other members" ON public.case_members FOR SELECT
USING (
  user_id = auth.uid() OR public.is_case_member(case_id, auth.uid())
);
"""

cur.execute(sql)
conn.commit()
print("Fix applied successfully!")

# Now test querying case_members and cases
from app.services.supabase_service import get_anon_supabase
sb = get_anon_supabase()
tables = ['profiles', 'cases', 'documents', 'case_members', 'parties', 'case_parties', 'document_chunks']
for t in tables:
    try:
        r = sb.table(t).select('*').limit(1).execute()
        print(f"{t}: OK (rows={len(r.data)})")
    except Exception as e:
        print(f"{t}: ERROR ({e})")

conn.close()
