"""Simulador didáctico de IPC, salarios y canastas básicas del INDEC.
Datos: IPC nacional y CBA/CBT Gran Buenos Aires, octubre 2025–octubre 2026.
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Salarios, inflación y canasta básica | INDEC", layout="wide")
st.title("Salarios, inflación y canasta básica")
st.caption("INDEC · octubre de 2025 a octubre de 2026 · 12 meses de variación")

MESES = ["Oct 2025", "Nov 2025", "Dic 2025", "Ene 2026", "Feb 2026",
         "Mar 2026", "Abr 2026", "May 2026", "Jun 2026", "Jul 2026",
         "Ago 2026", "Sep 2026", "Oct 2026"]
# IPC nacional, base diciembre de 2016 = 100.
IPC = [9603.8623, 9841.3581, 10121.3715, 10413.0309, 10714.6255,
       11077.0608, 11363.0904, 11607.3937, 11826.4103, 12076.3937,
       12276.7660, 12514.1508, 12785.9321]
# Valores oficiales del adulto equivalente del Gran Buenos Aires (pesos/mes).
# Informe INDEC canastas octubre 2026, cuadros 1 y 2.
CBA = [176150.29, 183289.46, 190780.09, 201938.62, 208442.85,
       212948.52, 215227.62, 220467.99, 223253.29, 229131.47,
       235103.36, 239058.22, 246362.93]
CBT = [392815.15, 406902.60, 423531.80, 440226.19, 452320.98,
       464227.77, 475653.04, 485029.58, 495622.30, 506380.55,
       519578.43, 528318.67, 546925.70]

# Los multiplicadores corresponden a los ejemplos de hogares publicados por INDEC.
HOGARES = {
    "1 adulto equivalente (referencia estadística)": 1.00,
    "Hogar de 3 personas (ejemplo INDEC)": 2.46,
    "Hogar de 4 personas (ejemplo INDEC)": 3.09,
    "Hogar de 5 personas (ejemplo INDEC)": 3.25,
}

def pesos(valor):
    return f"${valor:,.0f}".replace(",", ".")

def porcentaje(valor):
    return f"{valor:+.2f}%".replace(".", ",")

def veces(valor):
    return f"{valor:.2f}".replace(".", ",")

base = pd.DataFrame({"Mes": MESES, "IPC nacional": IPC,
                     "CBA adulto equivalente ($)": CBA,
                     "CBT adulto equivalente ($)": CBT})
base["Inflación mensual (%)"] = base["IPC nacional"].pct_change() * 100
base["Inflación desde oct. 2025 (%)"] = (base["IPC nacional"] / base["IPC nacional"].iloc[0] - 1) * 100
inflacion = IPC[-1] / IPC[0] - 1

st.subheader("1. Simulá tu salario")
a, b = st.columns(2)
with a:
    sueldo_inicial = st.number_input("Tu salario mensual en octubre de 2025 ($)",
                                    min_value=0.0, value=1_000_000.0, step=50_000.0)
with b:
    aumento = st.number_input("Aumento nominal acumulado hasta octubre de 2026 (%)",
                              min_value=-100.0, max_value=1000.0, value=20.0, step=1.0)
sueldo_final = sueldo_inicial * (1 + aumento / 100)
sueldo_necesario_ipc = sueldo_inicial * (1 + inflacion)
variacion_real = ((1 + aumento / 100) / (1 + inflacion) - 1) * 100
c1, c2, c3 = st.columns(3)
c1.metric("Inflación nacional oct. a oct.", f"{inflacion * 100:.2f}%")
c2.metric("Tu salario simulado en oct. 2026", pesos(sueldo_final))
c3.metric("Variación real del salario (IPC)", porcentaje(variacion_real))
st.write(f"**Salario necesario para conservar el poder de compra según IPC:** {pesos(sueldo_necesario_ipc)}")
if variacion_real > 0.001:
    st.success("El salario ganó poder adquisitivo medido con el IPC general.")
elif variacion_real < -0.001:
    st.error("El salario perdió poder adquisitivo medido con el IPC general.")
else:
    st.info("El salario mantuvo aproximadamente su poder adquisitivo medido con el IPC.")

st.subheader("2. ¿Cuánto cambió la canasta básica?")
st.write("Las canastas del INDEC tienen **valores propios**: no se calcula su costo aplicando el IPC general. "
         "La **CBA** comprende alimentos básicos; la **CBT** incluye además bienes y servicios no alimentarios. "
         "Estas series corresponden al **Gran Buenos Aires**, mientras que el IPC anterior es **nacional**.")
hogar = st.selectbox("Elegí la composición de hogar para comparar", list(HOGARES), index=2)
coef = HOGARES[hogar]
tipo = st.radio("Canasta para analizar", ["Canasta básica total (CBT)", "Canasta básica alimentaria (CBA)"], horizontal=True)
col_serie = "CBT adulto equivalente ($)" if "CBT" in tipo else "CBA adulto equivalente ($)"
valor_antes = float(base[col_serie].iloc[0]) * coef
valor_ahora = float(base[col_serie].iloc[-1]) * coef
crecimiento_canasta = (valor_ahora / valor_antes - 1) * 100

m1, m2, m3 = st.columns(3)
m1.metric("Costo en octubre de 2025", pesos(valor_antes))
m2.metric("Costo en octubre de 2026", pesos(valor_ahora))
m3.metric("Aumento de la canasta", porcentaje(crecimiento_canasta))

# Poder de compra en unidades de canasta: salario mensual / valor mensual de la canasta.
canastas_antes = sueldo_inicial / valor_antes
canastas_ahora = sueldo_final / valor_ahora
cobertura_antes = canastas_antes * 100
cobertura_ahora = canastas_ahora * 100
cambio_capacidad = ((canastas_ahora / canastas_antes) - 1) * 100 if canastas_antes > 0 else None
faltante = sueldo_final - valor_ahora

st.subheader("3. ¿Qué podés comprar con tu salario?")
st.caption("Cada 'canasta' equivale al costo mensual de la CBA o CBT para el hogar elegido. No representa unidades de un producto individual.")
n1, n2, n3 = st.columns(3)
n1.metric("Canastas cubiertas con salario de 2025", f"{veces(canastas_antes)} canastas")
n2.metric("Canastas cubiertas con salario de 2026", f"{veces(canastas_ahora)} canastas")
n3.metric("Cambio de capacidad de compra", "No calculable" if cambio_capacidad is None else porcentaje(cambio_capacidad))
st.write(f"En octubre de 2025 tu sueldo cubría **{veces(cobertura_antes)}%** de la canasta elegida; "
         f"en octubre de 2026 cubriría **{veces(cobertura_ahora)}%**.")
if faltante >= 0:
    st.success(f"Con el salario final simulado podés cubrir una canasta mensual y te sobrarían {pesos(faltante)}.")
else:
    st.warning(f"Con el salario final simulado te faltarían {pesos(abs(faltante))} para cubrir una canasta mensual.")
st.info("Esta comparación toma el **salario ingresado como único ingreso**. Para evaluar si un hogar supera "
        "las líneas oficiales de pobreza o indigencia deberían considerarse **todos los ingresos del hogar** "
        "y su composición real. Los valores ingresados son simulaciones, no salarios observados por INDEC.")

# Visualización mensual de las canastas para el hogar elegido.
grafico = base[["Mes", "CBA adulto equivalente ($)", "CBT adulto equivalente ($)"]].copy()
grafico["CBA ($)"] = grafico["CBA adulto equivalente ($)"] * coef
grafico["CBT ($)"] = grafico["CBT adulto equivalente ($)"] * coef
st.subheader("4. Evolución mensual de los precios")
t1, t2, t3, t4 = st.tabs(["Canastas básicas", "Capacidad de compra", "Inflación nacional", "Tabla y descarga"])
with t1:
    st.line_chart(grafico.set_index("Mes")[["CBA ($)", "CBT ($)"]])
with t2:
    comparacion = pd.DataFrame({
        "Mes": ["Oct 2025", "Oct 2026"],
        "Salario mensual ($)": [sueldo_inicial, sueldo_final],
        "Costo canasta ($)": [valor_antes, valor_ahora],
        "Canastas cubiertas": [canastas_antes, canastas_ahora],
    })
    st.bar_chart(comparacion.set_index("Mes")[["Canastas cubiertas"]])
    st.dataframe(comparacion.round(2), hide_index=True, use_container_width=True)
with t3:
    st.bar_chart(base.iloc[1:].set_index("Mes")[["Inflación mensual (%)"]])
    st.line_chart(base.set_index("Mes")[["Inflación desde oct. 2025 (%)"]])
with t4:
    tabla = base.copy()
    tabla["CBA hogar elegido ($)"] = tabla["CBA adulto equivalente ($)"] * coef
    tabla["CBT hogar elegido ($)"] = tabla["CBT adulto equivalente ($)"] * coef
    st.dataframe(tabla.round(2), hide_index=True, use_container_width=True)
    st.download_button("Descargar datos como CSV", tabla.to_csv(index=False).encode("utf-8-sig"),
                       file_name="indec_ipc_canastas_oct2025_oct2026.csv", mime="text/csv")

st.subheader("Fuentes oficiales y metodología")
st.markdown("""
- [INDEC: IPC nacional octubre de 2026](https://www.indec.gob.ar/uploads/informesdeprensa/ipc_11_269335F5BA6B.pdf)
- [INDEC: series históricas del IPC](https://www.indec.gob.ar/Nivel4/Tema/3/5/31)
- [INDEC: CBA y CBT, Gran Buenos Aires, octubre de 2026 (incluye toda la serie)](https://www.indec.gob.ar/uploads/informesdeprensa/canasta_11_26E40C7C2106.pdf)
- [INDEC: CBA y CBT, Gran Buenos Aires, octubre de 2025](https://www.indec.gob.ar/uploads/informesdeprensa/canasta_11_25B916D63817.pdf)
""")
st.caption("La variación salarial real respecto del IPC se calcula como (1 + aumento nominal)/(1 + inflación) − 1. "
           "La evolución de las canastas y sus valores se toma directamente de los cuadros oficiales de INDEC. "
           "Los hogares de 3, 4 y 5 personas son ejemplos estadísticos publicados por el organismo; "
           "no describen automáticamente el consumo de tu hogar.")
