(() => {
  'use strict';

  const core = window.Alo186SupplierReadiness;
  const labels = {
    category: {ups:'UPS ve enerji depolama',portable:'Power station ve taşınabilir enerji',ev:'EV şarj',solar:'GES ve inverter',safety:'Elektrik güvenliği ve koruma',measurement:'Ölçüm ve test cihazları'},
    type: {data:'Teknik veri doğrulama kartı',sponsored:'Açık sponsorlu teknik içerik',category:'Kategori destekçiliği',document:'Kılavuz / teknik doküman kalite kontrolü'},
    readiness: {complete:'Resmî teknik veri ve kılavuz hazır',partial:'Bazı teknik belgeler hazır',unknown:'Gerekli belge listesini öğrenmek istiyorum'},
    goal: {accuracy:'Teknik verinin doğru sunulması',education:'Kullanıcı eğitim içeriği',visibility:'Şeffaf sponsorlu görünürlük',launch:'Yeni ürün lansman desteği'}
  };
  const byId = (id) => document.getElementById(id);
  let currentBrief = '';
  let currentSelection = null;
  let documentationGapCount = 0;

  function safeChoice(group, id) {
    const value = String(byId(id).value || '');
    return Object.prototype.hasOwnProperty.call(labels[group], value) ? value : Object.keys(labels[group])[0];
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  }

  function track(name, data = {}) {
    const clean = {};
    for (const key of ['category','type','readiness','goal','readiness_band','source']) {
      if (typeof data[key] === 'string' && data[key].length < 60) clean[key] = data[key];
    }
    if (Number.isFinite(data.gap_count)) clean.gap_count = data.gap_count;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: name, ...clean });
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly','');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    area.remove();
  }

  function selectedDocuments() {
    return [...document.querySelectorAll('[data-document]:checked')].map((input) => input.value);
  }

  function safeParam(params, name, group, fallback) {
    const value = String(params.get(name) || '');
    return Object.prototype.hasOwnProperty.call(labels[group], value) ? value : fallback;
  }

  function applyDocumentationPrefill() {
    const params = new URLSearchParams(location.search);
    if (params.get('source') !== 'documentation_gap') return;
    const category = safeParam(params, 'category', 'category', 'portable');
    const type = safeParam(params, 'type', 'type', 'document');
    const readiness = safeParam(params, 'readiness', 'readiness', 'partial');
    const goal = safeParam(params, 'goal', 'goal', 'accuracy');
    const fields = String(params.get('fields') || '').split(',').map((item) => item.replace(/[^a-z0-9_]/gi, '')).filter(Boolean).slice(0, 8);
    documentationGapCount = fields.length;
    byId('category').value = category;
    byId('type').value = type;
    byId('readiness').value = readiness;
    byId('goal').value = goal;

    const notice = document.createElement('div');
    notice.className = 'policy';
    notice.setAttribute('role','status');
    notice.innerHTML = `<strong>Ürün merkezindeki teknik veri boşluğundan geldiniz.</strong> Ürün alanı ve doküman kalite kontrolü hedefi otomatik seçildi. ${documentationGapCount ? `${documentationGapCount} eksik teknik alan için soru paketi ürün merkezinde oluşturuldu.` : 'Teknik veri paketi eksik veya güncel değil.'} Bu bağlantı ürün, fiyat, ASIN, iletişim veya kişisel veri taşımaz.`;
    byId('partnerForm').insertAdjacentElement('beforebegin', notice);
    track('supplier_documentation_gap_prefilled', {source:'documentation_gap',category,type,readiness,goal,gap_count:documentationGapCount});
  }

  document.addEventListener('DOMContentLoaded', () => {
    byId('documentChecks').innerHTML = core.documents.map((item) => `<label class="document-check"><input type="checkbox" value="${escapeHtml(item.id)}" data-document><span><strong>${escapeHtml(item.label)}</strong><small>Hazır ve güncel resmî kaynak</small></span></label>`).join('');
    applyDocumentationPrefill();

    const form = byId('partnerForm');
    const link = byId('mailLink');
    const copyButton = byId('copyBriefBtn');
    const printButton = byId('printBriefBtn');

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const selection = {
        category: safeChoice('category','category'),
        type: safeChoice('type','type'),
        readiness: safeChoice('readiness','readiness'),
        goal: safeChoice('goal','goal'),
        documents: selectedDocuments()
      };
      const readable = {
        category: labels.category[selection.category],
        type: labels.type[selection.type],
        readiness: labels.readiness[selection.readiness],
        goal: labels.goal[selection.goal]
      };
      const assessment = core.assess(selection);
      currentSelection = {...selection,readiness_band:assessment.band,source:documentationGapCount?'documentation_gap':'direct',gap_count:documentationGapCount};
      currentBrief = core.brief(readable,assessment);
      if (documentationGapCount) currentBrief += `\n\nÜrün merkezinden aktarılan eksik teknik alan sayısı: ${documentationGapCount}. Alan adları ve ürün kimliği bu talebe taşınmadı; marka bağımsız soru paketi ayrıca paylaşılabilir.`;

      byId('resultTitle').textContent = `${readable.category} için teknik hazırlık özeti hazır.`;
      byId('resultText').textContent = 'Skor, kaynak paketinin değerlendirmeye ne kadar hazır olduğunu gösterir; yayın, ürün uygunluğu veya iş birliği kabulü değildir.';
      byId('readinessScoreBox').classList.remove('hidden');
      byId('readinessScore').textContent = `${assessment.score}/100`;
      byId('readinessLabel').textContent = assessment.label;
      byId('readinessScoreBox').dataset.band = assessment.band;
      byId('summary').innerHTML = [
        ['Ürün alanı',readable.category],['İş birliği türü',readable.type],['Kaynak hazırlığı',readable.readiness],['Hedef',readable.goal],['Hazır kaynak',`${assessment.selected.length}/${core.documents.length}`]
      ].map(([title,value]) => `<div><strong>${escapeHtml(title)}</strong>${escapeHtml(value)}</div>`).join('');
      byId('missingPanel').classList.remove('hidden');
      byId('missingList').innerHTML = assessment.missing.length ? assessment.missing.map((item) => `<li>${escapeHtml(item.label)}</li>`).join('') : '<li>Eksik zorunlu kaynak görünmüyor; kapsam yine editoryal incelemeden geçer.</li>';
      byId('nextStep').textContent = assessment.next;

      const subject = `ALO186 tedarikçi/üretici iş birliği — ${readable.category}`;
      const body = [
        'Merhaba,',
        '',
        currentBrief,
        '',
        'Sponsorlu ilişkinin açıkça etiketlenmesini, organik teknik sıralamanın ödeme ile değiştirilmemesini ve bütün teknik iddiaların resmî kaynaklarla doğrulanmasını kabul ediyorum.',
        '',
        'Kapsam, ücret, teslim, etiketleme ve gerekli belge listesinin yazılı olarak iletilmesini rica ederim.'
      ].join('\n');
      link.href = `mailto:bilgi@alo186.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      link.classList.remove('disabled');
      link.setAttribute('aria-disabled','false');
      link.tabIndex = 0;
      copyButton.disabled = false;
      printButton.disabled = false;
      byId('actionStatus').textContent = `${assessment.label}. ${assessment.next}`;
      track('supplier_data_readiness_scored', currentSelection);
      track('supplier_partnership_request_prepared', currentSelection);
    });

    link.addEventListener('click', (event) => {
      if (link.getAttribute('aria-disabled') === 'true') { event.preventDefault(); return; }
      track('supplier_partnership_email_opened', currentSelection || {});
    });

    copyButton.addEventListener('click', async () => {
      if (!currentBrief) return;
      try {
        await copyText(currentBrief);
        byId('actionStatus').textContent = 'Teknik hazırlık özeti panoya kopyalandı. Kişisel veri eklenmedi.';
        track('supplier_partnership_brief_copied', currentSelection || {});
      } catch (error) {
        byId('actionStatus').textContent = 'Kopyalama başarısız oldu; yazdır/PDF seçeneğini kullanın.';
      }
    });

    printButton.addEventListener('click', () => {
      if (!currentBrief) return;
      track('supplier_partnership_brief_printed', currentSelection || {});
      window.print();
    });
  });
})();
