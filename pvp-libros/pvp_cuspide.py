import csv, json, re, sys, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
src, out = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src, encoding='utf-8-sig')))
def get(url):
    for i in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40)
            return r.geturl(), r.read().decode('utf8', 'replace')
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    return None, f'ERROR {err}'
def products(h):
    res = []
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        try: d = json.loads(m.group(1))
        except Exception: continue
        for n in d.get('@graph', [d]) if isinstance(d, dict) else d:
            if isinstance(n, dict) and n.get('@type') == 'Product': res.append(n)
    return res
def look(ean):
    url, h = get('https://cuspide.com/?s=%s&post_type=product' % ean)
    if url is None: return dict(pvp=None, estado=h, url='')
    for p in products(h):
        if str(p.get('sku')) == ean:
            off = p.get('offers') or []
            off = off[0] if isinstance(off, list) and off else off
            price = None
            for ps in (off.get('priceSpecification') or []):
                if ps.get('price'): price = float(ps['price']); break
            if price is None and off.get('price'): price = float(off['price'])
            avail = (off.get('availability') or '').rsplit('/', 1)[-1]
            return dict(pvp=price, estado=avail or 'ok', url=p.get('url', url))
    return dict(pvp=None, estado='no encontrado' if '/producto/' not in url else 'sin precio', url=url if '/producto/' in url else '')
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(look, [r['EAN'].strip() for r in rows]))
json.dump([dict(r, **x) for r, x in zip(rows, res)], open(out, 'w'), ensure_ascii=False, indent=1)
print(sum(1 for x in res if x['pvp']), 'con precio de', len(res))
