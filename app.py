import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard de Apuestas Deportivas",
    page_icon="⚽",
    layout="wide"
)

# ==========================================
# 1. GENERACIÓN DE DATOS SINTÉTICOS
# ==========================================
@st.cache_data
def cargar_datos_sinteticos(n_registros=500):
    np.random.seed(42)
    
    deportes = ['Fútbol', 'Baloncesto', 'Tenis', 'Béisbol', 'E-Sports']
    casas_apuesta = ['Bet365', 'Betplay', 'Codere', 'Rushbet', 'Bwin']
    tipos_apuesta = ['Ganador Local', 'Empate', 'Ganador Visitante', 'Más/Menos Puntos', 'Hándicap']
    estados = ['Ganada', 'Perdida', 'Pendiente']

    fechas = pd.date_range(start="2024-01-01", periods=n_registros, freq="D")
    
    data = {
        'ID_Apuesta': [f"APT-{1000+i}" for i in range(n_registros)],
        'Fecha': np.random.choice(fechas, size=n_registros),
        'Deporte': np.random.choice(deportes, size=n_registros, p=[0.4, 0.25, 0.15, 0.1, 0.1]),
        'Casa_Apuestas': np.random.choice(casas_apuesta, size=n_registros),
        'Tipo_Apuesta': np.random.choice(tipos_apuesta, size=n_registros),
        'Monto_Apostado': np.round(np.random.exponential(scale=50, size=n_registros) + 5, 2), # Montos entre $5 y más
        'Cuota': np.round(np.random.uniform(1.2, 5.0, size=n_registros), 2),
        'Estado': np.random.choice(estados, size=n_registros, p=[0.45, 0.45, 0.10])
    }
    
    df = pd.DataFrame(data)
    
    # Calcular ganancia/pérdida neta hipotética
    def calcular_retorno(row):
        if row['Estado'] == 'Ganada':
            return np.round((row['Monto_Apostado'] * row['Cuota']) - row['Monto_Apostado'], 2)
        elif row['Estado'] == 'Perdida':
            return -row['Monto_Apostado']
        else:
            return 0.0

    df['Ganancia_Neta'] = df.apply(calcular_retorno, axis=1)
    return df

df_raw = cargar_datos_sinteticos()

# ==========================================
# 3. INTERACCIÓN DEL USUARIO (FILTROS)
# ==========================================
st.sidebar.header("🎯 Filtros de Interacción")

# Filtro por Deporte
deportes_unicos = list(df_raw['Deporte'].unique())
deportes_sel = st.sidebar.multiselect("Seleccionar Deporte(s):", deportes_unicos, default=deportes_unicos)

# Filtro por Casa de Apuestas
casas_unicas = list(df_raw['Casa_Apuestas'].unique())
casas_sel = st.sidebar.multiselect("Seleccionar Casa de Apuestas:", casas_unicas, default=casas_unicas)

# Filtro por Rango de Cuotas
min_cuota, max_cuota = float(df_raw['Cuota'].min()), float(df_raw['Cuota'].max())
rango_cuota = st.sidebar.slider("Rango de Cuota:", min_cuota, max_cuota, (min_cuota, max_cuota))

# Aplicar filtros
df_filtrado = df_raw[
    (df_raw['Deporte'].isin(deportes_sel)) &
    (df_raw['Casa_Apuestas'].isin(casas_sel)) &
    (df_raw['Cuota'] >= rango_cuota[0]) &
    (df_raw['Cuota'] <= rango_cuota[1])
]

# ==========================================
# ENCABEZADO Y KPI
# ==========================================
st.title("⚽ Dashboard y EDA de Apuestas Deportivas")
st.markdown("Plataforma interactiva para el análisis de rendimiento y estadísticas de apuestas.")

st.subheader("📌 Métricas Principales (KPIs)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_apostado = df_filtrado['Monto_Apostado'].sum()
balance_total = df_filtrado['Ganancia_Neta'].sum()
total_apuestas = len(df_filtrado)
win_rate = (len(df_filtrado[df_filtrado['Estado']=='Ganada']) / total_apuestas * 100) if total_apuestas > 0 else 0

kpi1.metric("Total Apuestas", f"{total_apuestas}")
kpi2.metric("Monto Apostado", f"${total_apostado:,.2f}")
kpi3.metric("Balance / Ganancia Neta", f"${balance_total:,.2f}", delta=f"{balance_total:,.2f}")
kpi4.metric("Tasa de Acierto (Win Rate)", f"{win_rate:.1f}%")

st.markdown("---")

# ==========================================
# 2. ANÁLISIS EXPLORATORIO DE DATOS (EDA)
# ==========================================
tab_cuanti, tab_cuali, tab_graficos, tab_tabla = st.tabs([
    "📊 Análisis Cuantitativo", 
    "🏷️ Análisis Cualitativo", 
    "📈 EDA Gráfico", 
    "📄 Vista de Datos"
])

# --- TAB 1: CUANTITATIVO ---
with tab_cuanti:
    st.header("Análisis Cuantitativo")
    st.write("Estadísticas descriptivas de las variables numéricas:")
    
    # Resumen numérico
    num_cols = ['Monto_Apostado', 'Cuota', 'Ganancia_Neta']
    st.dataframe(df_filtrado[num_cols].describe().T)

# --- TAB 2: CUALITATIVO ---
with tab_cuali:
    st.header("Análisis Cualitativo")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución por Estado de Apuesta")
        st.dataframe(df_filtrado['Estado'].value_counts().reset_index())
        
        st.subheader("Distribución por Deporte")
        st.dataframe(df_filtrado['Deporte'].value_counts().reset_index())

    with col2:
        st.subheader("Distribución por Casa de Apuestas")
        st.dataframe(df_filtrado['Casa_Apuestas'].value_counts().reset_index())

# --- TAB 3: GRÁFICOS INTERACTIVOS ---
with tab_graficos:
    st.header("EDA Gráfico")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Gráfico de barras: Ganancia por Deporte
        fig_deporte = px.bar(
            df_filtrado, 
            x='Deporte', 
            y='Ganancia_Neta', 
            color='Estado',
            title="Ganancia/Pérdida Neta por Deporte",
            barmode='group'
        )
        st.plotly_chart(fig_deporte, use_container_width=True)

        # Histograma de Cuotas
        fig_hist = px.histogram(
            df_filtrado, 
            x='Cuota', 
            nbins=20, 
            title="Distribución de las Cuotas Apostadas",
            color_discrete_sequence=['#3366cc']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_g2:
        # Pie Chart: Porcentaje de apuestas por Casa
        fig_pie = px.pie(
            df_filtrado, 
            names='Casa_Apuestas', 
            title="Proporción de Apuestas por Casa de Apuestas",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Scatter plot: Monto vs Cuota
        fig_scatter = px.scatter(
            df_filtrado, 
            x='Cuota', 
            y='Monto_Apostado', 
            color='Estado',
            title="Relación Cuota vs. Monto Apostado",
            size='Monto_Apostado'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# --- TAB 4: VER Y DESCARGAR DATOS ---
with tab_tabla:
    st.header("Explorador de Datos Filtrados")
    st.dataframe(df_filtrado)
    
    # Botón para descargar los datos filtrados en CSV
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Datos Filtrados como CSV",
        data=csv,
        file_name='apuestas_deportivas_filtrado.csv',
        mime='text/csv'
    )
