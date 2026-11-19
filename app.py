"""Simulador de salarios, inflación y poder adquisitivo (INDEC).
Período de comparación: octubre de 2025 a octubre de 2026.
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Salarios e inflación | INDEC", layout="wide")
st.title("Salarios, inflación y poder adquisitivo")
st.caption("IPC nacional del INDEC · octubre de 2025 a octubre de 2026")

meses = ["Oct 2025", "Nov 2025", "Dic 2025", "Ene 2026", "Feb 2026",
         "Mar 2026", "Abr 2026", "May 2026", "Jun 2026", "Jul 2026",
         "Ago 2026", "Sep 2026", "Oct 2026"]
# Niveles mensuales del IPC nacional (base diciembre de 2016 = 100).
ipc = [9603.8623, 9841.3581, 10121.3715, 10413.0309, 10714.6255,
       11077.0608, 11363.0904, 11607.3937, 11826.4103, 12076.3937,
       12276.7660, 12514.1508, 12785.9321]

def pesos(numero):
    return f"${numero:,.0f}".replace(",", ".")

def porcentaje(numero):
    return f"{numero:+.2f}%".replace(".", ",")

serie = pd.DataFrame({"Mes": meses, "IPC nacional": ipc})
serie["Inflación mensual (%)"] = serie["IPC nacional"].pct_change() * 100
serie["Inflación acumulada (%)"] = (serie["IPC nacional"] / ipc[0] - 1) * 100
inflacion = ipc[-1] / ipc[0] - 1

st.subheader("1. Simulador salarial")
izq, der = st.columns(2)
with izq:
    salario_inicial = st.number_input(
        "Salario mensual en octubre de 2025 ($)",
        min_value=0.0, value=1_000_000.0, step=50_000.0
    )
with der:
    aumento = st.number_input(
        "Aumento salarial acumulado hasta octubre de 2026 (%)",
        min_value=-100.0, max_value=1000.0, value=20.0, step=1.0
    )

salario_final = salario_inicial * (1 + aumento / 100)
salario_equilibrio = salario_inicial * (1 + inflacion)
variacion_real = ((1 + aumento / 100) / (1 + inflacion) - 1) * 100
salario_final_en_pesos_2025 = salario_final / (1 + inflacion)

m1, m2, m3 = st.columns(3)
m1.metric("Inflación acumulada (12 meses)", f"{inflacion * 100:.2f}%".replace(".", ","))
m2.metric("Salario final simulado", pesos(salario_final))
m3.metric("Variación del salario real", porcentaje(variacion_real))

st.write(f"**Salario necesario para mantener el poder adquisitivo:** {pesos(salario_equilibrio)}")
st.write(f"**Salario final expresado en pesos de octubre de 2025:** {pesos(salario_final_en_pesos_2025)}")
if variacion_real > 0.001:
    st.success("El aumento supera a la inflación: el salario gana poder adquisitivo.")
elif variacion_real < -0.001:
    st.error("El aumento no alcanza para compensar la inflación: el salario pierde poder adquisitivo.")
else:
    st.info("El aumento compensa aproximadamente la inflación y mantiene el poder adquisitivo.")

st.subheader("2. Evolución del IPC")
t1, t2, t3 = st.tabs(["Inflación mensual", "Inflación acumulada", "Datos y descarga"])
with t1:
    st.bar_chart(serie.iloc[1:].set_index("Mes")["Inflación mensual (%)"])
    st.caption("Se muestra la variación de cada mes respecto del mes anterior.")
with t2:
    st.line_chart(serie.set_index("Mes")["Inflación acumulada (%)"])
    st.caption("Cambio del IPC desde octubre de 2025; el punto de partida es 0 %.")
with t3:
    st.dataframe(serie.round(2), hide_index=True, use_container_width=True)
    st.download_button(
        "Descargar datos del IPC en CSV",
        data=serie.to_csv(index=False).encode("utf-8-sig"),
        file_name="indec_ipc_oct2025_oct2026.csv",
        mime="text/csv"
    )

st.subheader("3. ¿Qué significa para tu sueldo?")
st.write(
    f"Si en octubre de 2025 cobrabas **{pesos(salario_inicial)}** y recibiste "
    f"un aumento acumulado de **{porcentaje(aumento)}**, en octubre de 2026 "
    f"cobrarías **{pesos(salario_final)}**. Como el IPC aumentó "
    f"**{inflacion * 100:.2f}%** en ese período, tu salario real "
    f"{'aumentaría' if variacion_real > 0 else 'disminuiría' if variacion_real < 0 else 'se mantendría'} "
    f"aproximadamente **{porcentaje(variacion_real)}**."
)
st.caption("Los salarios y aumentos son datos simulados por el usuario, no observaciones salariales del INDEC.")

st.subheader("Fuentes y metodología")
st.markdown("""
- [INDEC: informe del IPC de octubre de 2026](https://www.indec.gob.ar/uploads/informesdeprensa/ipc_11_269335F5BA6B.pdf)
- [INDEC: series históricas del IPC](https://www.indec.gob.ar/Nivel4/Tema/3/5/31)
""")
st.caption(
    "Inflación = (IPC oct. 2026 / IPC oct. 2025 − 1) × 100. "
    "Variación real del salario = ((1 + aumento nominal) / (1 + inflación) − 1) × 100. "
    "El período tiene 13 observaciones mensuales y 12 variaciones entre octubre y octubre."
