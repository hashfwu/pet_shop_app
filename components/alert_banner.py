import streamlit as st

def render_alert_banner(alerts):
    """Renders active system alerts in a highlighted, color-coded banner section."""
    if not alerts:
        return
        
    st.markdown(
        """
        <style>
        .alerts-title {
            font-size: 15px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
        }
        .alerts-title::before {
            content: "⚠️";
            margin-right: 8px;
        }
        .alert-item {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 13px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .alert-high {
            background-color: rgba(229, 62, 62, 0.15);
            border: 1px solid rgba(229, 62, 62, 0.3);
            color: #feb2b2;
        }
        .alert-medium {
            background-color: rgba(221, 107, 32, 0.15);
            border: 1px solid rgba(221, 107, 32, 0.3);
            color: #fbd38d;
        }
        .alert-badge {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            padding: 2px 6px;
            border-radius: 4px;
        }
        .badge-high {
            background-color: #e53e3e;
            color: #ffffff;
        }
        .badge-medium {
            background-color: #dd6b20;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="alerts-title">Alertas Operacionales Activas</div>', unsafe_allow_html=True)
    
    for alert in alerts:
        urgency = alert.get("urgencia", "alta").lower()
        alert_class = "alert-high" if urgency == "alta" else "alert-medium"
        badge_class = "badge-high" if urgency == "alta" else "badge-medium"
        badge_text = "Crítico" if urgency == "alta" else "Advertencia"
        
        st.markdown(
            f"""
            <div class="alert-item {alert_class}">
                <div>{alert['mensaje']}</div>
                <span class="alert-badge {badge_class}">{badge_text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
