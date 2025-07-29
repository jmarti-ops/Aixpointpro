import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Reparto Socios e Inversores", layout="wide")
st.title("Reparto de Participaciones entre Socios e Inversores")

# --- Configuración inicial ---
pesos = {"Trabajo": 30, "Capital": 30, "Experiencia": 20, "Red de contactos": 20}

st.sidebar.header("Configuración de Pesos (%)")
for clave in pesos:
    pesos[clave] = st.sidebar.slider(clave, 0, 100, pesos[clave], 1)

# --- Input de socios ---
num_socios = st.number_input("Número de socios", min_value=1, max_value=10, value=3)
socios_data = []

for i in range(num_socios):
    nombre = st.text_input(f"Nombre del socio {i+1}", key=f"nombre_{i}")
    valores = []
    for b in pesos:
        val = st.slider(f"{b} - {nombre}", 0, 100, key=f"bloque_{b}_{i}")
        valores.append(val)
    blindado = st.number_input(f"% Blindado para {nombre}", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key=f"blindado_{i}")
    socios_data.append([nombre] + valores + [blindado])

# --- Input de inversores ---
st.subheader("Datos de Inversores")
num_inversores = st.number_input("Número de inversores", min_value=0, max_value=10, value=1)
inversores_data = []
valor_total_negocio = st.number_input("Valor estimado del negocio (€)", min_value=1000.0, value=100000.0, step=1000.0)

for j in range(num_inversores):
    nombre_inv = st.text_input(f"Nombre del inversor {j+1}", key=f"inversor_{j}")
    inversion = st.number_input(f"Aportación monetaria de {nombre_inv} (€)", min_value=0.0, value=10000.0, step=100.0, key=f"inversion_{j}")
    participacion = (inversion / valor_total_negocio) * 100 if valor_total_negocio else 0.0
    roi_estimado = participacion * 1.5  # simplificación de ROI estimado
    inversores_data.append([nombre_inv, inversion, participacion, roi_estimado])

# --- Botón de cálculo ---
if st.button("📊 Calcular Participaciones Totales"):
    columnas_socios = ["Socio"] + [f"{b} (%)" for b in pesos] + ["% Blindado"]
    df_socios = pd.DataFrame(socios_data, columns=columnas_socios)

    # Cálculo de participación
    for b in pesos:
        df_socios[f"{b} (%)"] = df_socios[f"{b} (%)"] * pesos[b] / 100
    df_socios["Participación Técnica"] = df_socios[[f"{b} (%)" for b in pesos]].sum(axis=1)
    df_socios["% Final Bruto"] = df_socios["Participación Técnica"] + df_socios["% Blindado"]
    total = df_socios["% Final Bruto"].sum()
    df_socios["% Final Normalizado"] = df_socios["% Final Bruto"] / total * 100 if total else 0

    st.subheader("📋 Participación de Socios")
    st.dataframe(df_socios)

    # --- Gráfico ---
    if df_socios["% Final Normalizado"].sum() == 0 or df_socios["% Final Normalizado"].isnull().any():
        st.warning("⚠️ No es posible generar el gráfico: los valores no son válidos o suman 0.")
    else:
        fig, ax = plt.subplots()
        ax.pie(df_socios["% Final Normalizado"], labels=df_socios["Socio"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

    # --- Inversores ---
    if inversores_data:
        df_inversores = pd.DataFrame(inversores_data, columns=["Inversor", "Aportación (€)", "% Participación", "ROI Estimado (%)"])
        st.subheader("💰 Participación de Inversores")
        st.dataframe(df_inversores)

    # --- Exportar ---
    st.download_button("⬇️ Descargar socios como CSV", data=df_socios.to_csv(index=False), file_name="socios.csv")
    if inversores_data:
        st.download_button("⬇️ Descargar inversores como CSV", data=df_inversores.to_csv(index=False), file_name="inversores.csv")
