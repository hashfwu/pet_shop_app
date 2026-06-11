import os
import sys
import streamlit as st
import psycopg2
import config


def get_connection():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        sslmode=config.DB_SSL_MODE,
        connect_timeout=3
    )
    return conn


def execute_query(query, params=None, fetch=True):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        if not fetch:
            conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'usuarios');")
        exists = cursor.fetchone()
        if exists and exists[0]:
            conn.close()
            return
    except Exception:
        pass

    schema_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "schema", "01_schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()
        sql_clean = "\n".join([line for line in sql.split(
            "\n") if not line.strip().startswith("\\echo")])
        try:
            cursor.execute(sql_clean)
            conn.commit()
        except Exception as e:
            print(f"Error running PostgreSQL schema: {e}", file=sys.stderr)
            conn.rollback()

    seed_db(conn)
    conn.close()


def seed_db(conn):
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM roles;")
        if cursor.fetchone()[0] > 0:
            return
    except Exception:
        return

    roles = [
        (1, "ADMIN", "Administrador del sistema"),
        (2, "USUARIO", "Cliente o usuario general")
    ]
    for r in roles:
        cursor.execute(
            "INSERT INTO roles (id_rol, nombre, descripcion) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", r)

    usuarios = [
        (1, 1, "Admin", "Spa", "admin@spademascotas.bo",
         "admin", "77777777", "activo"),
        (2, 2, "Juan", "Perez", "juan@gmail.com", "user", "66666666", "activo"),
        (3, 1, "Groomer", "Pivote", "pivote@spademascotas.bo",
         "groomer1", "00000000", "activo"),
        (4, 2, "Carlos", "Groomer", "carlos@spademascotas.bo",
         "carlos", "88888888", "activo"),
        (5, 2, "Ana", "Groomer", "ana@spademascotas.bo", "ana", "99999999", "activo")
    ]
    for u in usuarios:
        cursor.execute(
            "INSERT INTO usuarios (id_usuario, id_rol, nombres, apellidos, correo, contrasena, telefono, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", u)

    clientes = [
        (1, 2, "Av. Principal 123")
    ]
    for c in clientes:
        cursor.execute(
            "INSERT INTO clientes (id_cliente, id_usuario, direccion) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", c)

    empleados = [
        (1, 3, "Pivote", "Groomer de Referencia", "2026-01-01"),
        (2, 4, "Groomer", "Estilista Canino", "2026-02-15"),
        (3, 5, "Groomer", "Especialista Felino", "2026-03-01")
    ]
    for e in empleados:
        cursor.execute(
            "INSERT INTO empleados (id_empleado, id_usuario, cargo, especialidad, fecha_ingreso) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", e)

    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
    id_disp = 1
    for emp_id in [2, 3]:
        for dia in dias:
            disp = (id_disp, emp_id, dia, "08:00:00", "18:00:00", "disponible")
            cursor.execute(
                "INSERT INTO disponibilidad_empleado (id_disponibilidad, id_empleado, dia_semana, hora_inicio, hora_fin, estado) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", disp)
            id_disp += 1

    servicios = [
        (1, "Baño y secado", "Servicio completo de baño con shampoo antiparasitario y secado.",
         60, 80.00, "Todos", "activo"),
        (2, "Corte de pelo", "Corte de cabello según estilo de raza.",
         90, 120.00, "Perros y Gatos", "activo"),
        (3, "Corte de uñas", "Corte y limado protector de uñas.",
         20, 30.00, "Todos", "activo"),
        (4, "Limpieza de oídos", "Limpieza profunda de conducto auditivo externo.",
         20, 25.00, "Todos", "activo"),
        (5, "Tratamientos especiales", "Baño medicado e hidratación cutánea.",
         75, 100.00, "Todos", "activo"),
        (6, "Venta de productos para mascotas",
         "Accesorios, alimentos y juguetes.", 5, 0.00, "Todos", "activo")
    ]
    for s in servicios:
        cursor.execute(
            "INSERT INTO servicios (id_servicio, nombre, descripcion, duracion_minutos, precio, tipo_mascota, estado) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", s)

    categorias = [
        (1, "Alimentos", "Comida seca y snacks"),
        (2, "Higiene", "Shampoos y colonias"),
        (3, "Accesorios", "Collares y juguetes")
    ]
    for cat in categorias:
        cursor.execute(
            "INSERT INTO categorias_producto (id_categoria, nombre, descripcion) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", cat)

    productos = [
        (1, 1, "Croquetas Premium 3kg", "Alimento premium balanceado para perros",
         50.00, 75.00, 15, 5, "Bolsa", "activo"),
        (2, 1, "Snacks Saludables Gato 150g", "Premios de salmón para gatos",
         8.00, 15.00, 3, 5, "Bolsa", "activo"),
        (3, 2, "Shampoo Hipoalergénico 500ml", "Shampoo suave para pieles sensibles",
         20.00, 35.00, 12, 4, "Botella", "activo"),
        (4, 3, "Juguete Hueso Dental", "Mordedor de goma para higiene dental",
         12.00, 22.00, 2, 4, "Unidad", "activo")
    ]
    for p in productos:
        cursor.execute("INSERT INTO productos_venta (id_producto_venta, id_categoria, nombre, descripcion, precio_compra, precio_venta, stock, stock_minimo, unidad_medida, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", p)

    mascotas = [
        (1, 1, "Fido", "Perro", "Golden Retriever", "Macho", "2023-01-10", 28.5,
         "Dorado", "jugueton", "Ninguna", "Ninguno", "Muy amigable", None, "activa"),
        (2, 1, "Michi", "Gato", "Siamés", "Hembra", "2024-03-15", 4.1, "Crema",
         "nervioso", "Lácteos", "Limpieza suave", "Asustadizo", None, "activa")
    ]
    for m in mascotas:
        cursor.execute("INSERT INTO mascotas (id_mascota, id_cliente, nombre, especie, raza, sexo, fecha_nacimiento, peso, color, temperamento_general, alergias, cuidados_especiales, observaciones, foto, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", m)

    from datetime import date, timedelta
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    citas = [
        (1, 1, 1, 2, yesterday, "10:00:00", "11:00:00", 60, 60, 5, "concluido",
         "Estuvo muy tranquilo", "normal", yesterday + " 09:00:00"),
        (2, 2, 2, 2, today, "14:00:00", "15:30:00", 90, None, 10,
         "reservado", "Corte estilo león", "normal", today + " 08:30:00"),
        (3, 1, 1, 1, today, "16:00:00", "17:00:00", 60, None, 0,
         "reservado", "Baño antiparasitario", "normal", today + " 09:15:00")
    ]
    for ct in citas:
        cursor.execute("INSERT INTO citas (id_cita, id_mascota, id_servicio, id_empleado, fecha, hora_inicio, hora_fin, duracion_estimada_minutos, duracion_real_minutos, tiempo_estimado_llegada_minutos, estado, observaciones, tipo_cita, fecha_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", ct)

    calificaciones = [
        (1, 1, 5, "Fido quedó precioso, excelente atención.",
         yesterday + " 11:30:00")
    ]
    for cal in calificaciones:
        cursor.execute(
            "INSERT INTO calificaciones (id_calificacion, id_cita, puntuacion, comentario, fecha_calificacion) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", cal)

    ventas = [
        (1, 1, 1, yesterday + " 11:00:00", 80.00, "pagada")
    ]
    for v in ventas:
        cursor.execute(
            "INSERT INTO ventas (id_venta, id_cliente, id_cita, fecha_venta, total, estado) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", v)

    detalle_ventas = [
        (1, 1, None, 1, 1, 80.00, 80.00)
    ]
    for dv in detalle_ventas:
        cursor.execute("INSERT INTO detalle_ventas (id_detalle_venta, id_venta, id_producto_venta, id_servicio, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", dv)

    metodos = [
        (1, "Efectivo", "Pago físico"),
        (2, "QR / Transferencia", "Pago digital rápido"),
        (3, "Tarjeta", "Débito o crédito")
    ]
    for m in metodos:
        cursor.execute(
            "INSERT INTO metodos_pago (id_metodo_pago, nombre, descripcion) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", m)

    pagos = [
        (1, 1, 1, 80.00, yesterday + " 11:05:00", "confirmado", "REF-YEST-99")
    ]
    for p in pagos:
        cursor.execute(
            "INSERT INTO pagos (id_pago, id_venta, id_metodo_pago, monto, fecha_pago, estado, referencia) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", p)

    notifs = [
        (1, 1, "Telegram Bot", "Cliente Juan Perez consultó servicios disponibles",
         yesterday + " 08:30:00", "enviada"),
        (2, 1, "Telegram Bot", "Bot registró a Fido (Perro) para Juan Perez",
         yesterday + " 08:35:00", "enviada"),
        (3, 1, "Alerta Negocio", "Producto 'Snacks Saludables Gato' está por debajo del stock mínimo.",
         today + " 07:05:00", "pendiente")
    ]
    for nt in notifs:
        cursor.execute(
            "INSERT INTO notificaciones (id_notificacion, id_usuario, tipo, mensaje, fecha_envio, estado) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", nt)

    conn.commit()
