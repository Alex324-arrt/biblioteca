import streamlit as st
import pandas as pd
import requests
import calendar
from datetime import datetime

st.set_page_config(
    page_title="Calendario de Préstamos",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Calendario de préstamos")

st.write(
    "Consulta los préstamos de un usuario en formato calendario, "
    "diferenciando préstamos activos y cerrados."
)

API_URL = "http://fastapi:8000"

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}


def convertir_fecha(fecha_texto):
    try:
        if not fecha_texto or str(fecha_texto).strip().lower() == "pendiente":
            return None

        return datetime.strptime(str(fecha_texto), "%Y-%m-%d %H:%M:%S")

    except Exception:
        return None


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

            col_mes, col_anio = st.columns(2)

            fecha_actual = datetime.now()

            with col_mes:
                mes_seleccionado = st.selectbox(
                    "Mes",
                    list(MESES.keys()),
                    index=fecha_actual.month - 1,
                    format_func=lambda mes: MESES[mes]
                )

            with col_anio:
                anio_seleccionado = st.number_input(
                    "Año",
                    min_value=2020,
                    max_value=2035,
                    value=fecha_actual.year,
                    step=1
                )

            if st.button("Ver calendario"):
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

                        st.subheader(
                            f"Calendario de {MESES[mes_seleccionado]} de {anio_seleccionado}"
                        )

                        if not historial:
                            st.info("El usuario no tiene historial de préstamos.")
                        else:
                            eventos_por_dia = {}

                            for prestamo in historial:
                                fecha_prestamo = convertir_fecha(
                                    prestamo.get("fecha_prestamo", "")
                                )

                                if fecha_prestamo is None:
                                    continue

                                if (
                                    fecha_prestamo.month == mes_seleccionado
                                    and fecha_prestamo.year == anio_seleccionado
                                ):
                                    dia = fecha_prestamo.day

                                    estado = str(prestamo.get("estado", "")).lower()
                                    titulo = prestamo.get("titulo_libro", "Libro no encontrado")

                                    if estado == "activo":
                                        etiqueta_estado = "🟡 Activo"
                                    elif estado == "cerrado":
                                        etiqueta_estado = "🟢 Cerrado"
                                    else:
                                        etiqueta_estado = "⚪ Sin estado"

                                    fecha_devolucion = prestamo.get("fecha_devolucion", "Pendiente")

                                    evento = (
                                        f"📘 {titulo}<br>"
                                        f"{etiqueta_estado}<br>"
                                        f"Préstamo: {prestamo.get('fecha_prestamo', '')}<br>"
                                        f"Devolución: {fecha_devolucion}"
                                    )

                                    if dia not in eventos_por_dia:
                                        eventos_por_dia[dia] = []

                                    eventos_por_dia[dia].append(evento)

                            calendario = calendar.monthcalendar(
                                int(anio_seleccionado),
                                int(mes_seleccionado)
                            )

                            dias_semana = [
                                "Lunes",
                                "Martes",
                                "Miércoles",
                                "Jueves",
                                "Viernes",
                                "Sábado",
                                "Domingo"
                            ]

                            columnas = st.columns(7)

                            for i, dia_semana in enumerate(dias_semana):
                                columnas[i].markdown(f"**{dia_semana}**")

                            for semana in calendario:
                                columnas = st.columns(7)

                                for i, dia in enumerate(semana):
                                    with columnas[i]:
                                        if dia == 0:
                                            st.markdown("&nbsp;", unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"### {dia}")

                                            if dia in eventos_por_dia:
                                                for evento in eventos_por_dia[dia]:
                                                    st.markdown(
                                                        f"""
                                                        <div style="
                                                            border: 1px solid #d0d7de;
                                                            border-radius: 8px;
                                                            padding: 8px;
                                                            margin-bottom: 8px;
                                                            background-color: #f6f8fa;
                                                            font-size: 14px;
                                                        ">
                                                            {evento}
                                                        </div>
                                                        """,
                                                        unsafe_allow_html=True
                                                    )

                            if not eventos_por_dia:
                                st.info(
                                    "No hay préstamos registrados para este usuario en el mes seleccionado."
                                )

                            st.markdown("---")
                            st.markdown("**Leyenda:** 🟡 Activo | 🟢 Cerrado")

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