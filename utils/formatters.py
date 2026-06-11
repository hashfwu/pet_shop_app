from datetime import datetime, date, time
import config

def format_currency(value):
    """Formats a numeric value to the business currency (e.g. Bs. 150.00)"""
    try:
        val = float(value)
        return f"{config.NEGOCIO_MONEDA} {val:.2f}"
    except (ValueError, TypeError):
        return f"{config.NEGOCIO_MONEDA} 0.00"

def format_date(value):
    """Formats a date object or ISO string to DD/MM/YYYY format."""
    if not value:
        return ""
    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")
    try:
        # Try parsing ISO string
        dt = datetime.fromisoformat(str(value).replace("Z", ""))
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return str(value)

def format_time(value):
    """Formats a time object or string to HH:MM format."""
    if not value:
        return ""
    if isinstance(value, (time, datetime)):
        return value.strftime("%H:%M")
    try:
        # Try parsing string like "10:00:00"
        parts = str(value).split(":")
        if len(parts) >= 2:
            return f"{parts[0]:>02}:{parts[1]:>02}"
        return str(value)
    except Exception:
        return str(value)
