(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const state = { danger: null, scope: null, symptom: null };
  let currentStep = 0;
  let lastResult = null;

  const questions = [
    {
      key: 'danger',
      title: 'Şu anda acil bir tehlike var mı?',
      description: 'Önce can güvenliğini ayırın. Emin değilseniz tehlike varmış gibi davranın.',
      options: [
        { value: 'shock', label: 'Elektrik çarpması / yaralanma', note: 'Bir kişi akıma maruz kaldı veya yaralandı' },
        { value: 'fire', label: 'Duman, yangın, patlama veya yoğun kıvılcım', note: 'Pano, sayaç, direk, trafo veya cihazdan geliyor' },
        { value: 'fallen', label: 'Yere düşmüş kablo / eğilmiş direk', note: 'Kabloya veya çevresindeki yüzeylere yaklaşılmamalı' },
        { value: 'water', label: 'Elektrik ekipmanı suyla temas ediyor', note: 'Su basması, ıslak pano, priz veya cihaz' },
        { value: 'none', label: 'Bunların hiçbiri yok', note: 'Acil tehlike görmüyorum' }
      ]
    },
    {
      key: 'scope',
      title: 'Sorun ne kadar geniş bir alanı etkiliyor?',
      description: 'Panoyu açmadan ve ölçüm yapmadan yalnız güvenli gözleminizi seçin.',
      options: [
        { value: 'area', label: 'Sokakta veya komşularda da var', note: 'Bölgesel şebeke sorunu olabilir' },
        { value: 'building', label: 'Bina / site ortak alanında var', note: 'Birden fazla bağımsız bölüm veya ortak sistem etkileniyor' },
        { value: 'unit', label: 'Yalnız benim evimde / iş yerimde var', note: 'İç tesisat veya bina dağıtımı olabilir' },
        { value: 'unknown', label: 'Emin değilim', note: 'Çevreyi güvenli biçimde kontrol edemiyorum' }
      ]
    },
    {
      key: 'symptom',
      title: 'Sorunu en iyi hangi ifade anlatıyor?',
      description: 'En yakın seçeneği seçin; sonuç ekranında güvenli sonraki adımlar gösterilecektir.',
      options: [
        { value: 'outage', label: 'Elektrik tamamen yok', note: 'Tüm cihazlar ve aydınlatma çalışmıyor' },
        { value: 'partial', label: 'Bazı odalar, prizler veya fazlar çalışmıyor', note: 'Kısmi enerji veya faz eksikliği şüphesi' },
        { value: 'voltage', label: 'Lambalar çok parlak, sönük veya elektrik gelip gidiyor', note: 'Gerilim / nötr / bağlantı sorunu olabilir' },
        { value: 'breaker', label: 'Sigorta veya kaçak akım rölesi atıyor', note: 'Tekrar tekrar kaldırmak güvenli değildir' },
        { value: 'meter', label: 'Sayaç ekranı kapalı, yanık veya hasarlı', note: 'Sayaç ve bağlantı bölgesine dokunmayın' },
        { value: 'streetlight', label: 'Sokak lambası veya dış aydınlatma arızalı', note: 'Aydınlatma ihbarı gerekebilir' }
      ]
    }
  ];

  function emit(name, params = {}) {
    if (typeof window.gtag === 'function') window.gtag('event', name, params);
  }

  function renderQuestion() {
    const question = questions[currentStep];
    $('progressText').textContent = `Adım ${currentStep + 1} / ${questions.length}`;
    $('progressBar').style.width = `${((currentStep + 1) / questions.length) * 100}%`;
    $('validation').textContent = '';
    $('questionArea').innerHTML = `
      <div class="question">
        <h2>${question.title}</h2>
        <p>${question.description}</p>
        <div class="option-grid">
          ${question.options.map((option) => `
            <button type="button" class="option-button" data-value="${option.value}">
              ${option.label}<small>${option.note}</small>
            </button>`).join('')}
        </div>
      </div>`;

    $('questionArea').querySelectorAll('.option-button').forEach((button) => {
      button.addEventListener('click', () => choose(question.key, button.dataset.value));
    });
  }

  function choose(key, value) {
    state[key] = value;
    emit('electrical_decision_answered', { step: key, answer: value });

    if (key === 'danger' && value !== 'none') {
      showResult(emergencyResult(value));
      return;
    }

    if (currentStep < questions.length - 1) {
      currentStep += 1;
      renderQuestion();
      return;
    }

    showResult(routeResult(state));
  }

  function emergencyResult(type) {
    const map = {
      shock: {
        title: 'Önce 112’yi arayın',
        summary: 'Elektrik çarpması veya yaralanma can güvenliği acilidir. Enerji kaynağına ve kişiye çıplak elle temas etmeyin.',
        warning: 'Kişi hâlâ enerji kaynağına temas ediyorsa güvenli biçimde enerji kesilmeden dokunmayın. Ortamı boşaltın ve 112 talimatlarını izleyin.'
      },
      fire: {
        title: 'Uzaklaşın ve 112’yi arayın',
        summary: 'Duman, yangın, patlama veya yoğun kıvılcım acil durumdur. Pano, sayaç, direk veya trafoda müdahale etmeyin.',
        warning: 'Elektrik yangınında su kullanmayın. Bölgeyi boşaltın; güvenli mesafeden 112 ve dış şebeke şüphesinde 186 ile iletişime geçin.'
      },
      fallen: {
        title: 'Yaklaşmayın: 112 ve 186',
        summary: 'Yere düşmüş iletken veya hasarlı direk çevresindeki zemin de enerjili olabilir.',
        warning: 'En az birkaç metre uzaklaşın, kabloya ve temas ettiği hiçbir nesneye dokunmayın. İnsanları ve hayvanları bölgeden uzak tutun.'
      },
      water: {
        title: 'Islak bölgeye girmeyin ve 112’yi arayın',
        summary: 'Su ile temas eden elektrik ekipmanı ciddi çarpılma riski oluşturur.',
        warning: 'Islak zeminde anahtara, panoya veya prize ulaşmaya çalışmayın. Güvenli noktadan 112’yi arayın; dış şebeke etkileniyorsa 186’ya da bildirin.'
      }
    };
    const item = map[type];
    return {
      level: 'danger', icon: '!', eyebrow: 'Acil güvenlik durumu', title: item.title, summary: item.summary,
      warningTitle: 'Hayati güvenlik uyarısı', warningText: item.warning,
      actions: [
        { label: '112’yi ara', href: 'tel:112', kind: 'danger' },
        { label: '186’yı ara', href: 'tel:186', kind: 'secondary' },
        { label: 'Acil numaraları gör', href: 'https://alo186.com/ulusal-acil-numaralar', kind: 'secondary' }
      ],
      steps: ['Tehlikeli alana yaklaşmayın.', 'İnsanları ve hayvanları uzaklaştırın.', '112’ye olayın türünü ve güvenli konum bilgisini verin.', 'Şebeke, direk, sayaç veya dış hat etkileniyorsa 186’ya da bildirin.'],
      prep: ['Güvenli mesafeden görülen olay türü', 'İl, ilçe ve mümkünse cadde / sokak bilgisi', 'Yaralanan kişi veya yangın bilgisi', 'Direk, trafo, kablo veya bina bölgesi']
    };
  }

  function routeResult(s) {
    if (s.symptom === 'streetlight') return officialResult('Aydınlatma arızasını resmî kanala bildirin', 'Sokak ve genel aydınlatma arızaları dağıtım şirketi / TEDAŞ bildirim kanallarına iletilmelidir.', 'lighting');
    if (s.symptom === 'meter') return officialResult('Sayaç ve bağlantı bölgesine dokunmayın', 'Sayaç ekranı, mühür, yanık veya bağlantı sorunu için 186 ve yetkili dağıtım şirketinin resmî kanalını kullanın.', 'meter');

    if (s.scope === 'area') {
      if (s.symptom === 'voltage') return officialResult('Gerilim sorununu 186’ya bildirin', 'Komşularda da parlaklık değişimi, düşük / yüksek gerilim veya gelip gitme varsa şebeke kaynaklı olabilir.', 'voltage');
      return officialResult('Planlı kesintiyi kontrol edin, ardından 186’yı arayın', 'Sokak veya komşular da etkileniyorsa sorun dağıtım şebekesinde olabilir.', 'outage');
    }

    if (s.scope === 'building') {
      if (s.symptom === 'voltage') return mixedResult('Bina yönetimi ve 186 ile birlikte kontrol edin', 'Birden fazla bağımsız bölümde gerilim sorunu varsa bina ana dağıtımı veya şebeke bağlantısı etkilenmiş olabilir.');
      return electricianResult('Önce bina yönetimi veya teknik servise başvurun', 'Ortak alan ve birden fazla bağımsız bölüm etkileniyorsa bina ana panosu, kolon hattı veya ortak sistem kontrolü gerekebilir.', true);
    }

    if (s.scope === 'unit') {
      if (s.symptom === 'breaker') return electricianResult('Kaçak akım veya sigortayı tekrar tekrar kaldırmayın', 'Yalnız sizin bölümünüz etkileniyorsa iç tesisat, cihaz veya koruma elemanı sorunu olabilir.');
      if (s.symptom === 'voltage') return mixedResult('Cihazları kapatın; elektrikçi ve gerekirse 186', 'Yalnız sizin bölümünüzde gerilim belirtisi varsa iç bağlantı veya nötr sorunu olabilir; komşuları güvenli biçimde kontrol edin.');
      return electricianResult('Yetkili elektrikçi kontrolü önerilir', 'Komşularda enerji varken yalnız sizin eviniz veya iş yeriniz etkileniyorsa iç tesisat / bina dağıtım sorunu olasılığı yüksektir.');
    }

    return mixedResult('Önce çevreyi güvenli biçimde karşılaştırın', 'Sorunun kapsamı bilinmiyorsa planlı kesinti ekranını kontrol edin; komşu ve ortak alan durumuna göre 186 veya yetkili elektrikçiye ilerleyin.');
  }

  function officialResult(title, summary, type) {
    const extra = type === 'lighting' ? 'Aydınlatma direği numarası veya yakın konum bilgisini hazırlayın.' : 'Varsa önceki arıza kayıt numarasını hazırlayın.';
    return {
      level: 'official', icon: '186', eyebrow: 'Dağıtım şirketi / resmî kanal', title, summary,
      actions: [
        { label: '186’yı ara', href: 'tel:186', kind: '' },
        { label: 'EDAŞ’ı bul', href: 'https://alo186.com/edas', kind: 'secondary' },
        { label: 'Kesintiyi sorgula', href: 'https://alo186.com/elektrik-kesintisi', kind: 'secondary' }
      ],
      steps: ['Yetkili dağıtım şirketinin resmî planlı kesinti ekranını kontrol edin.', 'Kayıt yoksa 186 veya resmî online bildirim kanalını kullanın.', 'Verilen kayıt numarasını ve başvuru zamanını saklayın.', 'Tehlike oluşursa normal takip yerine 112’yi arayın.'],
      prep: ['İl ve ilçe', 'Sorunun başlama zamanı', 'Komşu / sokak durumuna ilişkin güvenli gözlem', extra]
    };
  }

  function electricianResult(title, summary, building = false) {
    return {
      level: 'electrician', icon: '⚙', eyebrow: building ? 'Bina yönetimi / teknik servis' : 'İç tesisat / yetkili elektrikçi', title, summary,
      actions: [
        { label: building ? 'Teknik hizmet talebi' : 'Elektrik arızası talebi', href: 'https://alo186.com/iletisim?konu=elektrik-arizasi', kind: '' },
        { label: 'Güvenlik rehberini aç', href: 'https://alo186.com/sektor-rehberi/elektrik-guvenligi', kind: 'secondary' },
        { label: '186’yı ara', href: 'tel:186', kind: 'secondary' }
      ],
      steps: ['Panoyu açmadan görülebilen şalter konumunu ve arıza belirtisini not edin.', 'Yanık kokusu, ısınma veya ses varsa enerji vermeye çalışmayın.', building ? 'Bina yönetimine ve yetkili teknik servise bildirin.' : 'Yetkili elektrikçiden iç tesisat ve bağlı cihaz kontrolü isteyin.', 'Komşularda da aynı belirti varsa ayrıca 186’ya bildirin.'],
      prep: ['Sorunun başladığı zaman', 'Etkilenen oda, priz veya cihazlar', 'Şalter / kaçak akım rölesinin durumu', 'Yanık kokusu, ses, ısınma veya su bilgisi']
    };
  }

  function mixedResult(title, summary) {
    return {
      level: 'mixed', icon: '?', eyebrow: 'Kapsamı doğrulayın', title, summary,
      actions: [
        { label: 'Kesintiyi sorgula', href: 'https://alo186.com/elektrik-kesintisi', kind: '' },
        { label: '186’yı ara', href: 'tel:186', kind: 'secondary' },
        { label: 'Teknik hizmet talebi', href: 'https://alo186.com/iletisim?konu=elektrik-arizasi', kind: 'secondary' }
      ],
      steps: ['Komşu, koridor veya ortak alan durumunu yalnız güvenli biçimde karşılaştırın.', 'Dağıtım şirketinin planlı kesinti ekranını kontrol edin.', 'Birden fazla yapı etkileniyorsa 186’ya bildirin.', 'Yalnız iç tesisat etkileniyorsa bina yönetimi veya yetkili elektrikçiye başvurun.'],
      prep: ['İl ve ilçe', 'Sorunun başlama zamanı', 'Etkilenen alanların kapsamı', 'Gözlenen belirti ve varsa fotoğraf']
    };
  }

  function showResult(result) {
    lastResult = result;
    $('engine').classList.add('hidden');
    $('result').classList.remove('hidden');
    $('resultIcon').textContent = result.icon;
    $('resultEyebrow').textContent = result.eyebrow;
    $('resultTitle').textContent = result.title;
    $('resultSummary').textContent = result.summary;
    $('actionGrid').innerHTML = result.actions.map((action) => `<a class="action-link ${action.kind}" href="${action.href}">${action.label}</a>`).join('');
    fillList('stepList', result.steps);
    fillList('prepList', result.prep);
    const warning = Boolean(result.warningText);
    $('warningCard').classList.toggle('hidden', !warning);
    if (warning) { $('warningTitle').textContent = result.warningTitle; $('warningText').textContent = result.warningText; }
    $('result').scrollIntoView({ behavior: 'smooth', block: 'start' });
    emit('electrical_decision_completed', { route: result.level, danger: state.danger, scope: state.scope || 'not_asked', symptom: state.symptom || 'not_asked' });
  }

  function fillList(id, values) {
    const list = $(id); list.innerHTML = '';
    values.forEach((value) => { const li = document.createElement('li'); li.textContent = value; list.appendChild(li); });
  }

  function restart() {
    state.danger = null; state.scope = null; state.symptom = null; currentStep = 0; lastResult = null;
    $('result').classList.add('hidden'); $('engine').classList.remove('hidden'); renderQuestion();
    $('engine').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  async function copyResult() {
    if (!lastResult) return;
    const text = ['ALO186 Elektrik Sorunu Ön Yönlendirmesi', lastResult.title, lastResult.summary, '', 'Şimdi ne yapın?', ...lastResult.steps.map((s, i) => `${i + 1}. ${s}`), '', 'Bu sonuç kesin teşhis veya resmî başvuru değildir.'].join('\n');
    try { await navigator.clipboard.writeText(text); $('copyBtn').textContent = 'Kopyalandı'; setTimeout(() => $('copyBtn').textContent = 'Sonucu kopyala', 1600); }
    catch (_) { window.prompt('Sonucu kopyalayın:', text); }
  }

  document.addEventListener('DOMContentLoaded', () => {
    renderQuestion();
    $('restartBtn').addEventListener('click', restart);
    $('copyBtn').addEventListener('click', copyResult);
  });
})();
