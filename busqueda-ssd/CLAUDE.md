# busqueda-ssd — SSD externo más barato en Mercado Libre

Búsqueda que se repite seguido: SSD externo nuevo, 500 GB o más, de marca confiable,
al menor precio en mercadolibre.com.ar. Resultado: top 10 en el chat + planilla Excel.

## Pedido del usuario
- Marcas: Kingston (XS1000/XS2000), Samsung (T7/T9), SanDisk (Extreme/Portable),
  Crucial (X9/X10), WD. Nada genérico ni sin marca. Solo nuevos.
- En el chat, los 10 más baratos: modelo, capacidad, precio, vendedor, envío gratis sí/no, link.
- Planilla Excel con todos los resultados y links.
- Navegar como una persona (navegador integrado de la app). No inventar datos.

## Cómo repetirla
1. **Navegador integrado**: Mercado Libre muestra el listado solo con la sesión iniciada.
   La sesión queda guardada en el navegador de la app; si se venció, pedirle al usuario
   que entre (Ctrl+Shift+B abre el panel). Claude in Chrome no estaba conectado
   (el usuario usa Edge; la extensión es para Chrome).
2. **Búsquedas** (Nuevo + Menor precio). Formato de URL:
   `https://listado.mercadolibre.com.ar/<busqueda>_OrderId_PRICE_ITEM*CONDITION_2230284_NoIndex_True`
   y para la página 2: `<busqueda>_Desde_49_OrderId_...`. Hay 48 publicaciones por página.
   Búsquedas usadas: ssd-externo-kingston, ssd-externo-samsung, ssd-externo-sandisk,
   ssd-externo-crucial, ssd-externo-wd, samsung-t7, samsung-t9, sandisk-extreme-portable-ssd,
   sandisk-portable-ssd, crucial-x9, crucial-x10, wd-my-passport-ssd, wd-elements-se-ssd.
   Las búsquedas genéricas por marca (ssd-externo-samsung/sandisk/crucial) devolvieron 0
   porque la página no había terminado de cargar; con las específicas alcanza.
3. **Extraer** en cada página con `extraer_listado.js` (javascript_tool). Hay que esperar a
   que aparezca `.poly-card` (la versión que se usó espera hasta 10 s). Acumula en
   `localStorage['ssd_resultados']` del dominio listado.mercadolibre.com.ar.
   Empezar de cero con `localStorage.removeItem('ssd_resultados')`.
4. **Filtrar** (en la página, mismo dominio): marca por título, modelo por regex, capacidad
   ≥ 500 GB, descartar accesorios, discos internos (SATA, M.2, 2,5"), usados,
   reacondicionados y precios irreales (< $150 por GB). Los "WD Elements SSD 4 TB" a
   $130.000–$350.000 son discos rígidos o publicaciones dudosas. WD Green no existe como
   SSD externo.
5. **Bajar los datos**: devolver `'<<DATA>>' + JSON.stringify(filas) + '<<END>>'`. Al ser
   largo, Claude Code lo guarda en un archivo de tool-results; `armar_planilla.py` lo lee
   directamente. Fila: `[id, titulo, precio, vendedor, envio_gratis, internacional, marca,
   modelo, capacidad_gb, motivo_descarte]`.
6. **Verificar el top 10** entrando a cada publicación (`extraer_detalle.js`): condición,
   vendedor (en compras internacionales el listado no lo muestra) y precio.
   Ojo: en publicaciones de catálogo (`/p/MLA...`) puede haber dos ofertas ("En cuotas" y
   "Mejor precio") de vendedores distintos; el precio del listado es el de "Mejor precio".
7. **Planilla**: `python armar_planilla.py datos/<fecha>_resultados.json datos/<fecha>_verificados.json planillas/ssd_mercadolibre_<fecha>.xlsx`
   (necesita openpyxl). Hojas: Top 10, Válidos, Descartados (con motivo), Info.
   Link corto que funciona: `https://articulo.mercadolibre.com.ar/MLA-<número>`
   (redirige a la publicación exacta).

## Última búsqueda: 05/11/2026
- 543 publicaciones leídas, 284 válidas.
- Los más baratos son SanDisk Portable 500 GB desde $239.346, casi todos compra
  internacional (EE.UU.). El más barato local fue un WD_Black 500 GB a $259.000 (01TEC),
  y después Kingston Dual Portable 512 GB a $355.510 (tienda oficial SGI).
- Lo más barato de Samsung fue un T7 1 TB a $488.437; de Crucial, un X9 a $478.002
  (ambos internacionales).
- Copia de la planilla en `C:\Users\osval\Documents\SSD Mercado Libre\`.

## Pendientes / ideas
- Si el usuario quiere, separar en el chat las opciones locales de las internacionales.
