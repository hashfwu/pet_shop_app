import streamlit as st
import components.navbar as navbar
import database.queries as queries
import utils.validators as val
from datetime import date

# 1. Enforce Admin only authentication
user = navbar.render_navbar(required_role="ADMIN")

st.title("✂️ Gestión de Estilistas (Groomers)")
st.markdown("---")

st.subheader("Personal del Spa")

groomers = queries.get_empleados()

if groomers:
    import pandas as pd
    df = pd.DataFrame(groomers)
    # Hide the pivot styling employee (id_empleado = 1) from general display to keep view clean, but show it if needed
    # Filter out id_empleado = 1 (pivote) if we want, or keep it. Let's filter it or show it as a special registry.
    df_visible = df[df["id_empleado"] != 1]
    
    if not df_visible.empty:
        st.dataframe(
            df_visible[["id_empleado", "apellidos", "nombres", "correo", "telefono", "cargo", "especialidad", "fecha_ingreso", "estado"]],
            column_config={
                "id_empleado": "ID Groomer",
                "apellidos": "Apellidos",
                "nombres": "Nombres",
                "correo": "Correo",
                "telefono": "Teléfono",
                "cargo": "Cargo",
                "especialidad": "Especialidad",
                "fecha_ingreso": "Fecha Ingreso",
                "estado": "Estado"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No hay groomers reales registrados aún.")
        
    st.markdown("---")
    st.markdown(
        """
        ℹ️ <b>Nota sobre Groomer Pivote:</b> El sistema tiene configurado el Stylist con <b>ID 1</b> como un marcador de posición (placeholder). 
        Cualquier cita reservada que quede asignada a este ID o que no tenga estilista asignado (NULL), será reasignada automáticamente 
        por el Agente 06 por Round-Robin según su disponibilidad.
        """, 
        unsafe_allow_html=True
    )
else:
    st.info("No hay empleados registrados en el sistema.")

st.markdown("---")
st.subheader("Registrar Nuevo Estilista")

with st.form("new_groomer_form"):
    col1, col2 = st.columns(2)
    with col1:
        nombres = st.text_input("Nombres")
        correo = st.text_input("Correo Electrónico")
        telefono = st.text_input("Teléfono")
        cargo = st.text_input("Cargo", value="Groomer / Estilista")
    with col2:
        apellidos = st.text_input("Apellidos")
        contrasena = st.text_input("Contraseña Temporal", type="password")
        especialidad = st.text_input("Especialidad (ej. Cortes Gatos, Tintura)")
        fecha_ingreso = st.date_input("Fecha de Ingreso", value=date.today())
        
    submitted = st.form_submit_button("Registrar Estilista", type="primary")
    if submitted:
        if not nombres or not apellidos or not correo or not contrasena or not cargo:
            st.error("Nombres, Apellidos, Correo, Contraseña y Cargo son campos obligatorios.")
        elif not val.validate_email(correo):
            st.error("El formato del correo electrónico es inválido.")
        elif telefono and not val.validate_phone(telefono):
            st.error("El formato del teléfono es inválido.")
        else:
            try:
                queries.insert_empleado(nombres, apellidos, correo, contrasena, telefono, cargo, especialidad, str(fecha_ingreso))
                st.success(f"¡Estilista {nombres} {apellidos} registrado exitosamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al registrar estilista: {e}")
