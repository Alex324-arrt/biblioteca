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
        # Convertimos la lista de libros en un DataFrame
        df = pd.DataFrame(libros)

        # Convertimos el campo booleano disponible en un texto más claro
        df["estado"] = df["disponible"].apply(
            lambda disponible: "Disponible" if disponible else "Prestado"
        )

        # -------------------------
        # BUSCADOR HU-07
        # -------------------------

        st.subheader("🔎 Buscar libros")

        texto_busqueda = st.text_input(
            "Busca por título o autor",
            placeholder="Ejemplo: Gatsby, Orwell, Martin..."
        )

        criterio_busqueda = st.radio(
            "Filtrar por",
            ["Título o autor", "Solo título", "Solo autor"],
            horizontal=True
        )

        df_filtrado = df.copy()

        if texto_busqueda.strip():
            busqueda = texto_busqueda.strip().lower()

            titulos = df_filtrado["titulo"].astype(str).str.lower()
            autores = df_filtrado["autor"].astype(str).str.lower()

            if criterio_busqueda == "Solo título":
                df_filtrado = df_filtrado[titulos.str.contains(busqueda, na=False)]

            elif criterio_busqueda == "Solo autor":
                df_filtrado = df_filtrado[autores.str.contains(busqueda, na=False)]

            else:
                df_filtrado = df_filtrado[
                    titulos.str.contains(busqueda, na=False)
                    | autores.str.contains(busqueda, na=False)
                ]

        # -------------------------
        # TABLA FINAL
        # -------------------------

        if df_filtrado.empty:
            st.warning("No se han encontrado libros que coincidan con la búsqueda.")
        else:
            st.write(f"Resultados encontrados: **{len(df_filtrado)}**")

            df_mostrar = df_filtrado[["titulo", "autor", "genero", "estado"]].rename(
                columns={
                    "titulo": "Título",
                    "autor": "Autor",
                    "genero": "Género",
                    "estado": "Estado"
                }
            )

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