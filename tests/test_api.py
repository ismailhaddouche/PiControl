from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_create_employee_and_checkin():
    # create employee
    r = client.post("/employees/", json={"document_id": "0001A", "name": "Ismail", "rfid_uid": "rfid-001"})
    assert r.status_code == 200
    emp = r.json()
    assert emp["name"] == "Ismail" or emp.get("name") == "Ismail"

    # create checkin via simulator
    r2 = client.post("/checkins/", json={"rfid_uid": "rfid-001"})
    assert r2.status_code == 200
    checkin = r2.json()
    assert checkin["type"] in ("entry", "exit")
    assert isinstance(checkin["employee_id"], str)
    # check that employee exists in the list
    rlist = client.get("/employees/")
    assert rlist.status_code == 200
    employees = rlist.json()
    assert any(e["document_id"] == checkin["employee_id"] for e in employees)

    # list checkins
    r3 = client.get("/checkins/")
    assert r3.status_code == 200
    lista = r3.json()
    assert isinstance(lista, list)


def test_hours_worked_basic():
    # create employee B
    r = client.post("/employees/", json={"document_id": "0002B", "name": "Ana", "rfid_uid": "rfid-ana"})
    assert r.status_code == 200
    emp = r.json()
    # entry
    r1 = client.post("/checkins/", json={"rfid_uid": "rfid-ana"})
    assert r1.status_code == 200
    # exit (simulate later timestamp by creating directly in DB via same endpoint)
    r2 = client.post("/checkins/", json={"rfid_uid": "rfid-ana"})
    assert r2.status_code == 200

    # request hours report
    r3 = client.get(f"/reports/hours/{emp['document_id']}")
    assert r3.status_code == 200
    rep = r3.json()
    assert rep["employee_id"] == emp["document_id"]
    assert isinstance(rep["total_hours"], float)
