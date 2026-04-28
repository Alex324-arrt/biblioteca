import streamlit as st
import pandas as pd
import requests

# Configuración general de la página
st.set_page_config(
    page_title="Catálogo de Libros",
    page_icon="📚",
    layout="centered"
)

# Título y descripción de la página
st.title("📚 Catálogo de Libros")

st.write(
    "Consulta el listado completo de libros registrados en la biblioteca, "
    "incluyendo su título, autor, género y estado de disponibilidad."
)

# URL del backend FastAPI dentro de Docker
API_URL = "http://fastapi:8000"


try:
    # Petición al backend para obtener los libros
    response = requests.get(f"{API_URL}/libros/", timeout=5)
    response.raise_for_status()

    # Convertimos la respuesta JSON en un diccionario de Python
    data = response.json()

    # Obtenemos la lista de libros desde la clave "libros"
    libros = data.get("libros", [])

    # Si no hay libros, mostramos un mensaje informativo
    if not libros:
        st.info("No hay libros registrados actualmente en el catálogo.")
    else:
        # Convertimos la lista de libros en un DataFrame para mostrarla como tabla
        df = pd.DataFrame(libros)

        # Convertimos el campo booleano disponible en un texto más claro
        df["estado"] = df["disponible"].apply(
            lambda disponible: "Disponible" if disponible else "Prestado"
        )

        # Seleccionamos solo las columnas necesarias para HU-01
        df_mostrar = df[["titulo", "autor", "genero", "estado"]].rename(
            columns={
                "titulo": "Título",
                "autor": "Autor",
                "genero": "Género",
                "estado": "Estado"
            }
        )

        # Mostramos la tabla final sin índice
        st.dataframe(
            df_mostrar,
            use_container_width=True,
            hide_index=True
        )

except requests.exceptions.ConnectionError:
    st.error("No se ha podido conectar con el servidor de libros.")

except requests.exceptions.Timeout:
    st.error("El servidor ha tardado demasiado en responder.")

except requests.exceptions.RequestException as error:
    st.error(f"Error al obtener el catálogo de libros: {error}")

except Exception as error:
    st.error(f"Ha ocurrido un error inesperado: {error}")