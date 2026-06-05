import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de la interfaz en Streamlit
st.set_page_config(page_title="Mining Forecast Optimizer", layout="wide")
st.title("🛠️ Optimizador No Lineal de Forecast - Operación Concentradora")
st.markdown("Plataforma de analítica predictiva para la gestión de costos mineros.")

# 2. Carga de datos de manera eficiente
@st.cache_data
def load_data():
    file_path = "Datos Proyecto Mejora  2026.xlsx"
    df = pd.read_excel(file_path, sheet_name='Forecast 5+7', skiprows=1)
    df.columns = df.columns.str.strip()
    df['Gerencia_Clean'] = df['Gerencia'].str.strip()
    df['Desc_Item_Clean'] = df['Desc Item'].str.strip()
    return df

df = load_data()

# Filtrar solo la Gerencia del análisis (Ruta A)
df_conc = df[df['Gerencia_Clean'] == 'Gerencia Operación Concentradora'].copy()

# 3. Sidebar para interactuar y simular escenarios (La "Invención")
st.sidebar.header("Parámetros de Simulación Operacional")
st.sidebar.markdown("Modifica las variables operacionales para calcular la proyección no lineal:")

# Control deslizante para el factor de saturación operacional (Beta)
beta_factor = st.sidebar.slider(
    "Factor de Complejidad Mineral (Exponente β)", 
    min_value=0.8, max_value=2.0, value=1.2, step=0.1,
    help="Valores > 1.0 significan que el mineral viene más complejo, disparando el uso de reactivos de forma no lineal."
)

# 4. Lógica Matemática del Modelo No Lineal Backend
meses_reales = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26']
meses_forecast = ['Jun-26', 'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26']

# Asegurar que los datos sean numéricos
for col in meses_reales + ['Budget FY']:
    df_conc[col] = pd.to_numeric(df_conc[col], errors='coerce').fillna(0)

# Calcular promedio real histórico de los primeros 5 meses
df_conc['Promedio_Real'] = df_conc[meses_reales].mean(axis=1)

# CREAR LA PROYECCIÓN NO LINEAL (Ajuste para los 7 meses de Forecast)
# Aplicamos una función exponencial basada en el promedio real y el factor de complejidad Beta
for i, mes in enumerate(meses_forecast):
    # Inventamos una variación estacional indexada (i) multiplicada por el comportamiento no lineal
    factor_estacional = 1 + (np.sin(i / len(meses_forecast) * np.pi) * 0.15) 
    df_conc[mes] = df_conc['Promedio_Real'] * (factor_estacional ** beta_factor)

# Recalcular métricas finales de control
df_conc['Nuevo_Forecast_7M'] = df_conc[meses_forecast].sum(axis=1)
df_conc['Total_Real_5M'] = df_conc[meses_reales].sum(axis=1)
df_conc['Nuevo_Total_Anual'] = df_conc['Total_Real_5M'] + df_conc['Nuevo_Forecast_7M']
df_conc['Nueva_Desviacion'] = df_conc['Nuevo_Total_Anual'] - df_conc['Budget FY']

# 5. Desplegar los Resultados en la App Web
st.subheader("📊 Resultados de la Optimización de Costos")

# Filtrar para mostrar los ítems clave que analizamos
items_clave = ['Espumante', 'Colector', 'Costo Energia Eléctrica Distribuida', 'Petroleo Diesel']
df_visualizacion = df_conc[df_conc['Desc_Item_Clean'].isin(items_clave)]

st.dataframe(
    df_visualizacion[['Desc_Item_Clean', 'Total_Real_5M', 'Nuevo_Forecast_7M', 'Nuevo_Total_Anual', 'Budget FY', 'Nueva_Desviacion']],
    use_container_width=True
)

st.success("✅ Proyección calculada exitosamente usando ingeniería de datos no lineal.")