import streamlit as st
import components.navbar as navbar
import database.queries as queries
import utils.formatters as fmt
from datetime import date

# 1. Auth check
user = navbar.render_navbar()

st.title("🐾 Gestión de Mascotas")
st.markdown("---")

is_admin = user["rol_nombre"] == "ADMIN"

# Fetch list of pets
try:
    if is_admin:
        pets_list = queries.get_mascotas()
    else:
        pets_list = queries.get_mascotas(user["id_cliente"])
except Exception as e:
    st.error(f"Error cargando lista de mascotas: {e}")
    pets_list = []

# List pets in standard styled layout
if pets_list:
    for m in pets_list:
        with st.container():
            st.markdown(
                f"""
                <div style="background: rgba(255,255,255,0.03); padding:16px; border-radius:12px; border:1px solid rgba(255,255,255,0.05); margin-bottom:12px;">
                    <div style="font-size:18px; font-weight:bold; margin-bottom:4px; color:#4299e1;">🐕 {m['nombre']}</div>
                    <div style="font-size:13px; color:#a0aec0; margin-bottom:6px;">
                        Especie: <b>{m['especie']}</b> | Raza: <b>{m['raza'] or 'N/A'}</b> | Sexo: <b>{m['sexo'] or 'N/A'}</b>
                    </div>
                    <div style="font-size:13px; color:#a0aec0; margin-bottom:6px;">
                        Peso: <b>{m['peso']} kg</b> | Color: <b>{m['color'] or 'N/A'}</b> | Temperamento: <b>{m['temperamento_general'] or 'N/A'}</b>
                    </div>
                    {"<div style='font-size:13px; color:#e2e8f0;'>👤 Dueño: <b>" + m['dueno_nombre'] + "</b></div>" if is_admin else ""}
                    <div style="font-size:12px; color:#cbd5e0; margin-top:8px;">
                        ⚠️ Alergias: {m['alergias'] or 'Ninguna'}<br/>
                        📋 Cuidados: {m['cuidados_especiales'] or 'Ninguno'}<br/>
                        📝 Notas: {m['observaciones'] or 'Ninguna'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Edit / Delete buttons for Admin only
            if is_admin:
                col_b1, col_b2, _ = st.columns([1.5, 1.5, 7])
                with col_b1:
                    with st.popover("✏️ Editar"):
                        with st.form(f"edit_pet_{m['id_mascota']}"):
                            nombre = st.text_input("Nombre", value=m["nombre"])
                            especie = st.text_input("Especie", value=m["especie"])
                            raza = st.text_input("Raza", value=m["raza"] or "")
                            sexo = st.selectbox("Sexo", ["Macho", "Hembra"], index=0 if m["sexo"] == "Macho" else 1)
                            nacimiento = st.date_input("Fecha Nacimiento", value=m["fecha_nacimiento"])
                            peso = st.number_input("Peso (kg)", value=float(m["peso"]) if m["peso"] else 0.0)
                            color = st.text_input("Color", value=m["color"] or "")
                            temperamento = st.selectbox("Temperamento", ["tranquilo", "nervioso", "agresivo", "miedoso", "jugueton", "otro"], index=["tranquilo", "nervioso", "agresivo", "miedoso", "jugueton", "otro"].index(m["temperamento_general"]) if m["temperamento_general"] in ["tranquilo", "nervioso", "agresivo", "miedoso", "jugueton", "otro"] else 0)
                            alergias = st.text_area("Alergias", value=m["alergias"] or "")
                            cuidados = st.text_area("Cuidados especiales", value=m["cuidados_especiales"] or "")
                            obs = st.text_area("Observaciones", value=m["observaciones"] or "")
                            
                            saved = st.form_submit_button("Guardar Cambios")
                            if saved:
                                queries.update_mascota(m["id_mascota"], nombre, especie, raza, sexo, nacimiento, peso, color, temperamento, alergias, cuidados, obs)
                                st.success("Mascota actualizada.")
                                st.rerun()
                with col_b2:
                    if st.button("🗑️ Eliminar", key=f"delete_pet_{m['id_mascota']}", use_container_width=True):
                        queries.delete_mascota(m["id_mascota"])
                        st.success("Mascota eliminada (inactiva).")
                        st.rerun()
else:
    st.info("No tienes mascotas registradas.")

# Register form display based on roles
st.markdown("---")
if is_admin:
    st.subheader("Registrar Nueva Mascota")
    clients = queries.get_clientes()
    
    if not clients:
        st.error("No hay clientes registrados en el sistema.")
    else:
        with st.form("register_pet_form"):
            selected_client = st.selectbox(
                "Cliente Dueño",
                options=clients,
                format_func=lambda x: f"{x['apellidos']}, {x['nombres']} ({x['correo']})"
            )
            nombre = st.text_input("Nombre de la Mascota")
            especie = st.selectbox("Especie", ["Perro", "Gato", "Conejo", "Ave", "Otro"])
            raza = st.text_input("Raza (ej. Poodle, Siamés)")
            sexo = st.selectbox("Sexo", ["Macho", "Hembra"])
            nacimiento = st.date_input("Fecha de Nacimiento", value=date.today())
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
            color = st.text_input("Color")
            temperamento = st.selectbox("Temperamento General", ["tranquilo", "nervioso", "agresivo", "miedoso", "jugueton", "otro"])
            alergias = st.text_area("Alergias")
            cuidados = st.text_area("Cuidados Especiales")
            obs = st.text_area("Observaciones generales")
            
            submitted = st.form_submit_button("Registrar Mascota", type="primary")
            if submitted:
                if not nombre:
                    st.error("El nombre de la mascota es obligatorio.")
                else:
                    queries.insert_mascota(
                        selected_client["id_cliente"], nombre, especie, raza, sexo, 
                        nacimiento, peso, color, temperamento, alergias, cuidados, obs
                    )
                    st.success(f"¡Mascota '{nombre}' registrada exitosamente!")
                    st.rerun()
else:
    st.markdown(
        """
        <div style="background: rgba(221,107,32,0.1); padding: 16px; border-radius: 12px; border-left: 4px solid #dd6b20;">
            💡 <b>Nota:</b> Para registrar una nueva mascota en el sistema, por favor ponte en contacto con nuestro 
            chatbot en Telegram <b>SpaBot</b> o solicítalo directamente al personal en la sucursal.
        </div>
        """,
        unsafe_allow_html=True
    )
