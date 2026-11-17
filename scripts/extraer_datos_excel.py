"""Regenera los datos (toolbox_calidad/data) desde las plantillas Excel originales.

Uso:  python scripts/extraer_datos_excel.py <carpeta_salida> <carpeta_con_xlsx>
Los .xls antiguos deben convertirse antes a .xlsx (p. ej. con LibreOffice:
soffice --headless --convert-to xlsx *.xls).
"""
import openpyxl, json, re, os, sys, csv
C=os.path.join(sys.argv[2], '')
OUT=sys.argv[1]; os.makedirs(OUT+'/checklists',exist_ok=True)
def cells(ws,row):
    return [(c.column, (str(c.value).strip() if not isinstance(c.value,float) else ('%g'%c.value))) for c in row if c.value not in (None,'') and str(c.value).strip()]
def save(name,obj):
    json.dump(obj,open(f'{OUT}/checklists/{name}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
def clean(t): return re.sub(r'\s+',' ',t).strip()

# 1 Recorridos
ws=openpyxl.load_workbook(C+'Recorridos de la Comisión de Seguridad e Higiene.xlsx')['Acta']
secs=[];cur=None
for row in ws.iter_rows(min_row=18,max_row=64):
    cs=cells(ws,row)
    for col,t in cs:
        m=re.match(r'^(\d+)\.\s+([A-ZÁÉÍÓÚÑ ,]+)\.?$',t)
        if m and len(cs)==1:
            cur={'name':clean(t).rstrip('.'),'items':[]};secs.append(cur);continue
        m=re.match(r'^(\d+\.\d+(?:\.\d+)?)\s*\.?\s+(.+)$',t)
        if m and cur is not None:
            cur['items'].append({'code':m.group(1),'text':clean(m.group(2)).rstrip('.')})
        elif t=='Otros' and cur is not None:
            cur['items'].append({'code':'','text':'Otros'})
# drop group headings (items whose code has children)
for s in secs:
    codes=[i['code'] for i in s['items']]
    s['items']=[i for i in s['items'] if not any(c.startswith(i['code']+'.') for c in codes if i['code'])]
    s['items']=[dict(i,text=(i['text'] if i['code'].count('.')<2 else i['text'])) for i in s['items']]
save('recorrido_comision_sh',{'title':'Acta de verificación de recorrido — Comisión de Seguridad e Higiene','options':['Cumple','No cumple','N/A'],'sections':secs,
 'source':'Recorridos de la Comisión de Seguridad e Higiene.xls'})

# 2 Ventilacion checklist
ws=openpyxl.load_workbook(C+'VENTILACION Y CLIMATIZACION - Check list.xlsx').active
items=[]
for row in ws.iter_rows():
    cs=cells(ws,row)
    if len(cs)>=2 and re.fullmatch(r'\d+',cs[0][1]): items.append({'code':cs[0][1],'text':clean(cs[1][1])})
save('ventilacion_climatizacion',{'title':'Condiciones medioambientales — Ventilación y climatización','options':['Sí','No','N/A'],'sections':[{'name':'Ventilación y climatización','items':items}],'source':'VENTILACION Y CLIMATIZACION - Check list.xls'})

# 3 Requisitos RP
ws=openpyxl.load_workbook(C+'REQUISITOS AUDITABLES — ALMACENAMIENTO RESIDUOS PELIGROSOS.xlsx').active
secs=[];cur=None
for row in ws.iter_rows(min_row=13):
    cs=cells(ws,row)
    if not cs: continue
    if len(cs)==1 and cs[0][1].isupper() and not cs[0][1].startswith('TOTAL'):
        cur={'name':clean(cs[0][1]),'items':[]};secs.append(cur)
    elif len(cs)>=2 and re.fullmatch(r'\d+',cs[0][1]) and cur:
        cur['items'].append({'code':cs[0][1],'text':clean(cs[1][1])})
save('almacen_residuos_peligrosos',{'title':'Requisitos auditables — Almacenamiento de residuos peligrosos (RLGPGIR Art. 82)','options':['S','N','NA'],'sections':secs,'source':'REQUISITOS AUDITABLES — ALMACENAMIENTO RESIDUOS PELIGROSOS.xls'})

# 4 PROFEPA simulacros (6 hojas)
wb=openpyxl.load_workbook(C+'SIMULACROS—LISTA DE VERIFICACION DE PROFEPA.xlsx')
secs=[]
for ws in wb.worksheets:
    title=None; items=[]
    for row in ws.iter_rows():
        cs=cells(ws,row)
        if not cs: continue
        if title is None and 'LISTA' in cs[0][1].upper(): title=clean(cs[0][1]); continue
        if len(cs)>=2 and re.fullmatch(r'\d+',cs[0][1]) and len(cs[1][1])>12:
            items.append({'code':cs[0][1],'text':clean(cs[1][1]).capitalize()})
    secs.append({'name':ws.title,'items':items})
save('simulacro_profepa',{'title':'Simulacros — Listas de verificación (PROFEPA)','options':['Sí','No','N/A'],'score':'0-5','sections':secs,'source':'SIMULACROS—LISTA DE VERIFICACION DE PROFEPA.xlsx'})

# 5 Proteccion civil
ws=openpyxl.load_workbook(C+'Protección Civil - Evaluación de Riesgos.xlsx')['riesgos']
secs=[];cur=None
for row in ws.iter_rows(min_row=24):
    cs=cells(ws,row)
    if len(cs)<2: continue
    code,txt=cs[0][1],clean(cs[1][1])
    if not re.fullmatch(r'\d+(\.\d+)?',code): continue
    dec=code.split('.')[1] if '.' in code else ''
    if len(dec)<=2 and (txt.isupper() or len(dec)==1) and not txt.startswith('Cuenta'):
        cur={'name':f'{code} {txt}','items':[]};secs.append(cur)
    elif cur is not None:
        cur['items'].append({'code':code,'text':txt})
secs=[s for s in secs if s['items']]
save('proteccion_civil_riesgos',{'title':'Identificación y análisis de riesgos — Protección Civil','options':['Sí','No','N/A'],'sections':secs,'source':'Protección Civil - Evaluación de Riesgos.xls'})

# 6 Talleres
ws=openpyxl.load_workbook(C+'Seguridad en Talleres.xlsx').active
secs=[];cur=None
for row in ws.iter_rows():
    cs=cells(ws,row)
    if not cs: continue
    t=clean(cs[0][1])
    if re.match(r'^[A-H]\. ',t): cur={'name':t,'items':[]};secs.append(cur);continue
    if cur is None: continue
    if '?' in t or (len(cs)>=2 and cs[1][1] in('SI','Orden')) : 
        if t.startswith('Conceptos'): continue
        cur['items'].append({'code':str(len(cur['items'])+1),'text':t})
    elif len(cs)>=3 and cs[1][1]=='' : pass
for s in secs:
    if s['name'].startswith('A.'):
        s['items']=[{'code':str(i+1),'text':x} for i,x in enumerate(['Distribución de maquinaria y/o equipo (orden y limpieza)','Herramientas utilizadas (orden y limpieza)','Lugar para guardar equipo de protección personal','Piso del área','Tipo de ventilación adecuada'])]+[dict(i,code=str(k+6)) for k,i in enumerate(s['items'])]
save('seguridad_talleres',{'title':'Diagnóstico de condiciones de seguridad y medio ambiente — Talleres','options':['Sí','No','N/A'],'sections':secs,'source':'Seguridad en Talleres.xls'})

# 7 Auditoria grupo de mejora
ws=openpyxl.load_workbook(C+'026 AUDITORIA DEL GRUPO DE MEJORA.xlsx')['F-GO-MT-026']
qs=[];cat=sub=None
for row in ws.iter_rows(min_row=16,max_row=56):
    cs=cells(ws,row)
    vals=[t for _,t in cs]
    idx=[i for i,t in enumerate(vals) if re.fullmatch(r'\d+',t) and i+2<len(vals) and '?' in vals[i+1]]
    if not idx: continue
    i=idx[0]
    pre=vals[:i]
    if len(pre)==2: cat,sub=pre
    elif len(pre)==1: sub=pre[0]
    qs.append({'n':int(vals[i]),'categoria':cat,'subcategoria':sub,'pregunta':clean(vals[i+1]),'puntos':int(vals[i+2])})
# fix categories by known blocks
blocks=[(1,8,'Planificación'),(9,23,'Implementación'),(24,25,'Control / resultados'),(26,33,'Estabilización'),(34,36,'Involucración')]
for q in qs:
    for a,b,n in blocks:
        if a<=q['n']<=b: q['categoria']=n
json.dump(qs,open(OUT+'/auditoria_grupo_mejora.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('audit',len(qs),sum(q['puntos'] for q in qs))

# 8 Incompatibilidad
ws=openpyxl.load_workbook(C+'Tabla de Incompatibilidad Quimica_2.xlsx')['Tabla universal']
groups={};matrix={}
for row in ws.iter_rows(min_row=4,max_row=44):
    vals=[(c.column,c.value) for c in row if c.value not in (None,'')]
    if len(vals)<2: continue
    g=int(vals[0][1]); groups[g]=clean(str(vals[1][1]))
    rest=vals[2:]
    # last value equals g (diagonal label); entries before map by column
    for col,v in rest:
        matrix.setdefault(g,{})[col]=str(v).strip()
# header row 45 maps columns->group numbers
colmap={c.column:int(c.value) for c in ws[45] if isinstance(c.value,(int,float))}
mat={}
for g,d in matrix.items():
    for col,v in d.items():
        h=colmap.get(col)
        if h is None or h==g: continue
        mat.setdefault(str(g),{})[str(h)]=v
nom={}
for r in range(49,57):
    a,b=ws.cell(r,2).value or ws.cell(r,1).value, None
    row=[c.value for c in ws[r] if c.value]
    if len(row)>=2: nom[str(row[0]).strip()]=clean(str(row[1]))
ex={};g=None
for (v,) in openpyxl.load_workbook(C+'Tabla de Incompatibilidad Quimica_2.xlsx')['Ejemplos'].iter_rows(values_only=True,max_col=1):
    if not v: continue
    v=clean(str(v)); m=re.match(r'GRUPO\s+(\d+)',v,re.I)
    if m: g=m.group(1); ex[g]=[]; continue
    if g: ex[g].append(v)
json.dump({'grupos':groups,'matriz':mat,'nomenclatura':nom,'ejemplos':ex},open(OUT+'/incompatibilidad_quimica.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('incomp',len(groups),sum(len(v) for v in mat.values()),nom.keys(),len(ex))

# 9 Materiales peligrosos tabla 2
ws=openpyxl.load_workbook(C+'Tablas de Materiales Peligrosos Para Su Transporte.xlsx')['Tabla 2']
hdr=[clean(str(c.value)) for c in ws[1] if c.value]
with open(OUT+'/materiales_peligrosos.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(hdr[:8]); n=0
    for row in ws.iter_rows(min_row=2,values_only=True):
        if row[0] is None: continue
        r=['' if v is None else clean(str(v) if not isinstance(v,float) else '%g'%v) for v in row[:8]]
        w.writerow(r); n+=1
print('matpel',n,hdr)

# 10 RLAN
ws=openpyxl.load_workbook(C+'REGLAMENTO DE LA LEY DE AGUAS NACIONALES.xlsx').active
rows=[]
for row in ws.iter_rows(min_row=8,values_only=True):
    v=[clean(str(x)) if x is not None else '' for x in row]
    nz=[x for x in v if x]
    if len(nz)>=4 and nz[0]=='AGUA':
        rows.append(nz[:6]+['']*(6-len(nz[:6])))
json.dump(rows,open(OUT+'/requisitos_rlan.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('rlan',len(rows))

# --- fixes
p=OUT+'/checklists/proteccion_civil_riesgos.json'; d=json.load(open(p,encoding='utf-8'))
new=[]
for s in d['sections']:
    if s['name'].startswith('3.21 '):
        a=[];b=None
        for it in s['items']:
            if it['code']=='3.22': b={'name':'3.22 LISTADO No. 2 — Agentes perturbadores','items':[]}; continue
            (b['items'] if b else a).append(it)
        new.append({'name':'3.21 LISTADO 1 — Elementos de riesgo externos (radio 500 m)','items':a}); new.append(b)
    else: new.append(s)
d['sections']=new; save('proteccion_civil_riesgos',d)
p=OUT+'/checklists/simulacro_profepa.json'; d=json.load(open(p,encoding='utf-8'))
ws=openpyxl.load_workbook(C+'SIMULACROS—LISTA DE VERIFICACION DE PROFEPA.xlsx')['Coordinacion con Autoridades']
items=[];grp='';n=0
for row in ws.iter_rows(min_row=4):
    cs=[t for col,t in cells(ws,row) if col<=3]
    if not cs: continue
    t=clean(cs[0])
    if re.fullmatch(r'[\d.]+',t) or t in('SI','NO','NA') or len(t)<3: continue
    if t.endswith(':'): grp=t.rstrip(':').capitalize(); continue
    n+=1; items.append({'code':str(n),'text':(grp+' — ' if grp else '')+t.capitalize()})
for s in d['sections']:
    if s['name']=='Coordinacion con Autoridades': s['items']=items
save('simulacro_profepa',d); print('coord',len(items), items[:3], items[-3:])

# Recortar notas finales de "Coordinación con autoridades" y agregar criterio de calificación
p=OUT+'/checklists/simulacro_profepa.json'; d=json.load(open(p,encoding='utf-8'))
for s in d['sections']:
    if s['name']=='Coordinacion con Autoridades':
        s['items']=[i for i in s['items'] if not i['text'].startswith(('Evaluación de refugios temporales — *coe','Datos del evaluador'))]
d['nota']=('Cada apartado se califica de 0 a 5. Si todos los apartados del rol aplicaron, se suman y se promedian entre el número de apartados; '
 'si no, la suma se promedia sólo entre los apartados que aplicaron.')
save('simulacro_profepa',d)

# Ejemplos de sustancias por grupo (columnas A y B)
ws=openpyxl.load_workbook(C+'Tabla de Incompatibilidad Quimica_2.xlsx')['Ejemplos']
ex={};g=None
for a,b in ws.iter_rows(values_only=True,max_col=2):
    v=a or b
    if not v: continue
    v=clean(str(v)); m=re.match(r'GRUPO\s+(\d+)',v,re.I)
    if m: g=m.group(1); ex.setdefault(g,[]); continue
    if g and v not in ex[g]: ex[g].append(v)
p=OUT+'/incompatibilidad_quimica.json'; d=json.load(open(p,encoding='utf-8')); d['ejemplos']=ex
json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
