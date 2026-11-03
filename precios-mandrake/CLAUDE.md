# Librería Mandrake — Actualización de Precios

## Proyecto
Sistema automatizado de actualización de precios para Librería Mandrake.

- **Mail de operación**: actualizar.mandrakelibros@gmail.com
- **Carpeta de trabajo**: `C:\Users\osval\Desktop\Precios prueba 4\`
- **Archivos procesados**: subcarpeta `Procesados\`

## Scripts
| Script | Función |
|--------|---------|
| `actualizar_precios.py` | Pipeline completo: baja adjuntos de mails con etiqueta `PRECIOS PARA ACTUALIZAR` → procesa → mueve → les pone `Resuelto` y les saca la etiqueta |
| `agente2.py` | Procesa archivos Excel y genera resultado. Acepta `--auto` (sin preguntas) y lista de archivos específicos |
| `bajar_adjuntos.py` | Solo descarga adjuntos del mail (sin procesar) |

## Credenciales Gmail API
- `credentials.json` — en la carpeta de trabajo (no versionar)
- `token.json` — se genera automáticamente al autenticarse por primera vez
- Usuario de prueba OAuth: `actualizar.mandrakelibros@gmail.com`
- Proyecto Google Cloud: `mandrake-precios`
- Las etiquetas se buscan **por nombre** (`PRECIOS PARA ACTUALIZAR`, `Resuelto`), no por ID: los IDs cambian entre cuentas.
- Las listas a actualizar llegan a **mandrake.dis@gmail.com** con la etiqueta `PRECIOS PARA ACTUALIZAR`.
  El token debe estar autorizado con esa cuenta (si `token.json` es de otra, borrarlo y reautenticar). El script imprime la cuenta usada.

## Convenciones y reglas importantes
- El pipeline procesa **solo** los archivos recién bajados del mail, no los que ya están en la carpeta
- **Conflictos de precio**: tomar siempre el precio más alto — el script ya lo hace automáticamente
- Al terminar el pipeline se mueven a `Procesados\`: archivos descargados + RESULTADO_FINAL + DUDAS
- Si se pide resolver un archivo de conflictos manualmente, generar **solo** un archivo con los ISBNs conflictivos resueltos (pueden ser cualquier cantidad) — **no mezclar con el resultado anterior**
- Los archivos Excel de entrada pueden tener múltiples hojas; solo procesar las que son listas de precios

## Reglas del proyecto "Listas De Precios" (claude.ai, memoria al 2/10/2026)
- Salida: `RESULTADO_FINAL_<hora>.csv` UTF-8, separador **coma** (con punto y coma no carga en Fierro),
  4 columnas: ISBN, Precio (entero), Titulo, Origen. Para Fierro se divide en tandas de ~5.000 filas.
- **Consultar al usuario las decisiones editoriales** antes de cerrar: qué columna de precio usar si hay varias,
  promo vs. PVP normal, identidad dudosa de una distribuidora. Decisiones ya tomadas:
  - Si hay PVP viejo y PVP nuevo, siempre el nuevo.
  - Las promos de distribuidoras (ej. Librum "Promos nov-dic") se cargan.
  - El Ateneo manda precios muy bajos (< $1.000) de libros descatalogados: no se cargan.
- DUDAS suele traer hojas vacías ("out-of-bounds"): no requieren acción.
- `agente2_config.json` guarda los mapeos por `archivo|hoja`. Si no hay entrada exacta, el script busca una
  de un archivo parecido (mismas palabras sin fecha/mes/remitente) y misma hoja, y la usa solo si el contenido
  valida (ISBN y precios razonables). Hojas marcadas `descartado` se omiten.

## Cargar precios en Fierro
Ventas > Listas de precios > LISTA MOSTRADOR > Precios > ícono "Importar precios desde un archivo".
Formato del archivo: **Personalizado** (CSV), separador coma, fin de línea Windows, empezar desde línea 2.
Vincular por **ISBN**, columna 1. **No** tildar "Actualizar el precio si se encuentra más de un libro con el
mismo código" (hay libros duplicados, ej. gemelos outlet). Filtro: **Carácter = LINEA** (no tocar OFERTA!,
OUTLET, USADO…). Al terminar, "Guardar errores..." como `errores_<nombre de la tanda>.csv` en la misma carpeta.
- **Desde la próxima vez el usuario quiere que se haga todo solo**: separar los casos raros (bajas fuertes,
  códigos dudosos) en un archivo aparte **sin procesar** para que los vea, y seguir con el resto de las tandas.
- En la pantalla :5 la tecla **Alt puede trabarse** (keycode 64): antes de escribir, verificar que no haya teclas
  apretadas; si las letras abren menús, parar y soltarla (pasó el 2/11/2026 y cerró los diálogos).
- Precio en la **columna 2** (el asistente propone 1). Moneda Pesos. Tandas en `~/fierro-claude/importaciones/precios_<mes>/`.
- **Script `cargar_fierro.py`** (PC Linux, hace todo lo anterior): `preparar N` → `finish N` → `errores N` (guarda
  errores y deja capturas de los extremos de la grilla en `/tmp/fierro_tandas/tN_9.png` y `tN_10.png`) → revisar →
  `quitar N arriba|abajo K` + `registrar "tanda|isbn|titulo|precio|nuevo|var|motivo"` → `aplicar N` (~4-7 min por
  tanda de 4.500). Criterio de raro: precio nuevo < $1.000 o > $500.000, variación > +500% o < −70%.
  Para quitar una fila hay que **seleccionarla con clic** (queda naranja): Ctrl+Home/End mueve el foco, no la selección.
  La carpeta de las tandas se pone en `/tmp/fierro_tandas/dir.txt` (los archivos se llaman `<carpeta>_tandaN.csv`,
  `errores_<carpeta>_tandaN.csv`, `RAROS_<carpeta>.csv`). Si Fierro pide "Reconectar", el script responde Sí.
- **Forma recomendada**: después de `errores N`, correr `quitar_ceros_todos.py` (grilla ordenada por Variación
  descendente: ceros entre positivos y negativos). Repite bloques con Shift+↑ desde el último 0 hasta que no quede
  ninguno junto a los negativos (la selección a veces se corta, por eso repite). Después `aplicar N`.
- **Filas con variación 0%: quitarlas antes de Aplicar** (pedido del usuario 2/11/2026), **todas juntas**:
  con la grilla ordenada por Variación, seleccionar con clic la primera fila en 0 y correr `quitar_ceros_bloque.py quitar`:
  extiende la selección con **Shift+↓** mientras siga en 0 (lee con OCR, tesseract + Pillow), verifica que no haya
  ninguna fila ≠ 0 seleccionada y aprieta Quitar una sola vez. Registra en `QUITADOS_variacion_0_<carpeta>.csv`.
  `quitar_ceros_fierro.py prueba` lee la vista; `quitar_ceros_fierro.py quitar` lo hace fila por fila (lento, ~10/min).

## Flujo completo (hacerlo solo, sin preguntar)
1. `herramientas/revisar.py`: lista los mails con `PRECIOS PARA ACTUALIZAR`. `bajar_nuevos.py` baja los adjuntos a
   `Nuevos_<fecha>/` y marca **repetidos** por md5 contra `Procesados/` y entre sí. Abrir links si la lista viene por link.
   Tablas en el cuerpo del mail (ej. PRH "Cambios de PVP"): `prh_cuerpo.py` las pasa a xlsx (solo PVP Nuevo).
2. Etiquetas: los nuevos llevan **`En Proceso`**; los repetidos (misma lista ya cargada) pasan directo a `Resuelto`
   (`etiquetar.py`, adaptar las reglas a cada tanda). Mails que no son listas (ej. Navarro "GRUPAL… DEVOLUCION"): no tocar.
3. `agente2.py --auto <archivos>` → `RESULTADO_FINAL_<hora>.csv`.
4. `herramientas/solo_cambios.py RESULTADO.csv precios_<mes>_<letra>`: deja solo ISBN nuevos o con precio distinto
   a lo ya cargado en `~/fierro-claude/importaciones/precios_*/` (los proveedores repiten listas acumuladas).
5. Cargar en Fierro (`cargar_fierro.py`), quitar raros y ceros, aplicar.
6. `herramientas/resolver.py`: pasa a `Resuelto` **solo** los mails con `PRECIOS PARA ACTUALIZAR` **y** `En Proceso`.
   ⚠ `En Proceso` también se usa en mails de transferencias y devoluciones: nunca etiquetar por `En Proceso` solo
   (pasó el 2/11/2026 y hubo que revertir).
- **Periférica**: no manda mail. Una vez por mes bajar `https://www.laperiferica.com.ar/catalogo.xls` (catálogo
  completo; la página es https://www.laperiferica.com.ar/catalogos/, botón "Catálogo"). Columnas ISBN (0) y PVP $ (10).
