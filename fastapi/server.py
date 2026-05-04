from fastapi import FastAPI
import pandas as pd
import os
from typing import List
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


# -------------------------
# MODELOS DE LIBROS
# -------------------------

class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    genero: str
    disponible: bool


class NuevoLibro(BaseModel):
    titulo: str
    autor: str
    genero: str


class ListadoLibros(BaseModel):
    libros: List[Libro] = []


# -------------------------
# MODELOS DE USUARIOS
# -------------------------

class Usuario(BaseModel):
    id: int
    nombre: str
    email: str


class NuevoUsuario(BaseModel):
    nombre: str
    email: str


class ListadoUsuarios(BaseModel):
    usuarios: List[Usuario] = []


# -------------------------
# CONFIGURACIÓN GENERAL
# -------------------------

app = FastAPI(
    title="Gestor de Bibliotecas API",
    description="Servidor de datos para la gestión de bibliotecas.",
    version="1.0.0",
)

BOOKS_CSV_PATH = "./books.csv"
USERS_CSV_PATH = "./users.csv"


# -------------------------
# FUNCIONES AUXILIARES
# -------------------------

def inicializar_archivo_usuarios():
    """
    Crea el archivo users.csv si no existe o si está vacío.
    """
    if not os.path.exists(USERS_CSV_PATH) or os.path.getsize(USERS_CSV_PATH) == 0:
        df = pd.DataFrame(columns=["id", "nombre", "email"])
        df.to_csv(USERS_CSV_PATH, sep=";", index=False)


def leer_usuarios():
    """
    Lee el archivo users.csv de forma segura.
    """
    inicializar_archivo_usuarios()

    df = pd.read_csv(USERS_CSV_PATH, sep=";")
    df = df.fillna("")

    return df


def guardar_usuarios(df):
    """
    Guarda el DataFrame de usuarios en users.csv.
    """
    df.to_csv(USERS_CSV_PATH, sep=";", index=False)


# -------------------------
# ENDPOINTS DE LIBROS
# -------------------------

@app.get("/libros/")
def retrieve_data():
    try:
        todosmisdatos = pd.read_csv(BOOKS_CSV_PATH, sep=";")
        todosmisdatos = todosmisdatos.fillna(0)
        todosmisdatosdict = todosmisdatos.to_dict(orient="records")

        listado = ListadoLibros()
        listado.libros = todosmisdatosdict

        return listado

    except Exception as e:
        return {"error": str(e)}


@app.post("/libros/")
def crear_libro(libro: NuevoLibro):
    try:
        df = pd.read_csv(BOOKS_CSV_PATH, sep=";")

        if not libro.titulo.strip():
            return {"error": "El título no puede estar vacío."}

        if not libro.autor.strip():
            return {"error": "El autor no puede estar vacío."}

        if not libro.genero.strip():
            return {"error": "El género no puede estar vacío."}

        if df.empty:
            nuevo_id = 1
        else:
            nuevo_id = int(df["id"].max()) + 1

        nuevo_libro = {
            "id": nuevo_id,
            "titulo": libro.titulo.strip(),
            "autor": libro.autor.strip(),
            "genero": libro.genero.strip(),
            "disponible": True
        }

        df = pd.concat([df, pd.DataFrame([nuevo_libro])], ignore_index=True)
        df.to_csv(BOOKS_CSV_PATH, sep=";", index=False)

        return {
            "mensaje": "Libro registrado correctamente.",
            "libro": nuevo_libro
        }

    except Exception as e:
        return {"error": str(e)}


# -------------------------
# ENDPOINTS DE USUARIOS
# -------------------------

@app.get("/usuarios/")
def listar_usuarios():
    try:
        df = leer_usuarios()

        usuarios = df.to_dict(orient="records")

        listado = ListadoUsuarios()
        listado.usuarios = usuarios

        return listado

    except Exception as e:
        return {"error": str(e)}


@app.post("/usuarios/")
def crear_usuario(usuario: NuevoUsuario):
    try:
        df = leer_usuarios()

        nombre = usuario.nombre.strip()
        email = usuario.email.strip().lower()

        if not nombre:
            return {"error": "El nombre no puede estar vacío."}

        if not email:
            return {"error": "El email no puede estar vacío."}

        if "@" not in email or "." not in email:
            return {"error": "El email no tiene un formato válido."}

        # Validación correcta de email duplicado
        if not df.empty and "email" in df.columns:
            emails_existentes = (
                df["email"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            if emails_existentes.eq(email).any():
                return {"error": "Ya existe un usuario registrado con ese email."}

        # Calculamos el nuevo ID
        if df.empty:
            nuevo_id = 1
        else:
            ids = pd.to_numeric(df["id"], errors="coerce").fillna(0)
            nuevo_id = int(ids.max()) + 1

        nuevo_usuario = {
            "id": nuevo_id,
            "nombre": nombre,
            "email": email
        }

        df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
        guardar_usuarios(df)

        return {
            "mensaje": "Usuario registrado correctamente.",
            "usuario": nuevo_usuario
        }

    except Exception as e:
        return {"error": str(e)}


# -------------------------
# ENDPOINT DE PRÉSTAMOS
# -------------------------

@app.post("/prestamos/")
async def create_loan(libro_id: int):
    # This is a stub for students to implement
    return {"message": "Préstamo creado (no realmente)", "libro_id": libro_id}