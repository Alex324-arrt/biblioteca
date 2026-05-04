from fastapi import FastAPI
import pandas as pd
import os
from typing import List
from datetime import datetime
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
# MODELOS DE PRÉSTAMOS
# -------------------------

class Prestamo(BaseModel):
    id: int
    usuario_id: int
    libro_id: int
    fecha_prestamo: str
    estado: str


class NuevoPrestamo(BaseModel):
    usuario_id: int
    libro_id: int


class ListadoPrestamos(BaseModel):
    prestamos: List[Prestamo] = []


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
LOANS_CSV_PATH = "./loans.csv"


# -------------------------
# FUNCIONES AUXILIARES
# -------------------------

def inicializar_csv(path: str, columnas: List[str]):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        df = pd.DataFrame(columns=columnas)
        df.to_csv(path, sep=";", index=False)


def normalizar_disponible(valor):
    if isinstance(valor, bool):
        return valor

    valor_texto = str(valor).strip().lower()

    return valor_texto in ["true", "1", "sí", "si", "yes"]


def leer_usuarios():
    inicializar_csv(USERS_CSV_PATH, ["id", "nombre", "email"])
    df = pd.read_csv(USERS_CSV_PATH, sep=";")
    return df.fillna("")


def guardar_usuarios(df):
    df.to_csv(USERS_CSV_PATH, sep=";", index=False)


def leer_prestamos():
    inicializar_csv(
        LOANS_CSV_PATH,
        ["id", "usuario_id", "libro_id", "fecha_prestamo", "estado"]
    )
    df = pd.read_csv(LOANS_CSV_PATH, sep=";")
    return df.fillna("")


def guardar_prestamos(df):
    df.to_csv(LOANS_CSV_PATH, sep=";", index=False)


# -------------------------
# ENDPOINTS DE LIBROS
# -------------------------

@app.get("/libros/")
def retrieve_data():
    try:
        df = pd.read_csv(BOOKS_CSV_PATH, sep=";")
        df = df.fillna(0)

        if "disponible" in df.columns:
            df["disponible"] = df["disponible"].apply(normalizar_disponible)

        libros = df.to_dict(orient="records")

        listado = ListadoLibros()
        listado.libros = libros

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
            ids = pd.to_numeric(df["id"], errors="coerce").fillna(0)
            nuevo_id = int(ids.max()) + 1

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

        if not df.empty:
            emails_existentes = df["email"].astype(str).str.strip().str.lower()

            if emails_existentes.eq(email).any():
                return {"error": "Ya existe un usuario registrado con ese email."}

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
# ENDPOINTS DE PRÉSTAMOS
# -------------------------

@app.get("/prestamos/")
def listar_prestamos():
    try:
        df = leer_prestamos()

        prestamos = df.to_dict(orient="records")

        listado = ListadoPrestamos()
        listado.prestamos = prestamos

        return listado

    except Exception as e:
        return {"error": str(e)}


@app.post("/prestamos/")
def crear_prestamo(prestamo: NuevoPrestamo):
    try:
        usuarios_df = leer_usuarios()
        libros_df = pd.read_csv(BOOKS_CSV_PATH, sep=";")
        libros_df = libros_df.fillna("")
        prestamos_df = leer_prestamos()

        # Validar que existan usuarios registrados
        if usuarios_df.empty:
            return {"error": "No hay usuarios registrados en el sistema."}

        # Validar que exista el usuario
        usuarios_ids = pd.to_numeric(usuarios_df["id"], errors="coerce").fillna(0)

        if not usuarios_ids.eq(prestamo.usuario_id).any():
            return {"error": "El usuario indicado no existe."}

        # Validar que existan libros registrados
        if libros_df.empty:
            return {"error": "No hay libros registrados en el sistema."}

        # Validar que exista el libro
        libros_ids = pd.to_numeric(libros_df["id"], errors="coerce").fillna(0)
        libro_existe = libros_ids.eq(prestamo.libro_id)

        if not libro_existe.any():
            return {"error": "El libro indicado no existe."}

        indice_libro = libros_df[libro_existe].index[0]

        # Validar que el libro esté disponible
        disponible = normalizar_disponible(libros_df.loc[indice_libro, "disponible"])

        if not disponible:
            return {"error": "El libro ya está prestado o no está disponible."}

        # Calcular nuevo ID del préstamo
        if prestamos_df.empty:
            nuevo_id = 1
        else:
            ids_prestamos = pd.to_numeric(prestamos_df["id"], errors="coerce").fillna(0)
            nuevo_id = int(ids_prestamos.max()) + 1

        nuevo_prestamo = {
            "id": nuevo_id,
            "usuario_id": prestamo.usuario_id,
            "libro_id": prestamo.libro_id,
            "fecha_prestamo": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo"
        }

        # Registrar préstamo
        prestamos_df = pd.concat(
            [prestamos_df, pd.DataFrame([nuevo_prestamo])],
            ignore_index=True
        )

        # Cambiar disponibilidad del libro
        libros_df.loc[indice_libro, "disponible"] = False

        # Guardar cambios
        guardar_prestamos(prestamos_df)
        libros_df.to_csv(BOOKS_CSV_PATH, sep=";", index=False)

        return {
            "mensaje": "Préstamo registrado correctamente.",
            "prestamo": nuevo_prestamo
        }

    except Exception as e:
        return {"error": str(e)}