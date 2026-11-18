import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador salarial e inflación",layout="wide")
st.title("Simulador de salarios e inflación")
st.caption("IPC nacional INDEC · enero–septiembre 2026 · nivel base: diciembre de 2025")
meses=["Dic 2025","Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep"]
indices=[10121.37,10413.03,10714.63,11077.06,11363.09,11607.39,11826.41,12076.39,12276.77,12514.15]
df=pd.DataFrame({"Mes":meses,"IPC":indices})
df["Inflación mensual (%)"]=df.IPC.pct_change()*100
df["Inflación acumulada (%)"]=(df.IPC/df.IPC.iloc[0]-1)*100
inf=df.IPC.iloc[-1]/df.IPC.iloc[0]-1
c1,c2=st.columns(2)
with c1: sueldo=st.number_input("Sueldo inicial ($)",min_value=0.0,value=1000000.0,step=50000.0)
with c2: aumento=st.number_input("Aumento nominal (%)",min_value=-100.0,max_value=1000.0,value=20.0,step=1.0)
final=sueldo*(1+aumento/100)
necesario=sueldo*(1+inf)
real=((1+aumento/100)/(1+inf)-1)*100
a,b,c=st.columns(3)
a.metric("Inflación acumulada",f"{inf*100:.2f}%")
b.metric("Sueldo final",f"${final:,.0f}")
c.metric("Variación real",f"{real:.2f}%")
st.write(f"**Sueldo necesario para mantener poder adquisitivo:** ${necesario:,.2f}")
st.info("El aumento supera la inflación: mejora el poder adquisitivo." if real>0 else "El aumento coincide con la inflación: mantiene el poder adquisitivo." if abs(real)<1e-8 else "El aumento no alcanza para compensar la inflación: cae el poder adquisitivo.")
t1,t2=st.tabs(["Inflación mensual","Inflación acumulada"])
with t1:st.bar_chart(df.iloc[1:].set_index('Mes')['Inflación mensual (%)'])
with t2:st.line_chart(df.iloc[1:].set_index('Mes')['Inflación acumulada (%)'])
st.dataframe(df.round(2),hide_index=True)
st.caption("Fuente: INDEC, IPC nacional. https://shiny.indec.gob.ar/vip/ · Salario y aumento son datos simulados.")
