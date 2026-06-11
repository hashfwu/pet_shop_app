import streamlit as st
import config
import database.queries as queries

def authenticate(username, password):
    """Verifies credentials against config (admin) and database (users)."""
    # 1. Check Hardcoded Admin
    if username == config.ADMIN_USER and password == config.ADMIN_PASSWORD:
        return {
            "id_usuario": 1,
            "nombres": "Administrador",
            "apellidos": "General",
            "correo": config.ADMIN_USER,
            "rol_nombre": "ADMIN",
            "id_cliente": None
        }
    
    # 2. Check Database Users
    try:
        user = queries.get_user_by_credentials(username, password)
        if user:
            return {
                "id_usuario": user["id_usuario"],
                "nombres": user["nombres"],
                "apellidos": user["apellidos"],
                "correo": user["correo"],
                "rol_nombre": user["rol_nombre"],  # 'ADMIN' or 'USUARIO'
                "id_cliente": user["id_cliente"]
            }
    except Exception as e:
        print(f"Auth database error: {e}")
        
    return None

def login(username, password):
    """Logs the user in by writing to st.session_state."""
    user = authenticate(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        return True
    return False

def logout():
    """Logs the user out and clears session state."""
    st.session_state.logged_in = False
    st.session_state.user = None
    if "agentes_estado_local" in st.session_state:
        del st.session_state.agentes_estado_local

def init_session():
    """Initializes standard session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
