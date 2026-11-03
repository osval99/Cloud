#!/usr/bin/env python3
"""Pedido de reposición a partir del CSV de la vista "Reposicion" de Fierro.

Velocidad real = ventas en el período / días con stock en el período.
Velocidad usada = confianza × real + (1 − confianza) × (ventas / días del período),
con confianza = días con stock / (días con stock + K): con pocos días con stock la
proyección se acerca al promedio del período; con muchos, a la velocidad real.
Necesidad = velocidad usada × (días de cobertura + días de demora) + stock de seguridad.
A pedir = necesidad − stock actual − cantidad ya pedida (redondeado hacia arriba).

Uso: python3 -I reposicion.py exportaciones/<export.csv> --desde dd/mm/aaaa --hasta dd/mm/aaaa [--cobertura 90] [--demora 10]
"""
import argparse, csv, io, math, os, re, subprocess, sys
from datetime import datetime
from collections import defaultdict

# Parámetros acordados con el usuario (cobertura 90 y K=15 confirmados; demora 10 es supuesto)
COBERTURA_DIAS = 90      # para cuántos días debe alcanzar el pedido (pedido por el usuario: 3 meses)
DEMORA_DIAS = 10         # días que tarda en llegar
SEGURIDAD_DIAS = 0       # colchón extra en días de venta
MIN_DIAS_CON_STOCK = 7   # con menos días la velocidad no es confiable → revisar a mano
PERIODO_DIAS = 93        # se recalcula con --desde/--hasta
K_CONFIANZA = 15         # días con stock en los que la confianza en la velocidad real llega al 50 %


def confianza(dias):
    return dias / (dias + K_CONFIANZA) if dias > 0 else 0.0


def leer(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "latin-1"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    dialect = csv.Sniffer().sniff(txt[:5000], delimiters=",;\t")
    return list(csv.DictReader(io.StringIO(txt), dialect=dialect))


def num(v):
    """'$ 31.600,00' / '1.234' / '-2' → float. Vacío → 0."""
    v = (v or "").strip().replace("$", "").replace(" ", "")
    if not v:
        return 0.0
    if "," in v:
        v = v.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", v):
        v = v.replace(".", "")
    try:
        return float(v)
    except ValueError:
        return 0.0


def col(row, *prefijos):
    for k in row:
        if k and any(k.strip().lower().startswith(p.lower()) for p in prefijos):
            return row[k]
    return ""


NO_REPONIBLE = re.compile(r"usad|gift card|bolsa|funda|vinilo", re.I)
CARACTER = "LINEA"  # solo libros de línea (no usados, oferta, outlet)


def excluir(r):
    """Motivo por el que la fila no entra en la reposición, o '' si entra."""
    if CARACTER and col(r, "Carácter", "Caracter").strip().upper() != CARACTER:
        return f"carácter distinto de {CARACTER}"
    if not col(r, "ISBN").strip():
        return "sin ISBN (usado / ejemplar único)"
    texto = " ".join([col(r, "Título", "Titulo"), col(r, "Proveedor")])
    if NO_REPONIBLE.search(texto):
        return "no reponible (usado, gift card, bolsa…)"
    return ""


def calcular(rows):
    out = []
    for r in rows:
        if excluir(r):
            continue
        ventas = num(col(r, "Ventas en el periodo"))
        dias = num(col(r, "Días con stock", "Dias con stock"))
        stock = num(col(r, "Stock (esta suc"))
        pedida = num(col(r, "Cant. Pedida"))
        if ventas <= 0:
            continue
        estado = "ok"
        if dias <= 0:
            vel = ventas / PERIODO_DIAS
            estado = "sin días con stock (vendido sin stock / reservas)"
        else:
            vel = ventas / dias
            if dias < MIN_DIAS_CON_STOCK:
                estado = f"pocos días con stock ({int(dias)})"
        if stock < 0:
            estado = (estado + "; " if estado != "ok" else "") + f"stock negativo ({int(stock)}): se usa el promedio del período"
        prov = col(r, "Proveedor")
        if "(BAJA)" in prov.upper():
            estado = (estado + "; " if estado != "ok" else "") + "proveedor dado de baja"
        # Stock negativo = se vendió mercadería no ingresada: los días con stock no reflejan
        # la disponibilidad física, así que se usa el promedio del período completo.
        conf = 0.0 if stock < 0 else confianza(dias)
        vel_usada = conf * vel + (1 - conf) * ventas / PERIODO_DIAS
        necesidad = vel_usada * (COBERTURA_DIAS + DEMORA_DIAS + SEGURIDAD_DIAS)
        if ventas <= 1:
            necesidad = 1.0  # una sola venta: mantener 1 ejemplar, no proyectar
        disponible = max(stock, 0) + pedida
        a_pedir = max(0, math.ceil(necesidad - disponible - 1e-9))
        out.append({
            "ISBN": col(r, "ISBN"), "Título": col(r, "Título", "Titulo"), "Autor": col(r, "Autor"),
            "Editorial": col(r, "Editorial"), "Proveedor": col(r, "Proveedor") or "(sin proveedor)",
            "Carácter": col(r, "Carácter", "Caracter"),
            "Precio": num(col(r, "Precio")), "Stock": stock, "Ya pedido": pedida,
            "Consignado": num(col(r, "Consignado")), "Firme": num(col(r, "Firme")),
            "Ventas 3m": ventas, "Días con stock": dias,
            "Ventas/día real": round(vel, 4),
            "Ventas/día ingenua": round(ventas / PERIODO_DIAS, 4),
            "Confianza": round(conf, 2), "Ventas/día usada": round(vel_usada, 4),
            "Necesidad": round(necesidad, 1), "A pedir": a_pedir, "Revisar": estado,
            "Últ. venta": col(r, "Fecha últ. venta"), "Últ. compra": col(r, "Fecha últ. compra"),
        })
    return out


def escribir(path, filas, campos):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)


