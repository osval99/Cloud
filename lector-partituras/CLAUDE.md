# lector-partituras (Atril)

PWA lector de partituras para celular. HTML + JS puro, sin build (mismo esquema que `metronomo/` y `pomodoro/`).

## Archivos
- `index.html`: toda la app. `manifest.json`, `icon.svg`, `sw.js`: instalación y modo sin conexión.
- Librerías por CDN, cargadas solo cuando hacen falta: pdf.js 3.11.174 (cdnjs) y
  OpenSheetMusicDisplay 1.8.9 (jsdelivr). El worker de pdf.js se carga como script en la página
  (no usa Web Worker externo; así funciona también dentro del artifact).

## Funciones (elegidas por el usuario)
- Formatos: PDF, imágenes (JPG/PNG/WebP/GIF/BMP; varias elegidas juntas = una partitura con varias páginas,
  ordenadas por nombre) y MusicXML (.musicxml/.xml/.mxl), que OSMD dibuja en páginas A4.
- Paso de página: tocar izquierda (35 %) = atrás, derecha = adelante, centro = mostrar/ocultar controles.
  También flechas / RePág / AvPág / espacio (sirve para pedales Bluetooth). Barra con deslizador para saltar.
- Ajuste "Página" (entera) o "Ancho" (con scroll: el toque baja media pantalla antes de cambiar de página).
- Dos páginas lado a lado con el celular horizontal (botón para desactivar).
- Biblioteca con búsqueda, orden Recientes/A–Z, renombrar, borrar; recuerda la última página.
- Setlists: crear, agregar, reordenar, quitar; al terminar una partitura pasa a la siguiente.
- Anotaciones a mano: negro, rojo, azul, resaltador; 3 grosores; goma (borra trazos); deshacer; borrar página.
  Se guardan por página en coordenadas relativas.
- Reproducción de MusicXML (botón de notas, solo aparece en partituras MusicXML): todas las voces e instrumentos
  con un piano sintetizado (Web Audio), velocidad 25–200 % guardada por partitura, marca azul en la nota
  que suena y paso de página automático. Arranca desde la página visible; pausa, detener, volver al inicio.
  Notas, duraciones, ligaduras, tempo y posición se leen con el cursor de OSMD al abrir (`musicEvents`).
  PDF e imágenes NO suenan (serían imágenes; habría que convertirlas antes a MusicXML con MuseScore/Audiveris).
- Metrónomo integrado (30–240, compás 1–12, acento, tap); el tempo se guarda por partitura.
- Ejemplo inicial: una melodía MusicXML y un setlist de ejemplo (solo la primera vez).

## Datos
- IndexedDB `atril` (stores: docs, files, anns, setlists, kv). Si no hay IndexedDB, usa memoria y avisa.
- `localStorage`: `atril.cfg` (ajuste, dos páginas, lápiz) y `atril.sort`.
- Todo queda en ese navegador de ese celular: borrar datos del sitio borra la biblioteca.

## Dónde se usa
- Publicada como artifact privado: https://claude.ai/artifact/9hG7wk4tApgVbm8WfJUCmg
  Es una copia de `index.html` sin doctype/html/head/body, sin manifest/ícono ni registro del service worker.
  Al cambiar `index.html`, regenerar esa copia y volver a publicar la misma URL.
- Opción local: `python -m http.server 8000` dentro de la carpeta y abrir http://localhost:8000.

## Estado
- Probado con Playwright (Chromium, Pixel 5 simulado, librerías servidas desde copias de npm):
  importar PDF/PNG/MXL y rechazo de formato desconocido, toques, teclado, dos páginas, ajuste ancho,
  anotaciones + deshacer + persistencia, metrónomo (estado), setlists con paso automático, recarga, borrado,
  modo oscuro; reproducción: acordes, silencios, ligaduras, dos instrumentos, velocidad, pausa, marca y
  paso de página automático. Sin errores (salvo fuentes bloqueadas en la prueba).
- NO verificado: en un celular real, sonido del metrónomo y del piano, repeticiones/saltos (D.C., al Coda), carga desde el CDN real dentro del artifact,
  .mxl reales de MuseScore, PDFs pesados (pdf.js corre en el hilo principal).
- Pendiente / ideas: zoom con pellizco, modo nocturno, agregar páginas a una partitura de imágenes, exportar/respaldar biblioteca.
