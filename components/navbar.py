import streamlit as st
import auth.login as auth

def render_navbar(required_role=None):
    """Renders the top/sidebar profile section and enforces access control."""
    auth.init_session()
    
    # 1. Enforce Authentication
    if not st.session_state.logged_in:
        st.markdown(
            """
            <style>
            .login-container {
                max-width: 400px;
                margin: 80px auto;
                padding: 40px;
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                text-align: center;
            }
            .login-header {
                font-size: 24px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 8px;
            }
            .login-subtitle {
                font-size: 14px;
                color: #a0aec0;
                margin-bottom: 24px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header">🐾 Spa de Mascotas</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sistema de Agentes Inteligentes</div>', unsafe_allow_html=True)
        
        email = st.text_input("Usuario / Correo", placeholder="admin o correo@cliente.com")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        if st.button("Iniciar Sesión", use_container_width=True):
            if auth.login(email, password):
                st.success("¡Inicio de sesión exitoso!")
                st.rerun()
            else:
                st.error("Credenciales inválidas. Intente nuevamente.")
                
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
        
    # 2. Render Sidebar Profile
    user = st.session_state.user
    role_badge_color = "#3182ce" if user["rol_nombre"] == "ADMIN" else "#38a169"
    
    st.sidebar.markdown(
        f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
            <div style="font-weight: bold; font-size: 16px; color: #fff;">{user['nombres']} {user['apellidos']}</div>
            <div style="font-size: 12px; color: #a0aec0; margin-bottom: 8px;">{user['correo']}</div>
            <span style="background: {role_badge_color}; color: #fff; font-size: 10px; padding: 3px 8px; border-radius: 99px; font-weight: bold; text-transform: uppercase;">
                {user['rol_nombre']}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Logout Button in Sidebar
    if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
        auth.logout()
        st.rerun()
        
    # 3. Enforce Role-based Authorization
    if required_role and user["rol_nombre"] != required_role:
        st.error(f"🚫 Acceso Denegado. Esta sección es exclusiva para el rol {required_role}.")
        st.info("Por favor, navega a otra página en el menú lateral.")
        st.stop()
        
    return user
