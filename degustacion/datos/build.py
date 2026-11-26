# Reconstruye RAW (tráfico + remarketing unificados) en degustacion/index.html a partir de datos/hoja.py.
import json, re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import hoja as H
C = 'CCN_LIT_TRF_DEGUSTACION_NOV_2026'
G = {'male': 'Hombre', 'female': 'Mujer', 'unknown': 'Desconocido'}
R = {'Región Autónoma del Atlántico Norte': 'RACCN', 'Región Autónoma del Atlántico Sur': 'RACCS', 'Unknown': 'Desconocido'}
reg = lambda x: R.get(x, x.replace(' Department', ''))
csv = lambda h, rows: h + "\n" + "".join(",".join(str(v) for v in r) + "\n" for r in rows)
rows = [l.split() for l in H.TRF.strip().split("\n")]
diario = csv("fecha,campana,alcance,impresiones,interacciones,cpm,clics,visitas,costo_por_visita,costo", [(r[0], C, *r[1:]) for r in sorted(rows)])
cre = []
for line in H.TRF_CRE.strip().split("\n"):
    d, rest = line.split("|")
    for it in rest.split(";"):
        n, a, i, e = it.split(); cre.append(("2026-11-" + d, n, a, i, e))
cre.sort(key=lambda r: r[0])
aud = [("Género", G[k], a, c, v) for k, a, c, v in H.TRF_GEN] + [("Edad", k, a, c, v) for k, a, c, v in H.TRF_EDAD] + [("Región", reg(k), a, c, 0) for k, a, c in H.TRF_REG]
RAW = {"diario": diario, "acumulado": csv("alcance_unico,frecuencia,cpm", [H.TRF_ACUM]),
       "creativos": csv("fecha,anuncio,alcance,impresiones,interacciones", cre), "audiencia": csv("dimension,segmento,alcance,clics,visitas", aud)}
p = os.path.join(os.path.dirname(__file__), "..", "index.html"); s = open(p, encoding="utf-8").read()
s, n = re.subn(r"const RAW = \{.*?\};\n", lambda m: "const RAW = " + json.dumps(RAW, ensure_ascii=False) + ";\n", s, count=1, flags=re.S); assert n == 1
s = re.sub(r"  window\.RMKT = \{.*?\};\n", "", s, count=1, flags=re.S)
open(p, "w", encoding="utf-8").write(s)
print("dias", len(rows), "creativos", len(cre), "audiencia", len(aud))
