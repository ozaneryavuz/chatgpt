(() => {
  'use strict';

  const allowedEvents = new Set([
    'tool_started',
    'tool_completed',
    'no_buy_selected',
    'affiliate_unlocked',
    'affiliate_clicked',
    'reminder_downloaded'
  ]);
  const allowedKeys = new Set(['journey', 'step', 'outcome', 'product_class']);
  const safeToken = /^[a-z0-9_-]{1,48}$/;

  function sanitize(value) {
    if (typeof value !== 'string') return undefined;
    const token = value.trim().toLowerCase();
    return safeToken.test(token) ? token : undefined;
  }

  function emit(eventName, fields = {}) {
    if (!allowedEvents.has(eventName)) return false;
    const detail = { event: eventName };
    Object.entries(fields).forEach(([key, value]) => {
      if (!allowedKeys.has(key)) return;
      const safe = sanitize(value);
      if (safe) detail[key] = safe;
    });

    window.dispatchEvent(new CustomEvent('alo186:journey', { detail }));
    if (window.ALO186_ANALYTICS_CONSENT === true && Array.isArray(window.dataLayer)) {
      window.dataLayer.push({ event: 'alo186_journey', ...detail });
    }
    return true;
  }

  window.ALO186Journey = Object.freeze({ emit });
})();
