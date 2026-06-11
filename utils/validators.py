import re
from datetime import datetime, date, time

def validate_email(email):
    """Checks if email has a valid format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """Validates phone number (contains only digits, spaces, dashes, or +, length 8-15)."""
    if not phone:
        return True  # Phone is optional in schema
    pattern = r"^\+?[\d\s-]{8,15}$"
    return bool(re.match(pattern, phone))

def validate_appointment_time(appt_date, start_time, end_time):
    """Validates that appointment is in the future and end_time > start_time."""
    if not appt_date or not start_time or not end_time:
        return False, "Todos los campos de fecha y hora son obligatorios."
        
    # Combine date and time
    start_dt = datetime.combine(appt_date, start_time)
    end_dt = datetime.combine(appt_date, end_time)
    
    if start_dt <= datetime.now():
        return False, "La hora de inicio de la cita debe ser en el futuro."
        
    if end_dt <= start_dt:
        return False, "La hora de fin debe ser posterior a la hora de inicio."
        
    return True, ""
