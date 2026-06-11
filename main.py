import streamlit as st
import database.connection as db
import auth.login as auth

# 1. Configuración de Página (Debe ser la primera llamada de Streamlit)
st.set_page_config(
    page_title="Spa de Mascotas — Agentes Inteligentes",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialización de la Base de Datos
db.init_db()

# 3. Inicialización de la Sesión
auth.init_session()

# 4. Cargar CSS personalizado
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# 5. Estilos Visuales Premium
st.markdown(
    """
    <style>
    .welcome-container {
        padding: 40px;
        background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(72, 187, 120, 0.1) 100%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 30px;
    }
    .welcome-title {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 12px;
    }
    .welcome-desc {
        font-size: 16px;
        color: #a0aec0;
        max-width: 600px;
        margin: 0 auto 24px auto;
    }
    .nav-tip {
        background: rgba(255, 255, 255, 0.05);
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #4299e1;
        font-size: 14px;
        color: #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
st.markdown('<div class="welcome-title">🐾 Sistema del Spa de Mascotas</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="welcome-desc">Plataforma inteligente de gestión integrada con agentes automatizados en n8n, Base de Datos en Supabase y Bot de Telegram.</div>', 
    unsafe_allow_html=True
)

# Show login card if not logged in
if not st.session_state.logged_in:
    import components.navbar as navbar
    navbar.render_navbar()
else:
    user = st.session_state.user
    st.markdown(f"### ¡Hola de nuevo, {user['nombres']}!")
    st.markdown(
        f"""
        Te has autenticado correctamente con el rol de <b style='color: #4299e1;'>{user['rol_nombre']}</b>.
        """, 
        unsafe_allow_html=True
    )
    
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="nav-tip">
        👉 <b>Consejo:</b> Utiliza el menú de navegación de la izquierda en la barra lateral para acceder a las distintas secciones,
        como <b>Inicio (Dashboard)</b>, <b>Citas</b>, <b>Mascotas</b>, y las herramientas exclusivas de administración.
    </div>
    """,
    unsafe_allow_html=True
)
