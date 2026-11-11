# PVP de libros

Bajar el precio de venta al público (pesos) de listas de libros por ISBN.

## Fuente
- **Cúspide** (cuspide.com): buscar `https://cuspide.com/?s=<ISBN>&post_type=product`; si existe redirige a la ficha
  y el precio está en el JSON-LD (`Product.sku` = ISBN, `offers[0].priceSpecification[0].price`).
- **Buscalibre** (buscalibre.com.ar): desde la nube bloquea consultas (HTTP 202). Desde la PC funciona con el
  navegador integrado de la app de Claude (11/11/2026 no pidió verificación anti-robot). La búsqueda
  `/libros/search?q=<ISBN>` redirige a la ficha; precio en `section#producto`, tras "Libro Nuevo".
  Usar solo "Origen: Argentina" y el precio de lista (el tachado, no el de la promo con -10%).
  "Importado" y "Libro Usado" no sirven como PVP; ficha sin precio = "Sin Stock".
- planetadelibros.com.ar no está habilitado en la red.
- La red de la sesión necesita el entorno **"cloud"** (permite cuspide.com, www.buscalibre.com.ar).
  Desde el celular el aviso de aprobación de red no aparece: hacerlo desde la PC/web.

## Script
`python3 -I pvp_cuspide.py <lista.csv> <salida.json>` — el CSV debe tener columna `EAN`.

## Hecho
- `PVP_RBA_Noviembre_2026.xlsx`: lista de oferta RBA (proveedor Riverside, costo $9.000). 209/255 con PVP final
  (11/11/2026): 169 de Cúspide + 40 de Buscalibre (hoja "Faltantes Buscalibre", col. E; col. F = motivo si falta).
  En "PVP RBA" las col. M y N son fórmulas que toman esos valores: no tocarlas.

## Pendientes
- 46 sin PVP: 17 agotados, 15 solo usados importados, 14 solo importados nuevos (precio de referencia en col. F).
  Opciones: decidir si se usa el precio importado, buscar edición argentina con otro ISBN, o poner precio a mano.
- Claude in Chrome no conectó en la PC (11/11/2026: extensión instalada, pero ningún navegador vinculado a la
  cuenta); se usó el navegador integrado.
- Lista de saldos Planeta (16/10/2026, 156 títulos) quedó sin PVP: necesitaría habilitar planetadelibros.com.ar.
