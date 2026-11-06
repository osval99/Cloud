// Lee los datos de una publicación (página de producto) de Mercado Libre.
// Devuelve título, condición, precio, vendedor, envío gratis y si es compra internacional.
(async () => {
  for (let i = 0; i < 20 && !document.querySelector('.ui-pdp-title'); i++) await new Promise((r) => setTimeout(r, 500));
  const q = (s) => document.querySelector(s)?.innerText.replace(/\s+/g, ' ').trim() || '';
  const main = document.querySelector('.ui-pdp-container__col.col-1, .ui-pdp-container--column-right, #root-app') || document.body;
  const txt = main.innerText;
  const precio = (document.querySelector('.ui-pdp-price__second-line .andes-money-amount')?.getAttribute('aria-label') || '').match(/^\s*(\d+)/);
  return {
    url: location.href.split('#')[0],
    titulo: q('.ui-pdp-title'),
    condicion: q('.ui-pdp-header__subtitle').split('|')[0].trim(),
    precio: precio ? Number(precio[1]) : null,
    vendedor: q('.ui-pdp-seller__header__title') || q('.ui-seller-data-header__title') || q('.ui-pdp-seller-summary__header__title'),
    envio_gratis: /(llega|env[ií]o) gratis/i.test(txt),
    internacional: /compra internacional|internacional/i.test(txt),
  };
})();
