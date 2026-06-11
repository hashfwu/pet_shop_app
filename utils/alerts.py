import database.queries as queries

def get_active_alerts():
    """Fetches automatically detected operational alerts."""
    try:
        return queries.get_alertas_automaticas()
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return []
