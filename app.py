import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de salarios e inflación", layout="wide")
st.title("Simulador de salarios e inflación")
st.caption("IPC nacional INDEC | Últimos 12 meses publicados: noviembre de 2025 a octubre de 2026")

# Variaciones mensuales del nivel general nacional, publicadas por INDEC.
# Octubre de 2025 es el mes anterior al primer aumento incluido.
meses = ["Nov 2025", "Dic 2025", "Ene 2026", "Feb 2026", "Mar 2026", "Abr 2026",
         "May 2026", "Jun 2026", "Jul 2026", "Ago 2026", "Sep 2026", "Oct 2026"]
variaciones = [2.5, 2.8, 2.9, 2.9, 3.4, 2.6, 2.1, 1.9, 2.1, 1.7, 1.9, 2.2]

df = pd.DataFrame({"Mes": meses, "Inflación mensual (%)": variaciones})
factor_acumulado = (1 + df["Inflación mensual (%)"] / 100).cumprod()
df["Inflación acumulada (%)"] = (factor_acumulado - 1) * 100
inflacion = float(factor_acumulado.iloc[-1] - 1)

st.warning("El IPC de noviembre de 2026 aún no está publicado. Se usan noviembre de 2025 a octubre de 2026.")
st.caption("El acumulado es aproximado: se compone a partir de tasas mensuales oficiales redondeadas a un decimal. Para máxima precisión se requieren niveles del índice.")

col1, col2 = st.columns(2)
with col1:
    sueldo = st.number_input("Sueldo inicial ($)", min_value=0.0, value=1000000.0, step=50000.0)
with col2:
    aumento = st.number_input("Aumento nominal del sueldo (%)", min_value=-100.0, max_value=1000.0, value=20.0, step=1.0)

sueldo_final = sueldo * (1 + aumento / 100)
sueldo_necesario = sueldo * (1 + inflacion)
variacion_real = ((1 + aumento / 100) / (1 + inflacion) - 1) * 100

m1, m2, m3 = st.columns(3)
m1.metric("Inflación acumulada aproximada", f"{inflacion*100:.2f}%")
m2.metric("Sueldo final", f"${sueldo_final:,.0f}")
m3.metric("Variación del salario real", f"{variacion_real:.2f}%")
st.write(f"**Sueldo necesario para mantener el poder adquisitivo:** ${sueldo_necesario:,.2f}")
if variacion_real > 0.000001:
    st.success("El salario ganó poder adquisitivo.")
elif variacion_real < -0.000001:
    st.error("El salario perdió poder adquisitivo.")
else:
    st.info("El salario mantuvo aproximadamente su poder adquisitivo.")

t1, t2 = st.tabs(["Inflación mensual", "Inflación acumulada"])
with t1:
    st.bar_chart(df.set_index("Mes")["Inflación mensual (%)"])
with t2:
    st.line_chart(df.set_index("Mes")["Inflación acumulada (%)"])
st.subheader("Datos utilizados")
st.dataframe(df.round(2), hide_index=True, use_container_width=True)
st.caption("Fuente: INDEC, informe IPC octubre 2026: https://www.indec.gob.ar/uploads/informesdeprensa/ipc_11_269335F5BA6B.pdf")
st.caption("Series históricas: https://www.indec.gob.ar/Nivel4/Tema/3/5/31 | Los salarios son valores simulados, no datos salariales oficiales.")


