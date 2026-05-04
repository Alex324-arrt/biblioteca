import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Historial de Préstamos",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Historial de préstamos por usuario")

st.write(
    "Selecciona un usuario para consultar todos sus préstamos activos y cerrados."
)

API_URL = "http://fastapi:8000"

try:
    response_usuarios = requests.get(f"{API_URL}/usuarios/", timeout=5)

    if response_usuarios.status_code == 200:
        data_usuarios = response_usuarios.json()
        usuarios = data_usuarios.get("usuarios", [])

        if usuarios:
            opciones_usuarios = {
                f'{usuario["id"]} - {usuario["nombre"]} ({usuario["email"]})': usuario["id"]
                for usuario in usuarios
            }

            seleccion_usuario = st.selectbox(
                "Selecciona un usuario",
                list(opciones_usuarios.keys())
            )

            usuario_id = opciones_usuarios[seleccion_usuario]

            if st.button("Consultar historial"):
                response_historial = requests.get(
                    f"{API_URL}/usuarios/{usuario_id}/historial-prestamos/",
                    timeout=5
                )

                if response_historial.status_code == 200:
                    data_historial = response_historial.json()

                    if "error" in data_historial:
                        st.error(data_historial["error"])
                    else:
                        usuario = data_historial.get("usuario", {})
                        historial = data_historial.get("historial", [])

                        st.subheader("Usuario seleccionado")
                        st.write(f'**Nombre:** {usuario.get("nombre", "")}')
                        st.write(f'**Email:** {usuario.get("email", "")}')

                        if historial:
                            df = pd.DataFrame(historial)

                            df_mostrar = df[
                                [
                                    "prestamo_id",
                                    "titulo_libro",
                                    "fecha_prestamo",
                                    "fecha_devolucion",
                                    "estado"
                                ]
                            ].copy()

                            df_mostrar.columns = [
                                "ID préstamo",
                                "Libro",
                                "Fecha préstamo",
                                "Fecha devolución",
                                "Estado"
                            ]

                            st.subheader("Historial de préstamos")

                            st.dataframe(
                                df_mostrar,
                                use_container_width=True,
                                hide_index=True
                            )

                            activos = df_mostrar[
                                df_mostrar["Estado"].astype(str).str.lower() == "activo"
                            ]

                            cerrados = df_mostrar[
                                df_mostrar["Estado"].astype(str).str.lower() == "cerrado"
                            ]

                            col1, col2 = st.columns(2)

                            with col1:
                                st.metric("Préstamos activos", len(activos))

                            with col2:
                                st.metric("Préstamos cerrados", len(cerrados))

                        else:
                            mensaje = data_historial.get(
                                "mensaje",
                                "El usuario no tiene historial de préstamos."
                            )
                            st.info(mensaje)

                else:
                    st.error(
                        f"Error al consultar el historial: {response_historial.status_code}"
                    )

        else:
            st.info("No hay usuarios registrados actualmente.")

    else:
        st.error(f"Error al obtener usuarios: {response_usuarios.status_code}")

except requests.exceptions.ConnectionError:
    st.error("No se ha podido conectar con el servidor de libros.")

except requests.exceptions.Timeout:
    st.error("El servidor ha tardado demasiado en responder.")

except Exception as error:
    st.error(f"Ha ocurrido un error inesperado: {error}")