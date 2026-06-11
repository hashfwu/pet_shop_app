import streamlit as st
import components.navbar as navbar
import components.agent_status as agent_status_comp
import agents.client as client

# 1. Enforce Admin only authentication
user = navbar.render_navbar(required_role="ADMIN")

st.title("🤖 Centro de Control de Agentes n8n")
st.markdown("---")

st.subheader("Monitoreo y Automatización en Tiempo Real")
st.markdown(
    """
    Este panel interactúa directamente con el <b>Agente 07 (API de Control)</b> para supervisar el estado de los flujos de trabajo 
    en n8n y forzar ejecuciones manuales de los agentes de negocio.
    """,
    unsafe_allow_html=True
)

# Callbacks for toggles and executions


def handle_toggle(workflow_id, action):
    with st.spinner("Modificando estado de agente..."):
        res = client.toggle_agente(workflow_id, action)
        if isinstance(res, list) and len(res) > 0:
            res = res[0]
        if res["success"]:
            st.success(f"Éxito: {res['message']}")
            st.rerun()
        else:
            st.error(f"Error: {res['message']}")


def handle_trigger(workflow_id):
    if workflow_id == "Agente_03":
        with st.spinner("Ejecutando Agente 03 (Resumen Diario)..."):
            res = client.ejecutar_resumen_diario()
            if res["success"]:
                st.success("¡Resumen Diario ejecutado con éxito!")
                st.info(res["reporte"])
            else:
                st.error(f"Error al ejecutar: {res['message']}")
    elif workflow_id == "Agente_06":
        with st.spinner("Ejecutando Agente 06 (Agenda Groomers)..."):
            res = client.ejecutar_agenda_groomers()
            if res["success"]:
                st.success(f"¡Agenda de Groomers generada y distribuida! {
                           res['reasignaciones']} reasignaciones realizadas.")
                # Show results in a clean table
                if res["citas_agendadas"]:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(res["citas_agendadas"])[
                                 ["hora_inicio", "mascota_nombre", "servicio_nombre", "groomer_nombre"]])
            else:
                st.error(f"Error al ejecutar: {res['message']}")


# Fetch list of agents
agents_list = client.obtener_estado_agentes()

# Render status grid using the component
agent_status_comp.render_agent_status_grid(
    agents_list,
    on_toggle=handle_toggle,
    on_trigger=handle_trigger
)

# Manual refresh button
st.markdown("<br/>", unsafe_allow_html=True)
if st.button("🔄 Actualizar Estados"):
    st.rerun()