def a_xlsx(csv_path):
    """Convierte un CSV (UTF-8, decimales con punto) a .xlsx con LibreOffice."""
    subprocess.run(["soffice", "--headless", "--infilter=CSV:44,34,76,1,,1033", "--convert-to", "xlsx",
                    "--outdir", os.path.dirname(os.path.abspath(csv_path)), csv_path],
                   capture_output=True, check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Pedido de reposición desde el CSV de la vista Reposicion")
    ap.add_argument("csv", help="exportación de Fierro (Catálogo > Libros, panel Ventas, vista Reposicion)")
    ap.add_argument("--desde", required=True, help="inicio del período de ventas, dd/mm/aaaa")
    ap.add_argument("--hasta", required=True, help="fin del período de ventas, dd/mm/aaaa")
    ap.add_argument("--cobertura", type=int, default=COBERTURA_DIAS, help="días que debe cubrir el pedido")
    ap.add_argument("--demora", type=int, default=DEMORA_DIAS, help="días de demora de entrega")
    ap.add_argument("--salida", default=None, help="prefijo de los archivos de salida (por defecto en pedidos/)")
    args = ap.parse_args()
    d0, d1 = (datetime.strptime(x, "%d/%m/%Y").date() for x in (args.desde, args.hasta))
    PERIODO_DIAS = (d1 - d0).days + 1
    COBERTURA_DIAS, DEMORA_DIAS = args.cobertura, args.demora
    base = args.salida or os.path.join(os.path.dirname(os.path.abspath(__file__)), "pedidos",
                                       f"pedido_reposicion_{CARACTER.lower()}_{d1:%Y-%m-%d}")
    filas = calcular(leer(args.csv))
    pedir = sorted((f for f in filas if f["A pedir"] > 0), key=lambda f: (f["Proveedor"], f["Título"]))
    por_prov = defaultdict(list)
    for f in pedir:
        por_prov[f["Proveedor"]].append(f)
    resumen = [{"Proveedor": p, "Títulos": len(fs), "Ejemplares": sum(f["A pedir"] for f in fs),
                "Importe a PVP": round(sum(f["A pedir"] * f["Precio"] for f in fs)),
                "Títulos a revisar": sum(1 for f in fs if f["Revisar"] != "ok")}
               for p, fs in sorted(por_prov.items(), key=lambda kv: -sum(f["A pedir"] for f in kv[1]))]
    escribir(f"{base}_detalle.csv", pedir, list(pedir[0]))
    escribir(f"{base}_resumen.csv", resumen, list(resumen[0]))
    for sufijo in ("_detalle.csv", "_resumen.csv"):
        a_xlsx(base + sufijo)
    print(f"Período: {args.desde}–{args.hasta} ({PERIODO_DIAS} días) | cobertura {COBERTURA_DIAS} + "
          f"demora {DEMORA_DIAS} | K={K_CONFIANZA}")
    print(f"Títulos analizados: {len(filas)} | a reponer: {len(pedir)} | "
          f"ejemplares: {sum(f['A pedir'] for f in pedir)} | proveedores: {len(por_prov)} | "
          f"importe a PVP: ${sum(r['Importe a PVP'] for r in resumen):,.0f}".replace(",", "."))
    print(f"Archivos: {base}_detalle.xlsx y {base}_resumen.xlsx")
    for r in resumen[:15]:
        print(f"  {r['Proveedor'][:40]:40} {r['Títulos']:4} títulos {r['Ejemplares']:5} ej.")
