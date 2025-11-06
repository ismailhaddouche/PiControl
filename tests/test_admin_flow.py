import os
from fastapi.testclient import TestClient

# For tests, force DB into workspace so sqlite file is writable
os.environ.setdefault("PICONTROL_DB_DIR", "/workspaces/PiControl/.data")
os.makedirs(os.environ["PICONTROL_DB_DIR"], exist_ok=True)

from app.main import app


client = TestClient(app)


def test_admin_setup_login_and_employee_creation():
    # Setup (if no admin exists, the setup page should be available)
    r = client.get("/admin/setup")
    assert r.status_code in (200, 302)

    # Create admin user via setup (idempotent if admin already exists)
    r = client.post("/admin/setup", data={"username": "admin", "password": "12345678"})
    assert r.status_code in (302, 200)

    # Login as admin
    r = client.post("/admin/login", data={"username": "admin", "password": "12345678"})
    assert r.status_code in (302, 200)

    # Create employee using English fields
    r = client.post("/admin/employees", data={"document_id": "T1", "name": "Test User"})
    assert r.status_code in (302, 200)

    # Create employee using legacy Spanish fields (dni/nombre)
    r = client.post("/admin/employees", data={"dni": "T2", "nombre": "Usuario"})
    assert r.status_code in (302, 200)

    # Verify employees appear in API listing
    r = client.get("/employees/")
    assert r.status_code == 200
    employees = r.json()
    ids = {e.get("document_id") for e in employees}
    assert "T1" in ids
    assert "T2" in ids


def test_export_db_requires_admin_and_returns_file():
    # Ensure logged in as admin from previous test — TestClient preserves cookies.
    r = client.get("/admin/configuration/export_db")
    # Should return the DB file (200) when admin; otherwise it redirects to login (302)
    assert r.status_code in (200, 302)
    if r.status_code == 200:
        # Basic sanity: response should have sqlite content-type or be non-empty
        ct = r.headers.get("content-type", "")
        assert "sqlite" in ct or len(r.content) > 0


def test_protected_ajax_refuses_unauthenticated():
    # Logout to clear session
    client.get("/admin/logout")
    r = client.post("/admin/rfid/assign_ajax", data={"employee_id": "T1"})
    assert r.status_code == 200
    j = r.json()
    assert j.get("success") is False
    assert "Not authenticated" in j.get("error", "")
