(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.ALO186EquipmentCare = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const EQUIPMENT = Object.freeze({
    'ups-battery': {
      label: 'UPS / power station akü-batarya durumu',
      route: 'consumer-after-check',
      productCategory: 'ups-battery',
      guidance: 'Üretici self-testini, uyarı göstergesini ve gerçek yükte çalışma süresini kontrol edin. Kasa açmayın; yalnız model kılavuzunda kullanıcı tarafından değiştirilebilir olduğu açıkça belirtilen bataryayı değerlendirin.'
    },
    generator: {
      label: 'Jeneratör ve transfer sistemi',
      route: 'professional',
      guidance: 'Bakım aralığını çalışma saati ve model kılavuzuna göre doğrulayın. Yakıt, egzoz, transfer şalteri, akü ve sabit bağlantı işlemlerini yetkili servis veya uzman yürütmelidir.'
    },
    rcd: {
      label: 'Kaçak akım koruma cihazı test düğmesi',
      route: 'professional',
      guidance: 'Yalnız erişilebilir test düğmesini üretici ve yerel kural talimatına göre kullanın. Cihaz açmazsa tekrar tekrar denemeyin; pano kapağını açmadan elektrik uzmanına başvurun.'
    },
    spd: {
      label: 'Parafudr / SPD durum göstergesi',
      route: 'professional',
      guidance: 'Yalnız dışarıdan görülebilen durum göstergesini kontrol edin. Kırmızı/arıza göstergesinde pano içi modül seçimi ve değişimi yetkili elektrikçi tarafından yapılmalıdır.'
    },
    'inverter-storage': {
      label: 'İnverter ve enerji depolama sistemi',
      route: 'professional',
      guidance: 'Alarm günlüğü, üretici uygulaması ve görünür durum göstergelerini kontrol edin. DC kablo, sigorta, BMS, batarya kabini veya sabit bağlantıya müdahale etmeyin.'
    },
    'ev-charger': {
      label: 'EV şarj cihazı, kablo ve konnektör',
      route: 'professional',
      guidance: 'Kablo, fiş ve konnektörde görünür hasar veya aşırı ısınma belirtisi varsa kullanımı durdurun. Sabit cihaz, koruma düzeni ve tesisat kontrolü yetkili uzman gerektirir.'
    },
    'emergency-light': {
      label: 'Acil aydınlatma / taşınabilir lamba',
      route: 'consumer-after-check',
      productCategory: 'emergency-lighting',
      guidance: 'Şarj durumunu, görünür hasarı ve üretici kılavuzundaki işlev testini kontrol edin. Sabit acil aydınlatma tesisatı ve batarya değişimi için yetkili servis sınırını izleyin.'
    }
  });

  const CONDITIONS = Object.freeze({
    ok: 'Normal / uyarı yok',
    attention: 'Uyarı, alarm veya performans düşüşü var',
    service: 'Servis / uzman kontrolü gerekli',
    unknown: 'Henüz kontrol edilmedi'
  });

  function parseDate(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    const date = new Date(`${value}T12:00:00Z`);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function isoDate(date) {
    return date.toISOString().slice(0, 10);
  }

  function addDays(dateValue, days) {
    const date = dateValue instanceof Date ? new Date(dateValue.getTime()) : parseDate(dateValue);
    const numericDays = Number(days);
    if (!date || !Number.isInteger(numericDays) || numericDays < 1 || numericDays > 3660) return null;
    date.setUTCDate(date.getUTCDate() + numericDays);
    return isoDate(date);
  }

  function dayDiff(fromValue, toValue) {
    const from = fromValue instanceof Date ? fromValue : parseDate(fromValue);
    const to = toValue instanceof Date ? toValue : parseDate(toValue);
    if (!from || !to) return null;
    return Math.round((to.getTime() - from.getTime()) / 86400000);
  }

  function validatePlan(input) {
    const errors = [];
    const equipment = EQUIPMENT[input && input.equipment];
    const lastCheck = parseDate(input && input.lastCheck);
    const intervalDays = Number(input && input.intervalDays);
    const condition = input && input.condition;

    if (!equipment) errors.push('Geçerli bir ekipman kategorisi seçin.');
    if (!lastCheck) errors.push('Geçerli bir son kontrol tarihi girin.');
    if (lastCheck && lastCheck.getTime() > Date.now() + 86400000) errors.push('Son kontrol tarihi gelecekte olamaz.');
    if (![30, 90, 180, 365].includes(intervalDays)) errors.push('Geçerli bir hatırlatma aralığı seçin.');
    if (!Object.prototype.hasOwnProperty.call(CONDITIONS, condition)) errors.push('Geçerli bir gözlem sonucu seçin.');
    if (!input || input.noUnsafeWork !== true) errors.push('Güvenli çalışma sınırını kabul edin.');

    return { valid: errors.length === 0, errors };
  }

  function createPlan(input, now) {
    const validation = validatePlan(input);
    if (!validation.valid) return { error: validation.errors };
    const created = now instanceof Date ? now : new Date();
    const nextCheck = addDays(input.lastCheck, Number(input.intervalDays));
    return {
      id: `care-${created.getTime()}-${Math.random().toString(36).slice(2, 8)}`,
      equipment: input.equipment,
      lastCheck: input.lastCheck,
      intervalDays: Number(input.intervalDays),
      nextCheck,
      condition: input.condition,
      manualKnown: input.manualKnown === true,
      createdAt: created.toISOString()
    };
  }

  function statusForPlan(plan, todayValue) {
    const today = todayValue instanceof Date ? todayValue : (parseDate(todayValue) || new Date());
    const next = parseDate(plan && plan.nextCheck);
    if (!next) return { key: 'invalid', label: 'Tarih hatası', days: null };
    const days = dayDiff(today, next);
    if (days < 0) return { key: 'overdue', label: `${Math.abs(days)} gün gecikti`, days };
    if (days === 0) return { key: 'today', label: 'Bugün kontrol edin', days };
    if (days <= 30) return { key: 'soon', label: `${days} gün kaldı`, days };
    return { key: 'scheduled', label: `${days} gün kaldı`, days };
  }

  function summarize(plans, todayValue) {
    const list = Array.isArray(plans) ? plans : [];
    const statuses = list.map((plan) => statusForPlan(plan, todayValue));
    return {
      total: list.length,
      overdue: statuses.filter((item) => item.key === 'overdue' || item.key === 'today').length,
      soon: statuses.filter((item) => item.key === 'soon').length,
      service: list.filter((plan) => plan.condition === 'attention' || plan.condition === 'service').length
    };
  }

  function commercialDecision(plan) {
    const equipment = EQUIPMENT[plan && plan.equipment];
    if (!equipment) return { showCommercial: false, showProfessional: true, reason: 'Ekipman türü doğrulanamadı.' };
    const abnormal = plan.condition === 'attention' || plan.condition === 'service';
    const checked = plan.manualKnown === true;

    if (equipment.route === 'professional') {
      return {
        showCommercial: false,
        showProfessional: abnormal || plan.condition === 'unknown',
        reason: equipment.guidance,
        productCategory: null
      };
    }

    const showCommercial = abnormal && checked;
    return {
      showCommercial,
      showProfessional: abnormal && !checked,
      reason: equipment.guidance,
      productCategory: showCommercial ? equipment.productCategory : null
    };
  }

  function sanitizePlans(value) {
    if (!Array.isArray(value)) return [];
    return value.filter((plan) => {
      return plan && EQUIPMENT[plan.equipment] && parseDate(plan.lastCheck) && parseDate(plan.nextCheck) &&
        [30, 90, 180, 365].includes(Number(plan.intervalDays)) && CONDITIONS[plan.condition] &&
        typeof plan.manualKnown === 'boolean' && typeof plan.id === 'string';
    }).slice(0, 100).map((plan) => ({
      id: plan.id,
      equipment: plan.equipment,
      lastCheck: plan.lastCheck,
      intervalDays: Number(plan.intervalDays),
      nextCheck: plan.nextCheck,
      condition: plan.condition,
      manualKnown: plan.manualKnown,
      createdAt: typeof plan.createdAt === 'string' ? plan.createdAt : null
    }));
  }

  function exportPayload(plans) {
    return {
      schema: 'alo186-equipment-care-v1',
      exportedAt: new Date().toISOString(),
      privacy: 'No name, address, contact, subscriber, serial number, brand/model or free text.',
      plans: sanitizePlans(plans)
    };
  }

  return { EQUIPMENT, CONDITIONS, addDays, dayDiff, validatePlan, createPlan, statusForPlan, summarize, commercialDecision, sanitizePlans, exportPayload };
});