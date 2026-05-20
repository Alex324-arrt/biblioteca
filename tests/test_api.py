import sys
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient


# Permite importar server.py desde la carpeta fastapi/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_DIR = PROJECT_ROOT / "fastapi"
sys.path.insert(0, str(FASTAPI_DIR))

import server  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """
    Crea un entorno de pruebas aislado para no modificar los CSV reales del proyecto.
    """

    books_csv = tmp_path / "books.csv"
    users_csv = tmp_path / "users.csv"
    loans_csv = tmp_path / "loans.csv"

    books_df = pd.DataFrame(
        [
            {
                "id": 1,
                "titulo": "The Great Gatsby",
                "autor": "F. Scott Fitzgerald",
                "genero": "Clásico",
                "disponible": True,
            },
            {
                "id": 2,
                "titulo": "Clean Code",
                "autor": "Robert C. Martin",
                "genero": "Técnico",
                "disponible": True,
            },
        ]
    )

    users_df = pd.DataFrame(
        [
            {
                "id": 1,
                "nombre": "Jesús Ramírez",
                "email": "jesus@email.com",
            }
        ]
    )

    loans_df = pd.DataFrame(
        columns=[
            "id",
            "usuario_id",
            "libro_id",
            "fecha_prestamo",
            "estado",
            "fecha_devolucion",
        ]
    )

    books_df.to_csv(books_csv, sep=";", index=False)
    users_df.to_csv(users_csv, sep=";", index=False)
    loans_df.to_csv(loans_csv, sep=";", index=False)

    monkeypatch.setattr(server, "BOOKS_CSV_PATH", str(books_csv))
    monkeypatch.setattr(server, "USERS_CSV_PATH", str(users_csv))
    monkeypatch.setattr(server, "LOANS_CSV_PATH", str(loans_csv))

    return TestClient(server.app)


def test_listar_libros(client):
    response = client.get("/libros/")

    assert response.status_code == 200

    data = response.json()

    assert "libros" in data
    assert len(data["libros"]) == 2
    assert data["libros"][0]["titulo"] == "The Great Gatsby"


def test_crear_libro_correctamente(client):
    nuevo_libro = {
        "titulo": "1984",
        "autor": "George Orwell",
        "genero": "Distopía",
    }

    response = client.post("/libros/", json=nuevo_libro)

    assert response.status_code == 200

    data = response.json()

    assert data["mensaje"] == "Libro registrado correctamente."
    assert data["libro"]["titulo"] == "1984"
    assert data["libro"]["autor"] == "George Orwell"
    assert data["libro"]["genero"] == "Distopía"
    assert data["libro"]["disponible"] is True


def test_no_crear_libro_sin_titulo(client):
    nuevo_libro = {
        "titulo": "",
        "autor": "Autor de prueba",
        "genero": "Género de prueba",
    }

    response = client.post("/libros/", json=nuevo_libro)

    assert response.status_code == 200

    data = response.json()

    assert "error" in data
    assert data["error"] == "El título no puede estar vacío."


def test_listar_usuarios(client):
    response = client.get("/usuarios/")

    assert response.status_code == 200

    data = response.json()

    assert "usuarios" in data
    assert len(data["usuarios"]) == 1
    assert data["usuarios"][0]["email"] == "jesus@email.com"


def test_crear_usuario_correctamente(client):
    nuevo_usuario = {
        "nombre": "Alex Sainz",
        "email": "alex@email.com",
    }

    response = client.post("/usuarios/", json=nuevo_usuario)

    assert response.status_code == 200

    data = response.json()

    assert data["mensaje"] == "Usuario registrado correctamente."
    assert data["usuario"]["nombre"] == "Alex Sainz"
    assert data["usuario"]["email"] == "alex@email.com"


def test_no_crear_usuario_con_email_repetido(client):
    usuario_repetido = {
        "nombre": "Otro Usuario",
        "email": "jesus@email.com",
    }

    response = client.post("/usuarios/", json=usuario_repetido)

    assert response.status_code == 200

    data = response.json()

    assert "error" in data
    assert data["error"] == "Ya existe un usuario registrado con ese email."


def test_crear_prestamo_correctamente(client):
    nuevo_prestamo = {
        "usuario_id": 1,
        "libro_id": 1,
    }

    response = client.post("/prestamos/", json=nuevo_prestamo)

    assert response.status_code == 200

    data = response.json()

    assert data["mensaje"] == "Préstamo registrado correctamente."
    assert data["prestamo"]["usuario_id"] == 1
    assert data["prestamo"]["libro_id"] == 1
    assert data["prestamo"]["estado"] == "activo"


def test_no_prestar_libro_no_disponible(client):
    prestamo = {
        "usuario_id": 1,
        "libro_id": 1,
    }

    primera_respuesta = client.post("/prestamos/", json=prestamo)
    segunda_respuesta = client.post("/prestamos/", json=prestamo)

    assert primera_respuesta.status_code == 200
    assert segunda_respuesta.status_code == 200

    data = segunda_respuesta.json()

    assert "error" in data
    assert data["error"] == "El libro ya está prestado o no está disponible."


def test_devolver_libro_correctamente(client):
    prestamo = {
        "usuario_id": 1,
        "libro_id": 1,
    }

    crear_response = client.post("/prestamos/", json=prestamo)
    prestamo_id = crear_response.json()["prestamo"]["id"]

    devolver_response = client.post(
        "/devoluciones/",
        params={"prestamo_id": prestamo_id},
    )

    assert devolver_response.status_code == 200

    data = devolver_response.json()

    assert data["mensaje"] == "Devolución registrada correctamente."
    assert data["prestamo"]["estado"] == "cerrado"
    assert data["libro"]["disponible"] is True
    assert data["prestamo"]["fecha_devolucion"] != ""


def test_no_devolver_dos_veces_el_mismo_prestamo(client):
    prestamo = {
        "usuario_id": 1,
        "libro_id": 1,
    }

    crear_response = client.post("/prestamos/", json=prestamo)
    prestamo_id = crear_response.json()["prestamo"]["id"]

    primera_devolucion = client.post(
        "/devoluciones/",
        params={"prestamo_id": prestamo_id},
    )

    segunda_devolucion = client.post(
        "/devoluciones/",
        params={"prestamo_id": prestamo_id},
    )

    assert primera_devolucion.status_code == 200
    assert segunda_devolucion.status_code == 200

    data = segunda_devolucion.json()

    assert "error" in data
    assert data["error"] == "El préstamo ya estaba cerrado. No se puede devolver de nuevo."


def test_historial_prestamos_usuario(client):
    prestamo = {
        "usuario_id": 1,
        "libro_id": 1,
    }

    client.post("/prestamos/", json=prestamo)

    response = client.get("/usuarios/1/historial-prestamos/")

    assert response.status_code == 200

    data = response.json()

    assert "usuario" in data
    assert "historial" in data
    assert data["usuario"]["id"] == 1
    assert len(data["historial"]) == 1
    assert data["historial"][0]["titulo_libro"] == "The Great Gatsby"
    assert data["historial"][0]["estado"] == "activo"


def test_historial_usuario_sin_prestamos(client):
    response = client.get("/usuarios/1/historial-prestamos/")

    assert response.status_code == 200

    data = response.json()

    assert "usuario" in data
    assert "historial" in data
    assert data["historial"] == []
    assert data["mensaje"] == "El usuario no tiene historial de préstamos."