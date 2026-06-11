import streamlit as st
import os
import components.navbar as navbar
import config

# 1. Enforce Admin only authentication
user = navbar.render_navbar(required_role="ADMIN")

st.title("⚙️ Configuración Global del Sistema")
st.markdown("---")

# Load existing values
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

# Tabs for configuration sections
tab_db, tab_webhooks, tab_keys, tab_smtp, tab_biz, tab_ollama, tab_adv = st.tabs([
    "🗄️ Base de Datos", "🔗 Webhooks", "🔑 API Keys", "📧 Email SMTP", "🏪 Negocio", "🤖 Ollama", "⚙️ Avanzado"
])

# Variables to collect from form
updates = {}

# Tab 1: Database Settings
with tab_db:
    st.subheader("Configuración de Base de Datos Supabase")
    db_host = st.text_input("Host", value=os.getenv("DB_HOST", config.DB_HOST))
    db_port = st.number_input("Puerto", value=int(os.getenv("DB_PORT", config.DB_PORT)), step=1)
    db_name = st.text_input("Nombre de BD", value=os.getenv("DB_NAME", config.DB_NAME))
    db_user = st.text_input("Usuario BD", value=os.getenv("DB_USER", config.DB_USER))
    db_pass = st.text_input("Contraseña BD", value=os.getenv("DB_PASSWORD", config.DB_PASSWORD), type="password")
    db_ssl = st.text_input("SSL Mode", value=os.getenv("DB_SSL_MODE", config.DB_SSL_MODE))
    
    # Test connection button
    if st.button("🔌 Probar Conexión a Base de Datos"):
        with st.spinner("Conectando..."):
            import psycopg2
            try:
                conn = psycopg2.connect(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_pass,
                    sslmode=db_ssl,
                    connect_timeout=3
                )
                conn.close()
                st.success("✅ ¡Conexión exitosa a Supabase!")
            except Exception as e:
                st.error(f"❌ Fallo de conexión: {e}")
                
    updates.update({
        "DB_HOST": db_host,
        "DB_PORT": str(db_port),
        "DB_NAME": db_name,
        "DB_USER": db_user,
        "DB_PASSWORD": db_pass,
        "DB_SSL_MODE": db_ssl
    })

# Tab 2: Webhooks (n8n + ngrok)
with tab_webhooks:
    st.subheader("Configuración de Integración n8n y ngrok")
    n8n_url = st.text_input("URL Base n8n", value=os.getenv("N8N_BASE_URL", config.N8N_BASE_URL))
    n8n_key = st.text_input("Clave API n8n (N8N_API_KEY)", value=os.getenv("N8N_API_KEY", config.N8N_API_KEY), type="password")
    ngrok_url = st.text_input("URL de ngrok (Túnel)", value=os.getenv("NGROK_URL", config.NGROK_URL))
    
    st.info(
        f"""
        <b>Webhooks Generados:</b><br/>
        • Reserva de citas: <code>{ngrok_url}/webhook/reserva-cita</code><br/>
        • Recomendación productos: <code>{ngrok_url}/webhook/recomendar-productos</code><br/>
        • Estado de agentes: <code>{ngrok_url}/webhook/agentes/estado</code><br/>
        • Resumen diario: <code>{ngrok_url}/webhook/resumen-diario</code>
        """,
        unsafe_allow_html=True
    )
    
    updates.update({
        "N8N_BASE_URL": n8n_url,
        "N8N_API_KEY": n8n_key,
        "NGROK_URL": ngrok_url
    })

# Tab 3: API Keys
with tab_keys:
    st.subheader("Claves de API Externas")
    gemini_key = st.text_input("Google Gemini API Key", value=os.getenv("GEMINI_API_KEY", config.GEMINI_API_KEY), type="password")
    tg_token = st.text_input("Telegram Bot Token", value=os.getenv("TELEGRAM_BOT_TOKEN", config.TELEGRAM_BOT_TOKEN), type="password")
    
    updates.update({
        "GEMINI_API_KEY": gemini_key,
        "TELEGRAM_BOT_TOKEN": tg_token
    })

