(() => {
  'use strict';
  const start = () => {
    const catalog = window.Alo186ModemEthernetSwitchCatalogV232;
    const toolChecks = ['toolPortNeed','toolSpeed','toolNoPoe','toolCable','toolScope','toolExisting'];
    const commerceChecks = ['gateNeed','gateAffiliate'];
    const toolButton = document.getElementById('runCompatibilityTool');
    const toolResult = document.getElementById('toolResult');
    const gatePanel = document.getElementById('gatePanel');
    const gateStatus = document.getElementById('gateStatus');
    const links = [...document.querySelectorAll('[data-affiliate-asin]')];
    let toolPassed = false;
    let toolEvaluated = false;
    if (!catalog || !toolButton || !toolResult || !gatePanel || !gateStatus) return;

    const retestWrap = document.createElement('div');
    retestWrap.className = 'result';
    retestWrap.dataset.alo186NetworkRetest = 'true';
    retestWrap.innerHTML = '<strong>Tekrar ziyaret nedeni</strong><p>Port sayısı, modem/router, uç cihaz veya bağlantı hızı değiştiğinde ölçümü yenileyin. Takvim kaydı yalnız cihazınızda oluşturulur; ad, e-posta, adres veya seri numarası istenmez.</p><button id="downloadNetworkRetest" type="button" disabled>90 günlük yeniden ölçümü takvime ekle</button><p id="networkRetestStatus" aria-live="polite">Önce teknik ön kontrolü çalıştırın.</p>';
    toolResult.insertAdjacentElement('afterend', retestWrap);
    const retestButton = retestWrap.querySelector('#downloadNetworkRetest');
    const retestStatus = retestWrap.querySelector('#networkRetestStatus');

    const checked = (ids) => ids.every((id) => document.getElementById(id)?.checked === true);
    const pad = (value) => String(value).padStart(2,'0');
    const utcStamp = (date) => `${date.getUTCFullYear()}${pad(date.getUTCMonth()+1)}${pad(date.getUTCDate())}T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}${pad(date.getUTCSeconds())}Z`;
    const downloadRetest = () => {
      if (!toolEvaluated) return;
      const now = new Date();
      const review = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000);
      review.setUTCHours(9,0,0,0);
      const uid = `alo186-network-retest-${now.getTime()}@alo186.com`;
      const description = 'Modem/router port sayısını, gerçek Ethernet link hızını, kabloyu, mevcut düzeni ve PoE ihtiyacını yeniden doğrulayın. Mevcut çözüm yeterliyse yeni ürün almayın.';
      const ics = [
        'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Ethernet Network Retest//TR','CALSCALE:GREGORIAN','METHOD:PUBLISH',
        'BEGIN:VEVENT',`UID:${uid}`,`DTSTAMP:${utcStamp(now)}`,`DTSTART:${utcStamp(review)}`,'DURATION:PT30M',
        'SUMMARY:ALO186 Ethernet ağı yeniden ölçümü',`DESCRIPTION:${description}`,
        'URL:https://alo186.com/amazon-elektrik-urunleri/modem-ethernet-switch-port-hiz-olcum-secimi/','END:VEVENT','END:VCALENDAR',''
      ].join('\r\n');
      const blob = new Blob([ics], {type:'text/calendar;charset=utf-8'});
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'alo186-ethernet-agi-90-gun-yeniden-olcum.ics';
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      retestStatus.textContent = '90 günlük yerel takvim kaydı oluşturuldu. Koşullar daha önce değişirse ölçümü beklemeden yenileyin.';
    };

    const sync = () => {
      const freshness = catalog.verificationStatus(new Date());
      const categoryAllowed = catalog.category.affiliatePolicy === 'after_tool'
        && catalog.category.requiredTool === 'embedded-modem-ethernet-switch-measurement-v232'
        && catalog.category.professionalOnly === false
        && catalog.category.risk === 'consumer-medium';
      const gateOpen = categoryAllowed && toolPassed && checked(commerceChecks) && freshness.fresh;
      const knownAsins = new Set(catalog.products.map((item) => item.asin));
      gatePanel.dataset.open = String(gateOpen);
      if (retestButton) retestButton.disabled = !toolEvaluated;
      if (retestStatus && !toolEvaluated) retestStatus.textContent = 'Önce teknik ön kontrolü çalıştırın.';
      links.forEach((link) => {
        const permitted = gateOpen && knownAsins.has(link.dataset.affiliateAsin);
        if (permitted) {
          link.href = catalog.amazonProductUrl(link.dataset.affiliateAsin);
          link.classList.remove('locked');
          link.removeAttribute('aria-disabled');
          link.tabIndex = 0;
        } else {
          link.removeAttribute('href');
          link.classList.add('locked');
          link.setAttribute('aria-disabled','true');
          link.tabIndex = -1;
        }
      });
      if (!freshness.fresh) gateStatus.textContent = 'Teknik doğrulama 45 günü aştı; Amazon bağlantıları kapalı.';
      else if (!toolPassed) gateStatus.textContent = 'Önce port sayısı, hız, PoE, kablo ve kullanım kapsamını doğrulayın.';
      else if (!checked(commerceChecks)) gateStatus.textContent = 'Teknik ön kontrol geçti; ihtiyaç ve satış ortaklığı açıklamasını doğrulayın.';
      else if (!categoryAllowed) gateStatus.textContent = 'Kategori güven sözleşmesi doğrulanamadı; bağlantılar kapalı.';
      else gateStatus.textContent = 'Koşullar tamamlandı. Amazon kaydında ASIN, MPN ve donanım sürümünü yeniden doğrulayın.';
    };
    toolButton.addEventListener('click', () => {
      toolEvaluated = true;
      toolPassed = checked(toolChecks);
      toolResult.dataset.passed = String(toolPassed);
      toolResult.textContent = toolPassed
        ? 'Ön kontrol geçti: yalnız kritik olmayan modem/ev-ofis Ethernet port genişletmesi için ürün karşılaştırılabilir.'
        : 'Ön kontrol geçmedi: port, hız, PoE, kablo, mevcut çözüm ve kritik olmayan kullanım birlikte doğrulanmalıdır.';
      if (retestStatus) retestStatus.textContent = toolPassed
        ? 'Ölçüm sonucu kaydedilmedi. İsterseniz 90 gün sonrası için yalnız cihazınızda takvim kaydı oluşturun.'
        : 'Eksikleri düzelttikten sonra yeniden ölçün; isterseniz 90 günlük yerel hatırlatıcı oluşturun.';
      sync();
    });
    [...toolChecks,...commerceChecks].forEach((id) => document.getElementById(id)?.addEventListener('change', () => {
      if (toolChecks.includes(id)) {
        toolPassed = false;
        toolEvaluated = false;
        toolResult.dataset.passed = 'false';
        toolResult.textContent = 'Teknik girdiler değişti; ön kontrolü yeniden çalıştırın.';
      }
      sync();
    }));
    document.getElementById('resetGate')?.addEventListener('click', () => {
      [...toolChecks,...commerceChecks].forEach((id) => {
        const input = document.getElementById(id);
        if (input) input.checked = false;
      });
      toolPassed = false;
      toolEvaluated = false;
      toolResult.dataset.passed = 'false';
      toolResult.textContent = 'Henüz değerlendirilmedi.';
      sync();
    });
    retestButton?.addEventListener('click', downloadRetest);
    links.forEach((link) => link.addEventListener('click', (event) => {
      if (!toolPassed || !checked(commerceChecks) || !catalog.verificationStatus(new Date()).fresh || !link.href) {
        event.preventDefault();
        sync();
      }
    }));
    sync();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();
