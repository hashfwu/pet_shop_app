import streamlit as st
import components.navbar as navbar
import components.metrics_cards as metrics_cards
import components.alert_banner as alert_banner
import components.charts as charts
import database.queries as queries
import agents.client as client
import utils.alerts as alerts_util
import utils.formatters as fmt
from datetime import date

# 1. Enforce Authentication and check role (available to all logged in users)
user = navbar.render_navbar()

st.title("🏠 Inicio — Panel Principal")
st.markdown("---")

if user["rol_nombre"] == "ADMIN":
    # ==========================================
    # ADMIN VIEW
    # ==========================================
    st.subheader("Resumen de Operaciones")
    
    # Fetch data
    try:
        metrics = queries.get_daily_metrics()
        active_alerts = alerts_util.get_active_alerts()
        all_citas = queries.get_citas()
        # Filter appointments of today for chart
        today_str = date.today().isoformat()
        today_citas = [c for c in all_citas if str(c["fecha"]) == today_str]
    except Exception as e:
        st.error(f"Error cargando datos del dashboard: {e}")
        metrics = {"ingresos": 0, "citas_total": 0, "citas_atendidas": 0, "citas_canceladas": 0, "citas_pendientes": 0, "calificacion_avg": 0, "stock_bajo": 0}
        active_alerts = []
        today_citas = []
        
    # Render KPI Cards
    metrics_cards.render_metrics_cards(metrics)
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Alerts and Quick Actions
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if active_alerts:
            alert_banner.render_alert_banner(active_alerts)
        else:
            st.success("✅ Todo funciona correctamente. No hay alertas operacionales activas.")
            
        # Chart
        st.markdown("<br/>", unsafe_allow_html=True)
        charts.render_appointments_by_hour(today_citas)
        
    with col2:
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.03); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                <h4 style="margin-top:0;">⚡ Acciones Rápidas de Agentes</h4>
                <p style="font-size:12px; color:#a0aec0;">Ejecuta de forma manual las tareas de automatización en cualquier momento.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Action Buttons
        if st.button("📊 Generar Resumen Diario Ahora", use_container_width=True):
            with st.spinner("Invocando Agente 03..."):
                res = client.ejecutar_resumen_diario()
                if res["success"]:
                    st.success("¡Resumen ejecutivo generado y enviado!")
                    st.info(res["reporte"])
                else:
                    st.error(f"Error: {res['message']}")
                    
        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
        
        if st.button("✂️ Distribuir Agenda de Hoy", use_container_width=True):
            with st.spinner("Invocando Agente 06..."):
                res = client.ejecutar_agenda_groomers()
                if res["success"]:
                    st.success(f"¡Agenda distribuida! Reasignaciones: {res['reasignaciones']}")
                    st.json(res["citas_agendadas"])
                else:
                    st.error(f"Error: {res['message']}")
                    
        # State of Agents (Mini display)
        st.markdown("---")
        st.subheader("Estado de Automatizaciones")
        agents = client.obtener_estado_agentes()
        for ag in agents:
            dot = "🟢" if ag["estado"] == "activo" else "🔴"
            st.markdown(f"**{dot} {ag['nombre']}** ({ag['estado'].upper()})")

else:
    # ==========================================
    # USER (CLIENT) VIEW
    # ==========================================
    st.subheader(f"¡Bienvenido de nuevo a {st.session_state.user['nombres']}! 🐾")
    st.markdown("Consiente a tu mascota con el mejor cuidado en manos de nuestros expertos.")
    
    # 1. Fetch own pets and upcoming appointments
    try:
        id_cliente = user["id_cliente"]
        mis_citas = queries.get_citas(id_cliente)
        # Filter for upcoming appointments
        today = date.today()
        upcoming = [c for c in mis_citas if date.fromisoformat(str(c["fecha"])) >= today and c["estado"] != "cancelado"][:3]
    except Exception as e:
        st.error(f"Error cargando tu información de citas: {e}")
        upcoming = []
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Layout
    col_citas, col_recom = st.columns([1.5, 1])
    
    with col_citas:
        st.markdown("### 📅 Tus Próximas Citas")
        if upcoming:
            for c in upcoming:
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 255, 255, 0.04); padding: 16px; border-radius: 12px; border-left: 5px solid #38a169; margin-bottom: 12px;">
                        <div style="font-weight: bold; font-size:16px;">{c['servicio_nombre']} para {c['mascota_nombre']}</div>
                        <div style="font-size:13px; color:#a0aec0;">
                            📅 Fecha: {fmt.format_date(c['fecha'])} | ⏰ Hora: {fmt.format_time(c['hora_inicio'])} - {fmt.format_time(c['hora_fin'])}
                        </div>
                        <div style="font-size:13px; color:#a0aec0;">
                            ✂️ Estilista: {c['groomer_nombre'] or 'Por asignar'} | 🏷️ Estado: <b>{c['estado'].upper()}</b>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        else:
            st.info("No tienes citas próximas agendadas.")
            
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("📅 Agendar Nueva Citas Ahora", type="primary"):
            st.info("Por favor, dirígete a la pestaña 'Citas' en el menú de la izquierda para realizar tu reserva.")
            
    with col_recom:
        st.markdown("### 🛍️ Recomendaciones Personalizadas (IA)")
        with st.spinner("Analizando preferencias con IA..."):
            recom_res = client.obtener_recomendacion_productos(user["id_cliente"], limit=2)
            if recom_res["success"]:
                st.markdown(
                    f"""
                    <div style="background: rgba(66, 153, 225, 0.05); padding: 16px; border-radius: 12px; border: 1px solid rgba(66, 153, 225, 0.2); margin-bottom: 16px; line-height: 1.5; font-size: 13.5px; color:#e2e8f0;">
                        ✨ <i>"{recom_res['recomendacion_ia']}"</i>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Render the products recommended
                for prod in recom_res["productos"][:2]:
                    st.markdown(
                        f"""
                        <div style="background: rgba(255, 255, 255, 0.03); padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <b style="font-size:13px;">{prod['nombre']}</b><br/>
                                <span style="font-size:11px; color:#a0aec0;">{prod['categoria_nombre']}</span>
                            </div>
                            <b style="color:#48bb78; font-size:13px;">Bs. {prod['precio_venta']:.2f}</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.caption("No pudimos cargar recomendaciones personalizadas en este momento.")
