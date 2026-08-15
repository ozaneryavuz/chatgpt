(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ALO186Parafudr = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const WEIGHTS = Object.freeze({
    lps: { yes: 34, no: 0, unknown: 12 },
    supply: { overhead: 18, mixed: 12, underground: 2, unknown: 8 },
    events: { frequent: 16, occasional: 8, rare: 1, unknown: 6 },
    sensitive: { many: 12, some: 6, none: 0 },
    existing: { none: 15, unknown: 10, type3: 12, type2: 3, type12: 0 },
    distance: { over10: 6, under10: 0, unknown: 3 },
    earthing: { verified: 0, old: 7, failed: 14, unknown: 9 },
    damage: { yes: 14, no: 0, unknown: 3 }
  });

  const MAX_SCORE = Object.values(WEIGHTS).reduce((sum, group) => sum + Math.max(...Object.values(group)), 0);
  const FIXED_TYPES = new Set(['type1', 'type12', 'type2', 'type23']);
  const valid = (group, value, fallback) => Object.prototype.hasOwnProperty.call(WEIGHTS[group], value) ? value : fallback;
  const uniq = (items) => Array.from(new Set(items));

  function normalizeAnswers(raw) {
    const s = raw || {};
    return {
      emergency: Boolean(s.emergency),
      activeStorm: s.activeStorm || 'no',
      useCase: s.useCase || 'home',
      specialSystem: s.specialSystem || 'no',
      phase: s.phase || 'single',
      lps: valid('lps', s.lps, 'unknown'),
      supply: valid('supply', s.supply, 'unknown'),
      events: valid('events', s.events, 'unknown'),
      sensitive: valid('sensitive', s.sensitive, 'some'),
      existing: valid('existing', s.existing, 'unknown'),
      indicator: s.indicator || 'unknown',
      documentation: s.documentation || 'unknown',
      inspection: s.inspection || 'unknown',
      distance: valid('distance', s.distance, 'unknown'),
      earthing: valid('earthing', s.earthing, 'unknown'),
      damage: valid('damage', s.damage, 'unknown'),
      candidateType: s.candidateType || 'none',
      candidateStandard: s.candidateStandard || 'unknown',
      candidateSystemMatch: s.candidateSystemMatch || 'unknown',
      candidateCoordination: s.candidateCoordination || 'unknown',
      confirmNeed: Boolean(s.confirmNeed),
      confirmSpecs: Boolean(s.confirmSpecs),
      confirmAffiliate: Boolean(s.confirmAffiliate)
    };
  }

  function calculateScore(raw) {
    const a = normalizeAnswers(raw);
    const keys = ['lps', 'supply', 'events', 'sensitive', 'existing', 'distance', 'earthing', 'damage'];
    const rawScore = keys.reduce((sum, key) => sum + WEIGHTS[key][a[key]], 0);
    return { answers: a, rawScore, score: Math.max(0, Math.min(100, Math.round(rawScore / MAX_SCORE * 100))) };
  }

  function classify(score) {
    if (score >= 65) return { key: 'high', label: 'Yüksek öncelik', css: 'bad' };
    if (score >= 35) return { key: 'medium', label: 'Orta öncelik', css: 'warn' };
    return { key: 'review', label: 'Temel kontrol', css: 'ok' };
  }

  function buildRecommendation(raw) {
    const base = calculateScore(raw);
    const a = base.answers;
    const level = classify(base.score);
    const stops = [];
    const professional = [];
    const evidence = [];
    const layers = [];
    const reasons = [];
    const warnings = [];
    const strengths = [];

    if (a.emergency) stops.push('Duman, erime, su teması, elektrik çarpması veya aktif kıvılcım riski varsa ürün seçmeyin; güvenli alana geçin, yangın/yaralanmada 112 önceliklidir.');
    if (a.activeStorm === 'yes') stops.push('Aktif gök gürültülü fırtına sırasında pano açmayın, SPD değiştirmeyin veya bağlantıya müdahale etmeyin. Değerlendirmeyi fırtına geçtikten sonra yetkili elektrikçiyle sürdürün.');
    if (a.earthing === 'failed') stops.push('Topraklama/eşpotansiyel kontrolde uygunsuzluk var. SPD satın almadan önce tesisat kusuru giderilmelidir.');
    if (a.indicator === 'failed') professional.push('Mevcut SPD durum göstergesi ömür sonu/arıza işareti veriyor. Ürün sınıfını büyütmek yerine aynı sistem için üretici talimatına göre profesyonel değişim gerekir.');

    if (a.useCase !== 'home') professional.push('Ticari, ortak pano veya kritik tesiste yıldırım risk analizi, seçicilik ve SPD koordinasyonu projelendirilmelidir.');
    if (a.specialSystem === 'yes') professional.push('PV, EV şarj, enerji depolama veya veri/anten hattı varsa AC pano SPD seçimi tek başına yeterli değildir; ilgili AC/DC/data koruma mimarisi birlikte projelendirilmelidir.');
    if (a.phase === 'three') professional.push('Trifaze sistemde şebeke/topraklama düzeni, kutup sayısı, Uc ve kısa devre koordinasyonu saha verisiyle doğrulanmalıdır.');
    if (a.phase === 'unknown') evidence.push('Faz ve şebeke/topraklama düzeni bilinmiyor; ürün kutup ve Uc seçimi güvenle yapılamaz.');
    if (a.earthing !== 'verified') evidence.push('Topraklama ve eşpotansiyel bağlantı güncel ölçümle doğrulanmadı.');

    const type1Need = a.lps === 'yes';
    const upstreamAdequate = type1Need ? a.existing === 'type12' : ['type2', 'type12'].includes(a.existing);
    const type2Need = !upstreamAdequate;
    const type3Useful = a.sensitive === 'many' && upstreamAdequate;

    if (type1Need) {
      layers.push('Dış yıldırımlık/LPS bulunan yapıda giriş kademesinde Tip 1 veya kombine Tip 1+2 SPD profesyonel olarak doğrulanmalıdır.');
      reasons.push('Dış yıldırımlık/LPS, yıldırım akımının tesis girişinde yönetilmesini gerektiren ana göstergedir.');
    } else {
      layers.push('Tipik konut dağıtım panosunda Tip 2 SPD, transient aşırı gerilim için ana pano koruma katmanı olarak değerlendirilir.');
    }
    if (a.supply === 'overhead' || a.supply === 'mixed') reasons.push('Havai veya karma besleme atmosferik transient maruziyetini artırabilir; bu tek başına Tip 1 seçimi anlamına gelmez, risk değerlendirmesini yükseltir.');
    if (a.events === 'frequent') reasons.push('Sık yıldırım veya gerilim darbesi gözlemi koruma ve bakım önceliğini artırır.');
    if (a.damage === 'yes') reasons.push('Geçmiş cihaz hasarı mevcut koruma, topraklama ve koordinasyonun yeniden incelenmesini gerektirir.');
    if (a.existing === 'type3') warnings.push('Yalnız priz tipi/Tip 3 ürün, panodaki Tip 2 veya gerekli Tip 1+2 katmanının yerine geçmez.');
    if (a.existing === 'unknown') evidence.push('Mevcut panodaki SPD tipi ve etiket değerleri bilinmiyor.');
    if (a.documentation !== 'verified' && a.existing !== 'none') evidence.push('Mevcut SPD için tam model teknik belge ve IEC/EN 61643-11 uygunluk beyanı doğrulanmadı.');
    if (a.inspection !== 'pass' && a.existing !== 'none') evidence.push('Mevcut SPD, yedek koruma ve bağlantı düzeni yetkili kontrolde doğrulanmadı.');
    if (a.indicator === 'unknown' && a.existing !== 'none') evidence.push('Mevcut SPD durum göstergesi/ömür sonu bilgisi doğrulanmadı.');
    if (a.distance === 'over10') warnings.push('Ana pano ile hassas yük arasındaki uzun hat, ikinci dağıtım kademesi veya cihaz yakınında ek koordinasyon ihtiyacını artırabilir; Tip 3 kararı otomatik verilmez.');

    if (type2Need && !type1Need) layers.push('Mevcut üst kademe doğrulanmadığı için Tip 2 SPD sınıfı, yetkili elektrikçi tarafından şebeke sistemi ve üretici koordinasyonuyla seçilmelidir.');
    if (type3Useful) layers.push('Üst kademe SPD doğrulanmışsa hassas elektronikler için cihaz yakınında Tip 3 ek koruma değerlendirilebilir; tek başına bina koruması sayılmaz.');

    const candidate = a.candidateType;
    const candidateMismatch = [];
    if (candidate !== 'none') {
      if (type1Need && !['type1', 'type12'].includes(candidate)) candidateMismatch.push('Bu yapıda LPS nedeniyle Tip 1 kapasitesi gereken giriş katmanını aday ürün karşılamıyor.');
      if (!type1Need && candidate === 'type1') warnings.push('Tip 1 “daha iyi Tip 2” değildir; seçim gerçek yıldırım akımı senaryosu ve koordinasyona göre yapılır.');
      if (candidate === 'type3' && !upstreamAdequate) candidateMismatch.push('Tip 3 aday ürünün önünde doğrulanmış Tip 2 veya Tip 1+2 katmanı yok.');
      if (FIXED_TYPES.has(candidate) && a.candidateSystemMatch !== 'verified') evidence.push('Aday sabit SPD’nin faz/topraklama sistemi, kutup düzeni ve Uc uyumu üretici belgesiyle doğrulanmadı.');
      if (FIXED_TYPES.has(candidate) && a.candidateCoordination !== 'verified') evidence.push('Aday sabit SPD’nin yedek sigorta/MCB ve kısa devre koordinasyonu üretici tablosuyla doğrulanmadı.');
      if (a.candidateStandard !== 'verified') evidence.push('Aday ürünün IEC/EN 61643-11 uygunluk beyanı doğrulanmadı.');
    }
    evidence.push(...candidateMismatch);

    const existingPass = upstreamAdequate && a.indicator === 'ok' && a.documentation === 'verified' && a.inspection === 'pass' && a.earthing === 'verified';
    if (existingPass) strengths.push('Mevcut üst kademe SPD tipi, durum göstergesi, teknik belge, topraklama ve yetkili kontrol kanıtı mevcut.');

    let status = 'recommend';
    let headline = type1Need ? 'Tip 1+2 giriş korumasını profesyonel olarak doğrulayın' : 'Tip 2 pano korumasını profesyonel olarak doğrulayın';
    if (stops.length) {
      status = 'stop'; headline = 'Önce can ve tesisat güvenliği';
    } else if (professional.length) {
      status = 'professional'; headline = 'Tek ürün yerine profesyonel SPD mimarisi gerekli';
    } else if (existingPass && !type3Useful && a.damage !== 'yes') {
      status = 'no-buy'; headline = 'Mevcut üst kademe koruma yeterli — yeni SPD almayın';
    } else if (candidateMismatch.length || a.phase === 'unknown' || a.earthing !== 'verified') {
      status = 'evidence'; headline = 'Ürün seçmeden önce eksik teknik kanıtları tamamlayın';
    } else if (existingPass && type3Useful) {
      status = 'downstream'; headline = 'Üst kademe yeterli; yalnız hassas cihaz için Tip 3 ek korumayı değerlendirin';
    }

    const confirmations = Boolean(a.confirmNeed && a.confirmSpecs && a.confirmAffiliate);
    const affiliateAllowed = status === 'downstream' && confirmations && a.earthing === 'verified' && upstreamAdequate && a.specialSystem === 'no';

    warnings.push('SPD sürekli düşük/yüksek gerilimi düzeltmez; gerilim izleme/regülasyon ve transient koruma farklı işlevlerdir.');
    warnings.push('Sabit pano SPD montajı, enerjili ölçüm ve bağlantı kullanıcı işi değildir; yetkili elektrikçi ve üretici talimatı gerekir.');
    warnings.push('IEC 61643-11:2025 güncel AC alçak gerilim SPD ürün standardıdır; ürünün tam model beyanı ve yerel uygulama şartları ayrıca doğrulanmalıdır.');

    return {
      score: base.score,
      level,
      answers: a,
      status,
      headline,
      type1Need,
      type2Need,
      type3Useful,
      upstreamAdequate,
      stops: uniq(stops),
      professional: uniq(professional),
      evidence: uniq(evidence),
      layers: uniq(layers),
      reasons: uniq(reasons),
      warnings: uniq(warnings),
      strengths: uniq(strengths),
      confirmations,
      affiliateAllowed,
      affiliateHref: 'https://www.amazon.com.tr/s?k=tip+3+akim+korumali+priz+IEC+61643-11&tag=alo186rehber-21',
      privacy: 'Form tarayıcıda değerlendirilir; kişisel veri, konum, kalıcı depolama veya ağ isteği kullanılmaz.'
    };
  }

  function readForm(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    ['emergency', 'confirmNeed', 'confirmSpecs', 'confirmAffiliate'].forEach((name) => { data[name] = Boolean(form.elements[name] && form.elements[name].checked); });
    return data;
  }
  function esc(value) { return String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
  function list(title, items) { return items.length ? `<section><h3>${esc(title)}</h3><ul>${items.map(i => `<li>${esc(i)}</li>`).join('')}</ul></section>` : ''; }

  function render(r) {
    const results = document.getElementById('results');
    document.getElementById('riskScore').textContent = `${r.score}/100`;
    const level = document.getElementById('riskLevel'); level.textContent = r.level.label; level.className = `status ${r.level.css}`;
    const bar = document.getElementById('riskBar'); bar.style.width = `${r.score}%`; bar.setAttribute('aria-valuenow', String(r.score));
    document.getElementById('resultTitle').textContent = r.headline;
    document.getElementById('resultBody').innerHTML =
      list('Önerilen koruma katmanları', r.layers) + list('Olumlu kanıtlar', r.strengths) + list('Önceliği yükselten göstergeler', r.reasons) +
      list('Önce durdurun', r.stops) + list('Profesyonel tasarım gerektirenler', r.professional) + list('Eksik teknik kanıtlar', r.evidence) + list('Sınırlar', r.warnings);
    const affiliate = document.getElementById('affiliateAction');
    if (r.affiliateAllowed) {
      affiliate.hidden = false;
      const link = affiliate.querySelector('a'); link.href = r.affiliateHref;
    } else affiliate.hidden = true;
    results.classList.remove('hidden'); results.focus();
    results.scrollIntoView({behavior: 'smooth', block: 'start'});
  }

  function init() {
    const form = document.getElementById('riskForm'); if (!form) return;
    form.addEventListener('submit', e => { e.preventDefault(); render(buildRecommendation(readForm(form))); });
    document.getElementById('resetBtn').addEventListener('click', () => { form.reset(); document.getElementById('results').classList.add('hidden'); document.getElementById('arac').scrollIntoView({behavior:'smooth'}); });
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  }
  return { WEIGHTS, MAX_SCORE, normalizeAnswers, calculateScore, classify, buildRecommendation };
});