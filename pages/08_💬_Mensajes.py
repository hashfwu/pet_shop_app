import streamlit as st
import components.navbar as navbar
import database.queries as queries
import utils.formatters as fmt

# 1. Enforce Admin only authentication
user = navbar.render_navbar(required_role="ADMIN")

st.title("💬 Centro de Mensajes y Notificaciones")
st.markdown("---")

st.subheader("Historial de Comunicaciones")
st.markdown(
    """
    Este panel registra todos los mensajes enviados/recibidos por el **Bot de Telegram (Agente 02)** y las 
    alertas automáticas del negocio guardadas en la base de datos.
    """,
    unsafe_allow_html=True
)

# Fetch messages
try:
    notifs = queries.get_notificaciones()
except Exception as e:
    st.error(f"Error cargando notificaciones: {e}")
    notifs = []

if notifs:
    for n in notifs:
        type_color = "#3182ce"
        if "alerta" in n["tipo"].lower():
            type_color = "#dd6b20"
        elif "email" in n["tipo"].lower() or "report" in n["tipo"].lower():
            type_color = "#805ad5"
        elif "telegram" in n["tipo"].lower():
            type_color = "#319795"
            
        with st.container():
            st.markdown(
                f"""
                <div style="background: rgba(255,255,255,0.03); padding: 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="background:{type_color}; color:#fff; font-size:10px; padding:2px 8px; border-radius:99px; font-weight:bold; text-transform:uppercase;">
                            {n['tipo']}
                        </span>
                        <span style="font-size:11px; color:#a0aec0;">{fmt.format_date(n['fecha_envio'])} - {n['fecha_envio']}</span>
                    </div>
                    <div style="font-size:13px; color:#e2e8f0; line-height:1.4;">
                        {n['mensaje']}
                    </div>
                    <div style="font-size:11px; color:#718096; margin-top:6px; text-align:right;">
                        Estado de Entrega: <b>{n['estado'].upper()}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("No hay mensajes o notificaciones registradas en la base de datos.")
