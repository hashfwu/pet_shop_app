import streamlit as st
import components.navbar as navbar
import database.queries as queries
import database.connection as db
import pandas as pd
import io

# 1. Enforce Admin only authentication
user = navbar.render_navbar(required_role="ADMIN")

st.title("📊 Reportes y Exportación")
st.markdown("---")

st.subheader("Generación de Reportes Operacionales")
st.markdown(
    """
    Selecciona y descarga reportes detallados en formato CSV para su análisis externo.
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs(["📅 Historial de Citas", "💵 Reporte de Ventas", "📦 Estado de Inventario"])

# Helper to convert df to csv bytes
def to_csv_bytes(dataframe):
    towrite = io.BytesIO()
    dataframe.to_csv(towrite, index=False, encoding='utf-8-sig')
    towrite.seek(0)
    return towrite.read()

# Tab 1: Appointments
with tab1:
    st.markdown("#### Historial Completo de Citas")
    citas_list = queries.get_citas()
    if citas_list:
        df_citas = pd.DataFrame(citas_list)
        st.dataframe(df_citas, use_container_width=True)
        
        csv_data = to_csv_bytes(df_citas)
        st.download_button(
            label="📥 Descargar Reporte de Citas (CSV)",
            data=csv_data,
            file_name="reporte_citas.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay citas registradas para reportar.")

# Tab 2: Sales
with tab2:
    st.markdown("#### Registro de Ventas Realizadas")
    # Fetch raw sales data
    query_sales = """
        SELECT v.id_venta, u.nombres || ' ' || u.apellidos as cliente, v.fecha_venta, v.total, v.estado
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id_cliente
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        ORDER BY v.fecha_venta DESC;
    """
    sales_list = db.execute_query(query_sales)
    if sales_list:
        df_sales = pd.DataFrame(sales_list)
        st.dataframe(df_sales, use_container_width=True)
        
        csv_data = to_csv_bytes(df_sales)
        st.download_button(
            label="📥 Descargar Reporte de Ventas (CSV)",
            data=csv_data,
            file_name="reporte_ventas.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay ventas registradas para reportar.")

# Tab 3: Inventory
with tab3:
    st.markdown("#### Estado de Productos y Alertas de Stock")
    prod_list = queries.get_productos()
    if prod_list:
        df_prods = pd.DataFrame(prod_list)
        st.dataframe(df_prods, use_container_width=True)
        
        csv_data = to_csv_bytes(df_prods)
        st.download_button(
            label="📥 Descargar Reporte de Inventario (CSV)",
            data=csv_data,
            file_name="reporte_inventario.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay productos en el inventario para reportar.")
