# Reconstruye el bloque RAW de lanzamiento/index.html a partir de datos/hoja.py.
# Uso: python3 lanzamiento/datos/build.py
import json, re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import hoja as H
REN = {'BOOST_MP_10NOV': 'BOOST_PPV_10NOV', 'BOOST_MP_11NOV': 'BOOST_PPL_11NOV'}  # Meta renombró estos boosts en IG
rn = lambda c: REN.get(c, c)
def csv(h, rows): return h + "\n" + "".join(",".join("" if v is None else str(v) for v in r) + "\n" for r in rows)
lines = lambda t: [l.split() for l in t.strip().split("\n")]
dia = []
for canal, txt in (("Facebook", H.FB), ("Instagram", H.IG)):
    for f, a, i, e, v, t, c in sorted(lines(txt)): dia.append((canal, f, a, i, e, v, t, None, c))
for f, a, i, v, c, k in sorted(lines(H.YT)): dia.append(("YouTube", f, a, i, None, v, None, k, c))
cre = []
for canal, txt in (("Facebook", H.CRE_FB), ("Instagram", H.CRE_IG)):
    for line in txt.strip().split("\n"):
        d, rest = line.split("|")
        for it in rest.split(";"):
            n, a, i, e = it.split(); cre.append((canal, "2026-11-" + d, rn(n), a, i, e))
p = os.path.join(os.path.dirname(__file__), "..", "index.html")
s = open(p, encoding="utf-8").read()
old = json.loads(re.search(r"const RAW = (\{.*?\});\n", s, re.S).group(1))
names = {l.split(",")[1]: l.split(",", 5)[5] for l in old["videos_yt"].strip().split("\n")[1:]}
vy = sorted(lines(H.VIDEOS), key=lambda r: (r[0], r[1]))
G = {'male': 'Hombre', 'female': 'Mujer', 'unknown': 'Desconocido', 'MALE': 'Hombre', 'FEMALE': 'Mujer', 'UNDETERMINED': 'Desconocido'}
R = {'Región Autónoma del Atlántico Norte': 'RACCN', 'Región Autónoma del Atlántico Sur': 'RACCS', 'North Caribbean Coast Autonomous Region': 'RACCN', 'South Caribbean Coast Autonomous Region': 'RACCS', 'Leon': 'León', 'Esteli': 'Estelí', 'Rio San Juan': 'Río San Juan', 'Unknown': 'Desconocido'}
reg = lambda x: R.get(x.replace(' Department', ''), x.replace(' Department', ''))
age = lambda x: {'65_UP': '65+', 'UNDETERMINED': 'Desconocido', 'Unknown': 'Desconocido'}.get(x, x.replace('_', '-'))
aud = []
for canal, (g, a, r) in H.AUD.items():
    aud += [(canal, 'Género', G[k], v) for k, v in g] + [(canal, 'Edad', age(k), v) for k, v in a] + [(canal, 'Región', reg(k), v) for k, v in r]
new = {
 "diario": csv("canal,fecha,alcance,impresiones,interacciones,reproducciones,thruplays,clics,costo", dia),
 "acumulado": csv("canal,alcance_unico,frecuencia,cpm", [(k,) + v for k, v in H.ACUM.items()]),
 "creativos_meta": csv("canal,fecha,creativo,alcance,impresiones,interacciones", cre),
 "videos_yt": csv("fecha,video_id,impresiones,views,costo_por_view,nombre", [tuple(r) + (names.get(r[1], "Video " + r[1]),) for r in vy]),
 "ubicaciones_meta": csv("plataforma,creativo,alcance,impresiones", [(pl.capitalize(), rn(c), a, i) for pl, c, a, i in lines(H.UBIC)]),
 "audiencia": csv("canal,dimension,segmento,valor", aud)}
assert set(new) == set(old), set(new) ^ set(old)
raw = "const RAW = " + json.dumps({k: new[k] for k in old}, ensure_ascii=False) + ";"
s = re.sub(r"const RAW = \{.*?\};\n", lambda m: raw + "\n", s, count=1, flags=re.S)
open(p, "w", encoding="utf-8").write(s)
print("diario", len(dia), "creativos", len(cre), "videos", len(vy), "audiencia", len(aud))
