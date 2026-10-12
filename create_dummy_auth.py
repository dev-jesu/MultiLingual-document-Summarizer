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

# Dummy credentials
USER_ID = "dba34454-4a6d-4d77-aa05-018f4074e117"
DUMMY_EMAIL = "advocate@ecourt.gov"
DUMMY_PASSWORD = "Password@123"
FULL_NAME = "Advocate Ramesh"
ROLE = "advocate"

def create_user():
    print(f"Connecting to Postgres at {DATABASE_URL[:30]}...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    # Enable extensions
    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # Remove existing dummy user if present
    cur.execute("DELETE FROM auth.identities WHERE email = %s OR user_id = %s;", (DUMMY_EMAIL, USER_ID))
    cur.execute("DELETE FROM auth.users WHERE email = %s OR id = %s;", (DUMMY_EMAIL, USER_ID))

    # Insert into auth.users
    insert_user_sql = """
    INSERT INTO auth.users (
        instance_id,
        id,
        aud,
        role,
        email,
        encrypted_password,
        email_confirmed_at,
        raw_app_meta_data,
        raw_user_meta_data,
        created_at,
        updated_at,
        confirmation_token
    ) VALUES (
        '00000000-0000-0000-0000-000000000000',
        %s,
        'authenticated',
        'authenticated',
        %s,
        crypt(%s, gen_salt('bf', 10)),
        NOW(),
        '{"provider":"email","providers":["email"]}'::jsonb,
        json_build_object('full_name', %s)::jsonb,
        NOW(),
        NOW(),
        ''
    );
    """
    cur.execute(insert_user_sql, (USER_ID, DUMMY_EMAIL, DUMMY_PASSWORD, FULL_NAME))
    print(f"[OK] Inserted into auth.users (id={USER_ID}, email={DUMMY_EMAIL})")

    # Insert into auth.identities (note: email column is a generated column)
    insert_identity_sql = """
    INSERT INTO auth.identities (
        id,
        user_id,
        identity_data,
        provider,
        provider_id,
        last_sign_in_at,
        created_at,
        updated_at
    ) VALUES (
        gen_random_uuid(),
        %s,
        json_build_object('sub', %s, 'email', %s, 'email_verified', true, 'phone_verified', false)::jsonb,
        'email',
        %s,
        NOW(),
        NOW(),
        NOW()
    );
    """
    cur.execute(insert_identity_sql, (USER_ID, USER_ID, DUMMY_EMAIL, USER_ID))
    print("[OK] Inserted into auth.identities")

    # Upsert public.profiles
    cur.execute("""
        INSERT INTO public.profiles (id, full_name, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name, role = EXCLUDED.role;
    """, (USER_ID, FULL_NAME, ROLE))
    print(f"[OK] Upserted public.profiles for {FULL_NAME} ({ROLE})")

    cur.close()
    conn.close()

if __name__ == "__main__":
    create_user()
