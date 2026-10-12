"""
Create a demo user directly in Supabase auth.users table via direct DB connection.
This bypasses the email confirmation flow entirely.
"""
import os
import uuid
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

db_url = os.getenv("DATABASE_URL", "").replace(":6543/", ":5432/")
if "?" not in db_url:
    db_url += "?sslmode=require"

DEMO_EMAIL    = "demo@ecourt.local"
DEMO_PASSWORD = "LegalAI@2025"
DEMO_FULLNAME = "Advocate Demo User"
DEMO_ROLE     = "advocate"
USER_ID       = str(uuid.uuid4())

def get_hashed_password(password: str) -> str:
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=10)).decode()
    except ImportError:
        pass
    try:
        from passlib.hash import bcrypt as pb
        return pb.hash(password, rounds=10)
    except ImportError:
        import subprocess
        subprocess.run(["pip", "install", "bcrypt"], capture_output=True)
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=10)).decode()

def main():
    try:
        print(f"Connecting to Supabase DB...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Check if demo user already exists
        cur.execute("SELECT id, email FROM auth.users WHERE email = %s", (DEMO_EMAIL,))
        existing = cur.fetchone()

        if existing:
            user_id = str(existing[0])
            print(f"User already exists: {user_id}")
        else:
            hashed = get_hashed_password(DEMO_PASSWORD)
            now = datetime.now(timezone.utc).isoformat()

            insert_sql = (
                "INSERT INTO auth.users ("
                "id, instance_id, email, encrypted_password, email_confirmed_at,"
                " created_at, updated_at,"
                " raw_app_meta_data, raw_user_meta_data,"
                " is_super_admin, role, aud, confirmation_token"
                ") VALUES ("
                " %s,"
                " '00000000-0000-0000-0000-000000000000',"
                " %s, %s, %s, %s, %s,"
                " '{\"provider\":\"email\",\"providers\":[\"email\"]}',"
                " '{}',"
                " FALSE, 'authenticated', 'authenticated', ''"
                ")"
            )
            cur.execute(insert_sql, (USER_ID, DEMO_EMAIL, hashed, now, now, now))
            user_id = USER_ID
            print(f"Created auth user: {user_id}")

        # Upsert profile
        upsert_sql = (
            "INSERT INTO public.profiles (id, full_name, role)"
            " VALUES (%s, %s, %s)"
            " ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name, role = EXCLUDED.role"
        )
        cur.execute(upsert_sql, (user_id, DEMO_FULLNAME, DEMO_ROLE))
        print(f"Upserted profile for: {user_id}")

        conn.commit()
        cur.close()
        conn.close()

        print()
        print("=" * 45)
        print("  DEMO LOGIN CREDENTIALS")
        print("=" * 45)
        print(f"  Email:    {DEMO_EMAIL}")
        print(f"  Password: {DEMO_PASSWORD}")
        print(f"  Role:     {DEMO_ROLE}")
        print(f"  User ID:  {user_id}")
        print("=" * 45)

    except Exception as e:
        print(f"Error: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()
