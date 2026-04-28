import streamlit as st
import time

st.set_page_config(page_title='Gestor de Bibliotecas', layout='wide', page_icon="📚")

# Placeholder for logo or header
st.write("# Gestor de Bibliotecas 📚")

st.markdown(
    """
    Bienvenido al sistema de gestión de bibliotecas.
    
    Esta aplicación es un esqueleto que debéis completar y mejorar.
    Actualmente conecta con un backend básico en FastAPI que lee de un CSV.
    
    **Vuestra misión**:
    1. Migrar a Base de Datos (SQLAlchemy).
    2. Implementar buenas prácticas (SOLID, Logs, Excepciones).
    3. Mejorar la interfaz.
    
    ¡Manos a la obra!
    """
)

st.sidebar.success("Selecciona una opción arriba.")
