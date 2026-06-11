import database.connection as db

def get_user_by_credentials(email, password):
    query = """
        SELECT u.id_usuario, u.nombres, u.apellidos, u.correo, u.telefono, u.estado, r.nombre as rol_nombre, c.id_cliente
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
        WHERE u.correo = %s AND u.contrasena = %s AND u.estado = 'activo';
    """
    res = db.execute_query(query, (email, password))
    return res[0] if res else None

def get_daily_metrics():
    # Earnings today
    query_earnings = """
        SELECT COALESCE(SUM(total), 0) as total_ingresos
        FROM ventas
        WHERE date(fecha_venta) = CURRENT_DATE AND estado = 'pagada';
    """
    # Appointments count today
    query_citas = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN estado = 'concluido' THEN 1 END) as atendidas,
            COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as canceladas,
            COUNT(CASE WHEN estado = 'reservado' OR estado = 'programado' THEN 1 END) as pendientes
        FROM citas
        WHERE fecha = CURRENT_DATE;
    """
    # Average rating
    query_rating = """
        SELECT COALESCE(AVG(puntuacion), 0) as avg_rating
        FROM calificaciones c
        JOIN citas ct ON c.id_cita = ct.id_cita
        WHERE ct.fecha = CURRENT_DATE;
    """
    # Low stock count
    query_low_stock = """
        SELECT COUNT(*) as low_stock_count
        FROM productos_venta
        WHERE stock <= stock_minimo AND estado = 'activo';
    """
    
    earnings = db.execute_query(query_earnings)
    citas = db.execute_query(query_citas)
    rating = db.execute_query(query_rating)
    low_stock = db.execute_query(query_low_stock)
    
    citas_data = citas[0] if citas else {"total": 0, "atendidas": 0, "canceladas": 0, "pendientes": 0}
    
    return {
        "ingresos": earnings[0]["total_ingresos"] if earnings else 0,
        "citas_total": citas_data["total"],
        "citas_atendidas": citas_data["atendidas"],
        "citas_canceladas": citas_data["canceladas"],
        "citas_pendientes": citas_data["pendientes"],
        "calificacion_avg": round(rating[0]["avg_rating"], 1) if rating else 0,
        "stock_bajo": low_stock[0]["low_stock_count"] if low_stock else 0
    }

def get_citas(id_cliente=None):
    if id_cliente:
        query = """
            SELECT c.id_cita, c.fecha, c.hora_inicio, c.hora_fin, c.estado, c.observaciones, c.tipo_cita,
                   m.nombre as mascota_nombre, s.nombre as servicio_nombre, s.precio as servicio_precio,
                   u_g.nombres || ' ' || u_g.apellidos as groomer_nombre
            FROM citas c
            JOIN mascotas m ON c.id_mascota = m.id_mascota
            JOIN servicios s ON c.id_servicio = s.id_servicio
            LEFT JOIN empleados e ON c.id_empleado = e.id_empleado
            LEFT JOIN usuarios u_g ON e.id_usuario = u_g.id_usuario
            WHERE m.id_cliente = %s
            ORDER BY c.fecha DESC, c.hora_inicio DESC;
        """
        return db.execute_query(query, (id_cliente,))
    else:
        query = """
            SELECT c.id_cita, c.fecha, c.hora_inicio, c.hora_fin, c.estado, c.observaciones, c.tipo_cita,
                   m.nombre as mascota_nombre, m.especie as mascota_especie, 
                   s.nombre as servicio_nombre, s.precio as servicio_precio,
                   u_g.nombres || ' ' || u_g.apellidos as groomer_nombre,
                   c.id_empleado, c.id_mascota, c.id_servicio,
                   u_c.nombres || ' ' || u_c.apellidos as cliente_nombre
            FROM citas c
            JOIN mascotas m ON c.id_mascota = m.id_mascota
            JOIN clientes cl ON m.id_cliente = cl.id_cliente
            JOIN usuarios u_c ON cl.id_usuario = u_c.id_usuario
            JOIN servicios s ON c.id_servicio = s.id_servicio
            LEFT JOIN empleados e ON c.id_empleado = e.id_empleado
            LEFT JOIN usuarios u_g ON e.id_usuario = u_g.id_usuario
            ORDER BY c.fecha DESC, c.hora_inicio DESC;
        """
        return db.execute_query(query)

def insert_cita(id_mascota, id_servicio, id_empleado, fecha, hora_inicio, hora_fin, observaciones, tipo_cita):
    query = """
        INSERT INTO citas (id_mascota, id_servicio, id_empleado, fecha, hora_inicio, hora_fin, observaciones, tipo_cita, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'reservado');
    """
    return db.execute_query(query, (id_mascota, id_servicio, id_empleado, fecha, hora_inicio, hora_fin, observaciones, tipo_cita), fetch=False)

def update_cita_estado(id_cita, estado):
    query = "UPDATE citas SET estado = %s WHERE id_cita = %s;"
    return db.execute_query(query, (estado, id_cita), fetch=False)

def update_cita_groomer(id_cita, id_groomer):
    query = "UPDATE citas SET id_empleado = %s WHERE id_cita = %s;"
    return db.execute_query(query, (id_groomer, id_cita), fetch=False)

def get_mascotas(id_cliente=None):
    if id_cliente:
        query = """
            SELECT m.*, u.nombres || ' ' || u.apellidos as dueno_nombre
            FROM mascotas m
            JOIN clientes c ON m.id_cliente = c.id_cliente
            JOIN usuarios u ON c.id_usuario = u.id_usuario
            WHERE m.id_cliente = %s AND m.estado = 'activa';
        """
        return db.execute_query(query, (id_cliente,))
    else:
        query = """
            SELECT m.*, u.nombres || ' ' || u.apellidos as dueno_nombre
            FROM mascotas m
            JOIN clientes c ON m.id_cliente = c.id_cliente
            JOIN usuarios u ON c.id_usuario = u.id_usuario
            WHERE m.estado = 'activa';
        """
        return db.execute_query(query)

def insert_mascota(id_cliente, nombre, especie, raza, sexo, fecha_nacimiento, peso, color, temperamento, alergias, cuidados, observaciones):
    query = """
        INSERT INTO mascotas (id_cliente, nombre, especie, raza, sexo, fecha_nacimiento, peso, color, temperamento_general, alergias, cuidados_especiales, observaciones, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'activa');
    """
    return db.execute_query(query, (id_cliente, nombre, especie, raza, sexo, fecha_nacimiento, peso, color, temperamento, alergias, cuidados, observaciones), fetch=False)

def update_mascota(id_mascota, nombre, especie, raza, sexo, fecha_nacimiento, peso, color, temperamento, alergias, cuidados, observaciones):
    query = """
        UPDATE mascotas 
        SET nombre = %s, especie = %s, raza = %s, sexo = %s, fecha_nacimiento = %s, peso = %s, color = %s, 
            temperamento_general = %s, alergias = %s, cuidados_especiales = %s, observaciones = %s
        WHERE id_mascota = %s;
    """
    return db.execute_query(query, (nombre, especie, raza, sexo, fecha_nacimiento, peso, color, temperamento, alergias, cuidados, observaciones, id_mascota), fetch=False)

def delete_mascota(id_mascota):
    query = "UPDATE mascotas SET estado = 'inactiva' WHERE id_mascota = %s;"
    return db.execute_query(query, (id_mascota,), fetch=False)

def get_clientes():
    query = """
        SELECT c.id_cliente, u.nombres, u.apellidos, u.correo, u.telefono, c.direccion, u.estado
        FROM clientes c
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        ORDER BY u.apellidos ASC, u.nombres ASC;
    """
    return db.execute_query(query)

def insert_cliente(nombres, apellidos, correo, contrasena, telefono, direccion):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (correo,))
        if cursor.fetchone():
            raise Exception("El correo ya está registrado.")

        cursor.execute("""
            INSERT INTO usuarios (id_rol, nombres, apellidos, correo, contrasena, telefono, estado)
            VALUES (2, %s, %s, %s, %s, %s, 'activo');
        """, (nombres, apellidos, correo, contrasena, telefono))

        cursor.execute("SELECT LASTVAL();")
        id_usuario = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO clientes (id_usuario, direccion)
            VALUES (%s, %s);
        """, (id_usuario, direccion))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_empleados():
    query = """
        SELECT e.id_empleado, u.nombres, u.apellidos, u.correo, u.telefono, e.cargo, e.especialidad, e.fecha_ingreso, u.estado
        FROM empleados e
        JOIN usuarios u ON e.id_usuario = u.id_usuario
        ORDER BY e.id_empleado ASC;
    """
    return db.execute_query(query)

