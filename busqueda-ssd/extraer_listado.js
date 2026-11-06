// Extrae las publicaciones de una página de listado de Mercado Libre Argentina
// y las acumula en localStorage ('ssd_resultados'), para juntar varias búsquedas.
// Uso: estando en listado.mercadolibre.com.ar, ejecutar este código (consola o
// javascript_tool). Devuelve cuántas publicaciones leyó y cuántas hay acumuladas.
// Para empezar de cero: localStorage.removeItem('ssd_resultados')
(async () => {
  // Esperar a que la página termine de mostrar las publicaciones (hasta 10 s)
  for (let i = 0; i < 20 && !document.querySelector('.poly-card'); i++) await new Promise((r) => setTimeout(r, 500));
  const monto = (el) => {
    const m = (el?.getAttribute('aria-label') || '').match(/^\s*([\d.]+)/);
    return m ? Number(m[1].replace(/\./g, '')) : null;
  };
  const limpiarLink = (href) => {
    const wid = (href.match(/[#&]wid=(MLA\d+)/) || [])[1];
    // Publicidad: el link es de tracking (click1.mercadolibre...), se arma el directo
    if (/mclics|click1\./.test(href) && wid) return 'https://articulo.mercadolibre.com.ar/MLA-' + wid.slice(3);
    return href.split('#')[0];
  };
  const leidos = [...document.querySelectorAll('.poly-card')].map((c) => {
    const a = c.querySelector('a.poly-component__title');
    const href = a?.href || '';
    const txt = c.innerText;
    return {
      id: (href.match(/[#&]wid=(MLA\d+)/) || href.match(/(MLA-?\d+)/) || [])[1]?.replace('-', '') || href,
      titulo: a ? a.innerText.trim() : '',
      precio: monto(c.querySelector('.poly-price__current .andes-money-amount')),
      precio_anterior: monto(c.querySelector('.andes-money-amount--previous')),
      vendedor: (c.querySelector('.poly-component__seller')?.innerText || '').replace(/^Por\s+/i, '').trim(),
      envio_gratis: /env[ií]o gratis|llega gratis/i.test(txt),
      internacional: /Internacional/i.test(txt),
      condicion_texto: (txt.match(/\b(Usado|Reacondicionado)\b/) || [])[1] || '',
      busqueda: location.pathname,
      link: limpiarLink(href),
    };
  }).filter((r) => r.titulo);
  const acum = JSON.parse(localStorage.getItem('ssd_resultados') || '{}');
  leidos.forEach((r) => { acum[r.id] = r; });
  localStorage.setItem('ssd_resultados', JSON.stringify(acum));
  return { leidos: leidos.length, acumulados: Object.keys(acum).length,
           siguiente: document.querySelector('.andes-pagination__button--next a')?.href || null };
})();
