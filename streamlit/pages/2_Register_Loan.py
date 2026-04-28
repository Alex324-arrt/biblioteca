import streamlit as st
import requests

st.set_page_config(page_title="Préstamo de Libros", page_icon="✍️")

st.markdown("# Gestionar Préstamo")
st.write("Formulario para realizar un préstamo.")

API_URL = "http://fastapi:8000"

with st.form("loan_form"):
    libro_id = st.number_input("ID del Libro", min_value=1, step=1)
    usuario_id = st.text_input("ID de Usuario")
    submitted = st.form_submit_button("Realizar Préstamo")

    if submitted:
        # STUDENT TASK: Implement the actual POST request logic properly
        st.info(f"Intentando prestar libro {libro_id} al usuario {usuario_id}...")
        
        try:
            # INEFFICIENCY: Not checking if payload structure matches what server expects
            response = requests.post(f"{API_URL}/prestamos/?libro_id={libro_id}")
            
            if response.status_code == 200:
                st.success("Préstamo registrado (simulado).")
                st.json(response.json())
            else:
                st.error("Error al registrar préstamo.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

st.markdown("---")
st.warning("⚠️ Este formulario es un esqueleto. Falta validación y gestión de errores real.")
