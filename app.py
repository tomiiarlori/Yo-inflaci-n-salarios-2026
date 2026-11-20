import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Costos del Crematorio | Parque Las Praderas', page_icon='🔥', layout='wide')
st.title('Análisis económico del crematorio')
st.caption('Parque Las Praderas · Costos reales, indicadores y simulaciones | Versión inicial')

st.info('Los datos precargados son los informados por la administración. Son aproximados y deben conciliarse por período. El importe de gas corresponde a una factura de **32 días** y las 150 cremaciones son un promedio mensual, por lo que el costo unitario mostrado es una estimación hasta incorporar la cantidad exacta de servicios de esos 32 días.')

with st.sidebar:
    st.header('Datos operativos')
    cremaciones = st.number_input('Cremaciones del período', min_value=1, value=150, step=1)
    hornos = st.number_input('Cantidad de hornos', min_value=1, value=2, step=1)
    dias = st.number_input('Días del período de gas', min_value=1, max_value=62, value=32)
    consumo = st.number_input('Gas facturado (m³ equivalentes a 9.300 kcal)', min_value=0.0, value=17009.0, step=100.0)
    gas_total = st.number_input('Total factura gas ($)', min_value=0.0, value=8806978.34, step=10000.0)
    empleados = st.number_input('Empleados dedicados', min_value=0, value=2, step=1)
    costo_empleado = st.number_input('Costo mensual completo por empleado ($)', min_value=0.0, value=2000000.0, step=100000.0)
    impuesto = st.number_input('Impuesto municipal por cremación ($)', min_value=0.0, value=40000.0, step=1000.0)
    insumos = st.number_input('Bolsa y urna, costo conjunto por cremación ($)', min_value=0.0, value=2000.0, step=500.0)
    electricidad_parque = st.number_input('Factura eléctrica total del parque ($/mes)', min_value=0.0, value=3000000.0, step=100000.0)
    electr_pct = st.slider('Porcentaje estimado atribuible al crematorio', 0, 100, 0, step=5, help='Dejar 0 hasta disponer de medición o criterio técnico fundamentado')
    mantenimiento = st.number_input('Mantenimiento atribuible al crematorio ($/mes)', min_value=0.0, value=0.0, step=10000.0)
    amortizacion = st.number_input('Amortización atribuible del horno ($/mes)', min_value=0.0, value=0.0, step=10000.0)
    adicionales = st.number_input('Otros costos mensuales ($)', min_value=0.0, value=0.0, step=10000.0)
    costo_gas_neto = st.number_input('Costo económico neto del gas ($, si corresponde)', min_value=0.0, value=0.0, step=10000.0, help='Dejar en 0 para usar el importe total de factura; ingresar el costo neto solo si contabilidad confirma impuestos recuperables.')

fmt = lambda v: f'$ {v:,.0f}'.replace(',', '.')
gas_aplicado = costo_gas_neto if costo_gas_neto > 0 else gas_total
personal = empleados*costo_empleado
elec = electricidad_parque*electr_pct/100
variables = cremaciones*(impuesto+insumos)
fijos = gas_aplicado+personal+elec+mantenimiento+amortizacion+adicionales
total = fijos+variables
costo_unitario = total/cremaciones

t1,t2,t3,t4 = st.tabs(['Resumen de costos','Gas y hornos','Escenarios','Histórico de períodos'])
with t1:
    a,b,c,d = st.columns(4)
    a.metric('Costo parcial / cremación', fmt(costo_unitario))
    b.metric('Costo del período', fmt(total))
    c.metric('Gas facturado / cremación', fmt(gas_total/cremaciones))
    d.metric('Gas equivalente / cremación', f'{consumo/cremaciones:,.1f} m³')
    st.warning('No es todavía el costo definitivo: falta confirmar asignación eléctrica, mantenimiento, amortización y tratamiento de IVA/percepciones. El gasto mensual de personal se compara provisionalmente con la cantidad de cremaciones del período de gas.')
    detalles = pd.DataFrame({'Concepto':['Gas (facturado o neto indicado)','Personal','Impuesto municipal','Bolsa y urna','Electricidad asignada','Mantenimiento','Amortización','Otros'], 'Costo ($)':[gas_aplicado,personal,cremaciones*impuesto,cremaciones*insumos,elec,mantenimiento,amortizacion,adicionales]})
    c1,c2=st.columns([1.2,1])
    with c1:
        st.dataframe(detalles.assign(**{'Por cremación ($)':detalles['Costo ($)']/cremaciones}),hide_index=True,use_container_width=True,column_config={'Costo ($)':st.column_config.NumberColumn(format='$ %.0f'),'Por cremación ($)':st.column_config.NumberColumn(format='$ %.0f')})
    with c2:
        fig=px.pie(detalles[detalles['Costo ($)']>0],values='Costo ($)',names='Concepto',hole=.55,title='Composición del costo')
        st.plotly_chart(fig,use_container_width=True)
