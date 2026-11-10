# Fierro — librería La Mandrágora

Carpeta de trabajo para operar el ERP **Fierro** (proveedor q123 / Lambda Sistemas) de la librería.
Fierro es un cliente de escritorio (Python/wx) sin API: se maneja por pantalla con `cu.py`.

**Ubicación**: los scripts y este archivo están versionados en `Cloud/fierro/` (repo osval99/cloud). La carpeta de
trabajo sigue siendo `~/fierro-claude/` (PC Linux), que tiene **enlaces simbólicos** a estos archivos más los datos
no versionados (`capturas/`, `exportaciones/`, `facturas/`, `importaciones/`, `novedades/`, `pedidos/`, `logs/`).
Editar siempre en `Cloud/fierro/` (o por el enlace) y subir los cambios al repo.

## Reglas del usuario (obligatorias)

- **Sucursal: solo La Mandrágora.** Prescindir de DISTRIBUIDORA y LIBRERIA.
- **El login de Fierro lo hace siempre el usuario.** Nunca escribir usuario ni clave.
- **No confirmar, guardar ni enviar pedidos** (ni modificar datos en Fierro) sin el visto bueno explícito del usuario. Consultar, buscar y exportar sí se puede.
- **Nunca buscar sin filtro de fecha**: Fierro avisa "Búsqueda sin filtros" porque traería todo el histórico y puede colgarse. Ese aviso sale en blanco en las capturas y Escape no lo cierra: pedirle al usuario que lo cierre.
- **No clicar íconos de la barra sin leer antes su descripción**: en Catálogo > Libros están "Eliminar el libro seleccionado" y "Desactivar libros". Preferir los menús (Ventana Activa, etc.).
- Solo una sesión de Claude maneja Fierro a la vez (hay una sola pantalla virtual).

## Arranque: pantalla virtual dedicada

Fierro se abre en una pantalla virtual propia (Xephyr `:5`, 1340×690) para no tocar el escritorio del usuario:

1. `./iniciar_fierro.sh` — abre la ventana "Fierro (Claude)" y Fierro adentro (teclado en español).
2. Si dice **FALTA LOGIN**, pedirle al usuario que inicie sesión en esa ventana y esperar.
3. `./iniciar_fierro.sh ajustar` — estira Fierro a toda la pantalla (no hay gestor de ventanas).

## Herramienta `cu.py`

Ejecutar siempre como `python3 -I /home/oficina1/fierro-claude/cu.py …` (trabaja en `:5`):

- `shot [salida.png] [x0 y0 x1 y1]` → captura (por defecto `capturas/pantalla.png`); mirarla con Read.
- `click X Y [botón] [veces]` (botón 3 = derecho), `move X Y`, `scroll X Y up|down [n]`
- `type "texto"` (acentos ok), `key Return Escape Down ctrl+b …`
- `fit <id>` estira una ventana a la pantalla; `shotwin <id>` captura una ventana.
- Ids de ventanas: `DISPLAY=:5 xwininfo -root -tree | grep '"fierro" "Fierro"'`

Consejos:
- **Capturar antes de cada clic** y verificar después. Recortar las capturas a la zona que importa.
- En menús y listas el teclado (Down/Right/Escape) es más fiable que el mouse.
- En listas, la búsqueda por escritura se corta en espacios y acentos: escribir solo la primera palabra y bajar con Down.
- Campos de fecha (máscara dd/mm/aaaa): clic, `key Home`, escribir los 8 dígitos.
- En Facturas de compra, el filtro **Número** busca en todas las sucursales (el combo Sucursal no lo limita).
- El botón Buscar a veces no responde: usar **Ctrl+B** (Ventana Activa > Herramientas de búsqueda > Búsqueda).
- Diálogos más grandes que la pantalla (ej. "Guardar como..."): `fit <id>` y escribir la ruta completa en "Nombre".

## Fierro: dónde está cada cosa