# Tab 4: Email SMTP
with tab_smtp:
    st.subheader("Servidor de Correo SMTP")
    smtp_host = st.text_input("Host SMTP", value=os.getenv("SMTP_HOST", config.SMTP_HOST))
    smtp_port = st.number_input("Puerto SMTP", value=int(os.getenv("SMTP_PORT", config.SMTP_PORT)), step=1)
    smtp_user = st.text_input("Usuario SMTP", value=os.getenv("SMTP_USER", config.SMTP_USER))
    smtp_pass = st.text_input("Contraseña SMTP", value=os.getenv("SMTP_PASSWORD", config.SMTP_PASSWORD), type="password")
    smtp_from = st.text_input("Remitente (Email From)", value=os.getenv("SMTP_FROM_EMAIL", config.SMTP_FROM_EMAIL))
    admin_email = st.text_input("Email Admin (Notificaciones)", value=os.getenv("ADMIN_EMAIL", config.ADMIN_EMAIL))
    
    updates.update({
        "SMTP_HOST": smtp_host,
        "SMTP_PORT": str(smtp_port),
        "SMTP_USER": smtp_user,
        "SMTP_PASSWORD": smtp_pass,
        "SMTP_FROM_EMAIL": smtp_from,
        "ADMIN_EMAIL": admin_email
    })

# Tab 5: Negocio
with tab_biz:
    st.subheader("Configuración de Reglas de Negocio")
    biz_name = st.text_input("Nombre del Negocio", value=os.getenv("NEGOCIO_NOMBRE", config.NEGOCIO_NOMBRE))
    biz_currency = st.text_input("Moneda", value=os.getenv("NEGOCIO_MONEDA", config.NEGOCIO_MONEDA))
    stock_alert_days = st.number_input("Días Alerta Stock", value=int(os.getenv("STOCK_ALERTA_DIAS", config.STOCK_ALERTA_DIAS)), step=1)
    citas_alert_hour = st.text_input("Hora de Alerta Citas", value=os.getenv("CITAS_ALERTA_HORA", config.CITAS_ALERTA_HORA))
    
    updates.update({
        "NEGOCIO_NOMBRE": biz_name,
        "NEGOCIO_MONEDA": biz_currency,
        "STOCK_ALERTA_DIAS": str(stock_alert_days),
        "CITAS_ALERTA_HORA": citas_alert_hour
    })

# Tab 6: Ollama
with tab_ollama:
    st.subheader("Configuración de Servidor de IA Local (Ollama)")
    ollama_url = st.text_input("URL de Ollama", value=os.getenv("OLLAMA_URL", config.OLLAMA_URL))
    ollama_model = st.text_input("Modelo de Ollama", value=os.getenv("OLLAMA_MODEL", config.OLLAMA_MODEL))
    
    updates.update({
        "OLLAMA_URL": ollama_url,
        "OLLAMA_MODEL": ollama_model
    })

# Tab 7: Avanzado
with tab_adv:
    st.subheader("Ajustes Avanzados del Sistema")
    pivot_id = st.number_input("ID Groomer Pivote (Placeholder)", value=int(os.getenv("GROOMER_PIVOTE_ID", config.GROOMER_PIVOTE_ID)), step=1)
    session_timeout = st.number_input("Timeout de Sesión (Minutos)", value=int(os.getenv("SESSION_TIMEOUT", config.SESSION_TIMEOUT_MINUTES)), step=1)
    
    admin_user = st.text_input("Usuario Administrador", value=os.getenv("ADMIN_USER", config.ADMIN_USER))
    admin_pass = st.text_input("Contraseña Administrador", value=os.getenv("ADMIN_PASSWORD", config.ADMIN_PASSWORD), type="password")
    
    updates.update({
        "GROOMER_PIVOTE_ID": str(pivot_id),
        "SESSION_TIMEOUT": str(session_timeout),
        "ADMIN_USER": admin_user,
        "ADMIN_PASSWORD": admin_pass
    })

# Save Section
st.markdown("---")
if st.button("💾 Guardar Configuración", type="primary", use_container_width=True):
    # Read existing environment variables to merge
    env_content = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env_content[k.strip()] = v.strip()
                    
    # Update with new values
    env_content.update(updates)
    
    # Write back to .env
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# .env (Generado por Panel Admin Streamlit)\n")
        for k, v in env_content.items():
            f.write(f"{k}={v}\n")
            
    st.success("✅ Configuración guardada en archivo .env local.")
    st.info("ℹ️ Para aplicar los cambios de manera global, por favor reinicia la aplicación Streamlit.")
