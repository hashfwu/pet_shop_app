import streamlit as st

def render_agent_status_grid(agents_list, on_toggle=None, on_trigger=None):
    """Renders the status grid of n8n agents with toggles and triggers."""
    st.markdown(
        """
        <style>
        .agent-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .agent-name {
            font-weight: 700;
            font-size: 16px;
            color: #ffffff;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
        }
        .status-active {
            background-color: #48bb78;
            box-shadow: 0 0 8px #48bb78;
        }
        .status-inactive {
            background-color: #e53e3e;
            box-shadow: 0 0 8px #e53e3e;
        }
        .agent-meta {
            font-size: 13px;
            color: #a0aec0;
            margin-bottom: 12px;
        }
        .agent-meta span {
            color: #ffffff;
            font-weight: 500;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    for agent in agents_list:
        with st.container():
            st.markdown(f'<div class="agent-card">', unsafe_allow_html=True)
            
            # Dot and Title
            is_active = agent["estado"].lower() == "activo"
            dot_class = "status-active" if is_active else "status-inactive"
            status_text = "Activo" if is_active else "Inactivo"
            
            st.markdown(
                f"""
                <div class="agent-header">
                    <div class="agent-name">{agent['nombre']}</div>
                    <div style="display: flex; align-items: center; font-size: 13px; color: #fff; font-weight: bold;">
                        <span class="status-dot {dot_class}"></span>{status_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Metadata
            st.markdown(
                f"""
                <div class="agent-meta">
                    ID Flujo: <span>{agent['id']}</span> | 
                    Último disparo: <span>{agent['ultimo_disparo']}</span> | 
                    Ejecuciones hoy: <span>{agent['ejecuciones_hoy']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Action Controls (columns)
            btn_col1, btn_col2, btn_col3 = st.columns([1.5, 1.5, 2])
            
            with btn_col1:
                action = "deactivate" if is_active else "activate"
                label = "🔴 Desactivar" if is_active else "🟢 Activar"
                if st.button(label, key=f"toggle_{agent['id']}", use_container_width=True):
                    if on_toggle:
                        on_toggle(agent['id'], action)
                        
            with btn_col2:
                # Trigger button for Agents that can be run manually (03 and 06)
                is_manual = agent['id'] in ["Agente_03", "Agente_06"]
                if is_manual:
                    if st.button("⚡ Ejecutar Ahora", key=f"trigger_{agent['id']}", use_container_width=True):
                        if on_trigger:
                            on_trigger(agent['id'])
                else:
                    st.button("⚡ Ejecutar Ahora", key=f"trigger_{agent['id']}", disabled=True, use_container_width=True)
                    
            with btn_col3:
                # Expander for logs inside each card
                with st.expander("📝 Ver Logs de Ejecución"):
                    import agents.client as client
                    logs = client.obtener_logs_agente(agent['id'], limit=5)
                    if logs:
                        for log in logs:
                            log_color = "#48bb78" if log["estado"] == "success" else "#e53e3e"
                            st.markdown(
                                f"""
                                <div style="font-size: 11px; margin-bottom: 6px; padding: 4px; background: rgba(0,0,0,0.2); border-radius: 4px;">
                                    <b>[{log['timestamp']}]</b> <span style="color: {log_color}; font-weight: bold;">{log['estado'].upper()}</span><br/>
                                    ID: {log['ejecucion_id']} - {log['detalles']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.caption("No hay logs disponibles.")
            
            st.markdown('</div>', unsafe_allow_html=True)
