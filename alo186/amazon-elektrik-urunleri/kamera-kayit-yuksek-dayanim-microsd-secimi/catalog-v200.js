(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && typeof root === 'object') root.Alo186EnduranceMicroSDCatalogV200 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';

  const version = 200;
  const affiliateTag = 'alo186rehber-21';
  const verifiedAt = '2026-08-02';
  const maxAgeDays = 45;
  const products = Object.freeze([
    Object.freeze({ asin: 'B07NY23WBG', mpn: 'SDSQQNR-128G-GN6IA', brand: 'SanDisk' }),
    Object.freeze({ asin: 'B07PGBYMVH', mpn: 'SDCE/128GB', brand: 'Kingston' }),
    Object.freeze({ asin: 'B084CJ9T2R', mpn: 'SDSQQVR-128G-GN6IA', brand: 'SanDisk' })
  ]);

  function dateOnly(value) {
    const text = value instanceof Date ? value.toISOString().slice(0, 10) : String(value || '').slice(0, 10);
    const date = new Date(`${text}T00:00:00Z`);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function verificationStatus(now = new Date()) {
    const checked = dateOnly(verifiedAt);
    const today = dateOnly(now);
    if (!checked || !today) return Object.freeze({ fresh: false, ageDays: null });
    const ageDays = Math.max(0, Math.floor((today - checked) / 86400000));
    return Object.freeze({ fresh: ageDays <= maxAgeDays, ageDays });
  }

  function amazonProductUrl(asin) {
    if (!products.some(item => item.asin === asin)) throw new Error('Katalog dışı ASIN');
    return `https://www.amazon.com.tr/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(affiliateTag)}`;
  }

  return Object.freeze({ version, affiliateTag, verifiedAt, maxAgeDays, products, verificationStatus, amazonProductUrl });
});
