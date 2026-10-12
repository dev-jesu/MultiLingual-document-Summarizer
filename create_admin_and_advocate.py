"""
Helper script to seed or ensure both Admin and Advocate accounts exist in Supabase Auth & Profiles
for testing the Admin Privilege and Document Allocation workflow.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    exit(1)

DATABASE_URL = DATABASE_URL.replace(":6543/", ":5432/")
if "?" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

USERS = [
    {
        "id": "a0000000-0000-4000-a000-000000000001",
        "email": "admin@ecourt.gov",
        "password": "Password@123",
        "full_name": "Court Administrator",
        "role": "admin"
    },
    {
        "id": "dba34454-4a6d-4d77-aa05-018f4074e117",
        "email": "advocate@ecourt.gov",
        "password": "Password@123",
        "full_name": "Advocate Ramesh",
        "role": "advocate"
    },
    {
        "id": "b0000000-0000-4000-b000-000000000002",
        "email": "advocate.priya@ecourt.gov",
        "password": "Password@123",
        "full_name": "Advocate Priya",
        "role": "advocate"
    }
]

def seed_users():
    print(f"Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        return

    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    
    # Run admin migration SQL
    try:
        with open("supabase_migration_admin.sql", "r", encoding="utf-8") as f:
            migration_sql = f.read()
        cur.execute(migration_sql)
        print("[OK] Applied supabase_migration_admin.sql")
    except Exception as e:
        print(f"[Note] Migration execution info: {e}")

    for u in USERS:
        # Delete existing identity & user to ensure clean state
        cur.execute("DELETE FROM auth.identities WHERE email = %s OR user_id = %s;", (u["email"], u["id"]))
        cur.execute("DELETE FROM auth.users WHERE email = %s OR id = %s;", (u["email"], u["id"]))

        # Insert user
        insert_user_sql = """
        INSERT INTO auth.users (
            instance_id, id, aud, role, email, encrypted_password,
            email_confirmed_at, raw_app_meta_data, raw_user_meta_data,
            created_at, updated_at, confirmation_token
        ) VALUES (
            '00000000-0000-0000-0000-000000000000',
            %s, 'authenticated', 'authenticated', %s,
            crypt(%s, gen_salt('bf', 10)),
            NOW(),
            '{"provider":"email","providers":["email"]}'::jsonb,
            json_build_object('full_name', %s)::jsonb,
            NOW(), NOW(), ''
        );
        """
        cur.execute(insert_user_sql, (u["id"], u["email"], u["password"], u["full_name"]))

        # Insert identity
        insert_identity_sql = """
        INSERT INTO auth.identities (
            id, user_id, identity_data, provider, provider_id,
            last_sign_in_at, created_at, updated_at
        ) VALUES (
            gen_random_uuid(), %s,
            json_build_object('sub', %s, 'email', %s, 'email_verified', true, 'phone_verified', false)::jsonb,
            'email', %s, NOW(), NOW(), NOW()
        );
        """
        cur.execute(insert_identity_sql, (u["id"], u["id"], u["email"], u["id"]))

        # Upsert profiles
        cur.execute("""
            INSERT INTO public.profiles (id, full_name, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name, role = EXCLUDED.role;
        """, (u["id"], u["full_name"], u["role"]))

        print(f"[OK] Seeded {u['role'].upper()}: {u['email']} (Password: {u['password']})")

    cur.close()
    conn.close()
    print("\nAll seed users created successfully!")

if __name__ == "__main__":
    seed_users()
