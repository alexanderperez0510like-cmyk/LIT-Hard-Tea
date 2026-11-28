# Genera datos.js para el dashboard LIT Hard Tea · Mantenimiento (nov 2026 – ene 2027).
# Lee los volcados de las pestañas Data_FB_MANT_Ads (fb), Data_GA_MANT_VIDEO_Ads (yt) y Data_GA_MANT_DISPLAY_Ads (gdn)
# desde la carpeta que se pase como argumento. Uso: python3 mantenimiento/datos/build_data.py /ruta/a/volcados
import json, os, sys, re, datetime as dt, collections
D0 = os.path.dirname(os.path.abspath(__file__)); SRC = sys.argv[1] if len(sys.argv) > 1 else D0
def L(f):
    o = json.load(open(os.path.join(SRC, f + '.json'), encoding='utf-8')); return o['values'] if isinstance(o, dict) else o
g = lambda r, i: r[i] if i < len(r) else ''
def N(x):
    s = str(x or '').replace(',', '').strip()
    if not s: return 0.0
    if re.fullmatch(r'\d{4}-\d\d-\d\d', s): return float((dt.date.fromisoformat(s) - dt.date(1899, 12, 30)).days)
    return float(s.rstrip('%')) / 100 if s.endswith('%') else float(s)
I = lambda x: int(round(N(x)))
fb, yt, gd = L('fb'), L('yt'), L('gdn')

def block(V, title):
    """Índice de la columna 'Date' del bloque cuyo encabezado contiene title."""
    h = V[0]; s = [i for i, x in enumerate(h) if title in x.replace('\n', ' ')][0]; return s + 1
NIC = {'Boaco', 'Carazo', 'Chinandega', 'Chontales', 'Estelí', 'Esteli', 'Granada', 'Jinotega', 'León', 'Leon', 'Madriz', 'Managua', 'Masaya', 'Matagalpa',
       'Nueva Segovia', 'Rivas', 'Río San Juan', 'Rio San Juan', 'Región Autónoma del Atlántico Norte', 'Región Autónoma del Atlántico Sur',
       'North Caribbean Coast Autonomous Region', 'South Caribbean Coast Autonomous Region'}
REG = {'Región Autónoma del Atlántico Norte': 'RACCN', 'North Caribbean Coast Autonomous Region': 'RACCN', 'Región Autónoma del Atlántico Sur': 'RACCS',
       'South Caribbean Coast Autonomous Region': 'RACCS', 'Leon': 'León', 'Esteli': 'Estelí', 'Rio San Juan': 'Río San Juan'}
reg = lambda x: REG.get(x.replace(' Department', ''), x.replace(' Department', ''))
GEN = {'male': 'Hombres', 'female': 'Mujeres', 'MALE': 'Hombres', 'FEMALE': 'Mujeres'}
age = lambda x: {'65_UP': '65+'}.get(x, x.replace('_', '-'))
def dem(V, gi, ai, ri, n=1):
    col = lambda i: [[g(r, i)] + [I(g(r, i + 1 + j)) for j in range(n)] for r in V[1:] if g(r, i)]
    return dict(genero=[[GEN[x[0]]] + x[1:] for x in col(gi) if x[0] in GEN], edad=sorted([[age(x[0])] + x[1:] for x in col(ai) if x[0] not in ('Unknown', 'UNDETERMINED')]),
                region=sorted([[reg(x[0])] + x[1:] for x in col(ri) if x[0].replace(' Department', '') in NIC], key=lambda x: -x[1]))

diario = []
# Meta por plataforma (bloques FB e IG, con costo)
for title, red in (('LIT_MANT_FB_META_ADS', 'Facebook'), ('LIT_MANT_IG_META_ADS', 'Instagram')):
    d = block(fb, title)
    for r in fb[1:]:
        if g(r, d):
            diario.append(dict(canal='Meta', red=red, campana=r[d + 1], fecha=r[d], alcance=I(r[d + 2]), impresiones=I(r[d + 3]), interacciones=I(r[d + 4]),
                               views=I(r[d + 6]), costo=round(N(r[d + 7]), 2), thruplays=I(r[d + 9])))
d = block(yt, 'LIT_MANT_GA_VIDEO_ADS')
for r in yt[1:]:
    if g(r, d): diario.append(dict(canal='Google', red='YouTube', campana=r[d + 1], fecha=r[d], alcance=I(r[d + 2]), impresiones=I(r[d + 3]), views=I(r[d + 4]), costo=round(N(r[d + 6]), 2), clics=I(r[d + 7])))
d = block(gd, 'LIT_MANT_GA_GDN_ADS')
for r in gd[1:]:
    if g(r, d): diario.append(dict(canal='Google', red='Display', campana=r[d + 1], fecha=r[d], alcance=I(r[d + 2]), impresiones=I(r[d + 3]), costo=round(N(r[d + 4]), 2), clics=I(r[d + 5])))
