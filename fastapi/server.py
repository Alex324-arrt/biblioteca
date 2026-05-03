from fastapi import FastAPI
import pandas as pd
from typing import List
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


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


app = FastAPI(
    title="Gestor de Bibliotecas API",
    description="Servidor de datos para la gestión de bibliotecas.",
    version="1.0.0",
)


@app.get("/libros/")
def retrieve_data():
    # EDUCATIONAL INEFFICIENCY: Reading CSV on every request
    # Students should optimize this by using a database or caching
    try:
        todosmisdatos = pd.read_csv("./books.csv", sep=";")
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
        # Leemos el archivo CSV donde se guardan los libros
        df = pd.read_csv("./books.csv", sep=";")

        # Validamos que ningún campo venga vacío
        if not libro.titulo.strip():
            return {"error": "El título no puede estar vacío."}

        if not libro.autor.strip():
            return {"error": "El autor no puede estar vacío."}

        if not libro.genero.strip():
            return {"error": "El género no puede estar vacío."}

        # Calculamos el nuevo ID del libro
        if df.empty:
            nuevo_id = 1
        else:
            nuevo_id = int(df["id"].max()) + 1

        # Creamos el nuevo libro
        nuevo_libro = {
            "id": nuevo_id,
            "titulo": libro.titulo.strip(),
            "autor": libro.autor.strip(),
            "genero": libro.genero.strip(),
            "disponible": True
        }

        # Añadimos el libro al DataFrame
        df = pd.concat([df, pd.DataFrame([nuevo_libro])], ignore_index=True)

        # Guardamos el CSV actualizado
        df.to_csv("./books.csv", sep=";", index=False)

        return {
            "mensaje": "Libro registrado correctamente.",
            "libro": nuevo_libro
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/prestamos/")
async def create_loan(libro_id: int):
    # This is a stub for students to implement
    return {"message": "Préstamo creado (no realmente)", "libro_id": libro_id}