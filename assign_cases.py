"""
Script to create cases and allocate documents from Case_Documents folder:
- 2 case documents assigned to Advocate Ramesh Kumar (adv001)
- 2 case documents assigned to Advocate Priya Singh (adv002)
"""
import os
import sys
import httpx
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
DOCS_DIR = Path(__file__).resolve().parent / "Case_Documents"

CASES_TO_ASSIGN = [
    {
        "advocate_username": "adv001",
        "case_data": {
            "case_number": "C.A. No. 3098-3099/2023",
            "title": "Airports Economic Regulatory Authority of India vs Delhi International Airport Ltd. & Ors.",
            "court_name": "Supreme Court of India",
            "court_level": "Supreme Court",
            "stage": "Judgment",
            "status": "active",
            "description": "Civil Appeal concerning tariff determination, aeronautical assets valuation, and regulatory framework under the Airports Economic Regulatory Authority of India Act, 2008.",
        },
        "document_filename": "14927_2023_1_1502_56564_Judgement_18-Oct-2024.pdf"
    },
    {
        "advocate_username": "adv001",
        "case_data": {
            "case_number": "SLP(C) No. 19499/2024",
            "title": "Maharashtra State Road Transport Corporation vs Subhash S/O Laxmanrao Bramhe",
            "court_name": "Supreme Court of India",
            "court_level": "Supreme Court",
            "stage": "Judgment",
            "status": "active",
            "description": "Civil Appeal on service jurisprudence, departmental disciplinary inquiry procedures, and reinstatement of state transport corporation employee.",
        },
        "document_filename": "15023_2024_12_1505_59769_Judgement_27-Feb-2025.pdf"
    },
    {
        "advocate_username": "adv002",
        "case_data": {
            "case_number": "C.A. No. 6776-6777/2013",
            "title": "Kazi Akiloddin vs State of Maharashtra & Ors.",
            "court_name": "Supreme Court of India",
            "court_level": "Supreme Court",
            "stage": "Judgment",
            "status": "active",
            "description": "Civil Appeal regarding land acquisition reference, market value determination of acquired land, and grant of statutory solatium and interest.",
        },
        "document_filename": "21896_2013_3_1502_53535_Judgement_10-Jul-2024.pdf"
    },
    {
        "advocate_username": "adv002",
        "case_data": {
            "case_number": "SLP(C) No. 26697/2019",
            "title": "Delhi Development Authority vs Tejpal & Ors.",
            "court_name": "Supreme Court of India",
            "court_level": "Supreme Court",
            "stage": "Judgment",
            "status": "active",
            "description": "Civil Appeal on land acquisition lapsing dispute under Section 24(2) of the Right to Fair Compensation Act, 2013.",
        },
        "document_filename": "22654_2019_4_1502_53374_Judgement_17-May-2024.pdf"
    }
]


def run():
    client = httpx.Client(base_url=BASE_URL, timeout=60.0, follow_redirects=True)

    # 1. Admin login
    print("1. Logging in as Admin...")
    admin_password = None
    for candidate in ["Admin@123", "Password@123"]:
        res = client.post("/auth/login", json={"username": "admin", "password": candidate})
        if res.status_code == 200:
            admin_password = candidate
            break

    if admin_password is None:
        print(f"Failed to log in as admin with available passwords: {res.text}")
        sys.exit(1)

    print(f"   Admin login successful using password: {admin_password}")
    admin_token = client.post("/auth/login", json={"username": "admin", "password": admin_password}).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Get advocates map
    print("2. Fetching advocates...")
    adv_res = client.get("/admin/advocates", headers=admin_headers)
    advocates = {u["username"]: u for u in adv_res.json()}
    print(f"   Found {len(advocates)} advocates: {list(advocates.keys())}")

    # Check existing cases
    existing_cases_res = client.get("/admin/cases", headers=admin_headers)
    existing_cases = {c["case_number"]: c for c in existing_cases_res.json()}

    # 3. Create cases, enroll advocates, and allocate documents
    for i, item in enumerate(CASES_TO_ASSIGN, 1):
        case_info = item["case_data"]
        adv_uname = item["advocate_username"]
        doc_fname = item["document_filename"]
        adv_user = advocates.get(adv_uname)

        if not adv_user:
            print(f"Error: advocate {adv_uname} not found!")
            continue

        print(f"\n--- [{i}/4] Processing Case: {case_info['case_number']} for {adv_user['full_name']} ({adv_uname}) ---")

        # Create or find case
        if case_info["case_number"] in existing_cases:
            case = existing_cases[case_info["case_number"]]
            case_id = case["id"]
            print(f"   Case already exists (ID: {case_id})")
        else:
            case_create_res = client.post("/admin/cases", json=case_info, headers=admin_headers)
            if case_create_res.status_code not in (200, 201):
                print(f"   Failed to create case: {case_create_res.text}")
                continue
            case = case_create_res.json()
            case_id = case["id"]
            print(f"   Created Case (ID: {case_id}): {case['title']}")

        # Enroll advocate
        enroll_res = client.post(
            f"/admin/cases/{case_id}/enroll",
            json={"advocate_id": adv_user["id"], "role": "advocate"},
            headers=admin_headers
        )
        if enroll_res.status_code in (200, 201):
            print(f"   Enrolled {adv_user['full_name']} into case.")
        elif enroll_res.status_code == 409:
            print(f"   Advocate {adv_user['full_name']} is already enrolled.")
        else:
            print(f"   Enrollment notice: {enroll_res.text}")

        # Check existing documents for this case
        case_details_res = client.get(f"/admin/cases/{case_id}", headers=admin_headers)
        existing_doc_names = [d["file_name"] for d in case_details_res.json().get("documents", [])]

        if doc_fname in existing_doc_names:
            print(f"   Document {doc_fname} already allocated.")
        else:
            file_path = DOCS_DIR / doc_fname
            if not file_path.exists():
                print(f"   Error: File {file_path} does not exist!")
                continue

            print(f"   Allocating document: {doc_fname} ({file_path.stat().st_size / 1024:.1f} KB)...")
            with open(file_path, "rb") as f:
                upload_res = client.post(
                    f"/admin/cases/{case_id}/allocate-document",
                    files={"file": (doc_fname, f, "application/pdf")},
                    headers=admin_headers
                )
            if upload_res.status_code in (200, 201):
                doc_obj = upload_res.json()
                print(f"   Document allocated successfully! Status: {doc_obj.get('processing_status')}, ID: {doc_obj.get('id')}")
            else:
                print(f"   Failed to allocate document: {upload_res.text}")

    # 4. Verify advocates can view their cases
    print("\n================== VERIFICATION ==================")
    for uname, pwd, expected_count in [("adv001", "Adv@12345", 2), ("adv002", "Adv@67890", 2)]:
        login_res = client.post("/auth/login", json={"username": uname, "password": pwd})
        if login_res.status_code != 200:
            print(f"Verification failed: could not login as {uname}")
            continue
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        cases_res = client.get("/cases/", headers=headers)
        user_cases = cases_res.json()
        full_name = login_res.json().get("full_name", uname)
        print(f"\nAdvocate {uname} ({full_name}):")
        print(f"  Enrolled Cases: {len(user_cases)} (Expected: {expected_count})")
        for c in user_cases:
            c_detail = client.get(f"/cases/{c['id']}", headers=headers).json()
            c_docs = c_detail.get("documents", [])
            print(f"   - [{c['case_number']}] {c['title'][:55]}...")
            print(f"     Documents ({len(c_docs)}): {[d['file_name'] for d in c_docs]}")


if __name__ == "__main__":
    run()
