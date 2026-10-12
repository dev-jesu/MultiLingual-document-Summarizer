import os
import psycopg2
from dotenv import load_dotenv
from app.services.supabase_service import get_supabase

load_dotenv()

ACCOUNTS = [
    {
        "email": "ecourt.admin@gmail.com",
        "password": "Password@123",
        "full_name": "Court Administrator",
        "role": "admin"
    },
    {
        "email": "ecourt.advocate@gmail.com",
        "password": "Password@123",
        "full_name": "Advocate Ramesh",
        "role": "advocate"
    },
    {
        "email": "ecourt.priya@gmail.com",
        "password": "Password@123",
        "full_name": "Advocate Priya",
        "role": "advocate"
    }
]

def setup_accounts():
    supabase = get_supabase()
    db_url = os.getenv("DATABASE_URL").replace(":6543/", ":5432/")
    if "?" not in db_url:
        db_url += "?sslmode=require"

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    print("Step 1: Signing up users via Supabase GoTrue Auth...")
    user_ids = {}

    for acc in ACCOUNTS:
        email = acc["email"]
        password = acc["password"]
        
        # Check if already in auth.users
        cur.execute("SELECT id FROM auth.users WHERE email = %s;", (email,))
        row = cur.fetchone()
        if row:
            uid = row[0]
            print(f" - Found existing user for {email} ({uid})")
            user_ids[email] = uid
        else:
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                if res.user:
                    uid = res.user.id
                    print(f" - Successfully signed up {email} ({uid})")
                    user_ids[email] = uid
            except Exception as e:
                print(f" - Signup error for {email}: {e}")

    print("\nStep 2: Confirming emails and assigning roles in PostgreSQL...")
    for acc in ACCOUNTS:
        email = acc["email"]
        role = acc["role"]
        name = acc["full_name"]
        
        # 1. Confirm email in auth.users
        cur.execute("UPDATE auth.users SET email_confirmed_at = NOW() WHERE email = %s;", (email,))
        
        # 2. Get user id
        cur.execute("SELECT id FROM auth.users WHERE email = %s;", (email,))
        row = cur.fetchone()
        if row:
            uid = row[0]
            # 3. Upsert into public.profiles
            cur.execute("""
                INSERT INTO public.profiles (id, full_name, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET full_name = EXCLUDED.full_name, role = EXCLUDED.role;
            """, (uid, name, role))
            print(f" - Set {email} -> role: {role}, full_name: {name}")

    cur.close()
    conn.close()

    print("\nStep 3: Verifying logins via Supabase Auth API...")
    for acc in ACCOUNTS:
        email = acc["email"]
        password = acc["password"]
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            print(f" ✅ Login SUCCESS for {email} ({acc['role'].upper()}) - Token OK!")
        except Exception as e:
            print(f" ❌ Login FAILED for {email}: {e}")

if __name__ == "__main__":
    setup_accounts()
