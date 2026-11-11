# PVP de libros

Bajar el precio de venta al público (pesos) de listas de libros por ISBN.

## Fuente
- **Cúspide** (cuspide.com): buscar `https://cuspide.com/?s=<ISBN>&post_type=product`; si existe redirige a la ficha
  y el precio está en el JSON-LD (`Product.sku` = ISBN, `offers[0].priceSpecification[0].price`).
- Buscalibre bloquea consultas automáticas (HTTP 202) y sus precios son de importación: no usar.
- planetadelibros.com.ar no está habilitado en la red.
- La red de la sesión necesita el entorno **"cloud"** (permite cuspide.com, www.buscalibre.com.ar).
  Desde el celular el aviso de aprobación de red no aparece: hacerlo desde la PC/web.

## Script
`python3 -I pvp_cuspide.py <lista.csv> <salida.json>` — el CSV debe tener columna `EAN`.

## Hecho
- `PVP_RBA_Noviembre_2026.xlsx`: lista de oferta RBA (proveedor Riverside, costo $9.000), 169/255 con PVP de Cúspide
  (11/11/2026); 86 ISBN no están en Cúspide.

## Pendientes
- Opcional: para los 86 faltantes, buscar en Cúspide la edición argentina del mismo título (marcar ISBN distinto).
- Lista de saldos Planeta (16/10/2026, 156 títulos) quedó sin PVP: necesitaría habilitar planetadelibros.com.ar.
