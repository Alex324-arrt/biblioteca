import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Registrar Préstamo",
    page_icon="📖",
    layout="centered"
)

st.title("📖 Registrar Préstamo")

st.write(
    "Desde esta pantalla puedes registrar el préstamo de un libro disponible "
    "a un usuario registrado en la biblioteca."
)

API_URL = "http://fastapi:8000"


def obtener_usuarios():
    response = requests.get(f"{API_URL}/usuarios/", timeout=5)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        st.error(data["error"])
        return []

    return data.get("usuarios", [])


def obtener_libros():
    response = requests.get(f"{API_URL}/libros/", timeout=5)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        st.error(data["error"])
        return []

    return data.get("libros", [])


st.subheader("Datos del préstamo")

try:
    usuarios = obtener_usuarios()
    libros = obtener_libros()

    libros_disponibles = [
        libro for libro in libros
        if str(libro.get("disponible")).strip().lower() in ["true", "1", "sí", "si", "yes"]
    ]

    if not usuarios:
        st.warning("No hay usuarios registrados. Primero debe existir al menos un usuario.")

    elif not libros_disponibles:
        st.warning("No hay libros disponibles para prestar.")

    else:
        opciones_usuarios = {
            f'{usuario["id"]} - {usuario["nombre"]} ({usuario["email"]})': usuario["id"]
            for usuario in usuarios
        }

        opciones_libros = {
            f'{libro["id"]} - {libro["titulo"]} | {libro["autor"]}': libro["id"]
            for libro in libros_disponibles
        }

        usuario_seleccionado = st.selectbox(
            "Selecciona un usuario",
            list(opciones_usuarios.keys())
        )

        libro_seleccionado = st.selectbox(
            "Selecciona un libro disponible",
            list(opciones_libros.keys())
        )

        if st.button("Registrar préstamo"):
            nuevo_prestamo = {
                "usuario_id": opciones_usuarios[usuario_seleccionado],
                "libro_id": opciones_libros[libro_seleccionado]
            }

            response = requests.post(
                f"{API_URL}/prestamos/",
                json=nuevo_prestamo,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if "error" in data:
                    st.error(data["error"])
                else:
                    st.success("Préstamo registrado correctamente.")
                    st.write("Préstamo añadido:")
                    st.json(data["prestamo"])
            else:
                st.error(f"Error al registrar préstamo: {response.status_code}")

    st.divider()

    st.subheader("Libros disponibles actualmente")

    if libros_disponibles:
        df_libros = pd.DataFrame(libros_disponibles)

        df_libros = df_libros.rename(columns={
            "id": "ID",
            "titulo": "Título",
            "autor": "Autor",
            "genero": "Género",
            "disponible": "Disponible"
        })

        st.dataframe(
            df_libros,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay libros disponibles actualmente.")

except requests.exceptions.ConnectionError:
    st.error("No se ha podido conectar con el servidor FastAPI.")

except requests.exceptions.Timeout:
    st.error("El servidor ha tardado demasiado en responder.")

except requests.exceptions.RequestException as error:
    st.error(f"Error al comunicarse con el servidor: {error}")

except Exception as error:
    st.error(f"Ha ocurrido un error inesperado: {error}")