- La Coop siempre adjunta "Lista de precios…"/"Aumentos…" (el "SN …" son solo novedades). En nov. 2026 anunció
  aumentos de Buena Cosecha **sin adjuntar la lista**; la web www.lacoop.com.ar está deshabilitada. Se dejó un
  borrador de respuesta pidiéndola (2/11/2026, cuenta mandrake.dis). **Pendiente**: cargarla cuando llegue.

## Validación de ISBN (agente2.py)
- El ISBN es casi siempre de **13 dígitos** (rara vez 10). Si la columna elegida tiene mayormente ISBN-10
  y hay otra con ISBN-13 (978/979), se usa la de 13 (también sobre la config guardada).
- Solo valen ISBN-13 con prefijo **978/979**; los ISBN-10 válidos se convierten a ISBN-13. Los demás códigos
  (779…, 750…, 290…) van a `ISBN_INVALIDOS_<hora>.xlsx` con el motivo.
- Se descartan las filas ocultas de los Excel.
- Se verifica el **dígito de control** (ISBN-13: pesos 1/3 mód. 10; ISBN-10: pesos 10..1 mód. 11, X=10).
  Los que no validan van a `ISBN_INVALIDOS_<hora>.xlsx`, no al resultado.
- Un valor con letras (ej. código interno "0084PT0000") no se toma como precio.
- Si la columna de "precio" tiene valores ≥ 100.000.000 (son códigos/ISBN), la hoja va a DUDAS.
- `agente2_config.json` guarda el mapeo de columnas por `archivo|hoja`; si un mapeo está mal, corregirlo ahí.

