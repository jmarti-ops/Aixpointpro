
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Reparto de Participaciones y Valoración del Proyecto")

st.markdown("Esta herramienta permite calcular participaciones por bloques ponderados, incluir porcentajes blindados y valorar la participación de inversores en función de la estimación de valor del negocio.")

# --- BLOQUE 1: PESOS CONFIGURABLES POR BLOQUE ---
st.sidebar.header("Pesos por Bloque")
pesos = {
    "Concepto, Idea e IP Fundacional": st.sidebar.slider("Concepto (%)", 0, 100, 30),
    "Inversión Económica Inicial": st.sidebar.slider("Inversión (%)", 0, 100, 30),
    "Operaciones y Gestión": st.sidebar.slider("Operaciones (%)", 0, 100, 25),
    "Estrategia, Dirección, Marketing": st.sidebar.slider("Estrategia (%)", 0, 100, 15)
}
total_peso = sum(pesos.values())
if total_peso != 100:
    st.sidebar.error(f"La suma de pesos debe ser 100%. Ahora suma: {total_peso}%")

# --- BLOQUE 2: INTRODUCCIÓN DE SOCIOS ---
st.subheader("Datos de Socios")
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

if st.button("Calcular Participaciones"):
    columnas = ["Socio"] + list(pesos.keys()) + ["% Blindado"]
    df = pd.DataFrame(socios_data, columns=columnas)

    for b in pesos:
        df[f"{b} (%)"] = (df[b] / 100) * pesos[b]
    df["Participación Técnica"] = df[[f"{b} (%)" for b in pesos]].sum(axis=1)
    df["% Final Bruto"] = df["Participación Técnica"] + df["% Blindado"]
    total = df["% Final Bruto"].sum()
    df["% Final Normalizado"] = df["% Final Bruto"] / total * 100

    st.subheader("Resultados")
    st.dataframe(df[["Socio"] + [f"{b} (%)" for b in pesos] + ["Participación Técnica", "% Blindado", "% Final Bruto", "% Final Normalizado"]])

    fig, ax = plt.subplots()
    ax.pie(df["% Final Normalizado"], labels=df["Socio"], autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    st.download_button("Descargar como CSV", data=df.to_csv(index=False), file_name="reparto_socios.csv", mime="text/csv")

    # --- BLOQUE 3: VALORACIÓN PRE-MONEY Y PARTICIPACIÓN INVERSORES ---
    st.header("Valoración estimada del negocio")

    horas_trabajadas = st.number_input("Horas totales dedicadas", min_value=0, value=300)
    valor_hora = st.number_input("Valor estimado por hora (€)", min_value=0.0, value=50.0)
    costes_directos = st.number_input("Costes directos (€)", min_value=0.0, value=5000.0)
    margen_proyeccion = st.number_input("Factor de proyección (x valor generado)", min_value=1.0, value=3.0)

    coste_equipo = horas_trabajadas * valor_hora
    valor_estimado = (coste_equipo + costes_directos) * margen_proyeccion

    st.write(f"**Valoración estimada pre-money:** {valor_estimado:,.2f} €")

    st.subheader("Cálculo de participación para inversores")
    aportacion = st.number_input("Aportación prevista del inversor (€)", min_value=0.0, step=1000.0)

    if aportacion > 0:
        participacion_inversor = (aportacion / (valor_estimado + aportacion)) * 100
        participacion_socios = df["% Final Normalizado"].sum()
        disponible = 100 - participacion_socios

        st.write(f"Participación lógica del inversor: **{participacion_inversor:.2f}%**")
        st.write(f"Participación actual de socios: **{participacion_socios:.2f}%**")
        st.write(f"Participación disponible para inversores: **{disponible:.2f}%**")

        if participacion_inversor > disponible:
            st.warning("⚠️ La participación del inversor supera el % disponible. Revisa la valoración o ajusta condiciones.")
        else:
            st.success("✅ Participación del inversor posible dentro del margen disponible.")