- **Catálogo > Libros** (Ctrl+L). La lista de la barra elige el panel de filtros; el panel **"Ventas"** = "Vendido entre fechas" + Sucursal + Consignados/No consignados ("Consignados" exige cliente: usar "Todos").
- **Columnas**: clic derecho en los encabezados → "Vistas personalizadas" / "Personalizar vista actual".
- **Vista "Reposicion"** (la última de la lista): ISBN, Título, Autor, Editorial, Proveedor Principal, Precio, Stock (esta suc.), Ventas en el periodo, Días con stock en el periodo, Cant. Pedida (esta suc.), Consignado, Firme, Fecha últ. venta, Fecha últ. compra, Carácter.
- **"Días con stock en el periodo"**: Fierro reconstruye el stock diario y cuenta los días con stock > 0 en la sucursal elegida. Requiere fechas; solo lista libros con ≥ 1 venta en el período.
- **Carácter** de los libros: LINEA, OFERTA!, USADO, OUTLET (y algunos sueltos).
- **Límite de resultados**: clic derecho sobre el Total o Ventana Activa > Herramientas de búsqueda > Límite de la búsqueda. Usar "Sin límite" (3 meses ≈ 5000 títulos, ~2 min de búsqueda).
- **Exportar**: Ventana Activa > Exportar resultados > "Planilla CSV" > Aceptar > (esperar; ~5000 filas ≈ 17 min) > "Guardar en un archivo" > ruta en `exportaciones/`.
- **Compras > Pedidos**: Pedidos, Pedidos de Baja, Sugerencias de compras (lista manual de los vendedores, no calcula), Generación de Pedidos (y a múltiples proveedores / por lote).
- **Compras > Reportes**: Consignaciones, Saldos cta. cte., Libro IVA Compras, Pedidos Pendientes…
- **Stock > Reportes**: Stock, Control de stock entre fechas, Kardex, Ingresos de mercadería, Tomas de inventario…
- **Ventas > Reportes**: Venta entre fechas, Ventas por período (por libro / por cliente), Análisis de la librería (Rentabilidad, Ventas por hora), Reporte de cajas…
- Manual: https://soporte.fierro.com.ar/portal/es/kb/fierro (leerlo con el navegador integrado).
- "Fierro acceso a datos": servicio pago de réplica SQL de solo lectura. Si el usuario lo contrata, reemplaza el manejo por pantalla para consultas.

## Reposición de libros

Método acordado con el usuario (comando `/reposicion`):

- Ventas de los **últimos 3 meses**, sucursal La Mandrágora, solo carácter **LINEA**.
- Velocidad real = ventas ÷ días con stock. **Curva de confianza** (sin topes fijos; el usuario rechazó el tope "2× ventas"): confianza = días con stock ÷ (días con stock + 15); velocidad usada = confianza × real + (1 − confianza) × ventas ÷ días del período.
- Necesidad = velocidad usada × (**90 días de cobertura** + **10 de demora**). La demora es un supuesto: confirmar si el usuario da otro valor.
- A pedir = necesidad − stock − cantidad ya pedida. 1 venta en el período → mantener 1 ejemplar.
- Stock negativo (vendido sin ingresar) → usar el promedio del período y marcar "Revisar".
- Se excluyen sin ISBN, usados, gift cards, bolsas.
- Script: `python3 -I reposicion.py exportaciones/<archivo>.csv --desde dd/mm/aaaa --hasta dd/mm/aaaa` → `pedidos/…_detalle.xlsx` y `…_resumen.xlsx`.

## Facturas de compra de Penguin Random House

- En Fierro el proveedor es **EDITORIAL SUDAMERICANA** (Compras > Facturas; buscar "random" + fechas).
- Los PDF llegan a mandrake.dis como "Fwd: Comprobante Electrónico 0016B000xxxxx"; se bajan a `facturas/prh/`.
- **Si el domicilio de entrega dice Quilmes** (12 de Octubre 2638, (1879) QUILMES): cargar como **Factura General
  (FG) sin movimiento de stock** (van a un depósito en Quilmes). Modelo: FG B 00016-00080252 y 00016-00080647.
  Criterio del usuario desde el 3/11/2026; no pedir confirmación. Se cargan en la **sucursal DISTRIBUIDORA**
  (excepción a la regla de La Mandrágora; el usuario inicia sesión en esa sucursal).
- Cómo: Facturas de compra > ícono **FG** "Ingresar una factura general". Proveedor `SUD` + Tab (pone letra B),
  Tipo "Factura general", Fecha = fecha de la factura, Vencimiento = el del PDF (60 días), Importe total = total
  del PDF, IVA 0, Descripción `DIS <ejemplares> ej`. Sin formas de pago (queda en cuenta corriente). Aceptar → Sí.
- **Campo Número** (`00000-00000000`): cada tramo se llena como calculadora, de derecha a izquierda. Escribir de a
  **un dígito por vez** (con `type` de varios dígitos se pierden): borrar con Ctrl+A/BackSpace, Home, `0 0 0 1 6`;
  después **clic en el segundo tramo** y escribir `8 1 4 6 2`. Verificar con captura (Home y End).
- Cargada así: FG B 00016-00081462 (24/08/2026, $877.939,70, 46 ej.) el 3/11/2026.

## Facturas de venta de saldos (Planeta) a clientes de RC

