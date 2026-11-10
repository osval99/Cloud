"""Arma la planilla Excel de la búsqueda de SSD externos en Mercado Libre.

Uso:
    python armar_planilla.py <datos.json> <verificados.json> <salida.xlsx>

- datos.json: lista de filas [id, titulo, precio, vendedor, envio_gratis, internacional,
  marca, modelo, capacidad_gb, motivo_descarte] tal como la devuelve el paso de filtrado
  en el navegador (ver CLAUDE.md). También acepta el archivo que guarda Claude Code
  cuando la salida es muy larga (texto con <<DATA>>...<<END>>).
- verificados.json: datos leídos entrando a cada publicación del top (vendedor real, etc.).
"""
import json
import re
import sys
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

LINK = "https://articulo.mercadolibre.com.ar/MLA-{}"
# Compras internacionales (courier, hasta USD 400): el precio publicado NO incluye IVA.
# Se suma 21% como estimación; el total exacto lo muestra Mercado Libre antes de pagar.
# Si la compra supera USD 400 se agregan derechos de importación (no calculados aquí).
IVA_INTERNACIONAL = 0.21


def total_estimado(precio, internacional):
    if not precio:
        return None
    return round(precio * (1 + IVA_INTERNACIONAL)) if internacional else precio


def leer_datos(ruta):
    texto = open(ruta, encoding="utf-8").read()
    if "<<DATA>>" in texto:
        # Archivo guardado por Claude Code: JSON con [{type, text}], text = '"<<DATA>>[...]<<END>>"'
        try:
            texto = json.loads(texto)[0]["text"]
            if texto.startswith('"'):
                texto = json.JSONDecoder().raw_decode(texto)[0]  # ignora el texto que sigue
        except (ValueError, KeyError, IndexError):
            pass
        texto = re.search(r"<<DATA>>(.*)<<END>>", texto, re.S).group(1)
    return json.loads(texto)


def ancho_columnas(ws, anchos):
    for i, w in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def encabezado(ws, columnas):
    ws.append(columnas)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2D3277")
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"


def poner_link(celda, url):
    celda.value = url
    celda.hyperlink = url
    celda.font = Font(color="0563C1", underline="single")


def main(ruta_datos, ruta_verif, salida):
    filas = leer_datos(ruta_datos)
    verif = json.load(open(ruta_verif, encoding="utf-8"))
    # Descartes detectados entrando a la publicación (p. ej. la ficha dice otra marca
    # que el título). Formato en verificados.json: "descartes_ficha": {"<id sin MLA>": "motivo"}
    descartes = verif.get("descartes_ficha", {})
    filas = [f[:9] + [descartes[str(f[0])]] if str(f[0]) in descartes else f for f in filas]
    wb = Workbook()

    # --- Top 10 verificado ---
    ws = wb.active
    ws.title = "Top 10"
    cols = ["#", "Marca", "Modelo", "Capacidad", "Precio publicado ($)", "Total estimado con IVA ($)",
            "Vendedor", "Envío gratis", "Origen", "Título de la publicación", "Link"]
    encabezado(ws, cols)
    top = sorted(verif["top"], key=lambda v: total_estimado(v["precio"], v["origen"] != "Local"))
    for i, v in enumerate(top, 1):
        ws.append([i, v["marca"], v["modelo"], v["capacidad"], v["precio"],
                   total_estimado(v["precio"], v["origen"] != "Local"), v["vendedor"],
                   "Sí" if v["envio_gratis"] else "No", v["origen"], v["titulo"], None])
        poner_link(ws.cell(ws.max_row, 11), v["link"])
    ancho_columnas(ws, [4, 10, 16, 10, 12, 14, 22, 8, 20, 55, 60])

    # --- Todos los válidos ---
    validos = [f for f in filas if not f[9]]
    descartados = [f for f in filas if f[9]]
    for nombre, lista, con_motivo in (("Válidos", validos, False), ("Descartados", descartados, True)):
        ws = wb.create_sheet(nombre)
        cols = ["Marca", "Modelo", "Capacidad (GB)", "Precio publicado ($)", "Total estimado con IVA ($)", "$ por GB", "Vendedor (listado)",
                "Envío gratis", "Internacional", "Título", "Link"]
        if con_motivo:
            cols.insert(0, "Motivo de descarte")
        encabezado(ws, cols)
        for f in sorted(lista, key=lambda x: total_estimado(x[2], x[5]) or 0):
            idp, tit, precio, vend, gratis, intl, marca, modelo, cap, motivo = f
            total = total_estimado(precio, intl)
            fila = [marca or "", modelo or "", cap or None, precio, total,
                    round(total / cap) if total and cap else None,
                    vend or "(no figura en el listado)", "Sí" if gratis else "No",
                    "Sí" if intl else "No", tit, None]
            if con_motivo:
                fila.insert(0, motivo)
            ws.append(fila)
            poner_link(ws.cell(ws.max_row, len(cols)), LINK.format(idp))
        base = [10, 16, 10, 12, 14, 9, 22, 8, 8, 60, 45]
        ancho_columnas(ws, ([38] + base) if con_motivo else base)
        ws.auto_filter.ref = ws.dimensions
        col_precio = 5 if con_motivo else 4
        for fila in ws.iter_rows(min_row=2, min_col=col_precio, max_col=col_precio + 2):
            for c in fila:
                c.number_format = "#,##0"

    # --- Info ---
    ws = wb.create_sheet("Info")
    for linea in verif["info"]:
        ws.append([linea])
    ws.append([])
    ws.append([f"Publicaciones leídas: {len(filas)}  |  válidas: {len(validos)}  |  descartadas: {len(descartados)}"])
    ws.append([f"Planilla generada el {date.today():%d/%m/%Y}"])
    ws.column_dimensions["A"].width = 120

    for col in ("E", "F"):
        for c in wb["Top 10"][col][1:]:
            c.number_format = "#,##0"
    wb.save(salida)
    print(f"OK: {salida} | leídas {len(filas)}, válidas {len(validos)}, descartadas {len(descartados)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
