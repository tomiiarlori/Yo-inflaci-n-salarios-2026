import html
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Costos del Crematorio | Parque Las Praderas', page_icon='🔥', layout='centered', initial_sidebar_state='collapsed')
st.markdown('''<style>
.block-container {max-width: 800px; padding: 1rem 1rem 3.5rem !important;}
h1 {font-size: clamp(1.8rem, 6vw, 2.6rem) !important; line-height: 1.13 !important;}
h2,h3 {line-height: 1.25 !important;}
[data-testid="stAppViewContainer"] {overflow-x: hidden;}
.lp-card {background:#172c42; color:#ffffff !important; border-radius:17px; padding:19px 20px; margin:10px 0 16px; border:1px solid #35516a; box-sizing:border-box; width:100%;}
.lp-card .lp-name {font-size: .94rem; color:#dbeaf8 !important; line-height:1.4;}
.lp-card .lp-number {font-size:clamp(1.9rem, 8vw, 2.8rem); color:#fff !important; font-weight:800; overflow-wrap:anywhere; line-height:1.25; margin-top:8px; font-variant-numeric:tabular-nums;}
.lp-card .lp-detail {font-size:.83rem; color:#c1d4e5 !important; margin-top:6px;}
.lp-row {display:flex; justify-content:space-between; align-items:flex-start; gap:10px; border-bottom:1px solid rgba(128,128,128,.26); padding:13px 1px;}
.lp-row .lp-label {flex:1; min-width:0; font-size:.98rem; line-height:1.35;}
.lp-row .lp-value {font-weight:750; font-variant-numeric:tabular-nums; text-align:right; white-space:nowrap; font-size:1.05rem;}
.lp-sub {font-size:.82rem; color:var(--text-color); opacity:.8; padding-bottom:8px;}
.lp-box {border:1px solid rgba(128,128,128,.22); border-radius:14px; padding:12px 16px; margin-bottom:14px;}
[data-testid="stNumberInput"] input {font-size: 1rem;}
.stTabs [data-baseweb="tab-list"] {gap:0; overflow-x:auto; flex-wrap:nowrap;}
.stTabs [data-baseweb="tab"] {flex-shrink:0; padding:10px 12px;}
[data-testid="stPlotlyChart"] {width:100%;}
@media(max-width:600px) { .block-container {padding-left: .85rem !important; padding-right:.85rem !important;} .lp-card {padding:16px;} .lp-row .lp-value {white-space:normal; overflow-wrap:anywhere;} }
</style>''', unsafe_allow_html=True)

def fmt(v):
    return '$ ' + f'{v:,.0f}'.replace(',', '.')

def numero(v, dec=1):
    return f'{v:,.{dec}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def tarjeta(titulo, valor, detalle=''):
    st.markdown(f'<div class="lp-card"><div class="lp-name">{html.escape(titulo)}</div><div class="lp-number">{html.escape(str(valor))}</div><div class="lp-detail">{html.escape(detalle)}</div></div>', unsafe_allow_html=True)

def fila(nombre, valor):
    st.markdown(f'<div class="lp-row"><div class="lp-label">{html.escape(nombre)}</div><div class="lp-value">{html.escape(str(valor))}</div></div>', unsafe_allow_html=True)

st.title('Costos del crematorio')
st.caption('Parque Las Praderas · Panel económico adaptado a celular')

