# Bot de WhatsApp — La Mandrágora

Bot que responde precio, stock y horarios, y asesora sobre libros usando Google Books.
**Estado: en diseño** (todavía no hay código). El usuario pidió **no avanzar con la implementación** hasta que lo diga.

## Decisiones tomadas (10/11/2026)
- **Número**: el actual del local, con **coexistencia** (app WhatsApp Business + Cloud API en el mismo número).
  - Requiere que el número esté en la app **WhatsApp Business** y conectarlo con un **proveedor autorizado por
    Meta** (Solution Partner / Tech Provider, ej. 360dialog, YCloud). No hay camino directo sin intermediario.
  - Argentina: según fuentes de terceros solo quedan excluidos Nigeria y Sudáfrica; Meta lo confirma al conectar.
  - Se pierden "eliminar para todos" y mensajes temporales; se sincronizan hasta 6 meses de chats individuales.
  - Al conectar se desvinculan los dispositivos: volver a escanear el QR de WhatsApp Web.
- **Atención humana**: desde **WhatsApp Web en el navegador** (la app de WhatsApp para Windows NO está soportada
  en coexistencia). Los mensajes del humano llegan al bot como webhook `smb_message_echoes` → el bot se calla en
  esa conversación.
- **Derivación**: a una persona cuando el cliente lo pide o el bot no sabe responder.
  Fuera de horario: avisa que le van a responder cuando haya alguien.
- **Precio/stock**: arrancar con **exportación CSV diaria de Fierro** (con `cu.py`, ver `fierro/CLAUDE.md`);
  evaluar después "Fierro acceso a datos" (réplica SQL paga). Avisar al cliente que el stock es "al día de hoy".
- **Servidor**: el usuario pidió comparar nube (10/11/2026). Opciones (precios de terceros, sin IVA, a confirmar):
  Google Cloud e2-micro gratis (1 GB RAM, regiones EE.UU.), DigitalOcean desde US$4-6/mes, Hetzner ~€4-5,5/mes,
  Oracle Always Free (gratis, pero puede reclamar VMs inactivas). **Elegido: Google Cloud e2-micro gratis** (confirmado 10/11/2026);
  si queda corto, VPS de US$6. En nube, la PC Linux sube el CSV diario de Fierro. Alternativa: PC Linux + túnel.
- **Horario de atención** (hora Argentina): lunes a viernes 09–20, sábados 10–14. Domingos y **feriados
  nacionales** cerrado. Fuera de ese horario el bot avisa que le responden cuando haya alguien.
  Feriados: tomarlos de una fuente automática (a definir) en vez de cargarlos a mano.
- **Local**: Rioja 1869, Rosario. **Envíos**: solo comprando desde la página web: mandrakelibros.com.ar.
- **Medios de pago**: efectivo, débito, crédito, transferencia, Mercado Pago. Tarjetas bancarias: 3 cuotas sin
  interés. En la página: 10% de descuento con transferencia. Hay promos en el local (definir después).
- **Precio que informa el bot**: LISTA MOSTRADOR.
- **Asesoramiento**: Claude (API de Anthropic) + Google Books API (gratis; cuota a ver en la consola de Google),
  recomendando solo lo que esté en stock.

## Asesoramiento por temas / contenido (análisis 10/11/2026)
- Enfoque propuesto: **catálogo enriquecido propio**. Por cada ISBN en stock se busca una vez (y luego solo los
  nuevos) sinopsis + categorías y se guardan. El bot busca por tema en ese catálogo (búsqueda semántica) y solo
  recomienda lo que hay. No consultar Google en vivo por cada mensaje (cuota y lentitud).
- **Almacenamiento propuesto**: base **SQLite** (un solo archivo, ej. `catalogo.db`) en el servidor de Google Cloud
  (disco gratis 30 GB). Tablas: libros (ISBN, título, autor, editorial, precio, stock, de Fierro) y fichas
  (sinopsis, temas, fuente, fecha). Búsqueda por texto con FTS5; búsqueda semántica (embeddings) opcional después.
  Respaldo: copia diaria a la PC Linux. **No** se versiona en GitHub (son datos). Estimación: ~300 MB para 50.000
  títulos (sin medir; falta saber el tamaño del catálogo).
- Fuentes: Google Books (principal; requiere **clave propia**: sin clave la cuota compartida da 0), Open Library,
  DILVE (España, ONIX, requiere usuario), webs de editoriales; conocimiento de Claude solo como apoyo y avisando.
- **Sin medir todavía** qué % del catálogo tiene sinopsis. Probarlo con 100-200 ISBNs de una exportación de Fierro
  (se conecta con el proyecto `datos-tecnicos-libros/`). En la nube: openlibrary.org bloqueado y Google sin clave.

## Costos (no verificados en fuentes oficiales)
- Meta: respuestas a clientes gratis desde 11/2024 (oficial). Terceros dicen que desde 1/10/2026 hay 1.000
  gratis/mes y luego ~US$0,026 por mensaje de servicio en Argentina. Confirmar en la tarifa de Meta.
- **Twilio (página oficial de soporte)** confirma que desde 10/2026 Meta cobra los mensajes de servicio enviados
  por API. Las respuestas que el humano manda desde la app/WhatsApp Web en coexistencia serían gratis (terceros).
- **Proveedores con coexistencia** (comparado 10/11/2026; todos sin recargo sobre la tarifa de Meta, salvo Twilio):
  - **YCloud**: plan gratis + Growth US$39/mes y Pro US$89/mes (datos de su propia web). Coexistencia anunciada.
    Falta confirmar si el plan gratis incluye API/webhooks y coexistencia. **Recomendado para verificar primero.**
  - **360dialog**: €49/mes por número (Regular), oficial. API pura, pensada para bots propios. Coexistencia sí.
  - **Twilio**: sin cuota fija, US$0,005 por mensaje enviado o recibido + Meta. Soporte de coexistencia sin confirmar.
- developers.facebook.com está bloqueado en la red de las sesiones en la nube: habilitarlo para leer la doc oficial.

## Pendiente (preguntas al usuario)
- ¿Stock solo de La Mandrágora?
- Cuentas: el usuario tiene cuenta personal de Meta (no a nombre de La Mandrágora) y **no** tiene cuenta en la
  consola de Anthropic. Hay que crear un portfolio comercial (Meta Business) a nombre de La Mandrágora desde su
  cuenta, y una cuenta en console.anthropic.com con crédito. Guiarlo cuando se elija el proveedor.
