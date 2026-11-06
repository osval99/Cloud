// Lee los datos de una publicación (página de producto) de Mercado Libre.
// Devuelve título, condición, precio, vendedor, envío gratis, si es internacional
// y la MARCA/MODELO de la ficha "Características del producto".
// Regla: si la marca de la ficha no coincide con la del título, la publicación se
// descarta (ej.: título "SanDisk 1 TB" con ficha "Marca: Movespeed").
(async () => {
  for (let i = 0; i < 20 && !document.querySelector('.ui-pdp-title'); i++) await new Promise((r) => setTimeout(r, 500));
  // La ficha de características se carga al bajar en la página
  window.scrollTo(0, document.body.scrollHeight / 2);
  await new Promise((r) => setTimeout(r, 1500));
  const q = (s) => document.querySelector(s)?.innerText.replace(/\s+/g, ' ').trim() || '';
  const txt = document.body.innerText;
  const precio = (document.querySelector('.ui-pdp-price__second-line .andes-money-amount')?.getAttribute('aria-label') || '').match(/^\s*(\d+)/);
  const ficha = (nombre) => (txt.match(new RegExp('\\n' + nombre + '\\n([^\\n]+)')) || [])[1] || '';
  const desc = txt.slice(txt.indexOf('Descripción'), txt.indexOf('Descripción') + 3000);
  return {
    url: location.href.split('#')[0],
    titulo: q('.ui-pdp-title'),
    condicion: q('.ui-pdp-header__subtitle').split('|')[0].trim(),
    precio: precio ? Number(precio[1]) : null,
    vendedor: (q('.ui-pdp-seller__header__title') || q('.ui-seller-data-header__title') || q('.ui-pdp-seller-summary__header__title')).replace(/^Vendido por\s*/i, ''),
    vendedor_sin_reputacion: /No tiene suficientes ventas/i.test(txt),
    envio_gratis: /(llega|env[ií]o) gratis/i.test(txt),
    precio_sin_impuestos: /no incluye impuestos/i.test(txt),
    ficha_marca: ficha('Marca'),
    ficha_modelo: ficha('Modelo'),
    numero_de_parte: (desc.match(/\b(WDB[A-Z0-9]{5,}-?[A-Z]*|SDSSDE[0-9A-Z-]+|MU-P[A-Z0-9]+|CT\d+X\d+SSD\d*|SXS\d+\/\d+G)\b/i) || [])[1] || '',
    tiene_descripcion: desc.length > 200,
  };
})();
