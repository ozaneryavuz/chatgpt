(() => {
  'use strict';

  const byId = (id) => document.getElementById(id);
  const allowedValues = {
    setting: ['home', 'small_business', 'hotel_site'],
    priority: ['internet', 'mobile', 'electronics', 'lighting', 'cold_chain', 'long_outage'],
    duration: ['short', 'medium', 'long'],
    existing: ['none', 'works', 'weak', 'unknown']
  };

  const routes = {
    internet: {
      title: 'İnternet sürekliliği planı',
      calculate: ['/hesaplama/modem-internet-yedekleme/', 'Önce modem ve ONT yükünü hesapla'],
      product: ['/akilli-urun-secimi?kategori=mini_ups', 'Teknik sonucu ürün merkezinde karşılaştır'],
      steps: ['Modem ve ONT etiketindeki voltaj, akım ve polariteyi kaydedin.', 'Toplam watt ve hedef süreye göre gerekli Wh değerini hesaplayın.', 'Yalnız voltaj, jak, polarite ve çıkış akımı doğrulanmışsa mini UPS sınıfına ilerleyin.']
    },
    mobile: {
      title: 'Telefon ve USB-C yedekleme planı',
      calculate: ['/hesaplama/powerbank-usb-c-uygunluk/', 'Önce powerbank ve USB-C uygunluğunu hesapla'],
      product: ['/akilli-urun-secimi?kategori=powerbank', 'Teknik minimumla powerbank karşılaştır'],
      steps: ['Cihazın ihtiyaç duyduğu USB-C PD watt değerini belirleyin.', 'mAh etiketini gerçek Wh ve aktarım kaybıyla değerlendirin.', 'Mevcut powerbank yeterliyse yeni ürün satın almayın.']
    },
    electronics: {
      title: 'Hassas elektronik koruma planı',
      calculate: ['/hesaplama/parafudr-risk-testi/', 'Önce aşırı gerilim riskini değerlendir'],
      product: ['/akilli-urun-secimi?kategori=surge_strip', 'Tak-çalıştır koruma sınıfını karşılaştır'],
      steps: ['Ani darbe ile sürekli yüksek/düşük gerilim sorununu ayırın.', 'Pano tipi SPD, gerilim rölesi, topraklama ve priz tipi ürünün farklı görevleri olduğunu kabul edin.', 'Yalnız fişli düşük riskli cihazlarda grup priz sınıfını değerlendirin.']
    },
    lighting: {
      title: 'Acil aydınlatma planı',
      calculate: ['/hesaplama/kesinti-hazirlik-plani/', 'Kesinti hazırlık planını oluştur'],
      product: ['/akilli-urun-secimi?kategori=emergency_light', 'Acil aydınlatma kontrol listesini aç'],
      steps: ['Karanlıkta fiziksel düğmeyle açılan en az bir aydınlatma noktası belirleyin.', 'En parlak mod yerine düşük moddaki gerçek çalışma süresini karşılaştırın.', 'Mevcut lambanın test ve runtime sonucu yeterliyse yeni ürün almayın.']
    },
    cold_chain: {
      title: 'Buzdolabı ve soğuk zincir planı',
      calculate: ['/hesaplama/yedek-guc-cozum-secici/', 'Yük ve süreye göre çözüm sınıfını belirle'],
      product: ['/akilli-urun-secimi?kategori=power_station', 'Düşük riskli taşınabilir sonucu karşılaştır'],
      steps: ['Buzdolabı/soğuk zincir yükünü, kompresör kalkışını ve hedef süreyi ayrı hesaplayın.', 'Kapı açma sıklığını azaltın ve sıcaklığı termometreyle izleyin.', 'İşletme veya uzun süreli kullanımda profesyonel jeneratör/UPS planına ilerleyin.']
    },
    long_outage: {
      title: 'Uzun süreli yedek güç planı',
      calculate: ['/hesaplama/yedek-guc-cozum-secici/', 'UPS, power station, inverter ve jeneratörü ayır'],
      product: ['/akilli-urun-secimi?kategori=power_station', 'Yalnız düşük riskli taşınabilir sonucu karşılaştır'],
      steps: ['Kritik ve kritik olmayan yükleri ayırın.', 'Sürekli watt, kalkış watt ve hedef Wh ihtiyacını hesaplayın.', 'Sabit tesisat, yüksek güç veya uzun süre sonucunda profesyonel proje ve transfer planına ilerleyin.']
    }
  };

  function safeValue(id) {
    const value = String(byId(id).value || '');
    return allowedValues[id].includes(value) ? value : allowedValues[id][0];
  }

  function track(name, data = {}) {
    const clean = {};
    for (const [key, value] of Object.entries(data)) {
      if (['setting', 'priority', 'duration', 'existing', 'route'].includes(key) && typeof value === 'string' && value.length < 80) clean[key] = value;
    }
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...clean });
  }

  function stepMarkup(items) {
    return items.map((text, index) => `<div class="step"><span>${index + 1}</span><div><strong>${index === 0 ? 'Önce doğrulayın' : index === 1 ? 'Sonra hesaplayın' : 'En son karar verin'}</strong>${text}</div></div>`).join('');
  }

  function action(url, label, secondary = false, dataRoute = '') {
    return `<a class="button ${secondary ? 'secondary' : 'primary'}" href="${url}" data-route="${dataRoute || url}">${label}</a>`;
  }

  function outcomeUrl({ priority }, route) {
    const params = new URLSearchParams({
      kaynak: 'kesinti-atolyesi',
      kategori: priority,
      rota: route
    });
    return `/hesaplama/cozum-sonucu/?${params.toString()}`;
  }

  function outcomeAction(selection, route) {
    return action(outcomeUrl(selection, route), 'Uyguladıktan sonra sonucu kaydet', true, 'solution_outcome');
  }

  function renderPlan({ setting, priority, duration, existing }) {
    const selection = { setting, priority, duration, existing };
    const plan = routes[priority];
    const resultTitle = byId('resultTitle');
    const resultText = byId('resultText');
    const steps = byId('resultSteps');
    const actions = byId('resultActions');
    const disclosure = byId('affiliateDisclosure');

    resultTitle.textContent = plan.title;
    steps.innerHTML = stepMarkup(plan.steps);
    disclosure.classList.add('hidden');

    if (existing === 'works') {
      resultText.textContent = 'Mevcut çözümünüz ihtiyacı karşılıyorsa yeni ürün almayın. Bakım ve yeniden test planı oluşturun.';
      actions.innerHTML = action('/hesaplama/ekipman-bakim-plani/', 'Mevcut ekipmanı koruma planı oluştur')
        + action(plan.calculate[0], plan.calculate[1], true)
        + outcomeAction(selection, 'buy_nothing');
      track('fast_revenue_plan_rendered', { setting, priority, duration, existing, route: 'buy_nothing' });
      return;
    }

    if (setting === 'hotel_site' || (setting === 'small_business' && (priority === 'cold_chain' || priority === 'long_outage')) || duration === 'long') {
      resultText.textContent = 'Bu senaryoda tek ürün seçimi yerine kritik yük, süre, transfer ve bakım planı birlikte değerlendirilmelidir. Ücretli profesyonel ön değerlendirme rotası açıldı.';
      actions.innerHTML = action('/kurumsal-elektrik-surekliligi-on-degerlendirme', 'Ücretli kurumsal ön değerlendirmeyi incele', false, 'paid_b2b')
        + action(plan.calculate[0], plan.calculate[1], true, 'free_tool')
        + outcomeAction(selection, 'paid_b2b');
      track('fast_revenue_plan_rendered', { setting, priority, duration, existing, route: 'paid_b2b' });
      return;
    }

    resultText.textContent = existing === 'unknown'
      ? 'Mevcut ekipmanın yeterli olup olmadığını önce ücretsiz hesapla doğrulayın. Sonuç yetersizse ürün merkezine ilerleyin.'
      : 'Önce ücretsiz hesabı tamamlayın; yalnız gerçek kapasite veya güvenlik açığı varsa ürün sınıfını karşılaştırın.';
    actions.innerHTML = action(plan.calculate[0], plan.calculate[1], false, 'free_tool')
      + action(plan.product[0], plan.product[1], true, 'affiliate_product_center')
      + outcomeAction(selection, 'affiliate_product_center');
    disclosure.classList.remove('hidden');
    track('fast_revenue_plan_rendered', { setting, priority, duration, existing, route: 'affiliate_product_center' });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = byId('workshopForm');
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const selection = {
        setting: safeValue('setting'),
        priority: safeValue('priority'),
        duration: safeValue('duration'),
        existing: safeValue('existing')
      };
      renderPlan(selection);
      byId('result').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    });

    byId('resultActions').addEventListener('click', (event) => {
      const link = event.target.closest('a[data-route]');
      if (!link) return;
      track('fast_revenue_route_opened', { route: link.dataset.route });
    });
  });
})();
