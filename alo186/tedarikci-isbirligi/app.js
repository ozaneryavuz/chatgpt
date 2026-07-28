(() => {
  'use strict';

  const labels = {
    category: {
      ups: 'UPS ve enerji depolama',
      portable: 'Power station ve taşınabilir enerji',
      ev: 'EV şarj',
      solar: 'GES ve inverter',
      safety: 'Elektrik güvenliği ve koruma',
      measurement: 'Ölçüm ve test cihazları'
    },
    type: {
      data: 'Teknik veri doğrulama kartı',
      sponsored: 'Açık sponsorlu teknik içerik',
      category: 'Kategori destekçiliği',
      document: 'Kılavuz / teknik doküman kalite kontrolü'
    },
    readiness: {
      complete: 'Resmî teknik veri ve kılavuz hazır',
      partial: 'Bazı teknik belgeler hazır',
      unknown: 'Gerekli belge listesini öğrenmek istiyorum'
    },
    goal: {
      accuracy: 'Teknik verinin doğru sunulması',
      education: 'Kullanıcı eğitim içeriği',
      visibility: 'Şeffaf sponsorlu görünürlük',
      launch: 'Yeni ürün lansman desteği'
    }
  };

  const byId = (id) => document.getElementById(id);
  const safeChoice = (group, id) => {
    const value = String(byId(id).value || '');
    return Object.prototype.hasOwnProperty.call(labels[group], value) ? value : Object.keys(labels[group])[0];
  };

  function track(name, data = {}) {
    const clean = {};
    for (const key of ['category', 'type', 'readiness', 'goal']) {
      if (typeof data[key] === 'string' && data[key].length < 60) clean[key] = data[key];
    }
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...clean });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = byId('partnerForm');
    const link = byId('mailLink');

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const selection = {
        category: safeChoice('category', 'category'),
        type: safeChoice('type', 'type'),
        readiness: safeChoice('readiness', 'readiness'),
        goal: safeChoice('goal', 'goal')
      };
      const readable = {
        category: labels.category[selection.category],
        type: labels.type[selection.type],
        readiness: labels.readiness[selection.readiness],
        goal: labels.goal[selection.goal]
      };

      byId('resultTitle').textContent = `${readable.category} için iş birliği talebi hazır.`;
      byId('resultText').textContent = 'Taslak; sponsorlu ilişkinin etiketlenmesi, teknik kaynak zorunluluğu ve organik sıralamanın satın alınamayacağı koşulunu içerir.';
      byId('summary').innerHTML = [
        ['Ürün alanı', readable.category],
        ['İş birliği türü', readable.type],
        ['Kaynak hazırlığı', readable.readiness],
        ['Hedef', readable.goal]
      ].map(([title, value]) => `<div><strong>${title}</strong>${value}</div>`).join('');

      const subject = `ALO186 tedarikçi/üretici iş birliği — ${readable.category}`;
      const body = [
        'Merhaba,',
        '',
        'ALO186 tedarikçi ve üretici iş birliği hakkında bilgi rica ediyorum.',
        '',
        `Ürün alanı: ${readable.category}`,
        `İş birliği türü: ${readable.type}`,
        `Kaynak hazırlığı: ${readable.readiness}`,
        `Hedef: ${readable.goal}`,
        '',
        'Sponsorlu ilişkinin açıkça etiketlenmesini, organik teknik sıralamanın ödeme ile değiştirilmemesini ve bütün teknik iddiaların resmî kaynaklarla doğrulanmasını kabul ediyorum.',
        '',
        'Kapsam, ücret, teslim ve gerekli belge listesinin yazılı olarak iletilmesini rica ederim.'
      ].join('\n');

      link.href = `mailto:bilgi@alo186.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      link.classList.remove('disabled');
      link.setAttribute('aria-disabled', 'false');
      link.tabIndex = 0;
      track('supplier_partnership_request_prepared', selection);
    });

    link.addEventListener('click', (event) => {
      if (link.getAttribute('aria-disabled') === 'true') {
        event.preventDefault();
        return;
      }
      track('supplier_partnership_email_opened', {
        category: safeChoice('category', 'category'),
        type: safeChoice('type', 'type'),
        readiness: safeChoice('readiness', 'readiness'),
        goal: safeChoice('goal', 'goal')
      });
    });
  });
})();