with st.expander('⚙️ EDITAR DATOS Y GASTOS', expanded=False):
    st.caption('Todos los cambios actualizan los resultados de abajo. No necesitás abrir la barra lateral.')
    cremaciones=st.number_input('Cremaciones del período', min_value=1,value=150,step=1)
    hornos=st.number_input('Cantidad de hornos',min_value=1,value=2,step=1)
    dias=st.number_input('Días de la factura de gas',min_value=1,max_value=62,value=32)
    consumo=st.number_input('Gas facturado (m³ equivalentes)',min_value=0.,value=17009.,step=100.)
    gas_total=st.number_input('Total factura de gas ($)',min_value=0.,value=8806978.34,step=10000.)
    empleados=st.number_input('Empleados dedicados',min_value=0,value=2,step=1)
    costo_empleado=st.number_input('Costo mensual por empleado, con cargas ($)',min_value=0.,value=2000000.,step=100000.)
    impuesto=st.number_input('Impuesto municipal por cremación ($)',min_value=0.,value=40000.,step=1000.)
    insumos=st.number_input('Bolsa y urna por cremación ($)',min_value=0.,value=2000.,step=500.)
    electricidad_parque=st.number_input('Electricidad total del parque ($/mes)',min_value=0.,value=3000000.,step=100000.)
    electr_pct=st.slider('Porcentaje de electricidad que corresponde al crematorio',0,100,0,step=5,help='Dejar 0 hasta medir o estimar con criterio técnico.')
    mantenimiento=st.number_input('Mantenimiento del crematorio ($/mes)',min_value=0.,value=0.,step=10000.)
    amortizacion=st.number_input('Amortización de hornos ($/mes)',min_value=0.,value=0.,step=10000.)
    adicionales=st.number_input('Otros costos ($/mes)',min_value=0.,value=0.,step=10000.)
    gas_neto=st.number_input('Gas neto contable opcional ($)',min_value=0.,value=0.,step=10000.,help='Dejar 0 para utilizar el total de la factura. Cambiarlo solamente si contabilidad confirma el costo neto.')

gas_aplicado=gas_neto if gas_neto>0 else gas_total
personal=empleados*costo_empleado
elec=electricidad_parque*electr_pct/100
fijos=gas_aplicado+personal+elec+mantenimiento+amortizacion+adicionales
total=fijos+cremaciones*(impuesto+insumos)
costo_unitario=total/cremaciones

st.info('**Atención:** la factura de gas cubre 32 días y las 150 cremaciones son aproximadas por mes. El costo es preliminar hasta utilizar datos del mismo período. IVA y percepciones requieren revisión contable.')

t1,t2,t3,t4=st.tabs(['💰 Resumen','🔥 Gas','📈 Escenarios','📅 Histórico'])
with t1:
    st.subheader('Resultados principales')
    tarjeta('Costo parcial por cremación',fmt(costo_unitario),'Gas, personal, impuesto, insumos y gastos adicionales cargados')
    tarjeta('Costo total del período',fmt(total),'Calculado con las cremaciones indicadas')
    tarjeta('Gas facturado por cremación',fmt(gas_total/cremaciones),'Importe bruto dividido por cantidad de servicios')
    tarjeta('Gas equivalente por cremación',numero(consumo/cremaciones)+' m³','Incluye precalentamiento, esperas y operaciones')
    st.warning('Todavía no es el costo definitivo. Falta confirmar electricidad del crematorio, mantenimiento, amortización y tratamiento de impuestos recuperables.')
    st.subheader('Detalle de costos')
    detalles=[('Gas',gas_aplicado),('Personal',personal),('Impuesto municipal',cremaciones*impuesto),('Bolsa y urna',cremaciones*insumos),('Electricidad asignada',elec),('Mantenimiento',mantenimiento),('Amortización',amortizacion),('Otros',adicionales)]
    for nombre, importe in detalles:
        fila(nombre,fmt(importe))
        st.markdown(f'<div class="lp-sub">Por cremación: {html.escape(fmt(importe/cremaciones))}</div>',unsafe_allow_html=True)
    st.subheader('Distribución de gastos')
    df=pd.DataFrame(detalles,columns=['Concepto','Costo ($)'])
    df=df[df['Costo ($)']>0].sort_values('Costo ($)')
    if not df.empty:
        fig=px.bar(df,x='Costo ($)',y='Concepto',orientation='h')
        fig.update_traces(marker_color='#3782ca',hovertemplate='%{y}: $%{x:,.0f}<extra></extra>')
        fig.update_layout(height=max(290,45*len(df)+100),margin=dict(l=0,r=8,t=10,b=30),xaxis_title='Pesos por período',yaxis_title='',showlegend=False,autosize=True)
        st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
