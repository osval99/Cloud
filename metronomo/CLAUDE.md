# metronomo

PWA de metrónomo configurable. HTML + JS puro, sin dependencias ni build (misma estructura que `pomodoro/`).

## Archivos
- `index.html`: toda la app (estilos, lógica y sonidos sintetizados con Web Audio).
- `manifest.json`, `icon.svg`, `sw.js`: instalación como app y funcionamiento offline.

## Funciones (elegidas por el usuario: uso general, 30–300 BPM)
- Velocidad: número grande, deslizador, botones ±1/±5, flechas del teclado y nombre italiano (Allegro, etc.).
- Tap tempo: promedia los últimos 6 toques; se reinicia si pasan más de 2 s (tecla T).
- Compás 1–12 / 2, 4 u 8. Cada tiempo es un círculo que se toca: acento → normal → silencio.
  En 6/8, 9/8 y 12/8 acentúa cada 3 por defecto. El BPM se refiere a la figura del denominador.
- Subdivisiones: ninguna, corcheas, tresillos, semicorcheas (con volumen propio).
- Sonidos: madera, click, beep, cencerro; volumen; destello visual opcional.
- Entrenador: sube X BPM cada N compases hasta un tope.
- Temporizador de práctica: se detiene solo a los N minutos.
- Configuraciones guardadas (nombre + cargar/borrar). Barra espaciadora = iniciar/detener.

## Detalles técnicos
- Programación con "lookahead" (golpes agendados en el reloj de audio, 120 ms adelante);
  el tick corre en un Web Worker para no frenarse con la pestaña en segundo plano.
- Pide Wake Lock para que no se apague la pantalla mientras suena.
- `localStorage`: claves `metro.cfg` y `metro.presets`.
- Necesita HTTPS o localhost para instalarse (service worker).

## Estado
- Probado con Playwright (Chromium): cantidad y orden de golpes con acentos y subdivisión,
  tap tempo, entrenador, ciclo de acentos, presets y persistencia al recargar; sin errores.
- Sonido y precisión rítmica NO verificados en un dispositivo real.

## Dónde se usa
- Publicada como página (artifact privado) en https://claude.ai/artifact/2LQFtuSznC7vBChENxa2Q5
  — se abre directo en PC o celular. Es una copia de `index.html` sin service worker ni manifest
  (no hacen falta ahí). Al cambiar `index.html`, volver a publicar esa misma URL.
- Opción local: `python -m http.server 8000` DENTRO de la carpeta `metronomo` y abrir http://localhost:8000.
