(() => {
  'use strict';

  const core = window.Alo186CorporateReadiness;
  const labels = {
    facility: {hotel:'Otel / tatil tesisi',site:'Site / apartman / villa projesi',restaurant:'Restoran / mağaza / soğuk zincir',office:'Ofis / küçük işletme',industrial:'Atölye / üretim tesisi'},
    problem: {outage:'Tekrarlayan elektrik kesintisi',voltage:'Düşük/yüksek gerilim ve cihaz riski',backup:'UPS/jeneratör kapasitesi belirsiz',energy:'GES, batarya veya enerji maliyeti',ev:'EV şarj ve güç kapasitesi',audit:'Genel elektrik sürekliliği ve risk incelemesi'},
    backup: {none:'Yok / bilinmiyor',ups:'UPS',generator:'Jeneratör',both:'UPS + jeneratör',solar_storage:'GES / batarya / hibrit sistem'},
    scope: {remote:'Uzaktan doküman ön incelemesi',comparison:'Yedek güç ve maliyet karşılaştırması',site:'Yerinde keşif ve teknik rapor',roadmap:'90 günlük süreklilik yol haritası'},
    urgency: {urgent:'0–30 gün içinde karar gerekli',soon:'30–90 gün içinde değerlendirme',planning:'Yıllık plan / bütçe hazırlığı'},
    evidence: {none:'Belge ve yük listesi henüz yok',partial:'Bazı fatura, etiket veya kayıtlar var',ready:'Tek hat, yük listesi ve kayıtlar hazır'}
  };
  const sourceProfiles = {
    generator:{label:'Jeneratör',problem:'backup',backup:'generator',scope:'comparison'},
    inverter:{label:'İnverter ve batarya sistemi',problem:'backup',backup:'solar_storage',scope:'comparison'},
    outlet_tester:{label:'Priz / RCD ve tesisat ölçümü',problem:'audit',backup:'none',scope:'site'},
    ups_battery:{label:'UPS aküsü ve kartuşu',problem:'backup',backup:'ups',scope:'remote'}
  };
  const serviceProfiles = {
    hotel_audit:{label:'Otel Elektrik Sürekliliği ve Risk Denetimi',facility:'hotel',problem:'audit',backup:'both',scope:'site',urgency:'soon',evidence:'partial'},
    proposal_review:{label:'Bağımsız Elektrik Teklif ve Teknik Şartname İncelemesi',facility:'office',problem:'audit',backup:'none',scope:'remote',urgency:'urgent',evidence:'partial'},
    energy_integration:{label:'GES, Batarya ve EV Şarj Entegrasyon Fizibilitesi',facility:'hotel',problem:'energy',backup:'solar_storage',scope:'comparison',urgency:'planning',evidence:'partial'},
    continuity_monitoring:{label:'Elektrik Sürekliliği İzleme ve Teknik Takip',facility:'hotel',problem:'audit',backup:'both',scope:'roadmap',urgency:'planning',evidence:'partial'}
  };

  const byId = (id) => document.getElementById(id);
  let currentBrief = '';
  let currentSelection = null;
  let sourceCategory = '';
  let sourceService = '';

  function safeChoice(group, id) {
    const value = String(byId(id).value || '');
    return Object.prototype.hasOwnProperty.call(labels[group], value) ? value : Object.keys(labels[group])[0];
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  }

  function track(name, data = {}) {
    const allowed = {};
    for (const key of ['facility','problem','backup','scope','urgency','evidence','readiness_band','source_category','source_service']) {
      if (typeof data[key] === 'string' && data[key].length < 80) allowed[key] = data[key];
    }
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...allowed });
  }

  function prefillFromProductCenter() {
    const params = new URLSearchParams(location.search);
    if (params.get('source') !== 'product_center') return;
    const category = String(params.get('category') || '');
    const profile = sourceProfiles[category];
    if (!profile) return;
    sourceCategory = category;
    byId('problem').value = profile.problem;
    byId('backup').value = profile.backup;
    byId('scope').value = profile.scope;
    byId('resultTitle').textContent = `${profile.label} seçiminiz için teknik kapsamı hazırlayın.`;
    byId('resultText').textContent = 'Ürün merkezinden gelen yüksek riskli seçim, doğrudan satın alma yerine belge hazırlık skoru ve yazılı kapsam teyidine yönlendirildi.';
    byId('actionStatus').textContent = 'Bu ön doldurma ürün önerisi değildir. Tesis türü, karar zamanı ve belge hazırlığını seçerek ücretsiz kapsam özetini oluşturun.';
    track('paid_assessment_source_prefilled',{problem:profile.problem,backup:profile.backup,scope:profile.scope,source_category:category});
  }

  function prefillFromServicePage() {
    const params = new URLSearchParams(location.search);
    if (params.get('source') !== 'service_page') return;
    const service = String(params.get('service') || '');
    const profile = serviceProfiles[service];
    if (!profile) return;
    sourceService = service;
    for (const key of ['facility','problem','backup','scope','urgency','evidence']) {
      if (Object.prototype.hasOwnProperty.call(labels[key], profile[key])) byId(key).value = profile[key];
    }
    byId('resultTitle').textContent = `${profile.label} için kapsam hazırlığına devam edin.`;
    byId('resultText').textContent = 'Uzmanlaşmış ticari sayfadan gelen seçimler kişisel veri olmadan ön dolduruldu. Karar zamanı, belge durumu ve istenen kapsamı değiştirerek talebi daraltabilirsiniz.';
    byId('actionStatus').textContent = 'Bu ön doldurma sözleşme veya ücret onayı değildir. Ücretsiz kapsam özetini oluşturduktan sonra iletişime geçip geçmemeye siz karar verirsiniz.';
    track('paid_assessment_service_prefilled',{facility:profile.facility,problem:profile.problem,backup:profile.backup,scope:profile.scope,urgency:profile.urgency,evidence:profile.evidence,source_service:service});
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    area.remove();
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = byId('serviceForm');
    const link = byId('mailLink');
    const copyButton = byId('copyBriefBtn');
    const printButton = byId('printBriefBtn');
    prefillFromServicePage();
    prefillFromProductCenter();

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const selection = {
        facility: safeChoice('facility','facility'),
        problem: safeChoice('problem','problem'),
        backup: safeChoice('backup','backup'),
        scope: safeChoice('scope','scope'),
        urgency: safeChoice('urgency','urgency'),
        evidence: safeChoice('evidence','evidence')
      };
      const readable = Object.fromEntries(Object.keys(selection).map((key) => [key, labels[key][selection[key]]]));
      const assessment = core.assess(selection);
      currentSelection = { ...selection, readiness_band: assessment.band, source_category: sourceCategory, source_service: sourceService };
      currentBrief = core.brief(readable, assessment);

      byId('resultTitle').textContent = `${readable.facility} için nitelikli ön değerlendirme özeti hazır.`;
      byId('resultText').textContent = 'Skor bir teklif veya uygunluk onayı değildir; ilk görüşmede hangi belgelerin hazırlanması gerektiğini gösterir.';
      byId('readiness').classList.remove('hidden');
      byId('readinessScore').textContent = `${assessment.score}/100`;
      byId('readinessLabel').textContent = assessment.label;
      byId('readiness').dataset.band = assessment.band;
      byId('summary').innerHTML = [
        ['Tesis türü',readable.facility],['Ana problem',readable.problem],['Mevcut yedek kaynak',readable.backup],['İstenen kapsam',readable.scope],['Karar zamanı',readable.urgency],['Belge hazırlığı',readable.evidence]
      ].map(([title,value]) => `<div><strong>${escapeHtml(title)}</strong>${escapeHtml(value)}</div>`).join('');
      byId('documentPanel').classList.remove('hidden');
      byId('documentList').innerHTML = assessment.docs.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
      byId('nextStep').textContent = assessment.next;

      const sourceNotes = [];
      if (sourceCategory && sourceProfiles[sourceCategory]) sourceNotes.push(`Ürün merkezi başlangıç kategorisi: ${sourceProfiles[sourceCategory].label}`);
      if (sourceService && serviceProfiles[sourceService]) sourceNotes.push(`Uzmanlaşmış hizmet başlangıcı: ${serviceProfiles[sourceService].label}`);
      const sourceNote = sourceNotes.length ? `\n${sourceNotes.join('\n')}\n` : '';
      const subjectLabel = sourceService && serviceProfiles[sourceService] ? serviceProfiles[sourceService].label : readable.facility;
      const subject = `ALO186 ücretli teknik ön değerlendirme talebi — ${subjectLabel}`;
      const body = ['Merhaba,','',currentBrief,sourceNote,'Çalışmaya başlamadan önce kapsam, ücret, teslim biçimi ve gerekiyorsa saha koşullarının yazılı olarak teyit edilmesini rica ederim.'].join('\n');
      link.href = `mailto:bilgi@alo186.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      link.classList.remove('disabled');
      link.setAttribute('aria-disabled','false');
      link.tabIndex = 0;
      copyButton.disabled = false;
      printButton.disabled = false;
      byId('actionStatus').textContent = `${assessment.label}. ${assessment.next}`;
      track('paid_assessment_readiness_scored', currentSelection);
      track('paid_assessment_request_prepared', currentSelection);
    });

    link.addEventListener('click', (event) => {
      if (link.getAttribute('aria-disabled') === 'true') { event.preventDefault(); return; }
      track('paid_assessment_email_opened', currentSelection || {});
    });

    copyButton.addEventListener('click', async () => {
      if (!currentBrief) return;
      try {
        await copyText(currentBrief);
        byId('actionStatus').textContent = 'Kapsam özeti panoya kopyalandı. Kişisel veri eklenmedi.';
        track('paid_assessment_brief_copied', currentSelection || {});
      } catch (error) {
        byId('actionStatus').textContent = 'Kopyalama başarısız oldu; yazdır/PDF seçeneğini kullanın.';
      }
    });

    printButton.addEventListener('click', () => {
      if (!currentBrief) return;
      track('paid_assessment_brief_printed', currentSelection || {});
      window.print();
    });
  });
})();
