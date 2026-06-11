import streamlit as st
import config

def render_metrics_cards(metrics):
    """Renders the dashboard KPIs in styled grid cards."""
    # Custom CSS for cards
    st.markdown(
        """
        <style>
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease-in-out;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.15);
        }
        .metric-title {
            font-size: 14px;
            color: #a0aec0;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .metric-footer {
            font-size: 12px;
            color: #48bb78;
            font-weight: 500;
        }
        .metric-footer.warning {
            color: #e53e3e;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">💵 Ingresos del Día</div>
                <div class="metric-value">{config.NEGOCIO_MONEDA} {metrics['ingresos']:.2f}</div>
                <div class="metric-footer">Ventas concluidas</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">📅 Total Citas</div>
                <div class="metric-value">{metrics['citas_total']}</div>
                <div class="metric-footer">{metrics['citas_pendientes']} pendientes</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">⭐ Calificación Promedio</div>
                <div class="metric-value">{metrics['calificacion_avg']} / 5.0</div>
                <div class="metric-footer">Calificaciones de hoy</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col4:
        # Stock warning color
        stock_footer_class = "warning" if metrics['stock_bajo'] > 0 else ""
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">📦 Stock Bajo</div>
                <div class="metric-value">{metrics['stock_bajo']}</div>
                <div class="metric-footer {stock_footer_class}">Productos por reponer</div>
            </div>
            """,
            unsafe_allow_html=True
        )
