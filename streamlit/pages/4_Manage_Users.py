import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Gestión de Usuarios",
    page_icon="👤",
    layout="centered"
)

st.title("👤 Gestión de Usuarios")

st.write(
    "Desde esta pantalla puedes registrar nuevos usuarios de la biblioteca "
    "y consultar el listado completo de usuarios registrados."
)

API_URL = "http://fastapi:8000"

st.subheader("Registrar nuevo usuario")

with st.form("form_registro_usuario"):
    nombre = st.text_input("Nombre")
    email = st.text_input("Email")

    boton_registrar = st.form_submit_button("Registrar usuario")

    if boton_registrar:
        if not nombre.strip():
            st.error("El nombre no puede estar vacío.")
        elif not email.strip():
            st.error("El email no puede estar vacío.")
        elif "@" not in email or "." not in email:
            st.error("El email no tiene un formato válido.")
        else:
            try:
                nuevo_usuario = {
                    "nombre": nombre.strip(),
                    "email": email.strip().lower()
                }

                response = requests.post(
                    f"{API_URL}/usuarios/",
                    json=nuevo_usuario,
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()

                    if "error" in data:
                        st.error(data["error"])
                    else:
                        st.success("Usuario registrado correctamente.")
                        st.write("Usuario añadido:")
                        st.json(data["usuario"])
                else:
                    st.error(f"Error al registrar usuario: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("No se ha podido conectar con el servidor FastAPI.")

            except requests.exceptions.Timeout:
                st.error("El servidor ha tardado demasiado en responder.")

            except Exception as error:
                st.error(f"Ha ocurrido un error inesperado: {error}")

st.divider()

st.subheader("Usuarios registrados")

try:
    response = requests.get(f"{API_URL}/usuarios/", timeout=5)

    if response.status_code == 200:
        data = response.json()

        if "error" in data:
            st.error(data["error"])
        else:
            usuarios = data.get("usuarios", [])

            if usuarios:
                df = pd.DataFrame(usuarios)

                df = df.rename(columns={
                    "id": "ID",
                    "nombre": "Nombre",
                    "email": "Email"
                })

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Todavía no hay usuarios registrados.")
    else:
        st.error(f"Error al obtener usuarios: {response.status_code}")

except requests.exceptions.ConnectionError:
    st.error("No se ha podido conectar con el servidor de usuarios.")

except requests.exceptions.Timeout:
    st.error("El servidor ha tardado demasiado en responder.")

except Exception as error:
    st.error(f"Ha ocurrido un error inesperado: {error}")