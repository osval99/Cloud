"""Baja los comprobantes de Planeta (facturas y notas de crédito) que avisa comfiar por mail y arma un resumen.

Lee por IMAP los mails de acliente.eplaneta@la.comfiar.com.ar a mandrake.dis desde una fecha, sigue el link
"DESCARGAR" de cada uno, guarda el PDF en facturas/planeta/ y anota cuenta, tipo, número, fecha, total,
ejemplares y condición de venta en facturas/planeta/resumen.csv. Los recibos se saltean. No envía nada.

La clave de aplicación se lee de "~/Documentos/CLAUDE MIO/codigos gmail.odt" y nunca se muestra.

Uso:  python3 -I planeta_comprobantes.py [--desde dd/mm/aaaa] [--etiqueta "Facturas de Planeta"]
"""
import csv
import email
import email.policy
import html
import http.cookiejar
import imaplib
import re
import subprocess
import sys
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

CUENTA = "mandrake.dis@gmail.com"
REMITENTE = "acliente.eplaneta@la.comfiar.com.ar"
CLAVES = Path.home() / "Documentos" / "CLAUDE MIO" / "codigos gmail.odt"
SALIDA = Path.home() / "fierro-claude" / "facturas" / "planeta"
BASE = "https://app.comfiar.com.ar/"
MESES = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def leer_clave(etiqueta):
    xml = zipfile.ZipFile(CLAVES).read("content.xml").decode("utf-8")
    texto = re.sub(r"<[^>]+>", "", re.sub(r"</text:p>|<text:line-break/>", "\n", xml))
    for linea in texto.splitlines():
        if linea.strip().lstrip("﻿").startswith(etiqueta):
            m = re.search(r"\b([a-z]{4} ?[a-z]{4} ?[a-z]{4} ?[a-z]{4})\b", linea)
            if m:
                return m.group(1).replace(" ", "")
    sys.exit(f"No encontré la clave con etiqueta {etiqueta!r} en {CLAVES}")


def carpeta(M, atributo):
    for linea in M.list()[1]:
        linea = linea.decode()
        if atributo in linea:
            return linea.rsplit(' "/" ', 1)[1]
    sys.exit(f"No encontré la carpeta {atributo}")


def bajar_pdf(link):
    """Abre la página de descarga de comfiar (con su sesión) y baja el PDF que enlaza."""
    abridor = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    abridor.addheaders = [("User-Agent", "Mozilla/5.0")]
    pagina = abridor.open(link, timeout=60).read().decode("utf-8", "replace")
    m = re.search(r"Descarga\.aspx\?accion=file&(?:amp;)?archivo=[^\"'<> ]+", pagina)
    if not m:
        return None
    pdf = abridor.open(urllib.request.Request(BASE + html.unescape(m.group(0)), headers={"Referer": link}),
                       timeout=60).read()
    return pdf if pdf.startswith(b"%PDF") else None


def datos(texto):
    def buscar(patron, grupo=1):
        m = re.search(patron, texto, re.M)
        return m.group(grupo).strip() if m else ""
    return {
        "cuenta": buscar(r"^\s*0*(\d{5,9})\s+SHCOLER"),
        "tipo": buscar(r"COMPROBANTE:\s+(FACTURA|NOTA DE CREDITO|NOTA DE DEBITO)"),
        "numero": buscar(r"N[º°]:\s*(\d{4}-\d{8})"),
        "fecha": buscar(r"COMPROBANTE:.*?FECHA:\s+(\d\d/\d\d/\d{4})"),
        "vencimiento": buscar(r"^\s*Vencimiento :\s+(\d\d/\d\d/\d{4})"),
        "total": buscar(r"^\s*TOTAL(?: FACTURA)?\s{3,}([\d.,]+)\s*$"),
        "descuento": buscar(r"Descuento \.+\s*([\d,]+%)"),
        "ejemplares": buscar(r"TOTAL EJEMPLARES\s+(\d+)"),
        "condicion": buscar(r"CONDICIONES DE VENTA:\s+(.+?)\s{2,}|CONDICIONES DE VENTA:\s+(.+)$"),
        "corresponde": buscar(r"CORRESPONDE A\s+(.+?)$"),
        "asociados": " ".join(re.findall(r"^\s*(F[A-Z]? \d{4}-\d+)\s*$", texto, re.M)),
    }


def main():
    desde = sys.argv[sys.argv.index("--desde") + 1] if "--desde" in sys.argv else "08/09/2026"
    etiqueta = sys.argv[sys.argv.index("--etiqueta") + 1] if "--etiqueta" in sys.argv else "Facturas de Planeta"
    d = datetime.strptime(desde, "%d/%m/%Y")
    SALIDA.mkdir(parents=True, exist_ok=True)

    M = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        M.login(CUENTA, leer_clave(etiqueta))
    except imaplib.IMAP4.error:
        sys.exit(f"Gmail rechazó la clave {etiqueta!r}. Probá con --etiqueta \"Bajar Adjunto Novedades\".")
    M.select(carpeta(M, "\\All"), readonly=True)
    nums = M.search(None, "FROM", REMITENTE, "SINCE", f"{d.day:02d}-{MESES[d.month - 1]}-{d.year}")[1][0].split()

    filas, vistos = [], set()
    for n in nums:
        msg = email.message_from_bytes(M.fetch(n, "(BODY.PEEK[])")[1][0][1], policy=email.policy.default)
        asunto = str(msg["Subject"])
        if "Recibo" in asunto:
            continue
        cuerpo = msg.get_body(("html", "plain")).get_content()
        links = re.findall(r"https://app\.comfiar\.com\.ar/FormDescargaFactura\.aspx\?edit=[^\"'<> )]+", cuerpo)
        nro = re.search(r"Nro (\d{4}-\d{8})", asunto)
        clave_c = (asunto.split("(")[1].split(")")[0] if "(" in asunto else "", nro.group(1) if nro else asunto)
        if clave_c in vistos or not links:
            continue
        vistos.add(clave_c)
        pdf = None
        for link in dict.fromkeys(html.unescape(l) for l in links):
            pdf = bajar_pdf(link)
            if pdf:
                break
        if not pdf:
            print(f"✗ No pude bajar {asunto}")
            continue
        tipo = "NC" if "Crédito" in clave_c[0] else "FC" if "Factura" in clave_c[0] else "ND"
        archivo = SALIDA / f"{tipo} {clave_c[1]}.pdf"
        archivo.write_bytes(pdf)
        texto = subprocess.run(["pdftotext", "-layout", str(archivo), "-"], capture_output=True, text=True).stdout
        fila = {"archivo": archivo.name, "comprobante": clave_c[0], **datos(texto)}
        filas.append(fila)
        print(f"✓ {fila['cuenta']:>8} | {clave_c[0]:<18} {fila['numero']} | {fila['fecha']} | $ {fila['total']:>14} | "
              f"{fila['ejemplares']:>4} ej | {fila['condicion']}")
    M.logout()

    if filas:
        with open(SALIDA / "resumen.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
        print(f"\n{len(filas)} comprobantes en {SALIDA} (resumen.csv)")


if __name__ == "__main__":
    main()
