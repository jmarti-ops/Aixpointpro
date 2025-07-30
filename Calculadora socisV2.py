# streamlit_participaciones.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import json
import os

st.title("Reparto de Participaciones y Valoración de Proyecto")

STORAGE_FILE = "session_data.json"

if st.sidebar.button("🗑️ Release: Borrar todos los datos"):
    if os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)
    st.experimental_rerun()

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

umbral_disolucion = st.sidebar.slider("Umbral máximo de disolución (%)", 1, 100, value=saved_session.get("umbral_disolucion", 25))

st.subheader("Datos de Socios")
num_socios = st.number_input("Número de socios", min_value=1, max_value=10, value=saved_session.get("num_socios", 4))
socios_data = []
session_state = {
    "pesos": pesos,
    "num_socios": num_socios,
    "socios": [],
    "inversores": saved_session.get("inversores", []),
    "umbral_disolucion": umbral_disolucion
}

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

if st.button("Calcular Participaciones"):
    if any(s[0] == "" for s in socios_data):
        st.error("⚠️ Todos los socios deben tener nombre.")
    else:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(session_state, f, ensure_ascii=False, indent=2)
        st.session_state["mostrar_inversores"] = True

if "mostrar_inversores" in st.session_state and st.session_state["mostrar_inversores"]:
    st.success("✔ Participaciones calculadas. Continúa con valoración y aportes.")

    st.header("Valoración y Aportes del Inversor")
    valoracion = st.number_input("Valoración total del proyecto (€)", min_value=1.0, step=1000.0)
    num_inversores = st.number_input("Número de inversores", min_value=0, max_value=10, value=len(saved_session.get("inversores", [])))

    inversores = []
    for i in range(num_inversores):
        nombre_inv = st.text_input(f"Nombre del inversor {i+1}", value=saved_session.get("inversores", [{}]*num_inversores)[i].get("nombre", ""), key=f"inv_nombre_{i}")
        aporte = st.number_input(f"Aporte de {nombre_inv or 'Inversor '+str(i+1)} (€)", min_value=0.0, step=100.0, value=saved_session.get("inversores", [{}]*num_inversores)[i].get("aporte", 0.0), key=f"inv_aporte_{i}")
        if nombre_inv and aporte > 0:
            participacion = (aporte / valoracion * 100) if valoracion else 0.0
            inversores.append({"nombre": nombre_inv, "aporte": aporte, "participacion": participacion})
        elif nombre_inv or aporte > 0:
            st.warning(f"⚠️ Inversor {i+1} debe tener nombre y aporte mayor a 0")

    total_socios = sum([s[-1] for s in socios_data])
    total_aportes = sum(i["aporte"] for i in inversores)
    total_participacion_inversores = sum(i["participacion"] for i in inversores)
    total_valorado = total_socios + total_aportes

    socios_df = pd.DataFrame(socios_data, columns=["Nombre"] + list(pesos.keys()) + ["Blindado", "Horas", "CosteHora", "CosteTotal"])
    socios_df["Participacion"] = socios_df["CosteTotal"] / total_valorado * (100 - total_participacion_inversores) if total_valorado > 0 else 0.0

    inversores_df = pd.DataFrame(inversores)
    if not inversores_df.empty and all(col in inversores_df.columns for col in ["nombre", "participacion"]):
        inversores_chart = inversores_df[["nombre", "participacion"]].rename(columns={"nombre": "Nombre", "participacion": "Participacion"})
    else:
        inversores_chart = pd.DataFrame(columns=["Nombre", "Participacion"])

    socios_chart = socios_df[["Nombre", "Participacion"]]
    chart_df = pd.concat([socios_chart, inversores_chart], ignore_index=True)

    st.subheader("Distribución de Participaciones")
    st.dataframe(chart_df)

    if chart_df.empty or chart_df["Participacion"].sum() <= 0:
        st.warning("⚠️ No hay datos válidos para graficar. Verifica socios e inversores.")
    elif chart_df["Participacion"].sum() > 100:
        st.error("❌ La suma de participaciones excede el 100%. Revisa aportes o valoración.")
    else:
        fig, ax = plt.subplots()
        ax.pie(chart_df["Participacion"], labels=chart_df["Nombre"], autopct="%1.1f%%")
        ax.axis("equal")
        st.pyplot(fig)

    session_state["inversores"] = inversores
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(session_state, f, ensure_ascii=False, indent=2)
