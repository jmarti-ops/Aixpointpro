# streamlit_participaciones.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import json
import os

st.title("Reparto de Participaciones y Valoración de Proyecto")

STORAGE_FILE = "session_data.json"

delete_data = st.sidebar.button("🗑️ Release: Borrar todos los datos")
if delete_data and os.path.exists(STORAGE_FILE):
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

        fig, ax = plt.subplots()
        ax.pie(df["% Final Normalizado"], labels=df["Socio"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        df.plot(x="Socio", y=["% Final Bruto", "% Final Normalizado", "Horas"], kind="bar", ax=ax2)
        st.pyplot(fig2)

        # BLOQUE VALORACIÓN PRE-MONEY
        st.header("Estimación de valoración pre-money")
        horas_totales = df["Horas"].sum()
        coste_laboral_total = df["Coste Total"].sum()
        st.write(f"Horas totales aportadas: **{horas_totales}**")
        st.write(f"Coste laboral total: **{coste_laboral_total:,.2f} €**")

        inversion_gastos = st.number_input("Gastos adicionales (infraestructura, IA, etc.) (€)", min_value=0.0, step=500.0, value=5000.0)
        valor_coste = coste_laboral_total + inversion_gastos
        st.write(f"Valoración por costes + gastos: **{valor_coste:,.2f} €**")

        st.subheader("Proyección futura")
        usuarios_pro = st.number_input("Usuarios de pago estimados (12 meses)", min_value=0, step=100, value=1000)
        precio_mensual = st.number_input("Precio mensual por usuario (€)", min_value=0.0, step=1.0, value=10.0)
        margen_neto = st.slider("Margen neto estimado (%)", 0, 100, 40)
        multiplicador_valor = st.slider("Multiplicador de valoración", 1, 10, 2)

        ingresos_anuales = usuarios_pro * precio_mensual * 12
        beneficio_estimado = ingresos_anuales * (margen_neto / 100)
        valor_potencial = beneficio_estimado * multiplicador_valor

        st.write(f"Ingresos anuales: **{ingresos_anuales:,.2f} €**")
        st.write(f"Beneficio neto estimado: **{beneficio_estimado:,.2f} €**")
        st.write(f"Valor futuro proyectado: **{valor_potencial:,.2f} €**")

        valor_final = (valor_coste + valor_potencial) / 2
        st.subheader(f"Valoración pre-money estimada: **{valor_final:,.2f} €**")

        # BLOQUE INVERSOR
        st.header("Cálculo de participación para inversores")
        aportacion = st.number_input("Aportación del inversor (€)", min_value=0.0, step=1000.0, value=0.0)

        if valor_final > 0 and aportacion > 0:
            valor_total_postinversion = valor_final + aportacion
            participacion_inversor = (aportacion / valor_total_postinversion) * 100
            participacion_socios = df["% Final Normalizado"].sum()
            disponible = 100 - participacion_socios

            valor_participacion_inversor = (participacion_inversor / 100) * valor_total_postinversion
            valor_esperado_roi = valor_participacion_inversor - aportacion

            st.write(f"Participación lógica del inversor: **{participacion_inversor:.2f}%**")
            st.write(f"Participación disponible (después de socios): **{disponible:.2f}%**")
            st.write(f"Valor de participación del inversor (post-inversión): **{valor_participacion_inversor:,.2f} €**")
            st.write(f"ROI estimado del inversor: **{valor_esperado_roi:,.2f} €**")

            if participacion_inversor > disponible:
                st.warning("⚠️ La participación del inversor supera el % disponible. Revisa condiciones o renegocia participación de socios.")
            else:
                st.success("✅ Participación del inversor posible dentro del % disponible.")

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Reparto Socios")
            resumen_df = df[["Socio", "% Final Normalizado", "Coste Total", "ROI por Socio (€)"]]
            resumen_df.to_excel(writer, index=False, sheet_name="Resumen ROI")
            premoney_data = pd.DataFrame({
                "Concepto": ["Coste Laboral", "Gastos", "Ingresos", "Beneficio", "Valor Potencial", "Valoración Final"],
                "Valor (€)": [coste_laboral_total, inversion_gastos, ingresos_anuales, beneficio_estimado, valor_potencial, valor_final]
            })
            premoney_data.to_excel(writer, index=False, sheet_name="Pre-money")
            if valor_final > 0 and aportacion > 0:
                inversor_df = pd.DataFrame({
                    "Elemento": ["Aportación", "Valor Negocio", "Post-inversión", "% Inversor", "% Disponible", "Valor Participación", "ROI Estimado"],
                    "Valor": [aportacion, valor_final, valor_total_postinversion, participacion_inversor, disponible, valor_participacion_inversor, valor_esperado_roi]
                })
                inversor_df.to_excel(writer, index=False, sheet_name="Inversor")
        excel_data = excel_buffer.getvalue()

        st.download_button(
            label="📥 Descargar Excel completo",
            data=excel_data,
            file_name="reparto_valoracion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
