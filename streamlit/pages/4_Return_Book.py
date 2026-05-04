import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Devolver Libro",
    page_icon="↩️",
    layout="centered"
)

st.title("↩️ Devolver libro prestado")

st.write(
    "Selecciona un préstamo activo para registrar la devolución del libro."
)

API_URL = "http://fastapi:8000"

try:
    response_prestamos = requests.get(f"{API_URL}/prestamos/", timeout=5)
    response_libros = requests.get(f"{API_URL}/libros/", timeout=5)

    if response_prestamos.status_code == 200 and response_libros.status_code == 200:
        data_prestamos = response_prestamos.json()
        data_libros = response_libros.json()

        prestamos = data_prestamos.get("prestamos", [])
        libros = data_libros.get("libros", [])

        prestamos_activos = [
            prestamo for prestamo in prestamos
            if str(prestamo.get("estado", "")).strip().lower() == "activo"
        ]

        if prestamos_activos:
            libros_por_id = {
                int(libro["id"]): libro
                for libro in libros
            }

            filas = []

            for prestamo in prestamos_activos:
                libro_id = int(prestamo["libro_id"])
                libro = libros_por_id.get(libro_id, {})

                filas.append({
                    "ID préstamo": prestamo["id"],
                    "Libro": libro.get("titulo", "Libro no encontrado"),
                    "Autor": libro.get("autor", "Autor no encontrado"),
                    "Fecha préstamo": prestamo.get("fecha_prestamo", ""),
                    "Estado": prestamo.get("estado", "")
                })

            df_mostrar = pd.DataFrame(filas)

            st.subheader("Préstamos activos")

            st.dataframe(
                df_mostrar,
                use_container_width=True,
                hide_index=True
            )

            opciones = {
                f'{fila["ID préstamo"]} - {fila["Libro"]} ({fila["Autor"]})': fila["ID préstamo"]
                for fila in filas
            }

            seleccion = st.selectbox(
                "Selecciona el préstamo que quieres devolver",
                list(opciones.keys())
            )

            if st.button("Registrar devolución"):
                prestamo_id = opciones[seleccion]

                respuesta_devolucion = requests.post(
                    f"{API_URL}/devoluciones/",
                    params={"prestamo_id": prestamo_id},
                    timeout=5
                )

                if respuesta_devolucion.status_code == 200:
                    resultado = respuesta_devolucion.json()

                    if "error" in resultado:
                        st.error(resultado["error"])
                    else:
                        st.success("Devolución registrada correctamente.")
                        st.write("Préstamo actualizado:")
                        st.json(resultado["prestamo"])

                        st.write("Libro actualizado:")
                        st.json(resultado["libro"])

                        st.info("Recarga la página para actualizar el listado.")
                else:
                    st.error(
                        f"Error al registrar la devolución: {respuesta_devolucion.status_code}"
                    )

        else:
            st.info("No hay préstamos activos actualmente.")

    else:
        st.error("Error al obtener los datos de préstamos o libros.")

except requests.exceptions.ConnectionError:
    st.error("No se ha podido conectar con el servidor de libros.")

except requests.exceptions.Timeout:
    st.error("El servidor ha tardado demasiado en responder.")

except Exception as error:
    st.error(f"Ha ocurrido un error inesperado: {error}")