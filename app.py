import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as _go

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA STREAMLIT
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
def generar_datos_sinteticos(n_registros=1000):
    np.random.seed(42)
    
    deportes = ['Fútbol', 'Baloncesto', 'Tenis', 'Béisbol', 'MMA']
    casas_apuesta = ['Bet365', 'Codere', 'Bwin', 'Betsson', '1xBet']
    tipos_apuesta = ['Ganador Local', 'Ganador Visitante', 'Empate', 'Más/Menos Goles', 'Hándicap']
    estados = ['Ganada', 'Perdida', 'Pendiente']
    
    fechas = pd.date_range(start='2023-01-01', periods=n_registros, freq='H')
    
    data = {
        'ID_Apuesta': [f"APT-{1000 + i}" for i in range(n_registros)],
        'Fecha': np.random.choice(fechas, n_registros),
        'Deporte': np.random.choice(deportes, n_registros, p=[0.4, 0.25, 0.15, 0.1, 0.1]),
        'Casa_Apuesta': np.random.choice(casas_apuesta, n_registros),
        'Tipo_Apuesta': np.random.choice(tipos_apuesta, n_registros),
        'Monto_Apostado': np.round(np.random.exponential(scale=50, size=n_registros) + 5, 2),
        'Cuota': np.round(np.random.uniform(1.2, 5.0, size=n_registros), 2),
        'Estado': np.random.choice(estados, n_registros, p=[0.45, 0.50, 0.05])
    }
    
    df = pd.DataFrame(data)
    
    # Calcular ganancia/pérdida
    def calcular_ganancia(row):
        if row['Estado'] == 'Ganada':
            return np.round((row['Monto_Apostado'] * row['Cuota']) - row['Monto_Apostado'], 2)
        elif row['Estado'] == 'Perdida':
            return -row['Monto_Apostado']
        else:
            return 0.0
            
    df['Ganancia_Neta'] = df.apply(calcular_ganancia, axis=1)
    return df

# Cargar datos
df_raw = generar_datos_sinteticos()

# ==========================================
# 3. INTERACCIÓN DEL USUARIO (BARRA LATERAL)
# ==========================================
st.sidebar.title("🎛️ Filtros de Interacción")

# Filtro por Deporte
deportes_seleccionados = st.sidebar.multiselect(
    "Selecciona Deportes:",
    options=df_raw['Deporte'].unique(),
    default=df_raw['Deporte'].unique()
)

# Filtro por Casa de Apuestas
casas_seleccionadas = st.sidebar.multiselect(
    "Selecciona Casas de Apuestas:",
    options=df_raw['Casa_Apuesta'].unique(),
    default=df_raw['Casa_Apuesta'].unique()
)

# Filtro por Rango de Monto Apostado
monto_min, monto_max = float(df_raw['Monto_Apostado'].min()), float(df_raw['Monto_Apostado'].max())
rango_monto = st.sidebar.slider(
    "Rango de Monto Apostado ($):",
    min_value=monto_min,
    max_value=monto_max,
    value=(monto_min, monto_max)
)

# Aplicar Filtros al DataFrame
df_filtrado = df_raw[
    (df_raw['Deporte'].isin(deportes_seleccionados)) &
    (df_raw['Casa_Apuesta'].isin(casas_seleccionadas)) &
    (df_raw['Monto_Apostado'].between(rango_monto[0], rango_monto[1]))
]

# ==========================================
# VISTA PRINCIPAL DE LA APLICACIÓN
# ==========================================
st.title("📊 Dashboard EDA - Apuestas Deportivas")
st.markdown("Análisis exploratorio interactivo sobre un conjunto de datos sintéticos de apuestas.")

# Pestañas de Navegación
tab1, tab2, tab3, tab4 = st.tabs(["📁 Vista Previa y Filtros", "🔤 EDA Cualitativo", "🔢 EDA Cuantitativo", "📈 EDA Gráfico"])