diario.sort(key=lambda x: (x['fecha'], x['red']))

# Alcance / usuarios, frecuencia y CPM de la campaña (no se suman entre días)
def nuevo(V, title, ri, fi, ci):
    d = block(V, title); r = next((r for r in V[1:] if g(r, d - 1 + ri)), None)
    return dict(alcance=I(r[d - 1 + ri]), frecuencia=N(r[d - 1 + fi]), cpm=N(r[d - 1 + ci])) if r else None
res = dict(meta=nuevo(fb, 'LIT_MANT_META_ADS', 12, 10, 11), facebook=nuevo(fb, 'LIT_MANT_FB_META_ADS', 13, 11, 12), instagram=nuevo(fb, 'LIT_MANT_IG_META_ADS', 13, 11, 12),
           youtube=nuevo(yt, 'LIT_MANT_GA_VIDEO_ADS', 11, 9, 10), display=nuevo(gd, 'LIT_MANT_GA_GDN_ADS', 11, 10, 9))

# Creativos
cre = collections.OrderedDict()
d = block(fb, 'LIT_Behaviour_MANT_META_ADS')
for r in sorted([r for r in fb[1:] if g(r, d)], key=lambda r: r[d]):
    n = r[d + 2]; p = {'facebook': 'Facebook', 'instagram': 'Instagram'}.get(r[d + 3], 'Otras')
    o = cre.setdefault(n, dict(anuncio=n, url=r[d + 1], impresiones=0, interacciones=0, plat={'Facebook': 0, 'Instagram': 0, 'Otras': 0}, desde=r[d], hasta=r[d]))
    o['impresiones'] += I(r[d + 5]); o['interacciones'] += I(r[d + 6]); o['plat'][p] += I(r[d + 5]); o['hasta'] = r[d]; o['url'] = r[d + 1] or o['url']
vid = collections.OrderedDict(); d = block(yt, 'LIT_MANT_VIDEO_GA_ADS')
for r in yt[1:]:
    if g(r, d):
        o = vid.setdefault(r[d + 2], dict(video=r[d + 2], impresiones=0, views=0, costo=0.0, desde=r[d], hasta=r[d]))
        o['impresiones'] += I(r[d + 5]); o['views'] += I(r[d + 3]); o['costo'] = round(o['costo'] + N(r[d + 4]) * I(r[d + 3]), 2); o['desde'] = min(o['desde'], r[d]); o['hasta'] = max(o['hasta'], r[d])
ban = collections.OrderedDict(); d = block(gd, 'LIT_MANT_GDN_GA_ADS')
for r in gd[1:]:
    if g(r, d):
        o = ban.setdefault(r[d + 1], dict(img=r[d + 1], nombre=r[d + 2], impresiones=0, clics=0, desde=r[d], hasta=r[d]))
        o['impresiones'] += I(r[d + 3]); o['clics'] += I(r[d + 4]); o['desde'] = min(o['desde'], r[d]); o['hasta'] = max(o['hasta'], r[d])

aud = dict(meta=dem(fb, block(fb, 'LIT_MANT_DEM_FB'), block(fb, 'LIT_MANT_DEM_FB') + 3, block(fb, 'LIT_MANT_DEM_FB') + 6),
           instagram=dem(fb, block(fb, 'LIT_MANT_DEM_IG'), block(fb, 'LIT_MANT_DEM_IG') + 3, block(fb, 'LIT_MANT_DEM_IG') + 6),
           youtube=dem(yt, block(yt, 'LIT_MANT_VIDEO_DEM_GA'), block(yt, 'LIT_MANT_VIDEO_DEM_GA') + 4, block(yt, 'LIT_MANT_VIDEO_DEM_GA') + 8, 2),
           display=dem(gd, block(gd, 'LIT_MANT_GDN_DEM_GA'), block(gd, 'LIT_MANT_GDN_DEM_GA') + 4, block(gd, 'LIT_MANT_GDN_DEM_GA') + 8, 2))

KPI = dict(Instagram=dict(alcance=400000, impresiones=2293650, frecuencia=3), Facebook=dict(alcance=594871, impresiones=6520067, frecuencia=3),
           YouTube=dict(views=239724, impresiones=2000000, frecuencia=3), Display=dict(impresiones=1666000))
ult = max(x['fecha'] for x in diario)
out = dict(actualizado=ult, diario=diario, resumen=res, kpi=KPI, cre_meta=list(cre.values()), cre_video=list(vid.values()), cre_display=list(ban.values()), audiencia=aud)
open(os.path.join(D0, '..', 'datos.js'), 'w', encoding='utf-8').write('window.LM_DATA = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
t = collections.defaultdict(lambda: [0, 0.0])
for r in diario: t[r['red']][0] += r['impresiones']; t[r['red']][1] += r['costo']
print('ultimo', ult, {k: (v[0], round(v[1], 2)) for k, v in t.items()}, res, len(cre), len(vid), len(ban))
