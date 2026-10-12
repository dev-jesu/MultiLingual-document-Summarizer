import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    exit(1)

DATABASE_URL = DATABASE_URL.replace(":6543/", ":5432/")

if "?" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

USER_ID = "11111111-1111-1111-1111-111111111111"
CASE_ID_1 = "22222222-2222-2222-2222-222222222222"
CASE_ID_2 = "33333333-3333-3333-3333-333333333333"

def seed_db():
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("Applying supabase_schema.sql...")
        with open("supabase_schema.sql", "r") as f:
            schema_sql = f.read()
        cur.execute(schema_sql)
        
        print("Removing auth.users foreign key constraint for demo purposes...")
        cur.execute("""
            ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;
        """)

        print("Inserting profile...")
        cur.execute("""
            INSERT INTO public.profiles (id, full_name, role)
            VALUES (%s, 'Advocate Ramesh', 'advocate')
            ON CONFLICT (id) DO NOTHING;
        """, (USER_ID,))

        print("Inserting cases...")
        cur.execute("""
            INSERT INTO public.cases (id, case_number, court_name, court_level, status, stage, description, created_by)
            VALUES 
            (%s, 'C.C. No. 1245/2025', 'Judicial Magistrate Court, Tirunelveli', 'District', 'pending', 'Arguments', 'Criminal Defamation Case', %s),
            (%s, 'O.S. No. 438/2024', 'Civil Court, Madurai', 'District', 'active', 'Evidence', 'Property Dispute', %s)
            ON CONFLICT (id) DO NOTHING;
        """, (CASE_ID_1, USER_ID, CASE_ID_2, USER_ID))

        print("Inserting case members...")
        cur.execute("""
            INSERT INTO public.case_members (case_id, user_id, role)
            VALUES 
            (%s, %s, 'owner'),
            (%s, %s, 'owner')
            ON CONFLICT (case_id, user_id) DO NOTHING;
        """, (CASE_ID_1, USER_ID, CASE_ID_2, USER_ID))

        print("Inserting parties...")
        PARTY_1 = "44444444-4444-4444-4444-444444444444"
        PARTY_2 = "55555555-5555-5555-5555-555555555555"
        cur.execute("""
            INSERT INTO public.parties (id, name, party_type)
            VALUES 
            (%s, 'Ramesh Kumar', 'individual'),
            (%s, 'State of Tamil Nadu', 'government')
            ON CONFLICT (id) DO NOTHING;
        """, (PARTY_1, PARTY_2))

        print("Linking parties to cases...")
        cur.execute("""
            INSERT INTO public.case_parties (case_id, party_id, role)
            VALUES 
            (%s, %s, 'Accused'),
            (%s, %s, 'Complainant')
            ON CONFLICT (case_id, party_id) DO NOTHING;
        """, (CASE_ID_1, PARTY_1, CASE_ID_1, PARTY_2))

        conn.commit()
        cur.close()
        conn.close()
        print("Successfully seeded the database!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    seed_db()
