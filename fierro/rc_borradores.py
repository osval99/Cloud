"""Deja en Gmail (mandrake.dis) borradores de respuesta a los pedidos de RC con la factura en PDF.

Por defecto no envía nada: agrega borradores (IMAP APPEND a la carpeta de borradores) en el hilo del mail
original. Con --enviar manda la respuesta directamente (SMTP de Gmail), también en el hilo. Sin dependencias externas.

La clave de aplicación se lee de "~/Documentos/CLAUDE MIO/codigos gmail.odt" (línea cuya etiqueta
se pasa con --etiqueta) y nunca se muestra.

Uso:  python3 -I rc_borradores.py [--probar] [--enviar] [--etiqueta "Facturas de Planeta"]
      --probar: entra, busca los mails y muestra qué haría, sin crear borradores ni enviar.
      --enviar: envía las respuestas en vez de dejar borradores (no reenvía si ya hay una respuesta enviada).
"""
import email
import email.policy
import imaplib
import re
import smtplib
import sys
import time
import zipfile
from email.message import EmailMessage
from email.utils import formatdate, make_msgid, parseaddr
from pathlib import Path

CUENTA = "mandrake.dis@gmail.com"
CLAVES = Path.home() / "Documentos" / "CLAUDE MIO" / "codigos gmail.odt"
RC = Path.home() / "Documentos" / "RC"
RC_MAIL = "rcquilmes@hotmail.com"

# Id de Gmail del mail de RC (hex, como lo muestra la API) → factura y texto de la respuesta.
RESPUESTAS = [
    # Id None = mail nuevo (no respuesta), con el asunto del 4.º elemento; 5.º opcional = destinatario (por defecto RC,
    # y si es otro va con copia a RC).
    (None, Path.home() / "Documentos" / "Saldos PLaneta 05102026" / "Malapalabra Nota de Credito 14-00000020.pdf",
     "Estimado/a Malapalabra:\nAdjuntamos la Nota de Crédito C 0014-00000020, que anula la Factura C 0014-00000457 (precio unitario equivocado). La reemplaza la Factura C 0014-00000458 que les enviamos hoy.\nSaludos,\nMandrake Libros\n",
     "Nota de Crédito C 0014-00000020 - Mandrake Libros", "casalibrera@gmail.com"),
]


def respuesta(M, todos, borradores, gid, enviar):
    """Arma la cabecera de la respuesta en el hilo del mail gid (o None si no hay que mandarla)."""
    M.select(todos, readonly=True)
    nums = M.search(None, "X-GM-MSGID", str(int(gid, 16)))[1][0].split()
    if not nums:
        print(f"✗ No encontré el mail {gid}")
        return None
    cab = M.fetch(nums[0], "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID REFERENCES SUBJECT FROM)])")[1][0][1]
    orig = email.message_from_bytes(cab, policy=email.policy.default)
    msgid = orig["Message-ID"].strip()
    if enviar:
        M.select(todos, readonly=True)
        if M.search(None, "FROM", CUENTA, "HEADER", "In-Reply-To", f'"{msgid}"')[1][0].split():
            print(f"= Ya se respondió «{orig['Subject']}»: no envío otra vez")
            return None
    else:
        M.select(borradores, readonly=True)
        if M.search(None, "HEADER", "In-Reply-To", f'"{msgid}"')[1][0].split():
            print(f"= Ya hay un borrador que responde a «{orig['Subject']}»: no creo otro")
            return None
    r = EmailMessage()
    r["From"] = CUENTA
    r["To"] = parseaddr(str(orig["From"]))[1]
    r["Subject"] = "Re: " + str(orig["Subject"])
    r["In-Reply-To"] = msgid
    r["References"] = (str(orig["References"] or "") + " " + msgid).strip()
    return r


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
    """Nombre de la carpeta de Gmail con ese atributo (\\Drafts, \\All), sea cual sea el idioma."""
    for linea in M.list()[1]:
        linea = linea.decode()
        if atributo in linea:
            return linea.rsplit(' "/" ', 1)[1]
    sys.exit(f"No encontré la carpeta {atributo}")


def main():
    probar = "--probar" in sys.argv
    enviar = "--enviar" in sys.argv
    etiqueta = sys.argv[sys.argv.index("--etiqueta") + 1] if "--etiqueta" in sys.argv else "Facturas de Planeta"

    clave = leer_clave(etiqueta)
    M = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        M.login(CUENTA, clave)
    except imaplib.IMAP4.error:
        sys.exit(f"Gmail rechazó la clave {etiqueta!r} para {CUENTA}. Probá con --etiqueta \"Bajar Adjunto Novedades\".")
    todos, borradores = carpeta(M, "\\All"), carpeta(M, "\\Drafts")

    for gid, pdf, cuerpo, *resto in RESPUESTAS:
        if gid is None:
            asunto = resto[0]
            M.select(todos if enviar else borradores, readonly=True)
            M.literal = asunto.encode("utf-8")  # el asunto puede tener acentos
            if M.search("UTF-8", "FROM", CUENTA, "SUBJECT")[1][0].split():
                print(f"= Ya hay un mail {'enviado' if enviar else 'borrador'} «{asunto}»: no lo repito")
                continue
            r = EmailMessage()
            r["From"] = CUENTA
            r["To"] = resto[1] if len(resto) > 1 else RC_MAIL
            if r["To"] != RC_MAIL:
                r["Cc"] = RC_MAIL
            r["Subject"] = asunto
        else:
            r = respuesta(M, todos, borradores, gid, enviar)
            if r is None:
                continue
        r["Date"] = formatdate(localtime=True)
        r["Message-ID"] = make_msgid(domain="gmail.com")
        r.set_content(cuerpo)
        r.add_attachment(pdf.read_bytes(), maintype="application", subtype="pdf", filename=pdf.name)

        print(f"{'(prueba) ' if probar else ''}→ {r['To']} | {r['Subject']} | adjunto {pdf.name} ({pdf.stat().st_size // 1024} KB)")
        if probar:
            continue
        if enviar:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as S:
                S.login(CUENTA, clave)
                S.send_message(r)
            print("  enviado")
        else:
            M.append(borradores, "(\\Draft)", imaplib.Time2Internaldate(time.time()), r.as_bytes())
            print("  borrador creado")
    M.logout()


if __name__ == "__main__":
    main()
