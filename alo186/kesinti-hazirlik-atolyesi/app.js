(() => {
  'use strict';

  const byId = (id) => document.getElementById(id);
  const allowedValues = {
    hazard: ['none', 'danger'],
    setting: ['home', 'small_business', 'hotel_site'],
    priority: ['internet', 'mobile', 'electronics', 'lighting', 'cold_chain', 'solar_backup', 'long_outage'],
    duration: ['short', 'medium', 'long'],
    existing: ['none', 'works', 'weak', 'unknown'],
    verified: ['yes', 'no']
  };

  const routes = {
    internet: {
      title: 'İnternet sürekliliği için önce yerel güç ile erişim ağını ayırın',
      calculate: ['/hesaplama/home-office-internet-sureklilik-plani/', 'İnternet sürekliliği planını tamamla'],
      product: ['/akilli-urun-secimi?kategori=mini_ups', 'Uygunluk sonrasında mini UPS sınıfını karşılaştır'],
      affiliateEligible: false,
      professional: true,
      steps: [
        'Modem ve ONT etiketindeki voltaj, akım, jak ve polariteyi kaydedin.',
        'Kesinti sırasında modem/ONT enerjiliyken internet yoksa upstream erişim ağı sorununu ayırın.',
        'Yalnız yerel güç açığı kanıtlandıktan sonra gerekli Wh ve çalışma süresini hesaplayın.'
      ]
    },
    mobile: {
      title: 'USB-C PD/PPS gücü doğrulanmış powerbank planı',
      calculate: ['/hesaplama/powerbank-usb-c-uygunluk/', 'Powerbank ve USB-C uygunluğunu hesapla'],
      product: ['/akilli-urun-secimi?kategori=powerbank', 'Satış ortaklığı ürünlerini teknik minimumla karşılaştır'],
      affiliateEligible: true,
      professional: false,
      steps: [
        'Cihazın azami USB-C PD/PPS watt değerini ve kablo sınıfını belirleyin.',
        'mAh etiketini gerçek Wh, aktarım kaybı ve eşzamanlı port paylaşımıyla değerlendirin.',
        'Mevcut powerbank hedefi karşılıyorsa yeni ürün satın almayın.'
      ]
    },
    electronics: {
      title: 'Hassas elektronik için ürün değil olay türü ve güç kalitesi planı',
      calculate: ['/hesaplama/gerilim-koruma-cozum-secici/', 'Gerilim ve koruma çözümünü ayır'],
      product: null,
      affiliateEligible: false,
      professional: true,
      steps: [
        'Ani darbe, gerilim çukuru, sürekli düşük/yüksek gerilim ve iç tesisat sorununu ayırın.',
        'UPS/AVR, SPD, gerilim rölesi ve topraklamanın farklı görevlerini değerlendirin.',
        'Cihaz reseti tekrarlıyorsa zaman damgalı ölçüm ve profesyonel inceleme oluşturun.'
      ]
    },
    lighting: {
      title: 'Taşınabilir acil aydınlatma planı',
      calculate: ['/hesaplama/acil-aydinlatma-sure-uygunluk/', 'Lümen ve çalışma süresi uygunluğunu hesapla'],
      product: ['/akilli-urun-secimi?kategori=emergency_light', 'Satış ortaklığı ürünlerini teknik minimumla karşılaştır'],
      affiliateEligible: true,
      professional: false,
      steps: [
        'Karanlıkta fiziksel düğmeyle açılabilen taşınabilir bir aydınlatma görevi belirleyin.',
        'En parlak mod yerine kullanacağınız moddaki gerçek lümen ve çalışma süresini karşılaştırın.',
        'Mevcut lambanın test ve runtime sonucu yeterliyse yeni ürün almayın.'
      ]
    },
    cold_chain: {
      title: 'Buzdolabı ve soğuk zincir için yük, kalkış ve süre planı',
      calculate: ['/hesaplama/yedek-guc-cozum-secici/', 'Yük ve süreye göre çözüm sınıfını belirle'],
      product: null,
      affiliateEligible: false,
      professional: true,
      steps: [
        'Kompresörün çalışma ve kalkış gücünü ayrı değerlendirin.',
        'Kapı açma sıklığını azaltın ve sıcaklığı bağımsız termometreyle izleyin.',
        'Uzun süre veya ticari soğuk zincirde jeneratör, transfer ve yakıt planını birlikte oluşturun.'
      ]
    },
    solar_backup: {
      title: 'GES yedek güç için önce sistem topolojisi ve ada işletmesini doğrulayın',
      calculate: ['/hesaplama/ges-elektrik-kesintisi-yedek-guc-uygunluk-kontrolu/', 'GES kesinti ve yedek güç uygunluğunu değerlendir'],
      product: null,
      affiliateEligible: false,
      professional: true,
      steps: [
        'İnverterin on-grid, hibrit veya off-grid olduğunu üretici belgesi ve mevcut proje üzerinden doğrulayın.',
        'Kesintide backup/EPS çıkışı, ayırma-transfer düzeni ve kritik yük devrelerinin gerçekten projelendirilmiş olup olmadığını kontrol edin.',
        'Mevcut sistem hedef yükleri kayıtlı gerçek kesinti testinde karşılıyorsa yeni ürün almayın; bakım ve periyodik test planını sürdürün.'
      ]
    },
    long_outage: {
      title: 'Uzun süreli yedek güç için profesyonel kapsam planı',
      calculate: ['/hesaplama/yedek-guc-cozum-secici/', 'UPS, power station, inverter ve jeneratörü ayır'],
      product: null,
      affiliateEligible: false,
      professional: true,
      steps: [
        'Kritik ve kritik olmayan yükleri ayırın.',
        'Sürekli watt, kalkış watt, hedef Wh ve yakıt/şarj döngüsünü hesaplayın.',
        'Sabit tesisat, transfer, topraklama ve bakım sorumluluklarını teknik kapsama bağlayın.'
      ]
    }
  };

  function safeValue(id) {
    const value = String(byId(id).value || '');
    return allowedValues[id].includes(value) ? value : allowedValues[id][0];
  }

  function track(name, data = {}) {
    const clean = {};
    const allowed = ['hazard', 'setting', 'priority', 'duration', 'existing', 'verified', 'route', 'segment'];
    for (const [key, value] of Object.entries(data)) {
      if (allowed.includes(key) && typeof value === 'string' && value.length < 100) clean[key] = value;
    }
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...clean });
    if (name === 'sales_funnel_rendered') {
      window.dataLayer.push({ event: 'fast_revenue_plan_rendered', ...clean });
    }
  }

  function stepMarkup(items) {
    return items.map((text, index) => `<div class="step"><span>${index + 1}</span><div><strong>${index === 0 ? 'Önce doğrulayın' : index === 1 ? 'Sonra hesaplayın' : 'En son karar verin'}</strong>${text}</div></div>`).join('');
  }

  function action(url, label, options = {}) {
    const kind = options.kind || 'primary';
    const route = options.route || url;
    const commercial = options.commercial || 'none';
    return `<a class="button ${kind}" href="${url}" data-route="${route}" data-commercial-stage="${commercial}">${label}</a>`;
  }

  function outcomeUrl(selection, route) {
    const params = new URLSearchParams({
      kaynak: 'kesinti-atolyesi',
      kategori: selection.priority,
      rota: route
    });
    return `/hesaplama/cozum-sonucu/?${params.toString()}`;
  }

  function outcomeAction(selection, route) {
    return action(outcomeUrl(selection, route), 'Uyguladıktan sonra sonucu kaydet', { kind: 'secondary', route: 'solution_outcome' });
  }

  function renderDanger(selection) {
    byId('resultTitle').textContent = 'Satın alma ve hizmet yönlendirmesi kapatıldı';
    byId('resultText').textContent = 'Aktif can veya yangın riski ürün seçimiyle çözülemez. Tehlikeli alana yaklaşmayın; güvenli mesafeden acil ve resmî kanalı kullanın.';
    byId('resultSteps').innerHTML = stepMarkup([
      'İnsanları riskli alandan uzaklaştırın; güvenli değilse şalter veya cihaza dokunmayın.',
      'Yangın, duman, elektrik çarpması veya aktif kıvılcımda 112’yi arayın.',
      'Şebeke, sayaç önü veya servis hattı şüphesinde 186 ve ilgili EDAŞ’ın resmî kanalını kullanın.'
    ]);
    byId('resultActions').innerHTML = action('tel:112', '112 Acil’i ara', { route: 'emergency_112' })
      + action('/edas-bul', 'Doğru EDAŞ kanalını bul', { kind: 'secondary', route: 'edas_official' });
    byId('affiliateDisclosure').classList.add('hidden');
    track('sales_funnel_rendered', { ...selection, route: 'hazard_closed', segment: 'safety' });
  }

  function renderPlan(selection) {
    const { hazard, setting, priority, duration, existing, verified } = selection;
    const plan = routes[priority];
    const resultTitle = byId('resultTitle');
    const resultText = byId('resultText');
    const steps = byId('resultSteps');
    const actions = byId('resultActions');
    const disclosure = byId('affiliateDisclosure');

    disclosure.classList.add('hidden');
    if (hazard === 'danger') {
      renderDanger(selection);
      return;
    }

    resultTitle.textContent = plan.title;
    steps.innerHTML = stepMarkup(plan.steps);

    if (existing === 'works') {
      resultText.textContent = 'Mevcut çözümünüz güvenli ve hedef süreyi karşılıyorsa yeni ürün almayın. Bakım, periyodik test ve sonuç kaydı oluşturun.';
      actions.innerHTML = action('/hesaplama/ekipman-bakim-plani/', 'Mevcut ekipmanı koruma planı oluştur', { route: 'no_buy_maintenance' })
        + action(plan.calculate[0], plan.calculate[1], { kind: 'secondary', route: 'free_tool' })
        + outcomeAction(selection, 'buy_nothing');
      track('sales_funnel_rendered', { ...selection, route: 'buy_nothing', segment: 'retention' });
      return;
    }

    const professional = setting === 'hotel_site'
      || duration === 'long'
      || priority === 'cold_chain'
      || priority === 'solar_backup'
      || priority === 'long_outage'
      || (setting === 'small_business' && ['internet', 'electronics'].includes(priority));

    if (professional) {
      resultText.textContent = 'Bu senaryoda tek ürün seçimi yerine kritik yük, süre, transfer, bakım ve güvenlik birlikte değerlendirilmelidir. Ücretli profesyonel ön değerlendirme rotası açıldı.';
      actions.innerHTML = action('/kurumsal-elektrik-surekliligi-on-degerlendirme', 'Ücretli kurumsal ön değerlendirmeyi incele', { kind: 'service', route: 'paid_b2b', commercial: 'paid-service' })
        + action(plan.calculate[0], plan.calculate[1], { kind: 'secondary', route: 'free_tool' })
        + outcomeAction(selection, 'paid_b2b');
      track('sales_funnel_rendered', { ...selection, route: 'paid_b2b', segment: 'professional' });
      return;
    }

    if (existing === 'unknown' || verified === 'no') {
      resultText.textContent = existing === 'unknown'
        ? 'Mevcut çözüm test edilmediği için yeni ürün sonucu açılmaz. Önce ücretsiz hesap ve çalışma süresi testiyle gerçek açığı doğrulayın.'
        : 'Teknik etiket bilgisi doğrulanmadığı için ticari sonuç açılmaz. Önce ücretsiz rehberle voltaj, watt, bağlantı veya protokol kanıtını tamamlayın.';
      actions.innerHTML = action(plan.calculate[0], plan.calculate[1], { route: 'free_tool_only' })
        + outcomeAction(selection, 'evidence_required');
      track('sales_funnel_rendered', { ...selection, route: 'evidence_required', segment: 'nurture' });
      return;
    }

    if (plan.affiliateEligible && plan.product) {
      resultText.textContent = 'Gerçek eksik ve teknik kanıt birlikte doğrulandı. Önce ücretsiz hesabı tamamlayın; sonuç yetersizse yalnız ilgili düşük riskli ürün sınıfını şeffaf ürün merkezinde karşılaştırın.';
      actions.innerHTML = action(plan.calculate[0], plan.calculate[1], { route: 'free_tool' })
        + action(plan.product[0], plan.product[1], { kind: 'affiliate', route: 'qualified_affiliate_product_center', commercial: 'affiliate' })
        + outcomeAction(selection, 'affiliate_product_center');
      disclosure.classList.remove('hidden');
      track('sales_funnel_rendered', { ...selection, route: 'qualified_affiliate_product_center', segment: 'qualified-consumer' });
      return;
    }

    resultText.textContent = 'Bu ihtiyaçta doğrudan ürün rotası açılmaz. Önce ücretsiz hesabı tamamlayın; tekrarlayan veya ölçüm gerektiren sonuçta profesyonel kapsamı değerlendirin.';
    actions.innerHTML = action(plan.calculate[0], plan.calculate[1], { route: 'free_tool' })
      + (plan.professional ? action('/kurumsal-elektrik-surekliligi-on-degerlendirme', 'Profesyonel kapsamı incele', { kind: 'service', route: 'paid_assessment', commercial: 'paid-service' }) : '')
      + outcomeAction(selection, 'guided_only');
    track('sales_funnel_rendered', { ...selection, route: 'guided_only', segment: 'guided' });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = byId('workshopForm');
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const selection = {
        hazard: safeValue('hazard'),
        setting: safeValue('setting'),
        priority: safeValue('priority'),
        duration: safeValue('duration'),
        existing: safeValue('existing'),
        verified: safeValue('verified')
      };
      renderPlan(selection);
      byId('result').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    });

    byId('resultActions').addEventListener('click', (event) => {
      const link = event.target.closest('a[data-route]');
      if (!link) return;
      track('sales_route_opened', {
        route: link.dataset.route,
        segment: link.dataset.commercialStage || 'none'
      });
    });
  });
})();
