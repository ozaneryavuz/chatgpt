(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ALO186Parafudr = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const WEIGHTS = Object.freeze({
    lps: { yes: 35, no: 0, unknown: 12 },
    supply: { overhead: 22, mixed: 14, underground: 3, unknown: 10 },
    events: { frequent: 18, occasional: 10, rare: 2, unknown: 7 },
    sensitive: { many: 14, some: 8, none: 1 },
    existing: { none: 18, unknown: 12, type3: 12, type2: 4, type12: 0 },
    distance: { over10: 8, under10: 1, unknown: 4 },
    earthing: { verified: 0, old: 6, unknown: 7 },
    damage: { yes: 15, no: 0, unknown: 3 }
  });

  const MAX_SCORE = Object.values(WEIGHTS).reduce((total, group) => {
    return total + Math.max.apply(null, Object.values(group));
  }, 0);

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function normalizeAnswers(raw) {
    const source = raw || {};
    const valid = (group, fallback) => {
      const value = source[group];
      return Object.prototype.hasOwnProperty.call(WEIGHTS[group], value) ? value : fallback;
    };
    return {
      lps: valid('lps', 'unknown'),
      supply: valid('supply', 'unknown'),
      events: valid('events', 'unknown'),
      sensitive: valid('sensitive', 'some'),
      existing: valid('existing', 'unknown'),
      distance: valid('distance', 'unknown'),
      earthing: valid('earthing', 'unknown'),
      damage: valid('damage', 'unknown')
    };
  }

  function calculateScore(raw) {
    const answers = normalizeAnswers(raw);
    const rawScore = Object.keys(answers).reduce((total, key) => total + WEIGHTS[key][answers[key]], 0);
    const score = Math.round((rawScore / MAX_SCORE) * 100);
    return { answers, rawScore, score: clamp(score, 0, 100) };
  }

  function classify(score) {
    if (score >= 66) return { key: 'critical', label: 'Yüksek öncelik', css: 'bad' };
    if (score >= 36) return { key: 'elevated', label: 'Orta–yüksek öncelik', css: 'warn' };
    return { key: 'review', label: 'Temel kontrol önerilir', css: 'ok' };
  }

  function dedupe(items) {
    return Array.from(new Set(items));
  }

  function buildRecommendation(raw) {
    const result = calculateScore(raw);
    const a = result.answers;
    const level = classify(result.score);
    const layers = [];
    const reasons = [];
    const checks = [];
    const warnings = [];
    const productCategories = [];

    const type1Need = a.lps === 'yes' || a.supply === 'overhead' || (a.events === 'frequent' && a.damage === 'yes');
    const type2Need = a.existing === 'none' || a.existing === 'unknown' || a.existing === 'type3' || a.events !== 'rare' || a.sensitive !== 'none';
    const type3Need = a.sensitive === 'many' || a.distance === 'over10' || a.damage === 'yes';

    if (type1Need) {
      layers.push('Ana girişte Tip 1 veya Tip 1+2 SPD uygunluğu profesyonel olarak değerlendirilmeli.');
      productCategories.push('Tip 1+2 parafudr');
    }
    if (type2Need) {
      layers.push('Ana veya tali dağıtım panosunda Tip 2 SPD ve üreticiye uygun yedek koruma/koordinasyon kontrol edilmeli.');
      productCategories.push('Tip 2 parafudr');
    }
    if (type3Need) {
      layers.push('Hassas cihazlara yakın noktada, üst kademe korumayı tamamlayan Tip 3 koruma değerlendirilebilir.');
      productCategories.push('Tip 3 cihaz koruyucu');
    }

    if (a.lps === 'yes') reasons.push('Binada dış yıldırımlık/paratoner sistemi bulunması, yıldırım akımının girişte yönetilmesini önemli hâle getirir.');
    if (a.supply === 'overhead') reasons.push('Havai besleme hattı, atmosferik geçici aşırı gerilimlere maruziyeti artırabilir.');
    if (a.events === 'frequent') reasons.push('Sık yıldırım veya gerilim olayı bildirimi risk puanını yükseltti.');
    if (a.damage === 'yes') reasons.push('Daha önce cihaz hasarı yaşanması, mevcut koruma düzeninin incelenmesini önceliklendirir.');
    if (a.sensitive === 'many') reasons.push('Çok sayıda hassas veya yüksek değerli elektronik cihaz bulunuyor.');
    if (a.existing === 'none') reasons.push('Panoda bilinen bir SPD bulunmuyor.');
    if (a.existing === 'unknown') reasons.push('Mevcut koruma tipi bilinmediği için pano etiketi ve ürün bilgisi doğrulanmalı.');
    if (a.distance === 'over10') reasons.push('Ana pano ile hassas yük arasındaki mesafe, ek koordineli koruma ihtiyacını artırabilir.');

    checks.push('Şebeke sistemi (TT/TN/IT), faz sayısı, Uc/Up değerleri ve kutup düzeni cihaz etiketinden/projeden doğrulanmalı.');
    checks.push('SPD bağlantı iletkenleri mümkün olduğunca kısa tutulmalı; montaj ve yedek koruma üretici talimatına göre yapılmalı.');
    checks.push('SPD durum göstergesi ve değiştirilebilir kartuşlar periyodik olarak kontrol edilmeli.');
    checks.push('Enerji, data/telefon, koaksiyel ve dışarıdan gelen metal hatlar birlikte değerlendirilmeden tam koruma varsayılmamalı.');

    if (a.earthing !== 'verified') {
      checks.push('Topraklama ve eşpotansiyel bağlantılar yetkili uzman tarafından ölçülüp doğrulanmalı.');
      warnings.push('Topraklama durumu bilinmiyor veya ölçüm eski; yalnız parafudr satın almak tesisat uygunluğunu garanti etmez.');
    }
    if (a.existing === 'type12' && level.key === 'review') {
      layers.push('Mevcut Tip 1+2 korumanın gösterge durumu, koordinasyonu ve bakım kaydı doğrulanmalı; gereksiz ikinci ürün eklenmemeli.');
    }
    if (a.existing === 'type2' && type1Need) {
      warnings.push('Mevcut Tip 2 cihaz, doğrudan yıldırım akımı riski bulunan senaryoda tek başına yeterli kabul edilmemelidir.');
    }
    if (a.existing === 'type3') {
      warnings.push('Priz tipi/Tip 3 koruma, üst kademe Tip 1 veya Tip 2 korumanın yerine geçmez.');
    }

    warnings.push('Bu sonuç keşif veya proje değildir; pano içinde çalışma yalnız yetkili elektrikçi tarafından, enerjisiz çalışma prosedürüyle yapılmalıdır.');

    return {
      score: result.score,
      rawScore: result.rawScore,
      maxScore: MAX_SCORE,
      level,
      answers: a,
      layers: dedupe(layers),
      reasons: dedupe(reasons),
      checks: dedupe(checks),
      warnings: dedupe(warnings),
      productCategories: dedupe(productCategories),
      type1Need,
      type2Need,
      type3Need
    };
  }

  function readForm(form) {
    const data = new FormData(form);
    return Object.fromEntries(data.entries());
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char];
    });
  }

  function renderList(target, items) {
    target.innerHTML = items.map(function (item) { return '<li>' + escapeHtml(item) + '</li>'; }).join('');
  }

  function init() {
    const form = document.getElementById('riskForm');
    if (!form) return;

    const results = document.getElementById('results');
    const scoreEl = document.getElementById('riskScore');
    const levelEl = document.getElementById('riskLevel');
    const bar = document.getElementById('riskBar');
    const layersEl = document.getElementById('layers');
    const reasonsEl = document.getElementById('reasons');
    const checksEl = document.getElementById('checks');
    const warningsEl = document.getElementById('warnings');
    const productsEl = document.getElementById('productCategories');
    const resetBtn = document.getElementById('resetBtn');

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      const recommendation = buildRecommendation(readForm(form));
      scoreEl.textContent = recommendation.score + '/100';
      levelEl.textContent = recommendation.level.label;
      levelEl.className = 'status ' + recommendation.level.css;
      bar.style.width = recommendation.score + '%';
      bar.setAttribute('aria-valuenow', String(recommendation.score));
      renderList(layersEl, recommendation.layers);
      renderList(reasonsEl, recommendation.reasons.length ? recommendation.reasons : ['Belirgin yüksek risk göstergesi seçilmedi; mevcut koruma ve bakım durumu yine de doğrulanmalıdır.']);
      renderList(checksEl, recommendation.checks);
      renderList(warningsEl, recommendation.warnings);
      productsEl.innerHTML = recommendation.productCategories.map(function (category) {
        return '<div class="category-link">' + escapeHtml(category) + '<span>Teknik kriterleri ürün merkezinde doğrulayın</span></div>';
      }).join('') || '<p>Bu sonuçta doğrudan ürün yönlendirmesi yapılmadı; önce mevcut tesisat ve SPD durumu doğrulanmalıdır.</p>';
      results.classList.remove('hidden');
      results.focus();
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    resetBtn.addEventListener('click', function () {
      form.reset();
      results.classList.add('hidden');
      document.getElementById('arac').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
  }

  return { WEIGHTS, MAX_SCORE, normalizeAnswers, calculateScore, classify, buildRecommendation };
});