def get_groomers_disponibles(dia_semana):
    # Returns employees who are available on a given day and are not the placeholder pivot (id != 1)
    query = """
        SELECT e.id_empleado, u.nombres || ' ' || u.apellidos as nombre_completo, e.especialidad
        FROM empleados e
        JOIN usuarios u ON e.id_usuario = u.id_usuario
        JOIN disponibilidad_empleado d ON e.id_empleado = d.id_empleado
        WHERE e.id_empleado != 1 
          AND d.dia_semana = %s 
          AND d.estado = 'disponible'
          AND u.estado = 'activo';
    """
    return db.execute_query(query, (dia_semana,))

def insert_empleado(nombres, apellidos, correo, contrasena, telefono, cargo, especialidad, fecha_ingreso):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (correo,))
        if cursor.fetchone():
            raise Exception("El correo ya está registrado.")

        cursor.execute("""
            INSERT INTO usuarios (id_rol, nombres, apellidos, correo, contrasena, telefono, estado)
            VALUES (2, %s, %s, %s, %s, %s, 'activo');
        """, (nombres, apellidos, correo, contrasena, telefono))

        cursor.execute("SELECT LASTVAL();")
        id_usuario = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO empleados (id_usuario, cargo, especialidad, fecha_ingreso)
            VALUES (%s, %s, %s, %s);
        """, (id_usuario, cargo, especialidad, fecha_ingreso))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_servicios():
    query = "SELECT * FROM servicios WHERE estado = 'activo' ORDER BY id_servicio ASC;"
    return db.execute_query(query)

def get_productos():
    query = """
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos_venta p
        JOIN categorias_producto c ON p.id_categoria = c.id_categoria
        WHERE p.estado = 'activo'
        ORDER BY p.nombre ASC;
    """
    return db.execute_query(query)

def get_notificaciones():
    query = """
        SELECT n.*, u.nombres || ' ' || u.apellidos as usuario_nombre
        FROM notificaciones n
        JOIN usuarios u ON n.id_usuario = u.id_usuario
        ORDER BY n.fecha_envio DESC;
    """
    return db.execute_query(query)

def insert_notificacion(id_usuario, tipo, mensaje, estado='pendiente'):
    query = """
        INSERT INTO notificaciones (id_usuario, tipo, mensaje, estado)
        VALUES (%s, %s, %s, %s);
    """
    return db.execute_query(query, (id_usuario, tipo, mensaje, estado), fetch=False)

def get_alertas_automaticas():
    alertas = []
    # 1. Check stock
    query_stock = """
        SELECT nombre, stock, stock_minimo 
        FROM productos_venta 
        WHERE stock <= stock_minimo AND estado = 'activo';
    """
    low_stocks = db.execute_query(query_stock)
    for prod in low_stocks:
        alertas.append({
            "tipo": "Stock Bajo",
            "mensaje": f"El producto '{prod['nombre']}' tiene stock de {prod['stock']} (Mínimo: {prod['stock_minimo']})",
            "urgencia": "alta" if prod['stock'] == 0 else "media"
        })
        
    # 2. Check unassigned appointments (id_empleado = 1 or NULL) for today/tomorrow

    query_unassigned = """
        SELECT c.id_cita, c.fecha, c.hora_inicio, m.nombre as mascota_nombre, s.nombre as servicio_nombre
        FROM citas c
        JOIN mascotas m ON c.id_mascota = m.id_mascota
        JOIN servicios s ON c.id_servicio = s.id_servicio
        WHERE (c.id_empleado = 1 OR c.id_empleado IS NULL)
          AND c.fecha >= CURRENT_DATE
          AND c.estado = 'reservado';
    """
    unassigned = db.execute_query(query_unassigned)
    for cita in unassigned:
        alertas.append({
            "tipo": "Cita sin Groomer Real",
            "mensaje": f"Cita del {cita['fecha']} {cita['hora_inicio']} para la mascota '{cita['mascota_nombre']}' ({cita['servicio_nombre']}) no tiene estilista asignado.",
            "urgencia": "alta"
        })
        
    return alertas
