(() => {
  'use strict';

  const catalog = window.ALO186SmartPlugCatalogV253;
  if (!catalog) return;

  const readinessIds = [
    'gateConsumerUse',
    'gateGrounded',
    'gateLoad',
    'gateNoHighRisk',
    'gateCondition',
    'gateIndoor',
    'gateFeature',
    'gateVariant'
  ];
  const commerceIds = ['gateNeed', 'gateAffiliate'];
  const allGateIds = readinessIds.concat(commerceIds);
  const status = document.getElementById('gateStatus');
  const unlock = document.getElementById('unlockProducts');
  const noBuy = document.getElementById('noBuySmartPlug');
  const reminder = document.getElementById('smartPlugReminder90');
  const links = Array.from(document.querySelectorAll('[data-affiliate-asin]'));

  function track(name, params) {
    if (typeof window.Alo186Track === 'function') window.Alo186Track(name, params || {});
  }

  function checked(id) {
    const element = document.getElementById(id);
    return Boolean(element && element.checked);
  }

  function setStatus(message) {
    if (status) status.textContent = message;
  }

  function lockLinks(state) {
    links.forEach((link) => {
      link.removeAttribute('href');
      link.removeAttribute('target');
      link.setAttribute('aria-disabled', 'true');
      link.setAttribute('tabindex', '-1');
      link.dataset.state = state || 'locked';
    });
  }

  function updateUnlockState() {
    if (!unlock) return;
    unlock.disabled = !allGateIds.every(checked);
  }

  function openLinks() {
    if (!allGateIds.every(checked)) {
      setStatus('Önce güvenlik, kullanım, gerçek ihtiyaç ve satış ortaklığı koşullarının tamamını doğrulayın.');
      return;
    }

    if (catalog.category.affiliatePolicy !== 'after_tool' || catalog.category.professionalOnly || catalog.category.highRiskDirectCta) {
      lockLinks('blocked');
      setStatus('Bu kullanım kapsamı doğrudan ürün bağlantısına uygun değildir.');
      track('affiliate_products_blocked', { category: catalog.category.id, reason: 'policy' });
      return;
    }

    let opened = 0;
    links.forEach((link) => {
      const product = catalog.products.find((item) => item.asin === link.dataset.affiliateAsin);
      const url = product ? catalog.amazonProductUrl(product, new Date()) : null;
      if (!url) {
        link.dataset.state = 'stale';
        return;
      }
      link.href = url;
      link.target = '_blank';
      link.rel = 'sponsored nofollow noopener';
      link.removeAttribute('aria-disabled');
      link.removeAttribute('tabindex');
      link.dataset.state = 'open';
      opened += 1;
    });

    if (opened) {
      setStatus('Kontroller tamamlandı. Yalnız ihtiyacınıza uyan kartın Amazon Türkiye sayfasında ASIN, MPN, akım, güç, fiş tipi ve ölçüm işlevini yeniden doğrulayın.');
      track('affiliate_gate_passed', { category: catalog.category.id, product_count: opened });
    } else {
      setStatus('Ürün kimliği doğrulama süresi dolmuş veya katalog uygun değil; mağaza bağlantıları kapalı kaldı.');
      track('affiliate_products_blocked', { category: catalog.category.id, reason: 'stale_catalog' });
    }
  }

  function selectNoBuy() {
    lockLinks('no_buy');
    allGateIds.forEach((id) => {
      const element = document.getElementById(id);
      if (!element) return;
      element.checked = false;
      element.disabled = true;
    });
    if (unlock) unlock.disabled = true;
    if (noBuy) noBuy.disabled = true;
    setStatus('Satın almama kararı hiçbir yere kaydedilmedi. Mevcut güvenli çözümü kullanın; yalnız yük, cihaz, ağ veya ölçüm ihtiyacı değişirse yeniden değerlendirin.');
    track('affiliate_no_buy_selected', { category: catalog.category.id, reason: 'existing_product_sufficient' });
  }

  function formatIcsDate(date) {
    return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
  }

  function escapeIcs(value) {
    return String(value)
      .replace(/\\/g, '\\\\')
      .replace(/\n/g, '\\n')
      .replace(/,/g, '\\,')
      .replace(/;/g, '\\;');
  }

  function downloadReminder() {
    const start = new Date();
    start.setDate(start.getDate() + 90);
    start.setHours(10, 0, 0, 0);
    const end = new Date(start.getTime() + 30 * 60 * 1000);
    const pageUrl = 'https://alo186.com/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/';
    const description = escapeIcs([
      'Akıllı priz veya enerji ölçer ihtiyacını yeniden değerlendirin.',
      'Priz ve fişte ısınma, gevşeklik veya kararma varsa ürün bağlamayın.',
      'Yük, cihaz, ağ ya da ölçüm ihtiyacı değişmediyse ve mevcut çözüm yeterliyse yeni ürün almayın.',
      pageUrl
    ].join('\n'));
    const ics = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Akilli Priz Kontrolu//TR',
      'CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',
      `UID:alo186-akilli-priz-kontrol-${Date.now()}@alo186.com`,
      `DTSTAMP:${formatIcsDate(new Date())}`,
      `DTSTART:${formatIcsDate(start)}`,
      `DTEND:${formatIcsDate(end)}`,
      'SUMMARY:ALO186 akıllı priz güvenlik ve ihtiyaç kontrolü',
      `DESCRIPTION:${description}`,
      `URL:${pageUrl}`,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');

    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = 'alo186-akilli-priz-90-gun-kontrol.ics';
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
    setStatus('90 günlük kontrol takvimi yalnız cihazınızda oluşturuldu; kişisel veri gönderilmedi.');
    track('return_visit_reminder_downloaded', { category: catalog.category.id, days: 90, placement: 'smart_plug_page' });
  }

  allGateIds.forEach((id) => {
    const element = document.getElementById(id);
    if (element) element.addEventListener('change', updateUnlockState);
  });
  if (unlock) unlock.addEventListener('click', openLinks);
  if (noBuy) noBuy.addEventListener('click', selectNoBuy);
  if (reminder) reminder.addEventListener('click', downloadReminder);

  links.forEach((link) => {
    link.addEventListener('click', (event) => {
      if (!link.getAttribute('href')) {
        event.preventDefault();
        setStatus('Mağaza bağlantısı kapalı. Önce bütün güvenlik ve ihtiyaç koşullarını doğrulayın veya satın almama seçeneğini kullanın.');
        return;
      }
      const product = catalog.products.find((item) => item.asin === link.dataset.affiliateAsin);
      track('affiliate_product_clicked', {
        category: catalog.category.id,
        product_id: product ? product.id : 'unknown',
        asin: link.dataset.affiliateAsin,
        placement: 'smart_plug_page_after_gate'
      });
    });
  });

  lockLinks('locked');
  updateUnlockState();
  setStatus('Mağaza bağlantıları güvenlik, teknik uygunluk, gerçek ihtiyaç ve satış ortaklığı açıklaması doğrulanana kadar kapalıdır.');
  track('affiliate_gate_viewed', { category: catalog.category.id, product_count: links.length });
})();
