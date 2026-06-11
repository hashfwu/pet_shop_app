import streamlit as st
import pandas as pd
import plotly.express as px

def render_appointments_by_hour(citas):
    """Renders a Plotly bar chart showing the distribution of appointments by hour for the day."""
    if not citas:
        st.info("No hay citas programadas hoy para graficar.")
        return
        
    # Create DataFrame
    df = pd.DataFrame(citas)
    
    # Ensure we have date and hour fields
    if "hora_inicio" not in df.columns:
        st.info("Datos de citas incompletos para graficar.")
        return
        
    # Extract hour
    df['hora'] = df['hora_inicio'].apply(lambda x: str(x).split(':')[0] + ":00")
    
    # Group by hour
    grouped = df.groupby('hora').size().reset_index(name='Cantidad')
    
    fig = px.bar(
        grouped, 
        x='hora', 
        y='Cantidad',
        labels={'hora': 'Hora de Inicio', 'Cantidad': 'Número de Citas'},
        title='Distribución de Citas por Hora (Hoy)',
        color_discrete_sequence=['#4299e1']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_earnings_chart(ventas):
    """Renders a line/bar chart of earnings over time."""
    if not ventas:
        st.info("No hay ventas registradas para graficar.")
        return
        
    df = pd.DataFrame(ventas)
    
    # Check fields
    if "fecha_venta" not in df.columns or "total" not in df.columns:
        return
        
    # Group by day
    df['fecha'] = pd.to_datetime(df['fecha_venta']).dt.strftime('%d/%m/%Y')
    grouped = df.groupby('fecha')['total'].sum().reset_index()
    
    fig = px.line(
        grouped, 
        x='fecha', 
        y='total',
        labels={'fecha': 'Fecha', 'total': 'Ingresos (Bs.)'},
        title='Desempeño de Ingresos (Histórico)',
        markers=True,
        color_discrete_sequence=['#48bb78']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    
    st.plotly_chart(fig, use_container_width=True)