with t2:
    st.subheader('Gas y funcionamiento de los hornos')
    tarjeta('Consumo promedio por día',numero(consumo/dias)+' m³','Volumen equivalente facturado')
    tarjeta('Costo bruto por m³',fmt(gas_total/consumo) if consumo else 'Sin datos','Factura completa dividida por m³')
    tarjeta('Cantidad de hornos',str(hornos),'Hornos disponibles')
    horas_l_s=st.number_input('Horas por día de lunes a sábado',min_value=0.,value=8.,step=.5)
    horas_dom=st.number_input('Horas por domingo',min_value=0.,value=4.,step=.5)
    domingos=st.number_input('Domingos durante el período',min_value=0,max_value=9,value=4)
    horas=max(0,dias-domingos)*horas_l_s+domingos*horas_dom
    horas_horno=horas*hornos
    tarjeta('Horas-horno posibles',numero(horas_horno,0),'Si ambos hornos funcionan toda la jornada')
    tarjeta('Consumo por hora-horno posible',numero(consumo/horas_horno)+' m³' if horas_horno else 'Sin datos','Indicador orientativo, no medición efectiva del quemador')
    st.caption('Para evaluar los apagados de aproximadamente 30 minutos y los reinicios hay que registrar horas reales y lecturas del medidor. No se puede concluir aún si conviene apagarlos.')
with t3:
    st.subheader('Simulador de cremaciones')
    proyectadas=st.slider('Cremaciones por período',min_value=50,max_value=350,value=150,step=10)
    unit_proy=fijos/proyectadas+impuesto+insumos
    tarjeta('Costo unitario simulado',fmt(unit_proy),f'Con {proyectadas} cremaciones')
    st.caption('Supuesto simplificado: el gas y otros gastos mensuales se mantienen constantes aunque cambie la cantidad. No representa el consumo físico real.')
    xs=list(range(50,351,10))
    sim=pd.DataFrame({'Cremaciones':xs,'Costo unitario ($)':[fijos/x+impuesto+insumos for x in xs]})
    fig=px.line(sim,x='Cremaciones',y='Costo unitario ($)',markers=False)
    fig.update_layout(height=340,margin=dict(l=0,r=12,t=20,b=20))
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    ahorro=st.slider('Reducción hipotética del gasto de gas (%)',0,20,5)
    tarjeta('Ahorro hipotético por período',fmt(gas_total*ahorro/100),f'Escenario de reducción del {ahorro}%')
    st.caption('Una reducción de factura no equivale necesariamente a un ahorro técnicamente alcanzable. Debe respetarse el funcionamiento seguro y las exigencias ambientales.')
with t4:
    st.subheader('Comparación de períodos')
    st.write('Descargá la plantilla CSV, completala con datos que correspondan al mismo período y subila acá.')
    plantilla=pd.DataFrame([{'periodo':'2026-10','cremaciones':150,'gas_m3':17009,'gas_pesos':8806978.34,'personal_pesos':4000000,'impuesto_unitario':40000,'insumos_unitario':2000}])
    st.download_button('⬇️ Descargar plantilla CSV',data=plantilla.to_csv(index=False).encode('utf-8-sig'),file_name='plantilla_costos_crematorio.csv',mime='text/csv',use_container_width=True)
    st.caption('La fila precargada es ilustrativa: mezcla factura de 32 días con volumen mensual aproximado; reemplazala antes de comparar.')
    archivo=st.file_uploader('Subir CSV con históricos',type='csv')
    if archivo:
        try:
            hist=pd.read_csv(archivo)
            requeridas=set(plantilla.columns)
            if not requeridas.issubset(hist.columns):
                st.error('Faltan columnas: '+', '.join(sorted(requeridas-set(hist.columns))))
            else:
                for c in requeridas-{'periodo'}:
                    hist[c]=pd.to_numeric(hist[c],errors='raise')
                if hist['cremaciones'].isna().any() or (hist['cremaciones']<=0).any():
                    st.error('Las cremaciones deben ser cantidades positivas en todas las filas.')
                else:
                    hist['costo_unitario']=(hist['gas_pesos']+hist['personal_pesos'])/hist['cremaciones']+hist['impuesto_unitario']+hist['insumos_unitario']
                    hist['gas_unitario_m3']=hist['gas_m3']/hist['cremaciones']
                    for _,r in hist.iterrows():
                        st.markdown(f'**{html.escape(str(r["periodo"]))}**')
                        fila('Cremaciones',numero(r['cremaciones'],0))
                        fila('Costo parcial por cremación',fmt(r['costo_unitario']))
                        fila('Gas por cremación',numero(r['gas_unitario_m3'])+' m³')
                    fig=px.line(hist,x='periodo',y='costo_unitario',markers=True,labels={'periodo':'Período','costo_unitario':'Costo parcial ($)'})
                    fig.update_layout(height=320,margin=dict(l=0,r=8,t=10,b=20))
                    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        except Exception as exc:
            st.error(f'No se pudo leer el archivo: {exc}')
  


