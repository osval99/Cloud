# afinador

PWA de afinador por micrófono, pensada sobre todo para guitarra en afinación estándar.
HTML + JS puro, sin dependencias ni build (misma estructura que `metronomo/` y `pomodoro/`).

## Archivos
- `index.html`: toda la app (estilos, detección de altura, interfaz y tono de referencia).
- `manifest.json`, `icon.svg`, `sw.js`: instalación como app y funcionamiento offline.

## Funciones (elegidas por el usuario)
- Modo Guitarra: detecta sola la cuerda más cercana de E2 A2 D3 G3 B3 E4; marca ✓ la cuerda
  que se mantuvo afinada 0,6 s. Tocar un botón de cuerda hace sonar su nota 3 s (tono de referencia).
- Modo Cromático: cualquier nota de 40 a 2000 Hz; botón "Tocar nota" repite la última detectada.
- La4 ajustable 430–450 Hz (440 por defecto). Nombres Do Re Mi o C D E.
- Aguja ±50 cents, cents con un decimal, Hz medidos y objetivo; verde = ±2 cents, naranja ≤10.
- Indicaciones "tensá / aflojá". `localStorage`: clave `afin.cfg`.

## Detalles técnicos
- Algoritmo YIN (umbral 0,12) con interpolación parabólica, ventana de 4096 muestras,
  análisis cada 60 ms, mediana de las últimas 7 lecturas (se reinicia si salta >60 cents).
- Micrófono sin cancelación de eco, supresión de ruido ni control de ganancia; filtro pasa-altos 35 Hz.
- Mientras suena el tono de referencia no analiza (para no escucharse a sí mismo).
- Wake Lock para que no se apague la pantalla.
- El código del detector está entre `/*DETECT-START*/` y `/*DETECT-END*/` para probarlo con Node.

## Estado
- Probado en Node con señales sintéticas tipo cuerda (6 cuerdas × ±30 cents): error máx. 0,25 cents.
- Probado con Playwright y micrófono simulado (La2 +5 cents): muestra La2 +5,0, cuerda 5ª;
  cromático, nombres en inglés y La=442 (−2,9 cents) correctos; sin errores de consola.
- NO probado con una guitarra real ni en un celular.

## Dónde se usa
- El micrófono exige HTTPS (o localhost). Los artifacts de claude.ai bloquean el micrófono,
  así que no sirve publicarlo ahí como el metrónomo.
- Hosting elegido: Netlify Drop (https://app.netlify.com/drop). Se sube un zip con
  `index.html`, `manifest.json`, `sw.js` e `icon.svg` (sin carpeta adentro), con la sesión de Netlify iniciada
  para que el sitio no caduque. Pendiente: anotar acá la URL del sitio cuando el usuario la pase.
- Para actualizar: en Netlify, sitio → Deploys → arrastrar el zip nuevo (misma URL).
- PC sin internet: `python -m http.server 8000` DENTRO de `afinador` y abrir http://localhost:8000.