# ------------------------------------------
# TAB 1: DATOS Y RESUMEN GENERAL
# ------------------------------------------
with tab1:
    st.subheader("Datos Filtrados")
    st.markdown(f"Mostrando **{len(df_filtrado)}** de **{len(df_raw)}** registros.")
    
    # KPIs rápidos
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Apostado", f"${df_filtrado['Monto_Apostado'].sum():,.2f}")
    col2.metric("Ganancia/Pérdida Neta", f"${df_filtrado['Ganancia_Neta'].sum():,.2f}")
    col3.metric("Cuota Promedio", f"{df_filtrado['Cuota'].mean():.2f}")
    
    win_rate = (len(df_filtrado[df_filtrado['Estado'] == 'Ganada']) / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
    col4.metric("% Apuestas Ganadas", f"{win_rate:.1f}%")
    
    st.dataframe(df_filtrado, use_container_width=True)

# ------------------------------------------
# TAB 2: EDA CUALITATIVO
# ------------------------------------------
with tab2:
    st.subheader("Análisis Cualitativo (Variables Categóricas)")
    
    col_cat1, col_cat2 = st.columns(2)
    
    with col_cat1:
        st.write("### Frecuencia por Deporte")
        freq_deporte = df_filtrado['Deporte'].value_counts().reset_index()
        freq_deporte.columns = ['Deporte', 'Frecuencia']
        st.dataframe(freq_deporte, use_container_width=True)
        
        st.write("### Frecuencia por Estado de Apuesta")
        freq_estado = df_filtrado['Estado'].value_counts().reset_index()
        freq_estado.columns = ['Estado', 'Frecuencia']
        st.dataframe(freq_estado, use_container_width=True)

    with col_cat2:
        st.write("### Frecuencia por Casa de Apuesta")
        freq_casa = df_filtrado['Casa_Apuesta'].value_counts().reset_index()
        freq_casa.columns = ['Casa de Apuesta', 'Frecuencia']
        st.dataframe(freq_casa, use_container_width=True)

        st.write("### Frecuencia por Tipo de Apuesta")
        freq_tipo = df_filtrado['Tipo_Apuesta'].value_counts().reset_index()
        freq_tipo.columns = ['Tipo de Apuesta', 'Frecuencia']
        st.dataframe(freq_tipo, use_container_width=True)

# ------------------------------------------
# TAB 3: EDA CUANTITATIVO
# ------------------------------------------
with tab3:
    st.subheader("Análisis Cuantitativo (Variables Numéricas)")
    
    st.write("### Estadísticas Descriptivas Generales")
    num_cols = ['Monto_Apostado', 'Cuota', 'Ganancia_Neta']
    st.dataframe(df_filtrado[num_cols].describe().T, use_container_width=True)
    
    st.write("### Ganancia Neta por Deporte y Casa de Apuesta")
    pivot_ganancia = df_filtrado.pivot_table(
        index='Deporte', 
        columns='Casa_Apuesta', 
        values='Ganancia_Neta', 
        aggfunc='sum', 
        fill_value=0
    )
    st.dataframe(pivot_ganancia, use_container_width=True)

# ------------------------------------------
# TAB 4: EDA GRÁFICO
# ------------------------------------------
with tab4:
    st.subheader("Visualización Gráfica Interactiva")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Gráfico de Barras: Distribución por Deporte
        fig_bar = px.bar(
            df_filtrado, 
            x='Deporte', 
            color='Estado', 
            title="Distribución de Apuestas por Deporte y Estado",
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Histogram de Montos Apostados
        fig_hist = px.histogram(
            df_filtrado, 
            x='Monto_Apostado', 
            nbins=30, 
            title="Distribución del Monto Apostado",
            color_discrete_sequence=['#636EFA']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_g2:
        # Gráfico de Dispersión: Cuota vs Monto Apostado
        fig_scatter = px.scatter(
            df_filtrado, 
            x='Cuota', 
            y='Ganancia_Neta', 
            color='Estado',
            hover_data=['ID_Apuesta', 'Deporte'],
            title="Relación Cuota vs Ganancia Neta"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Gráfico Torta: Proporción por Casa de Apuesta
        fig_pie = px.pie(
            df_filtrado, 
            names='Casa_Apuesta', 
            title="Proporción de Apuestas por Casa de Apuesta",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