with t2:
    st.subheader('Consumo y operación')
    c1,c2,c3=st.columns(3)
    c1.metric('m³/día facturado',f'{consumo/dias:,.1f}')
    c2.metric('Factura promedio / m³',fmt(gas_total/consumo) if consumo else '—')
    c3.metric('Hornos',str(hornos))
    st.write('Indicadores orientativos: el consumo por servicio incluye precalentamiento, operación, espera y reinicios. Para aislar cada etapa se necesitan lecturas horarias del medidor o un medidor por horno.')
    lunes_sabado=st.number_input('Horas diarias por horno (lunes a sábado)',min_value=0.0,value=8.0,step=.5)
    domingo=st.number_input('Horas diarias por horno (domingo)',min_value=0.0,value=4.0,step=.5)
    n_domingos=st.number_input('Domingos dentro del período de referencia',min_value=0,max_value=9,value=4)
    horas_periodo=(dias-n_domingos)*lunes_sabado+n_domingos*domingo
    st.metric('Horas-horno posibles (si ambos operan toda la jornada)',f'{horas_periodo*hornos:,.0f}')
    if horas_periodo*hornos:
        st.metric('Consumo medio por hora-horno posible',f'{consumo/(horas_periodo*hornos):,.1f} m³')
    st.caption('Este cociente no mide consumo real por hora de quemador. Los hornos pueden detenerse y las fechas de operación deben coincidir con las de la factura.')
    st.markdown('**Registro sugerido:** fecha, horno, hora de encendido, hora de apagado, cremaciones por horno, tiempo de espera entre servicios y lectura de medidor.')
with t3:
    st.subheader('Simulador de volumen y costos')
    proyectadas=st.slider('Cremaciones hipotéticas por período',min_value=50,max_value=350,value=150,step=10)
    st.caption('Supuesto provisional: gas + otros gastos mensuales se mantienen constantes al cambiar volumen. En la realidad el gas tiene componente variable; no usar para presupuestar sin medirlo.')
    unit_proy=fijos/proyectadas+impuesto+insumos
    st.metric('Costo unitario simulado',fmt(unit_proy))
    xs=list(range(50,351,10))
    df=pd.DataFrame({'Cremaciones':xs,'Costo unitario ($)':[fijos/n+impuesto+insumos for n in xs]})
    st.plotly_chart(px.line(df,x='Cremaciones',y='Costo unitario ($)',markers=True,title='Costo unitario bajo supuesto de costos mensuales fijos'),use_container_width=True)
    ahorro=st.slider('Reducción hipotética de la factura de gas (%)',0,20,5)
    st.metric('Ahorro hipotético por período',fmt(gas_total*ahorro/100))
    st.caption('Esto es solo una sensibilidad matemática: no significa que sea posible reducir el consumo sin afectar seguridad, equipos o exigencias ambientales.')
with t4:
    st.subheader('Cargar períodos para observar tendencias')
    st.write('Subí un CSV con columnas **periodo, cremaciones, gas_m3, gas_pesos, personal_pesos, impuesto_unitario, insumos_unitario**. Todos los registros deben utilizar períodos homogéneos.')
    plantilla=pd.DataFrame([{'periodo':'2026-10','cremaciones':150,'gas_m3':17009,'gas_pesos':8806978.34,'personal_pesos':4000000,'impuesto_unitario':40000,'insumos_unitario':2000}])
    st.download_button('Descargar plantilla CSV',data=plantilla.to_csv(index=False).encode('utf-8-sig'),file_name='plantilla_costos_crematorio.csv',mime='text/csv')
    st.caption('La fila de ejemplo mezcla un consumo facturado de 32 días con 150 cremaciones mensuales aproximadas: reemplazala por cifras del mismo período antes de sacar conclusiones.')
    archivo=st.file_uploader('Cargar CSV de períodos',type='csv')
    if archivo:
        try:
            hist=pd.read_csv(archivo)
            req=set(plantilla.columns)
            if not req.issubset(hist.columns):
                st.error('Faltan columnas: '+', '.join(sorted(req-set(hist.columns))))
            elif (pd.to_numeric(hist['cremaciones'],errors='coerce')<=0).any():
                st.error('Todas las cantidades de cremaciones deben ser positivas.')
            else:
                for col in req-{'periodo'}:
                    hist[col]=pd.to_numeric(hist[col],errors='raise')
                hist['costo_por_cremacion']=(hist['gas_pesos']+hist['personal_pesos'])/hist['cremaciones']+hist['impuesto_unitario']+hist['insumos_unitario']
                hist['m3_por_cremacion']=hist['gas_m3']/hist['cremaciones']
                st.dataframe(hist,use_container_width=True,hide_index=True)
                st.plotly_chart(px.line(hist,x='periodo',y='costo_por_cremacion',markers=True,title='Costo parcial por cremación por período'),use_container_width=True)
                st.plotly_chart(px.line(hist,x='periodo',y='m3_por_cremacion',markers=True,title='Gas por cremación por período'),use_container_width=True)
        except Exception as exc:
            st.error(f'No se pudo leer el CSV: {exc}')

