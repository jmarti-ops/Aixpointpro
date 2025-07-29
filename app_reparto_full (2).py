
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Reparto de Participaciones y Valoración de Proyecto")

st.markdown("Esta herramienta permite calcular participaciones con lógica por bloques, porcentajes blindados, inversores y estimación de valoración del negocio.")

# Pesos configurables
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

    # -------- BLOQUE VALORACIÓN PRE-MONEY --------
    st.header("Estimación de valoración pre-money")

    st.markdown("Introduce tus estimaciones para calcular un valor de referencia de la empresa antes de recibir inversión.")

    horas_trabajadas = st.number_input("Horas dedicadas por el equipo", min_value=0, step=10, value=300)
    coste_hora = st.number_input("Valor estimado por hora (€)", min_value=0.0, step=10.0, value=50.0)
    inversion_gastos = st.number_input("Gastos directos (dominios, herramientas, IA, etc.) (€)", min_value=0.0, step=100.0, value=5000.0)

    valor_coste = (horas_trabajadas * coste_hora) + inversion_gastos
    st.write(f"Valor estimado por coste y tiempo aportado: **{valor_coste:,.2f} €**")

    st.subheader("Proyección futura (opcional)")
    usuarios_pro = st.number_input("Usuarios de pago estimados (a 12 meses)", min_value=0, step=100, value=2000)
    precio_mensual = st.number_input("Precio mensual por usuario (€)", min_value=0.0, step=1.0, value=10.0)
    margen_neto = st.slider("Margen estimado (%)", 0, 100, 40)

    ingresos_anuales = usuarios_pro * precio_mensual * 12
    beneficio_estimado = ingresos_anuales * (margen_neto / 100)
    valor_potencial = beneficio_estimado * 2  # Multiplicador conservador

    st.write(f"Ingresos anuales estimados: {ingresos_anuales:,.2f} €")
    st.write(f"Beneficio estimado: {beneficio_estimado:,.2f} €")
    st.write(f"Valor proyectado por potencial: {valor_potencial:,.2f} €")

    valor_final = (valor_coste + valor_potencial) / 2
    st.subheader(f"Valoración pre-money estimada: **{valor_final:,.2f} €**")

    # -------- BLOQUE INVERSOR --------
    st.header("Cálculo de participación para inversores")

    valor_negocio = valor_final
    aportacion = st.number_input("Aportación del inversor (€)", min_value=0.0, step=1000.0)

    if valor_negocio > 0 and aportacion > 0:
        valor_total_postinversion = valor_negocio + aportacion
        participacion_inversor = (aportacion / valor_total_postinversion) * 100
        participacion_socios = df["% Final Normalizado"].sum()
        disponible = 100 - participacion_socios

        valor_participacion_inversor = (participacion_inversor / 100) * valor_total_postinversion
        valor_esperado_roi = valor_participacion_inversor - aportacion

        st.write(f"Participación lógica del inversor: **{participacion_inversor:.2f}%**")
        st.write(f"Participación disponible (después de socios): **{disponible:.2f}%**")
        st.write(f"Valor de participación del inversor (post-inversión): **{valor_participacion_inversor:,.2f} €**")
        st.write(f"ROI estimado (ganancia teórica): **{valor_esperado_roi:,.2f} €**")

        if participacion_inversor > disponible:
            st.warning("⚠️ La participación del inversor supera el % disponible. Revisa condiciones o renegocia participación de socios.")
        else:
            st.success("✅ Participación del inversor posible dentro del % disponible.")
