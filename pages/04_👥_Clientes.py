import streamlit as st
import components.navbar as navbar
import database.queries as queries
import utils.validators as val

# 1. Enforce Admin only authentication
user = navbar.render_navbar(required_role="ADMIN")

st.title("👥 Gestión de Clientes")
st.markdown("---")

# List existing clients
st.subheader("Clientes Registrados")

clients = queries.get_clientes()

if clients:
    import pandas as pd
    df = pd.DataFrame(clients)
    
    # Render table nicely
    st.dataframe(
        df[["id_cliente", "apellidos", "nombres", "correo", "telefono", "direccion", "estado"]],
        column_config={
            "id_cliente": "ID Cliente",
            "apellidos": "Apellidos",
            "nombres": "Nombres",
            "correo": "Correo Electrónico",
            "telefono": "Teléfono",
            "direccion": "Dirección",
            "estado": "Estado de Cuenta"
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No hay clientes registrados en el sistema.")

st.markdown("---")
st.subheader("Registrar Nuevo Cliente")

with st.form("new_client_form"):
    col1, col2 = st.columns(2)
    with col1:
        nombres = st.text_input("Nombres")
        correo = st.text_input("Correo Electrónico")
        telefono = st.text_input("Teléfono (Opcional)")
    with col2:
        apellidos = st.text_input("Apellidos")
        contrasena = st.text_input("Contraseña Temporal", type="password")
        direccion = st.text_input("Dirección (Opcional)")
        
    submitted = st.form_submit_button("Crear Cliente", type="primary")
    if submitted:
        if not nombres or not apellidos or not correo or not contrasena:
            st.error("Nombres, Apellidos, Correo y Contraseña son campos obligatorios.")
        elif not val.validate_email(correo):
            st.error("El formato del correo electrónico es inválido.")
        elif telefono and not val.validate_phone(telefono):
            st.error("El formato del teléfono es inválido.")
        else:
            try:
                queries.insert_cliente(nombres, apellidos, correo, contrasena, telefono, direccion)
                st.success(f"¡Cliente {nombres} {apellidos} creado correctamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al registrar cliente: {e}")