- RC = Ricardo (rcquilmes@hotmail.com), maneja el depósito de Quilmes. Manda remitos (`Remito_Saldos_<cliente>_<fecha>.xlsx`).
- Se factura en la **sucursal DISTRIBUIDORA**: Ventas > Facturas de venta > ícono **FG** "Crear una nueva factura general".
  Cliente (Macao = `Maca`, Cuevas Cristian Matías; Patres = `16455` PATRES MARCELO DARIO, no Odiseya). Al elegir
  cliente Fierro pone "FC Electrónica": **cambiar Punto de Venta a "14 - Fac. Distribución Mayorista"**. Tipo
  "Factura con leyenda", vencimiento +30 días, Importe total = ejemplares × $3.000 (precio en
  `~/Documentos/Saldos PLaneta 05102026/Balance cobranza saldos…xlsx`), IVA 0. Descripción (modelo FG 14-00000428):
  `N libros de saldo según detalle adjunto.` / `Precio unitario: $3000.-` / `Total: $X.-` / `Pago con e-cheq: 30/60/90 días`.
  Formas de Pago → ícono "Ingresar pago de cuenta corriente" → Aceptar. Aceptar → Sí (límite de crédito) → emite en ARCA.
  No imprimir ticket ni factura.
- Acentos: si `type` dice "Carácter sin tecla", correr `DISPLAY=:6 setxkbmap es` y reescribir.
- **PDF**: Fierro lo manda por mail al cliente si tiene correo (queda en Enviados de mandrake.dis). Si no, en la lista
  seleccionar la factura e ícono "Imprimir factura de venta": abre el visor con `/tmp/tmpXXXX.pdf`; copiarlo.
- Guardar en `~/Documentos/Saldos PLaneta 05102026/` como `<Cliente> Factura Saldos <número>.pdf` y mandarlos a RC.
- 3/11/2026: FG 14-00000448 Macao 457 ej $1.371.000 y FG 14-00000449 Patres 462 ej $1.386.000 (remitos del 18/10/2026).
- ARCA avisa que desde el **01/12/2026** rechaza comprobantes sin "Condición frente al IVA del receptor": revisar
  que Fierro lo envíe antes de esa fecha.

## Comprobantes de Planeta (comfiar) en DISTRIBUIDORA

- Llegan a mandrake.dis desde acliente.eplaneta@la.comfiar.com.ar ("Aviso de emisión del comprobante (Factura B / Nota de
  Crédito B) Nro …"). Link "DESCARGAR" → `planeta_comprobantes.py` (IMAP, lo corre el usuario) o, con el conector de
  Gmail, sacar los links y bajar con `bajar_pdf()` del mismo script. PDFs y `resumen.csv` en `facturas/planeta/`.
- **Solo cuenta 1006187** (DISTRIBUIDORA; la 1005707 es la otra). El punto de venta (0028/0032) no indica la cuenta:
  mirar "001006187 SHCOLER…" en cada PDF.
- Facturas → Facturas de compra > ícono **FG**: proveedor `PLA` + Tab, letra B, tipo "Factura general", número (de a un
  dígito, como en PRH), fecha, vencimiento del PDF, importe total, IVA 0, descripción `dd/mm/aaaa vto Nej. importe`
  (modelo FG B 00028-00045711). Aceptar → Sí.
- Notas de crédito → Compras > Créditos > ícono **NG** "nota de crédito general (sin ejemplares)": `PLA` + Tab, motivo
  "Faltantes" ("NOTA DE CRÉDITO POR FALTANTE") o "Error de facturación", letra B, número, fecha, importe, descripción
  `dd/mm/aaaa Nej. importe FB 0028-xxxxx`. Aceptar → Sí.
- 4/11/2026: cargadas 23 FG (07/09 a 29/10, 0028-45692 … 0028-46258) y 10 NG (hasta 0032-5473, diferencia de precios
  → motivo "Error de facturación"), más FG 0032-8410 (16/07, saldos, $19.600.000, vto 1ª cuota 15/11). Detalle en `facturas/planeta/Cargado DIS 04-11-2026.xlsx`.

## Facturas de Planeta (SINLI) en LIBRERIA

- Cuenta Planeta **1005707** = sucursal **LIBRERIA** (el usuario inicia sesión ahí). Las declaraciones de ventas
  ("DECLARACION DE VENTAS <mes>") son **Baja Consignación**.
- Se cargan por **SINLI**: Compras > Facturas > ícono **FC** "Ingresar una nueva factura" → Proveedor `PLA` + Tab →
  se abre "Selección de mensajes" (bandeja SINLI) → elegir la factura → Aceptar. Fierro completa tipo, número,
  fechas y renglones.
