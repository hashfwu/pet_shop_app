import streamlit as st
import config
import components.navbar as navbar
import database.queries as queries
import agents.client as client
import utils.formatters as fmt
import utils.validators as val
from datetime import date, time, datetime, timedelta

# 1. Auth check
user = navbar.render_navbar()

st.title("📅 Gestión de Citas")
st.markdown("---")

is_admin = user["rol_nombre"] == "ADMIN"

# Fetch services, groomers
services = queries.get_servicios()
all_groomers = queries.get_empleados()

if is_admin:
    # ==========================================
    # ADMIN VIEW
    # ==========================================
    st.subheader("Todas las Citas")
    
    # 1. State change controls
    citas = queries.get_citas()
    
    if citas:
        import pandas as pd
        df = pd.DataFrame(citas)
        
        # Display clean table
        for c in citas:
            status_color = "#3182ce"
            if c["estado"] == "concluido":
                status_color = "#38a169"
            elif c["estado"] == "cancelado":
                status_color = "#e53e3e"
            
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: rgba(255,255,255,0.03); padding:16px; border-radius:12px; border:1px solid rgba(255,255,255,0.05); margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <b style="font-size:16px;">{c['servicio_nombre']} — Mascota: {c['mascota_nombre']} ({c['mascota_especie']})</b>
                            <span style="background:{status_color}; color:#fff; font-size:11px; padding:2px 8px; border-radius:10px; font-weight:bold;">
                                {c['estado'].upper()}
                            </span>
                        </div>
                        <div style="font-size:13px; color:#a0aec0; margin-bottom:8px;">
                            👤 Cliente: <b>{c['cliente_nombre']}</b> | 
                            📅 Fecha: <b>{fmt.format_date(c['fecha'])}</b> | 
                            ⏰ Horario: <b>{fmt.format_time(c['hora_inicio'])} - {fmt.format_time(c['hora_fin'])}</b> | 
                            ✂️ Estilista: <b>{c['groomer_nombre'] or 'Sin asignar'}</b>
                        </div>
                        <div style="font-size:12px; color:#a0aec0; font-style:italic; margin-bottom:12px;">
                            Observaciones: {c['observaciones'] or 'Ninguna'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Admin action row inside streamlit columns
                col_btn1, col_btn2, col_btn3, _ = st.columns([1.5, 1.5, 2, 4])
                with col_btn1:
                    if c["estado"] == "reservado":
                        if st.button("✓ Completar", key=f"complete_{c['id_cita']}", use_container_width=True):
                            queries.update_cita_estado(c['id_cita'], 'concluido')
                            st.success("Cita completada.")
                            st.rerun()
                with col_btn2:
                    if c["estado"] in ["reservado", "programado"]:
                        if st.button("✗ Cancelar", key=f"cancel_{c['id_cita']}", use_container_width=True):
                            queries.update_cita_estado(c['id_cita'], 'cancelado')
                            st.success("Cita cancelada.")
                            st.rerun()
                with col_btn3:
                    # Reassign styler
                    with st.popover("✂️ Reasignar Estilista"):
                        selected_g = st.selectbox(
                            "Estilista", 
                            options=all_groomers, 
                            format_func=lambda x: f"{x['nombres']} {x['apellidos']} ({x['cargo']})",
                            key=f"g_sel_{c['id_cita']}"
                        )
                        if st.button("Guardar Asignación", key=f"save_g_{c['id_cita']}"):
                            queries.update_cita_groomer(c['id_cita'], selected_g["id_empleado"])
                            st.success(f"Asignado a {selected_g['nombres']}")
                            st.rerun()
    else:
        st.info("No hay citas registradas en el sistema.")
        
    st.markdown("---")
    st.subheader("Reserva Manual (Nueva Cita)")
    
    with st.form("admin_citas_form"):
        # Select client
        clients = queries.get_clientes()
        if not clients:
            st.error("Primero debes tener clientes registrados.")
            selected_client = None
        else:
            selected_client = st.selectbox(
                "Cliente",
                options=clients,
                format_func=lambda x: f"{x['apellidos']}, {x['nombres']} ({x['correo']})"
            )
            
        # Select pet based on client
        if selected_client:
            client_pets = queries.get_mascotas(selected_client["id_cliente"])
            selected_pet = st.selectbox(
                "Mascota",
                options=client_pets,
                format_func=lambda x: f"{x['nombre']} ({x['especie']} - {x['raza']})"
            )
        else:
            selected_pet = st.selectbox("Mascota", options=[], disabled=True)
            
        selected_service = st.selectbox(
            "Servicio",
            options=services,
            format_func=lambda x: f"{x['nombre']} — {fmt.format_currency(x['precio'])}"
        )
        
        selected_groomer = st.selectbox(
            "Estilista Groomer",
            options=all_groomers,
            format_func=lambda x: f"{x['nombres']} {x['apellidos']} ({x['cargo']})"
        )
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            appt_date = st.date_input("Fecha", min_value=date.today())
        with col_f2:
            start_t = st.time_input("Hora de Inicio", value=time(9, 0))
        with col_f3:
            end_t = st.time_input("Hora de Fin", value=time(10, 0))
            
        appt_type = st.selectbox("Tipo de Cita", ["normal", "especial", "personalizada"])
        notes = st.text_area("Observaciones")
        
        submitted = st.form_submit_button("Crear Cita Directa", type="primary")
        if submitted:
            if not selected_pet:
                st.error("Debes seleccionar una mascota.")
            else:
                is_valid, msg = val.validate_appointment_time(appt_date, start_t, end_t)
                if not is_valid:
                    st.error(msg)
                else:
                    res = client.enviar_reserva_cita(
                        selected_pet["id_mascota"], 
                        selected_service["id_servicio"], 
                        selected_groomer["id_empleado"],
                        appt_date, start_t, end_t, 
                        notes, appt_type, 
                        user_role="admin"
                    )
                    if res["success"]:
                        st.success("¡Cita creada exitosamente!")
                        st.rerun()
                    else:
                        st.error(f"Error al registrar cita: {res['message']}")

else:
    # ==========================================
    # USER (CLIENT) VIEW
    # ==========================================
    st.subheader("Agendar una Cita")
    
    # 1. Booking Form
    id_cliente = user["id_cliente"]
    my_pets = queries.get_mascotas(id_cliente)
    
    if not my_pets:
        st.warning("⚠️ No tienes mascotas registradas. Registra una mascota primero en la pestaña 'Mascotas' para poder agendar una cita.")
    else:
        with st.form("user_booking_form"):
            selected_pet = st.selectbox(
                "¿Para qué mascota?",
                options=my_pets,
                format_func=lambda x: f"{x['nombre']} ({x['especie']})"
            )
            
            selected_service = st.selectbox(
                "Selecciona el Servicio",
                options=services,
                format_func=lambda x: f"{x['nombre']} — {fmt.format_currency(x['precio'])}"
            )
            
            # Show list of groomers
            selected_groomer = st.selectbox(
                "Estilista Preferido (Opcional)",
                options=[{"id_empleado": config.GROOMER_PIVOTE_ID, "nombres": "Cualquier estilista disponible", "apellidos": ""}] + all_groomers,
                format_func=lambda x: f"{x['nombres']} {x['apellidos']}"
            )
            
            col_u1, col_u2, col_u3 = st.columns(3)
            with col_u1:
                appt_date = st.date_input("Fecha deseada", min_value=date.today() + timedelta(days=1))
            with col_u2:
                start_t = st.time_input("Hora de inicio", value=time(9, 0))
            with col_u3:
                # Add service duration dynamically or default to 1 hour
                end_t = st.time_input("Hora de fin (estimada)", value=time(10, 0))
                
            appt_type = st.selectbox("Tipo de cita", ["normal", "especial", "personalizada"])
            notes = st.text_area("Comentarios o indicaciones especiales (ej. alergias, miedo, corte deseado)")
            
            submitted = st.form_submit_button("Reservar Cita", type="primary")
            if submitted:
                is_valid, msg = val.validate_appointment_time(appt_date, start_t, end_t)
                if not is_valid:
                    st.error(msg)
                else:
                    res = client.enviar_reserva_cita(
                        selected_pet["id_mascota"],
                        selected_service["id_servicio"],
                        selected_groomer["id_empleado"],
                        appt_date, start_t, end_t,
                        notes, appt_type,
                        user_role="usuario",
                        id_cliente=id_cliente
                    )
                    if res["success"]:
                        st.success("🎉 Tu cita ha sido solicitada. Recibirás una confirmación por correo/Telegram.")
                        st.rerun()
                    else:
                        st.error(f"Ocurrió un error al reservar: {res['message']}")
                        
    # 2. View My Bookings
    st.markdown("---")
    st.subheader("Tus Citas Registradas")
    
    my_citas = queries.get_citas(id_cliente)
    if my_citas:
        for c in my_citas:
            status_color = "#3182ce"
            if c["estado"] == "concluido":
                status_color = "#38a169"
            elif c["estado"] == "cancelado":
                status_color = "#e53e3e"
                
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: rgba(255,255,255,0.03); padding:16px; border-radius:12px; border-left: 4px solid {status_color}; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <b style="font-size:15px;">{c['servicio_nombre']} para {c['mascota_nombre']}</b>
                            <span style="background:{status_color}; color:#fff; font-size:11px; padding:2px 8px; border-radius:10px; font-weight:bold;">
                                {c['estado'].upper()}
                            </span>
                        </div>
                        <div style="font-size:12px; color:#a0aec0;">
                            📅 Fecha: {fmt.format_date(c['fecha'])} | ⏰ Horario: {fmt.format_time(c['hora_inicio'])} - {fmt.format_time(c['hora_fin'])} | Precio: {fmt.format_currency(c['servicio_precio'])}
                        </div>
                        <div style="font-size:12px; color:#a0aec0; margin-top:4px;">
                            ✂️ Estilista: {c['groomer_nombre'] or 'Por asignar (Round-Robin a las 7:00 AM)'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("Aún no tienes citas agendadas.")
