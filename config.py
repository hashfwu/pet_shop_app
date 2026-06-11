# ================================================================
# config.py — Configuración Central del Sistema
# Spa de Mascotas · Modificar aquí o desde el Panel Admin
# ================================================================

import tomllib
from pathlib import Path

_SECRETS_PATH = Path(".streamlit/secrets.toml")


def _load_secrets():
    if _SECRETS_PATH.exists():
        with open(_SECRETS_PATH, "rb") as f:
            return tomllib.load(f)
    return {}


_secrets = _load_secrets()


def _require(name):
    value = _secrets.get(name)
    if value is None or value == "":
        raise ValueError(
            f"Variable faltante: {name}. "
            f"Defínela en .streamlit/secrets.toml o en las Secrets de Streamlit Cloud."
        )
    return value


# ── AUTENTICACIÓN ─────────────────────────────────────────────
ADMIN_USER = _secrets.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = _secrets.get("ADMIN_PASSWORD", "admin")
SESSION_TIMEOUT_MINUTES = int(_secrets.get("SESSION_TIMEOUT", "60"))

# ── BASE DE DATOS (SUPABASE) ──────────────────────────────────
DB_HOST = _require("DB_HOST")
DB_PORT = int(_secrets.get("DB_PORT", "5432"))
DB_NAME = _secrets.get("DB_NAME", "postgres")
DB_USER = _secrets.get("DB_USER", "postgres")
DB_PASSWORD = _require("DB_PASSWORD")
DB_SSL_MODE = _secrets.get("DB_SSL_MODE", "require")

# ── N8N (LOCAL + NGROK) ───────────────────────────────────────
N8N_BASE_URL = _secrets.get("N8N_BASE_URL", "http://localhost:5678")
N8N_API_KEY = _secrets.get("N8N_API_KEY", "")
NGROK_URL = _require("NGROK_URL")

# ── WEBHOOKS N8N ──────────────────────────────────────────────
WEBHOOK_RESERVA_CITA = f"{NGROK_URL}/webhook/reserva-cita"
WEBHOOK_RECOMENDAR_PROD = f"{NGROK_URL}/webhook/recomendar-productos"
WEBHOOK_AGENTES_ESTADO = f"{NGROK_URL}/webhook/agentes/estado"
WEBHOOK_AGENTES_TOGGLE = f"{NGROK_URL}/webhook/agentes/toggle"
WEBHOOK_AGENTES_LOGS = f"{NGROK_URL}/webhook/agentes/logs"
WEBHOOK_METRICAS_HOY = f"{NGROK_URL}/webhook/metricas/hoy"
WEBHOOK_ALERTAS = f"{NGROK_URL}/webhook/alertas"
WEBHOOK_TELEGRAM_MENSAJES = f"{NGROK_URL}/webhook/telegram/mensajes"
WEBHOOK_RESUMEN_DIARIO = f"{NGROK_URL}/webhook/resumen-diario"
WEBHOOK_AGENDA_GROOMERS = f"{NGROK_URL}/webhook/agenda-groomers"


# ── EMAIL / SMTP ──────────────────────────────────────────────
SMTP_HOST = _secrets.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(_secrets.get("SMTP_PORT", "587"))
SMTP_USER = _secrets.get("SMTP_USER", "")
SMTP_PASSWORD = _secrets.get("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = _secrets.get("SMTP_FROM_EMAIL", "spa@spademascotas.bo")
ADMIN_EMAIL = _secrets.get("ADMIN_EMAIL", "admin@spademascotas.bo")


# ── NEGOCIO ───────────────────────────────────────────────────
NEGOCIO_NOMBRE = _secrets.get("NEGOCIO_NOMBRE", "Spa de Mascotas")
NEGOCIO_MONEDA = _secrets.get("NEGOCIO_MONEDA", "Bs.")
STOCK_ALERTA_DIAS = int(_secrets.get("STOCK_ALERTA_DIAS", "7"))
CITAS_ALERTA_HORA = _secrets.get("CITAS_ALERTA_HORA", "08:00")

# ── ID PIVOTE (empleado placeholder) ─────────────────────────
GROOMER_PIVOTE_ID = int(_secrets.get("GROOMER_PIVOTE_ID", "1"))
