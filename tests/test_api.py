from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_crear_empleado_y_fichaje():
    # crear empleado
    r = client.post("/empleados/", json={"dni": "0001A", "nombre": "Ismail", "rfid_uid": "rfid-001"})
    assert r.status_code == 200
    emp = r.json()
    assert emp["nombre"] == "Ismail" or emp.get("nombre") == "Ismail"

    # crear fichaje via simulador
    r2 = client.post("/fichajes/", json={"rfid_uid": "rfid-001"})
    assert r2.status_code == 200
    ficha = r2.json()
    assert ficha["tipo"] in ("entrada", "salida")
    assert isinstance(ficha["empleado_id"], str)
    # comprobar que el empleado existe en la lista
    rlist = client.get("/empleados/")
    assert rlist.status_code == 200
    empleados = rlist.json()
    assert any(e["dni"] == ficha["empleado_id"] for e in empleados)

    # listar fichajes
    r3 = client.get("/fichajes/")
    assert r3.status_code == 200
    lista = r3.json()
    assert isinstance(lista, list)


def test_horas_trabajadas_basicas():
    # crear empleado B
    r = client.post("/empleados/", json={"dni": "0002B", "nombre": "Ana", "rfid_uid": "rfid-ana"})
    assert r.status_code == 200
    emp = r.json()
    # entrada
    r1 = client.post("/fichajes/", json={"rfid_uid": "rfid-ana"})
    assert r1.status_code == 200
    # salida (simulate later timestamp by creating directly in DB via same endpoint)
    r2 = client.post("/fichajes/", json={"rfid_uid": "rfid-ana"})
    assert r2.status_code == 200

    # pedir reporte de horas
    r3 = client.get(f"/reportes/horas/{emp['dni']}")
    assert r3.status_code == 200
    rep = r3.json()
    assert rep["empleado_id"] == emp["dni"]
    assert isinstance(rep["total_hours"], float)
