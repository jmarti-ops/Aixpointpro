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
        st.dataframe(df)

        fig, ax = plt.subplots()
        ax.pie(df["% Final Normalizado"], labels=df["Socio"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        st.header("Valoración Pre-Money y Participación de Inversores")

        horas_totales = df["Horas"].sum()
        coste_laboral_total = df["Coste Total"].sum()
        st.write(f"Horas totales aportadas: **{horas_totales}**")
        st.write(f"Coste laboral total: **{coste_laboral_total:,.2f} €**")

        inversion_gastos = st.number_input("Gastos adicionales (€)", min_value=0.0, value=5000.0)
        valor_coste = coste_laboral_total + inversion_gastos

        usuarios_pro = st.number_input("Usuarios pago (12m)", 0, value=1000)
        precio_mensual = st.number_input("Precio mensual (€)", 0.0, value=10.0)
        margen_neto = st.slider("Margen neto (%)", 0, 100, 40)
        multiplicador_valor = st.slider("Multiplicador valoración", 1, 10, 2)

        ingresos_anuales = usuarios_pro * precio_mensual * 12
        beneficio_estimado = ingresos_anuales * (margen_neto / 100)
        valor_potencial = beneficio_estimado * multiplicador_valor
        valor_final = (valor_coste + valor_potencial) / 2

        st.subheader(f"Valoración pre-money estimada: **{valor_final:,.2f} €**")

        st.markdown("### Inversores")
        num_inversores = st.number_input("Cantidad de inversores", min_value=1, max_value=10, value=max(1, len(session_state["inversores"])))
        while len(session_state["inversores"]) < num_inversores:
            session_state["inversores"].append({"nombre": "", "aportacion": 0.0})
        inversores = []
        for i in range(num_inversores):
            col1, col2 = st.columns(2)
            inv_data = session_state["inversores"][i]
            with col1:
                nombre = st.text_input(f"Nombre Inversor {i+1}", value=inv_data.get("nombre", ""), key=f"inversor_nombre_{i}")
            with col2:
                aportacion = st.number_input(f"Aportación € Inversor {i+1}", min_value=0.0, value=inv_data.get("aportacion", 0.0), key=f"aportacion_{i}")
            if aportacion > 0:
                post_money = valor_final + aportacion
                participacion = (aportacion / post_money) * 100
                disponible = 100 - df["% Final Normalizado"].sum()
                valor_part = (participacion / 100) * post_money
                roi_est = valor_part - aportacion
                disolucion = participacion
                st.write(f"{nombre or 'Inversor'} participa con: **{participacion:.2f}%**, ROI: **{roi_est:,.2f} €**, Disolución: **{disolucion:.2f}%**")
                if participacion > disponible:
                    st.warning("⚠️ Supera % disponible de socios")
                inversores.append({"nombre": nombre, "aportacion": aportacion, "participacion": participacion, "roi": roi_est, "disolucion": disolucion})

        total_disolucion = sum([inv["disolucion"] for inv in inversores])
        if total_disolucion > umbral_disolucion:
            st.error(f"⚠️ La disolución total de inversores ({total_disolucion:.2f}%) supera el umbral definido de {umbral_disolucion}%")

        session_state["inversores"] = inversores
        session_state["umbral_disolucion"] = umbral_disolucion
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(session_state, f)

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Reparto Socios")
            resumen = df[["Socio", "% Final Normalizado", "Coste Total", "ROI por Socio (€)"]]
            resumen.to_excel(writer, index=False, sheet_name="Resumen ROI")
            pre_df = pd.DataFrame({"Concepto": ["Costes", "Gastos", "Ingresos", "Beneficio", "Valor Potencial", "Valor Final"], "Valor": [valor_coste, inversion_gastos, ingresos_anuales, beneficio_estimado, valor_potencial, valor_final]})
            pre_df.to_excel(writer, index=False, sheet_name="Pre-money")
            if inversores:
                inv_df = pd.DataFrame(inversores)
                inv_df.to_excel(writer, index=False, sheet_name="Inversores")
        st.download_button("📥 Descargar Excel completo", data=excel_buffer.getvalue(), file_name="reparto_valoracion.xlsx")
