(() => {
  'use strict';

  if (typeof window.Alo186Track === 'function') return;

  const blockedKeyPattern = /(email|mail|phone|telefon|address|adres|name|isim|query|search|text|message|mesaj|tc|identity|abonelik|tesisat|location|konum)/i;
  const allowedKeys = new Set([
    'category',
    'product_id',
    'asin',
    'placement',
    'route',
    'days',
    'state',
    'reason',
    'source',
    'product_count',
    'link_count',
    'changes',
    'original_host',
    'technical_route'
  ]);

  function safeEventName(value) {
    const normalized = String(value || '')
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9_]+/g, '_')
      .replace(/^_+|_+$/g, '')
      .slice(0, 64);
    return normalized && /^[a-z][a-z0-9_]*$/.test(normalized) ? normalized : '';
  }

  function safeString(value) {
    return String(value || '')
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9_./:-]+/g, '_')
      .replace(/_+/g, '_')
      .slice(0, 96);
  }

  function sanitize(params) {
    const output = {};
    Object.entries(params || {}).forEach(([key, value]) => {
      if (!allowedKeys.has(key) || blockedKeyPattern.test(key)) return;
      if (typeof value === 'number' && Number.isFinite(value)) {
        output[key] = Math.max(-1000000, Math.min(1000000, value));
        return;
      }
      if (typeof value === 'boolean') {
        output[key] = value;
        return;
      }
      if (typeof value === 'string') {
        const normalized = safeString(value);
        if (normalized) output[key] = normalized;
      }
    });
    return output;
  }

  window.Alo186Track = function Alo186Track(name, params) {
    const eventName = safeEventName(name);
    if (!eventName) return false;

    const detail = Object.freeze({
      event: `alo186_${eventName}`,
      ...sanitize(params)
    });

    if (Array.isArray(window.dataLayer)) {
      window.dataLayer.push(detail);
    }

    window.dispatchEvent(new CustomEvent('alo186:analytics', { detail }));
    return true;
  };
})();
