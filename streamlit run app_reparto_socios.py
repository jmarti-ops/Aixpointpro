import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Reparto de Socios", layout="wide")
st.title("🧮 Calculadora de Participaciones entre Socios")

st.markdown("Esta herramienta permite calcular participaciones con lógica por bloques + % blindado.")

# Pesos configurables
st.sidebar.header("⚙️ Pesos por Bloque")
pesos = {
    "Concepto, Idea e IP Fundacional": st.sidebar.slider("Concepto (%)", 0, 100, 30),
    "Inversión Económica Inicial": st.sidebar.slider("Inversión (%)", 0, 100, 30),
    "Operaciones y Gestión": st.sidebar.slider("Operaciones (%)", 0, 100, 25),
    "Estrategia, Dirección, Marketing": st.sidebar.slider("Estrategia (%)", 0, 100, 15)
}

total_peso = sum(pesos.values())
if total_peso != 100:
    st.sidebar.error(f"La suma de pesos debe ser 100%. Ahora suma: {total_peso}%")

st.subheader("👥 Datos de Socios")
num_socios = st.number_input("Número de socios", min_value=1, max_value=10, value=4)
socios_data = []

for i in range(num_socios):
    nombre = st.text_input(f"Nombre del socio {i+1}", key=f"nombre_{i}")
    bloque_vals = []
    for bloque in pesos:
        val = st.slider(f"{bloque} - {nombre}", 0, 100, 0, key=f"bloque_{bloque}_{i}")
        bloque_vals.append(val)
    blindado = st.number_input(f"% Blindado para {nombre}", min_value=0.0, max_value=100.0, value=0.0, key=f"blindado_{i}")
    socios_data.append([nombre] + bloque_vals + [blindado])

if st.button("📊 Calcular Participaciones"):
    columnas = ["Socio"] + list(pesos.keys()) + ["% Blindado"]
    df = pd.DataFrame(socios_data, columns=columnas)

    # Cálculo técnico
    for b in pesos:
        df[f"{b} (%)"] = (df[b] / 100) * pesos[b]
    df["Participación Técnica"] = df[[f"{b} (%)" for b in pesos]].sum(axis=1)
    df["% Final Bruto"] = df["Participación Técnica"] + df["% Blindado"]
    total = df["% Final Bruto"].sum()
    df["% Final Normalizado"] = df["% Final Bruto"] / total * 100

    st.subheader("📄 Resultados")
    st.dataframe(df[["Socio"] + [f"{b} (%)" for b in pesos] + ["Participación Técnica", "% Blindado", "% Final Bruto", "% Final Normalizado"]])

    # Gráfico
    fig, ax = plt.subplots()
    ax.pie(df["% Final Normalizado"], labels=df["Socio"], autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Descarga CSV
    st.download_button("⬇️ Descargar como CSV", data=df.to_csv(index=False), file_name="reparto_socios.csv", mime="text/csv")
