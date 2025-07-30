# streamlit_participaciones.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import json
import os

st.title("Reparto de Participaciones y Valoración de Proyecto")

STORAGE_FILE = "session_data.json"

# Botón para borrar datos guardados
delete_data = st.sidebar.button("🗑️ Release: Borrar todos los datos")
if delete_data and os.path.exists(STORAGE_FILE):
    os.remove(STORAGE_FILE)
    st.experimental_rerun()

# Cargar sesión anterior si existe
saved_session = {}
if os.path.exists(STORAGE_FILE):
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        saved_session = json.load(f)

st.markdown("Esta herramienta permite calcular participaciones con lógica por bloques, porcentajes blindados, inversores y estimación de valoración del negocio.")

st.sidebar.header("Pesos por Bloque")
pesos = {
    "Concepto, Idea e IP Fundacional": st.sidebar.slider("Concepto (%)", 0, 100, saved_session.get("pesos", {}).get("Concepto, Idea e IP Fundacional", 30)),
    "Inversión Económica Inicial": st.sidebar.slider("Inversión (%)", 0, 100, saved_session.get("pesos", {}).get("Inversión Económica Inicial", 30)),
    "Operaciones y Gestión": st.sidebar.slider("Operaciones (%)", 0, 100, saved_session.get("pesos", {}).get("Operaciones y Gestión", 25)),
    "Estrategia, Dirección, Marketing": st.sidebar.slider("Estrategia (%)", 0, 100, saved_session.get("pesos", {}).get("Estrategia, Dirección, Marketing", 15))
}

st.subheader("Datos de Socios")
num_socios = st.number_input("Número de socios", min_value=1, max_value=10, value=saved_session.get("num_socios", 4))
socios_data = []
session_state = {"pesos": pesos, "num_socios": num_socios, "socios": []}

for i in range(num_socios):
    nombre = st.text_input(f"Nombre del socio {i+1}", value=saved_session.get("socios", [{}]*num_socios)[i].get("nombre", ""), key=f"nombre_{i}")
    bloque_vals = []
    for bloque in pesos:
        val = st.slider(f"{bloque} - {nombre or 'Socio '+str(i+1)}", 0, 100, saved_session.get("socios", [{}]*num_socios)[i].get(bloque, 0), key=f"bloque_{bloque}_{i}")
        bloque_vals.append(val)
    horas_socio = st.number_input(f"Total de horas de {nombre or 'Socio '+str(i+1)}", min_value=0, step=1, value=saved_session.get("socios", [{}]*num_socios)[i].get("horas", 0), key=f"horas_{i}")
    coste_hora_socio = st.number_input(f"Precio por hora de {nombre or 'Socio '+str(i+1)} (€)", min_value=0.0, step=1.0, value=saved_session.get("socios", [{}]*num_socios)[i].get("coste", 0.0), key=f"coste_hora_{i}")
    coste_total_socio = horas_socio * coste_hora_socio
    blindado = st.number_input(f"% Blindado para {nombre or 'Socio '+str(i+1)}", min_value=0.0, max_value=100.0, value=saved_session.get("socios", [{}]*num_socios)[i].get("blindado", 0.0), key=f"blindado_{i}")
    socios_data.append([nombre] + bloque_vals + [blindado, horas_socio, coste_hora_socio, coste_total_socio])

    session_state["socios"].append({
        "nombre": nombre,
        "blindado": blindado,
        "horas": horas_socio,
        "coste": coste_hora_socio,
        **{bloque: bloque_vals[j] for j, bloque in enumerate(pesos)}
    })

# Guardar sesión actual
with open(STORAGE_FILE, "w", encoding="utf-8") as f:
    json.dump(session_state, f)

if st.button("Calcular Participaciones"):
    if any(s[0] == "" for s in socios_data):
        st.error("⚠️ Todos los socios deben tener nombre.")
    else:
        columnas = ["Socio"] + list(pesos.keys()) + ["% Blindado", "Horas", "€/Hora", "Coste Total"]
        df = pd.DataFrame(socios_data, columns=columnas)

        for b in pesos:
            df[f"{b} (%)"] = (df[b] / 100) * pesos[b]
        df["Participación Técnica"] = df[[f"{b} (%)" for b in pesos]].sum(axis=1)
        df["% Final Bruto"] = df["Participación Técnica"] + df["% Blindado"]
        total = df["% Final Bruto"].sum()
        df["% Final Normalizado"] = df["% Final Bruto"] / total * 100 if total > 0 else 0
        df["ROI por Socio (€)"] = (df["% Final Normalizado"] / 100) * df["Coste Total"].sum() - df["Coste Total"]

        df = df.sort_values(by="% Final Normalizado", ascending=False)

        st.subheader("Resultados")
        st.dataframe(df[["Socio"] + [f"{b} (%)" for b in pesos] + ["Participación Técnica", "% Blindado", "% Final Bruto", "% Final Normalizado", "Horas", "€/Hora", "Coste Total", "ROI por Socio (€)"]])

        # Pie chart
        fig, ax = plt.subplots()
        ax.pie(df["% Final Normalizado"], labels=df["Socio"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        # Bar chart
        fig2, ax2 = plt.subplots()
        df.plot(x="Socio", y=["% Final Bruto", "% Final Normalizado", "Horas"], kind="bar", ax=ax2)
        st.pyplot(fig2)

        # Descargar como Excel con múltiples hojas
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Reparto Socios")
            resumen_df = df[["Socio", "% Final Normalizado", "Coste Total", "ROI por Socio (€)"]]
            resumen_df.to_excel(writer, index=False, sheet_name="Resumen ROI")
        excel_data = excel_buffer.getvalue()

        st.download_button(
            label="📥 Descargar Excel completo",
            data=excel_data,
            file_name="reparto_valoracion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
