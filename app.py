import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de página con estilo profesional
st.set_page_config(
    page_title="Mining Cost Optimizer 2026", 
    page_icon="🛠️", 
    layout="wide"
)

# Estilo CSS personalizado para mejorar la interfaz de usuario (UI)
st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: 700; color: #1E3A8A; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #4B5563; margin-bottom: 25px; }
    .kpi-box { background-color: #F3F4F6; padding: 20px; border-radius: 10px; border-left: 5px solid #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛠️ Sistema de Optimización de Forecast Minero 4.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Plataforma analítica interactiva para la Gerencia de Operación Concentradora</div>', unsafe_allow_html=True)

# 2. Carga optimizada de datos
@st.cache_data
def load_data():
    import os
    archivos = [f for f in os.listdir('.') if 'Datos' in f and f.endswith('.xlsx')]
    if not archivos:
        st.error("🚨 ¡No encontré ningún archivo Excel en el repositorio que empiece con 'Datos'!")
        st.stop()
    
    file_path = archivos[0]
    df = pd.read_excel(file_path, sheet_name='Forecast 5+7', skiprows=1)
    df.columns = df.columns.str.strip()
    df['Gerencia_Clean'] = df['Gerencia'].str.strip()
    df['Desc_Item_Clean'] = df['Desc Item'].str.strip()
    return df

df = load_data()
df_conc = df[df['Gerencia_Clean'] == 'Gerencia Operación Concentradora'].copy()

# Meses de la matriz de datos
meses_reales = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26']
meses_forecast = ['Jun-26', 'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26']

for col in meses_reales + ['Budget FY']:
    df_conc[col] = pd.to_numeric(df_conc[col], errors='coerce').fillna(0)

# 3. Panel de Control Lateral (Sidebar) con más acciones
st.sidebar.header("🎯 Panel de Control Operacional")
st.sidebar.markdown("Modifica las condiciones de la planta para recalcular las proyecciones:")

# Acción 1: Selección del escenario base
escenario = st.sidebar.selectbox(
    "1. Escenario de Producción",
    ["Estándar (Plan Minero)", "Alta Complejidad Metalúrgica", "Optimizado Operacional"]
)

# Definición automática de Beta según el escenario seleccionado
if escenario == "Estándar (Plan Minero)":
    beta_default = 1.1
elif escenario == "Alta Complejidad Metalúrgica":
    beta_default = 1.5
else:
    beta_default = 0.9

# Acción 2: Control fino mediante el Slider
beta_factor = st.sidebar.slider(
    "2. Factor de Complejidad Mineral (β)", 
    min_value=0.7, max_value=2.0, value=beta_default, step=0.05,
    help="Define el exponente de la ley de potencia para reactivos."
)

# Acción 3: Multiplicador de contingencia de energía
ajuste_energia = st.sidebar.slider(
    "3. Factor de Corrección Energética", 
    min_value=1.0, max_value=2.0, value=1.3, step=0.1,
    help="Ajusta el Forecast de energía eléctrica para corregir el déficit del Excel original."
)

# 4. Motor de Cálculo Matemático No Lineal
df_conc['Promedio_Real'] = df_conc[meses_reales].mean(axis=1)

# Aplicación del modelo predictivo a los 7 meses de Forecast
for i, mes in enumerate(meses_forecast):
    factor_estacional = 1 + (np.sin(i / len(meses_forecast) * np.pi) * 0.12)
    
    # Condición especial para Reactivos Químicos Complejos
    mask_reactivos = df_conc['Desc_Item_Clean'].isin(['Espumante', 'Colector'])
    df_conc.loc[mask_reactivos, mes] = df_conc['Promedio_Real'] * (factor_estacional ** beta_factor)
    
    # Condición especial para Energía Eléctrica (Corrección de subestimación)
    mask_energia = df_conc['Desc_Item_Clean'] == 'Costo Energia Eléctrica Distribuida'
    df_conc.loc[mask_energia, mes] = df_conc['Promedio_Real'] * ajuste_energia

# Recalcular métricas consolidadas
df_conc['Total_Real_5M'] = df_conc[meses_reales].sum(axis=1)
df_conc['Nuevo_Forecast_7M'] = df_conc[meses_forecast].sum(axis=1)
df_conc['Nuevo_Total_Anual'] = df_conc['Total_Real_5M'] + df_conc['Nuevo_Forecast_7M']
df_conc['Desviacion_Final'] = df_conc['Nuevo_Total_Anual'] - df_conc['Budget FY']

# 5. Despliegue de Indicadores Clave (KPIs) Visuales
items_clave = ['Espumante', 'Colector', 'Costo Energia Eléctrica Distribuida']
df_resumen = df_conc[df_conc['Desc_Item_Clean'].isin(items_clave)]

total_budget = df_resumen['Budget FY'].sum()
total_nuevo_forecast = df_resumen['Nuevo_Total_Anual'].sum()
balance_global = total_budget - total_nuevo_forecast

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="Presupuesto Base Inicial (USD)", value=f"${total_budget:,.0f}")
with kpi2:
    st.metric(label="Nuevo Forecast Optimizado (USD)", value=f"${total_nuevo_forecast:,.0f}")
with kpi3:
    st.metric(
        label="Balance Financiero (Eficiencia)", 
        value=f"${balance_global:,.0f}", 
        delta=f"{'Ahorro' if balance_global >= 0 else 'Déficit'}"
    )

st.markdown("---")

# 6. Tablas y Alertas Dinámicas de Control (Más Acciones)
st.subheader("📋 Matriz de Costos Optimizada por Modelo Predictivo")

# Formatear la tabla para presentación ejecutiva
df_tabla = df_resumen[['Desc_Item_Clean', 'Total_Real_5M', 'Nuevo_Forecast_7M', 'Nuevo_Total_Anual', 'Budget FY', 'Desviacion_Final']].copy()
df_tabla.columns = ['Ítem de Gasto', 'Real Ejecutado (5M)', 'Forecast Calculado (7M)', 'Proyección Anual', 'Presupuesto Inicial', 'Desviación']

st.dataframe(df_tabla.style.format({
    'Real Ejecutado (5M)': '${:,.0f}',
    'Forecast Calculado (7M)': '${:,.0f}',
    'Proyección Anual': '${:,.0f}',
    'Presupuesto Inicial': '${:,.0f}',
    'Desviación': '${:,.0f}'
}), use_container_width=True)

# Acción Nueva: Alertas Inteligentes automáticas basadas en la desviación
st.subheader("⚠️ Alertas de Control de Gestión")
for index, row in df_tabla.iterrows():
    if row['Desviación'] > 0:
        st.error(f"🔴 **Alerta de Sobrepresupuesto en {row['Ítem de Gasto']}:** La proyección supera al presupuesto inicial por **${row['Desviación']:,.0f}**. Requiere revisión de inventario.")
    else:
        st.success(f"🟢 **Eficiencia Presupuestaria en {row['Ítem de Gasto']}:** Optimización exitosa. Liberación de capital de trabajo por **${abs(row['Desviación']):,.0f}**.")

# Acción Nueva: Botón de Descarga para Auditoría de Datos
st.markdown("### 📥 Descargar Resultados Corporativos")
@st.cache_data
def convert_df(df_to_convert):
    return df_to_convert.to_csv(index=False).encode('utf-8')

csv = convert_df(df_tabla)

st.download_button(
    label="Descargar Informe de Forecast en CSV",
    data=csv,
    file_name='Informe_Forecast_Optimizado_Concentradora.csv',
    mime='text/csv',
)
