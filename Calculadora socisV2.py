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

mostrar_inversores = False
if st.button("Calcular Participaciones"):
    if any(s[0] == "" for s in socios_data):
        st.error("⚠️ Todos los socios deben tener nombre.")
    else:
        mostrar_inversores = True

if mostrar_inversores:
    # ... (bloque de cálculo de socios y pre-money igual hasta inversores)

    # ... dentro del loop de inversores, validación extra:
        if aportacion > 0:
            post_money = valor_final + aportacion
            participacion = (aportacion / post_money) * 100
            disponible = 100 - df["% Final Normalizado"].sum()
            if participacion > disponible:
                st.error(f"❌ La participación ({participacion:.2f}%) supera el % disponible: {disponible:.2f}%")
            else:
                valor_part = (participacion / 100) * post_money
                roi_est = valor_part - aportacion
                disolucion = participacion
                if roi_est <= 0:
                    st.warning(f"⚠️ El ROI estimado para {nombre} es bajo o negativo: {roi_est:,.2f} €")
                st.write(f"{nombre or 'Inversor'} participa con: **{participacion:.2f}%**, ROI: **{roi_est:,.2f} €**, Disolución: **{disolucion:.2f}%**")
                inversores.append({"nombre": nombre, "aportacion": aportacion, "participacion": participacion, "roi": roi_est, "disolucion": disolucion})
