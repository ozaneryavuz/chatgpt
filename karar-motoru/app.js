(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const rules = window.Alo186DecisionRules;
  const state = { danger: null, category: null, problem: null, scope: null };
  let screen = 'danger';
  let lastResult = null;

  const dangerOptions = [
    { value: 'shock', label: 'Elektrik çarpması / yaralanma', note: 'Bir kişi akıma maruz kaldı veya yaralandı' },
    { value: 'fire', label: 'Duman, yangın, patlama veya yoğun kıvılcım', note: 'Pano, sayaç, direk, trafo veya cihazdan geliyor' },
    { value: 'fallen', label: 'Yere düşmüş kablo / eğilmiş direk', note: 'Kabloya veya çevresindeki yüzeylere yaklaşılmamalı' },
    { value: 'water', label: 'Elektrik ekipmanı suyla temas ediyor', note: 'Su basması, ıslak pano, priz veya cihaz' },
    { value: 'none', label: 'Bunların hiçbiri yok', note: 'Acil tehlike görmüyorum' }
  ];

  const scopeOptions = [
    { value: 'area', label: 'Sokakta veya komşu binalarda da var', note: 'Dağıtım şebekesi kaynaklı olabilir' },
    { value: 'building', label: 'Bina / site ortak alanında veya birden fazla bölümde var', note: 'Bina ana dağıtımı veya şebeke bağlantısı olabilir' },
    { value: 'unit', label: 'Yalnız benim evimde / iş yerimde var', note: 'İç tesisat veya bağlı cihaz kaynaklı olabilir' },
    { value: 'unknown', label: 'Emin değilim', note: 'Kapsam güvenli biçimde doğrulanamıyor' }
  ];

  function emit(name, params = {}) {
    if (typeof window.Alo186Track === 'function') window.Alo186Track(name, params);
    else if (typeof window.gtag === 'function') window.gtag('event', name, params);
  }

  function renderQuestion() {
    const model = currentModel();
    const stepInfo = progressInfo();
    $('progressText').textContent = `Adım ${stepInfo.current} / ${stepInfo.total}`;
    $('progressBar').style.width = `${(stepInfo.current / stepInfo.total) * 100}%`;
    $('validation').textContent = '';
    $('questionArea').innerHTML = `
      <div class="question">
        ${screen !== 'danger' ? '<button type="button" class="back-button">← Geri</button>' : ''}
        <h2>${model.title}</h2>
        <p>${model.description}</p>
        <div class="option-grid ${screen === 'problem' ? 'problem-grid' : ''}">
          ${model.options.map((option) => `
            <button type="button" class="option-button" data-value="${option.value}">
              ${option.label}<small>${option.note || ''}</small>
            </button>`).join('')}
        </div>
      </div>`;

    $('questionArea').querySelectorAll('.option-button').forEach((button) => {
      button.addEventListener('click', () => choose(button.dataset.value));
    });
    const back = $('questionArea').querySelector('.back-button');
    if (back) back.addEventListener('click', goBack);
    const first = $('questionArea').querySelector('.option-button');
    if (first) first.focus({ preventScroll: true });
  }

  function currentModel() {
    if (screen === 'danger') return {
      title: 'Şu anda acil bir tehlike var mı?',
      description: 'Önce can güvenliğini ayırın. Emin değilseniz tehlike varmış gibi davranın.',
      options: dangerOptions
    };
    if (screen === 'category') return {
      title: 'Sorun hangi gruba daha yakın?',
      description: 'Bir sonraki adımda tam belirtiyi seçeceksiniz.',
      options: rules.categories.map(c => ({ value: c.id, label: c.label, note: c.note }))
    };
    if (screen === 'problem') return {
      title: 'Sorunu en iyi anlatan belirtiyi seçin',
      description: `${rules.listByCategory(state.category).length} seçenek içinden en yakın olanı seçin.`,
      options: rules.listByCategory(state.category).map(p => ({ value: p.id, label: p.label, note: p.note }))
    };
    return {
      title: 'Bu belirti ne kadar geniş bir alanı etkiliyor?',
      description: 'Panoyu açmadan ve ölçüm yapmadan yalnız güvenli gözleminizi seçin.',
      options: scopeOptions
    };
  }

  function progressInfo() {
    const total = 4;
    const map = { danger: 1, category: 2, problem: 3, scope: 4 };
    return { current: map[screen], total };
  }

  function choose(value) {
    emit('electrical_decision_answered', { screen, answer: value });
    if (screen === 'danger') {
      state.danger = value;
      if (value !== 'none') return showResult(emergencyResult(value));
      screen = 'category';
      return renderQuestion();
    }
    if (screen === 'category') {
      state.category = value;
      state.problem = null;
      state.scope = null;
      screen = 'problem';
      return renderQuestion();
    }
    if (screen === 'problem') {
      state.problem = value;
      const problem = rules.getProblem(value);
      if (!problem) return showValidation('Seçilen problem bulunamadı.');
      if (problem.inherentDanger) return showResult(rules.resolve(problem.id, 'unknown'));
      if (problem.requiresScope) {
        screen = 'scope';
        return renderQuestion();
      }
      return showResult(rules.resolve(problem.id, 'unknown'));
    }
    state.scope = value;
    showResult(rules.resolve(state.problem, value));
  }

  function goBack() {
    if (screen === 'category') {
      screen = 'danger'; state.category = null; state.problem = null; state.scope = null;
    } else if (screen === 'problem') {
      screen = 'category'; state.problem = null; state.scope = null;
    } else if (screen === 'scope') {
      screen = 'problem'; state.scope = null;
    }
    renderQuestion();
  }

  function showValidation(message) { $('validation').textContent = message; }

  function emergencyResult(type) {
    const base = rules.routeTemplates.emergency;
    const map = {
      shock: {
        title: 'Önce 112’yi arayın',
        summary: 'Elektrik çarpması veya yaralanma can güvenliği acilidir. Enerji kaynağına ve kişiye çıplak elle temas etmeyin.',
        steps: ['Tehlikeli alana yaklaşmayın.', 'Kişi hâlâ enerji kaynağına temas ediyorsa güvenli enerji kesilmeden dokunmayın.', '112 talimatlarını izleyin.'],
        prep: ['Yaralanan kişi sayısı', 'Olayın güvenli konumu', 'Enerji kaynağının türü']
      },
      fire: {
        title: 'Uzaklaşın ve 112’yi arayın',
        summary: 'Duman, yangın, patlama veya yoğun kıvılcım acil durumdur. Elektrik yangınında su kullanmayın.',
        steps: ['Bölgeyi boşaltın.', 'Panoya, sayaç veya cihaza müdahale etmeyin.', '112’yi; dış şebeke etkileniyorsa ayrıca 186’yı arayın.'],
        prep: ['Yangın/duman bölgesi', 'Yaralanma bilgisi', 'Direk, trafo, sayaç veya bina ayrımı']
      },
      fallen: {
        title: 'Yaklaşmayın: 112 ve 186',
        summary: 'Yere düşmüş iletken veya hasarlı direk çevresindeki zemin ve temas ettiği nesneler enerjili olabilir.',
        steps: ['En az birkaç metre uzaklaşın.', 'İnsanları ve hayvanları uzak tutun.', '112 ve 186’ya güvenli konumu bildirin.'],
        prep: ['İl/ilçe ve güvenli konum', 'Kablonun temas ettiği alan', 'Yaralanma veya yangın bilgisi']
      },
      water: {
        title: 'Islak bölgeye girmeyin ve 112’yi arayın',
        summary: 'Su ile temas eden elektrik ekipmanı ciddi çarpılma riski oluşturur.',
        steps: ['Islak zemine girmeyin.', 'Panoya, prize veya anahtara ulaşmaya çalışmayın.', 'Güvenli noktadan 112’yi arayın.'],
        prep: ['Su basan alan', 'Elektrik ekipmanının türü', 'İçeride kişi bulunup bulunmadığı']
      }
    };
    return { ...base, ...map[type], problemId: `danger-${type}` };
  }

  function outcomeCategory() {
    if (state.category === 'panel') return 'indoor_fault';
    if (['outage', 'external', 'meter'].includes(state.category)) return 'outage_official';
    return 'outage_official';
  }

  function outcomeAction(result) {
    if (result.level === 'danger') return 'official_channel';
    if (['official', 'admin'].includes(result.level)) return 'official_channel';
    if (['electrician', 'building', 'mixed'].includes(result.level)) return 'electrician';
    return 'free_tool';
  }

  function updateOutcomeLink(result) {
    const params = new URLSearchParams({
      kaynak: 'karar-motoru',
      kategori: outcomeCategory(),
      eylem: outcomeAction(result)
    });
    if (result.level === 'danger' || (state.danger && state.danger !== 'none')) {
      params.set('guvenlik', 'true');
      params.set('sonuc', 'safety');
    }
    $('outcomeBtn').href = `/hesaplama/cozum-sonucu/?${params.toString()}`;
  }

  function showResult(result) {
    lastResult = result;
    $('engine').classList.add('hidden');
    $('result').classList.remove('hidden');
    $('result').dataset.revenueAllowed = result.revenueAllowed ? 'true' : 'false';
    $('resultIcon').textContent = result.icon;
    $('resultEyebrow').textContent = result.eyebrow;
    $('resultTitle').textContent = result.title;
    $('resultSummary').textContent = result.summary;
    const visibleActions = result.revenueAllowed === false
      ? result.actions.filter((action) => !action.href.includes('/iletisim?konu=') && !action.label.toLocaleLowerCase('tr-TR').includes('teknik hizmet'))
      : result.actions;
    $('actionGrid').innerHTML = visibleActions.map((action) => `<a class="action-link ${action.kind || ''}" href="${action.href}">${action.label}</a>`).join('');
    $('actionGrid').querySelectorAll('a').forEach(a => a.addEventListener('click', () => emit('electrical_decision_action_clicked', { problem: result.problemId, route: result.level, action: a.textContent.trim(), revenue_allowed: result.revenueAllowed })));
    fillList('stepList', result.steps && result.steps.length ? result.steps : ['Tehlikeli bölüme müdahale etmeyin.', 'Önerilen kanalı kullanın.', 'Kayıt numarasını saklayın.']);
    fillList('prepList', result.prep && result.prep.length ? result.prep : ['İl ve ilçe', 'Sorunun başlama zamanı', 'Güvenli gözlem notu']);
    const warning = Boolean(result.warningText);
    $('warningCard').classList.toggle('hidden', !warning);
    if (warning) { $('warningTitle').textContent = result.warningTitle || 'Güvenlik uyarısı'; $('warningText').textContent = result.warningText; }
    updateOutcomeLink(result);
    $('result').scrollIntoView({ behavior: 'smooth', block: 'start' });
    emit('electrical_decision_completed', { route: result.level, problem: result.problemId, danger: state.danger, scope: state.scope || 'not_asked', revenue_allowed: result.revenueAllowed });
  }

  function fillList(id, values) {
    const list = $(id); list.innerHTML = '';
    values.forEach((value) => { const li = document.createElement('li'); li.textContent = value; list.appendChild(li); });
  }

  function restart() {
    state.danger = null; state.category = null; state.problem = null; state.scope = null;
    screen = 'danger'; lastResult = null;
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
    if (!rules || rules.problems.length !== 25) {
      showValidation('Karar kural kataloğu yüklenemedi. Şebeke arızası için 186, can güvenliği riski için 112’yi arayın.');
      return;
    }
    renderQuestion();
    $('restartBtn').addEventListener('click', restart);
    $('copyBtn').addEventListener('click', copyResult);
    $('outcomeBtn').addEventListener('click', () => emit('electrical_decision_outcome_handoff', { problem: lastResult ? lastResult.problemId : 'unknown', route: lastResult ? lastResult.level : 'unknown' }));
  });
})();
