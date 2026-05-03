import streamlit as st
import requests

st.set_page_config(
    page_title="Registrar Libro",
    page_icon="➕",
    layout="centered"
)

st.title("➕ Registrar nuevo libro")

st.write(
    "Completa el formulario para añadir un nuevo libro al catálogo de la biblioteca."
)

API_URL = "http://localhost:8000"

with st.form("form_registrar_libro"):
    titulo = st.text_input("Título del libro")
    autor = st.text_input("Autor")
    genero = st.text_input("Género")

    boton_guardar = st.form_submit_button("Guardar libro")

    if boton_guardar:
        if not titulo.strip() or not autor.strip() or not genero.strip():
            st.warning("Todos los campos son obligatorios.")
        else:
            nuevo_libro = {
                "titulo": titulo.strip(),
                "autor": autor.strip(),
                "genero": genero.strip()
            }

            try:
                response = requests.post(
                    f"{API_URL}/libros/",
                    json=nuevo_libro,
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()

                    if "error" in data:
                        st.error(data["error"])
                    else:
                        st.success("Libro registrado correctamente.")
                        st.write("Libro añadido:")
                        st.json(data["libro"])
                else:
                    st.error(f"Error al registrar el libro: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("No se ha podido conectar con el servidor FastAPI.")

            except requests.exceptions.Timeout:
                st.error("El servidor ha tardado demasiado en responder.")

            except Exception as error:
                st.error(f"Ha ocurrido un error inesperado: {error}")