- Avisos "¿Desea cambiar el precio … LISTA MOSTRADOR?" uno por libro: **nunca bajar precios** → "No" si el nuevo es
  menor (script OCR con tesseract en capturas, recorte 467 261 873 372, botón No en 719 408); si sube, consultar.
- Corregir a mano: letra **B** (en el combo está arriba de la C, hay que subir con scroll) y punto de venta del
  número (`00028`, de a un dígito). Formas de Pago → "Ingresar pago de cuenta corriente" → Aceptar.
- Aceptar → Sí (guardar) → Sí (marcar el mensaje como procesado).
- "Liquidación por conciliación" = libros que Planeta pidió en devolución y no devolvimos (no aparecieron o nos los
  quedamos). Fierro avisa "ítems no asignados a remitos… creará un crédito" y "precio distinto al del pedido de baja":
  contestar **Sí** (criterio del usuario; puede haber errores nuestros). Crédito generado: no imprimir.
- 5/11/2026: FC B 00028-00046099 (13/10, $4.697.445,00, 242 ej.) y FC B 00028-00046234 (28/10, $2.274.600,00,
  108 ej., generó crédito CD 523, saldo $2.118.000). La 00028-00045701 ya estaba.

## Remitos de consignación de Planeta: LIBRERIA → La Mandrágora

Procedimiento reiterado (pedido del usuario, 10/11/2026). Todo se hace **con sesión en La Mandrágora**, eligiendo
Sucursal y Depósito en cada remito (no hace falta loguearse en LIBRERIA):

1. **Remito de Planeta en LIBRERIA**: Compras > Remitos > Ctrl+N. **Primero** Sucursal `LIBRERIA` y Depósito
   `LIBRERIA`, después Proveedor `PLA` + Tab → bandeja SINLI (si el mensaje ya está procesado, Cancelar y cargar a
   mano). Tipo Consignación, número (de a un dígito por tramo), fecha del remito, renglones.
   Error a evitar: cargarlo en La Mandrágora/Sucursal3 (no se puede cambiar sucursal ni depósito después; solo
   eliminar el remito y recargarlo).
2. **Reconsignación**: Ventas > Remitos > ícono RE "Ingresar un remito". Cliente **`mandrag`** MANDRAKE LIBROS (COOP)
   (buscar con la lupa; no el 315), Tipo Consignación, Sucursal y Depósito `LIBRERIA`, mismos libros y cantidades.
   Aceptar → Sí → "¿Desea imprimirlo?" **No**. Fierro numera solo (ej. RE 1-1855).
3. **Recepción en La Mandrágora**: Compras > Remitos > Ctrl+N, Proveedor **`OS`** (Mandrake Libros), Sucursal
   La Mandrágora / Depósito Sucursal3, Tipo Consignación, **número = el del remito de venta de LIBRERIA**
   (1-1855 → `00001-00001855`), fecha del paso 2, mismos renglones. Aviso "proveedor principal distinto" → Sí. Aceptar → Sí.
- En los remitos de compra, **Enter en Cantidad agrega el renglón y abre "¿guardar?"**: usar el botón Agregar.
- 10/11/2026: RE 00014-00186011 (Planeta, 27/10, 50 ej. 9786310200217 LA HORA ANTES DEL ALBA) recargado en LIBRERIA →
  RE venta 1-1855 a mandrag → RE compra 00001-00001855 de OS en La Mandrágora.

## Segunda pantalla

Si otra sesión está usando `:5`, se puede abrir `:6` (Xephyr con título "Fierro (Claude 2)" + `/opt/bin/fierro`) y
manejarla con `CU_DISPLAY=:6 python3 -I cu.py …`. El usuario tiene que iniciar sesión ahí. Si las teclas no entran o
el menú muestra letras subrayadas, quedó **Alt trabada**: soltarla con XTest (keycode 64, presionar y soltar).

## Carpetas

- `exportaciones/` CSV que salen de Fierro · `pedidos/` resultados (`anteriores/` versiones viejas)
- `capturas/` capturas de trabajo (descartables) · `logs/` logs de Xephyr y Fierro

## Otros datos

- PC: Ubuntu 24.04, sesión X11 (escritorio del usuario en `:1`). Python 3.12 del sistema sin librerías extra: `cu.py` y `reposicion.py` no usan dependencias externas (Excel vía LibreOffice `soffice`).
- Ya se importan a Fierro CSV de novedades (ej. `~/Descargas/Novedades_Octubre_2026_Fierro.csv`); ese archivo tiene títulos con comas sin comillas → columnas corridas.
- El usuario a veces trabaja a distancia (Remote Control): enviarle los resultados con SendUserFile.
