(() => {
  'use strict';
  const local = location.protocol === 'file:' || ['localhost', '127.0.0.1'].includes(location.hostname);
  const base = local ? '../../urun-eslestirme/' : '../../akilli-urun-secimi/';
  for (const file of ['catalog.js', 'catalog-knowledge-extension.js', 'catalog-sales-extension.js']) {
    document.write(`<script src="${base}${file}"><\/script>`);
  }
})();