## Listas que llegan por link
El script solo baja adjuntos. Las listas por link se bajan resolviendo el link de seguimiento del mail
(curl -L; los de Brevo/sendibm redirigen con JavaScript: buscar la URL dentro del HTML).
Google Sheets: `.../export?format=xlsx`; Drive: `drive.google.com/uc?export=download&id=<ID>`.
Se guardan en `Procesados/` como `2026-10-31 [link] <nombre>.xlsx` y se procesan junto con los adjuntos.

## Estado actual (31/10/2026) — tanda noviembre 2026
Corrida en la PC Linux `/home/oficina1/Cloud/precios-mandrake/`, cuenta mandrake.dis@gmail.com.
Los 34 mails de la etiqueta quedaron con `Resuelto`.
- 37 adjuntos (25 mails) + 6 listas por link (Coma Cuatro, FCE, Sigmar, Abrazandocuentos, Del Naranjo, Manolito).
- **Resultado**: `RESULTADO_FINAL_1418.csv` (36.538) + `PRECIOS_CUERPO_MAIL.xlsx` (2) → 8 tandas en
  `~/fierro-claude/importaciones/precios_nov2026/` (36.532 precios; sin los 7 descatalogados de El Ateneo).
- `ISBN_INVALIDOS_1418.xlsx`: 430 filas que no son ISBN válidos. `DUDAS_1418.xlsx`: 17, todas hojas vacías o repetidas.
- **Carga en Fierro: HECHA (2/11/2026)**, LISTA MOSTRADOR, filtro LINEA: **29.047 precios aplicados**;
  7.691 filas no vinculadas (libro inexistente o no LINEA) en `errores_precios_nov2026_tandaN.csv` (falta el de la tanda 1).
- `RAROS_precios_nov2026.csv` (misma carpeta): 7 casos NO aplicados para revisar a mano (subas > 500%, un ISBN
  múltiple en Fierro y "Atlas descrito por el cielo" 9789685679091, quitado por error: cargar $9.000 si corresponde).
- `Descartados/`: corridas anteriores con errores. No usar.

### Segunda tanda (2/11/2026)
16 mails. Repetidos → Resuelto: Herramienta, UNL, AKAL. Nuevos: Hule, Bikini Ninja/Zindo, La Coop, Ciraolo III,
PRH Labati (cuerpo del mail), Konemann, Carbono. `RESULTADO_FINAL_1804.csv` 9.793 filas, 8.836 ya cargadas igual →
`precios_nov2026_b/` 957 filas: **161 aplicados**, 0 raros (variaciones −34% a +15%). Mails → Resuelto.
**Periférica** (`RESULTADO_FINAL_1816.csv`, 606) → `precios_nov2026_c/` 604 filas: 343 vinculadas en Fierro,
322 en 0% quitadas → **21 aplicados** (−51% a +38%, 0 raros). Próxima Periférica: diciembre 2026.
**Losada y Aique** (mail de la Salle, 2/11/2026; `RESULTADO_FINAL_2346.csv`, 1.744) → `precios_nov2026_d/`:
1.605 vinculadas, 357 en 0% quitadas → **1.248 aplicados** (−6% a +175%, 0 raros). Mail → Resuelto.
- **El usuario NO quiere que se le pida autorización ni confirmación**: da la orden y espera solo el aviso final.
  `Cloud/.claude/settings.local.json` (no versionado) tiene todos los permisos habilitados para eso.

### Pendientes
- Conflictos manuales viejos: 9789871374915 (Carbono, $23.000 vs $37.500); 9789872349417 (Herramienta, 2 títulos).
- El pipeline no mueve RESULTADO_FINAL/DUDAS a `Procesados/` (quedan en la carpeta).

## Mejoras pendientes al script
1. Descartar automáticamente hojas que no son listas de precios (Editoriales, Puntos de venta, Contactos)
2. Mostrar ISBN pre-detectado cuando el precio es ambiguo
3. Arreglar el error "single positional indexer is out-of-bounds" (Galerna, Cien Flores, Herramienta)
4. Reconocer encabezados con tilde ("Código Barras")
5. Bajar automáticamente las listas por link desde `actualizar_precios.py`

## Google Apps Script (bajar adjuntos de Gmail)
- **Cuenta**: actualizar.mandrakelibros@gmail.com
- **Etiqueta Gmail**: `precios-para-actualizar`
- **Bug pendiente**: `getUserLabelByName()` devuelve `null` — la etiqueta no se está resolviendo correctamente
