import streamlit as st
import components.navbar as navbar
import database.queries as queries
import agents.client as client
import utils.formatters as fmt

# 1. Auth check
user = navbar.render_navbar()

st.title("🛍️ Tienda y Productos")
st.markdown("---")

is_admin = user["rol_nombre"] == "ADMIN"
products = queries.get_productos()

if is_admin:
    # ==========================================
    # ADMIN VIEW (INVENTORY MANAGEMENT)
    # ==========================================
    st.subheader("Control de Inventario")
    
    if products:
        # Highlight products with low stock
        import pandas as pd
        df = pd.DataFrame(products)
        
        # Display warning for low stock
        low_stock_prods = df[df["stock"] <= df["stock_minimo"]]
        if not low_stock_prods.empty:
            st.warning(f"⚠️ Alerta: Hay {len(low_stock_prods)} productos por debajo del stock mínimo.")
            
        for p in products:
            status_color = "#38a169"
            is_low = p["stock"] <= p["stock_minimo"]
            if is_low:
                status_color = "#e53e3e"
                
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: rgba(255,255,255,0.03); padding:16px; border-radius:12px; border-left: 5px solid {status_color}; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                            <b style="font-size:16px;">{p['nombre']}</b>
                            <span style="font-size:11px; color:#cbd5e0; background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:8px;">
                                {p['categoria_nombre']}
                            </span>
                        </div>
                        <div style="font-size:13px; color:#a0aec0; margin-bottom:6px;">
                            {p['descripcion']}
                        </div>
                        <div style="font-size:13px; color:#e2e8f0;">
                            Precio Compra: <b>Bs. {p['precio_compra']:.2f}</b> | Precio Venta: <b>Bs. {p['precio_venta']:.2f}</b>
                        </div>
                        <div style="font-size:14px; margin-top:8px; font-weight:bold; color:{status_color};">
                            Stock Actual: {p['stock']} {p['unidad_medida'] or 'uds'} (Mínimo: {p['stock_minimo']}) 
                            {'- STOCK BAJO ⚠️' if is_low else '✓ Stock OK'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Inline stock adjustment popover
                col_adj, _ = st.columns([2, 8])
                with col_adj:
                    with st.popover("⚙️ Ajustar Stock"):
                        import database.connection as db
                        new_stock = st.number_input("Nuevo Stock", min_value=0, value=p["stock"], step=1, key=f"stock_in_{p['id_producto_venta']}")
                        if st.button("Actualizar Stock", key=f"btn_stock_{p['id_producto_venta']}"):
                            db.execute_query("UPDATE productos_venta SET stock = %s WHERE id_producto_venta = %s;", (new_stock, p["id_producto_venta"]), fetch=False)
                            st.success("Stock actualizado.")
                            st.rerun()
    else:
        st.info("No hay productos registrados en el inventario.")

else:
    # ==========================================
    # USER VIEW (SHOP FRONT & IA RECOMMENDATIONS)
    # ==========================================
    st.subheader("Catálogo de Productos")
    
    # 1. Display IA Textural Description at the top
    st.markdown("### ✨ Recomendaciones de Estilismo para tus Mascotas")
    with st.spinner("Analizando tu perfil y el de tus mascotas..."):
        recom_res = client.obtener_recomendacion_productos(user["id_cliente"], limit=4)
        if recom_res["success"]:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(159, 122, 234, 0.1) 100%); padding: 20px; border-radius: 16px; border: 1px solid rgba(66, 153, 225, 0.2); margin-bottom: 24px; line-height: 1.6; font-size: 14.5px; color:#e2e8f0;">
                    🌟 <b>Sugerencia Textural de nuestro Experto IA:</b><br/>
                    <i>"{recom_res['recomendacion_ia']}"</i>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display products recommended in cards grid
            st.markdown("#### Productos Sugeridos")
            cols = st.columns(2)
            for idx, prod in enumerate(recom_res["productos"]):
                col = cols[idx % 2]
                with col:
                    st.markdown(
                        f"""
                        <div style="background: rgba(255, 255, 255, 0.04); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 12px;">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
                                <b style="font-size:15px; color:#fff;">🛒 {prod['nombre']}</b>
                                <span style="font-size:10px; background:rgba(255,255,255,0.1); color:#cbd5e0; padding:2px 6px; border-radius:6px;">
                                    {prod['categoria_nombre']}
                                </span>
                            </div>
                            <p style="font-size:12px; color:#a0aec0; min-height:40px; margin-bottom:10px;">{prod['descripcion']}</p>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:12px; color:#cbd5e0;">Unidad: {prod['unidad_medida'] or 'unidad'}</span>
                                <b style="font-size:16px; color:#48bb78;">Bs. {prod['precio_venta']:.2f}</b>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("No pudimos conectar con el recomendador en este momento.")
            
    # Show full catalog
    st.markdown("---")
    st.subheader("Todos los Productos")
    if products:
        cols_all = st.columns(3)
        for idx, prod in enumerate(products):
            col = cols_all[idx % 3]
            with col:
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 255, 255, 0.03); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 12px;">
                        <b style="font-size:14px; color:#fff;">{prod['nombre']}</b><br/>
                        <span style="font-size:11px; color:#a0aec0;">{prod['categoria_nombre']}</span><br/>
                        <span style="font-size:14px; color:#48bb78; font-weight:bold; display:block; margin-top:8px;">
                            Bs. {prod['precio_venta']:.2f}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
