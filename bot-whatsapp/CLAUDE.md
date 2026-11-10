# Bot de WhatsApp — La Mandrágora

Bot que responde precio, stock y horarios, y asesora sobre libros usando Google Books.
**Estado: en diseño** (todavía no hay código).

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
- **Servidor recomendado**: la PC Linux del local (donde corre Fierro), con un túnel tipo Cloudflare Tunnel para
  el webhook. Condición: PC prendida 24 h. Pendiente que el usuario lo confirme.
- **Horario de atención** (hora Argentina): lunes a viernes 09–20, sábados 10–14. Domingos y **feriados
  nacionales** cerrado. Fuera de ese horario el bot avisa que le responden cuando haya alguien.
  Feriados: tomarlos de una fuente automática (a definir) en vez de cargarlos a mano.
- **Precio que informa el bot**: LISTA MOSTRADOR.
- **Asesoramiento**: Claude (API de Anthropic) + Google Books API (gratis; cuota a ver en la consola de Google),
  recomendando solo lo que esté en stock.

## Costos (no verificados en fuentes oficiales)
- Meta: respuestas a clientes gratis desde 11/2024 (oficial). Terceros dicen que desde 1/10/2026 hay 1.000
  gratis/mes y luego ~US$0,026 por mensaje de servicio en Argentina. Confirmar en la tarifa de Meta.
- Proveedor de coexistencia: precio a comparar.
- developers.facebook.com está bloqueado en la red de las sesiones en la nube: habilitarlo para leer la doc oficial.

## Pendiente (preguntas al usuario)
- Dirección, medios de pago y si hacen envíos.
- Cuentas: el usuario tiene cuenta personal de Meta (no a nombre de La Mandrágora) y **no** tiene cuenta en la
  consola de Anthropic. Hay que crear un portfolio comercial (Meta Business) a nombre de La Mandrágora desde su
  cuenta, y una cuenta en console.anthropic.com con crédito. Guiarlo cuando se elija el proveedor.
- ¿Stock solo de La Mandrágora?
- ¿Confirma la PC Linux como servidor? ¿Comparar 2-3 proveedores de coexistencia?
