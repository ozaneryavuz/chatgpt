(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.Alo186SolutionOutcome = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';

  const VERSION = 1;
  const MAX_RECORDS = 12;
  const TTL_DAYS = 180;
  const DAY_MS = 24 * 60 * 60 * 1000;

  const SOURCES = {
    decision_engine: 'Karar motoru',
    outage_workshop: 'Kesintiye hazırlık atölyesi',
    calculator: 'Ücretsiz hesaplayıcı',
    product_center: 'Akıllı Ürün Merkezi',
    guide: 'Teknik rehber',
    professional: 'Profesyonel değerlendirme'
  };

  const CATEGORIES = {
    outage_official: {
      label: 'Kesinti ve resmî işlem',
      tool: '/karar-motoru',
      monitor: '/hesaplama/kesinti-gunlugu/',
      professional: '/edas-bul',
      maintenance: '/hesaplama/kesinti-hazirlik-plani/',
      highRisk: false
    },
    indoor_fault: {
      label: 'İç tesisat, pano veya priz',
      tool: '/karar-motoru',
      monitor: '/hesaplama/ekipman-bakim-plani/',
      professional: '/kurumsal-elektrik-surekliligi-on-degerlendirme?problem=genel_risk&scope=saha_inceleme',
      maintenance: '/hesaplama/ekipman-bakim-plani/',
      highRisk: true
    },
    backup_power: {
      label: 'UPS, jeneratör ve yedek güç',
      tool: '/hesaplama/yedek-guc-cozum-secici/',
      monitor: '/hesaplama/ekipman-bakim-plani/',
      professional: '/kurumsal-elektrik-surekliligi-on-degerlendirme?problem=yedek_guc&scope=karsilastirma',
      maintenance: '/hesaplama/ekipman-bakim-plani/',
      highRisk: true
    },
    protection: {
      label: 'RCD, parafudr ve gerilim koruması',
      tool: '/hesaplama/gerilim-koruma-cozum-secici/',
      monitor: '/hesaplama/ekipman-bakim-plani/',
      professional: '/kurumsal-elektrik-surekliligi-on-degerlendirme?problem=genel_risk&scope=saha_inceleme',
      maintenance: '/hesaplama/ekipman-bakim-plani/',
      highRisk: true
    },
    solar_storage: {
      label: 'GES, inverter ve enerji depolama',
      tool: '/hesaplama/inverter-uygunluk/',
      monitor: '/hesaplama/ekipman-bakim-plani/',
      professional: '/kurumsal-elektrik-surekliligi-on-degerlendirme?problem=ges_batarya&scope=karsilastirma',
      maintenance: '/hesaplama/ekipman-bakim-plani/',
      highRisk: true
    },
    ev_charging: {
      label: 'EV şarj ve wallbox',
      tool: '/hesaplama/ev-sarj-uygunluk/',
      monitor: '/hesaplama/ekipman-bakim-plani/',
      professional: '/kurumsal-elektrik-surekliligi-on-degerlendirme?problem=ev_sarj&scope=saha_inceleme',
      maintenance: '/hesaplama/ekipman-bakim-plani/',
      highRisk: true
    },
    product_selection: {
      label: 'Tak-çalıştır ürün seçimi',
      tool: '/akilli-urun-secimi',
      monitor: '/hesaplama/ekipman-bakim-plani/',
      professional: '/kurumsal-elektrik-surekliligi-on-degerlendirme?problem=urun_uygunlugu&scope=uzaktan_dokuman',
      maintenance: '/hesaplama/ekipman-bakim-plani/',
      highRisk: false
    },
    business_continuity: {
      label: 'Otel, site ve işletme sürekliliği',
      tool: '/hesaplama/elektrik-surekliligi-olgunluk-skoru/',
      monitor: '/isletme-surekliligi',
      professional: '/kurumsal-elektrik-surekliligi-on-degerlendirme',
      maintenance: '/hesaplama/elektrik-surekliligi-pasaportu/',
      highRisk: true
    }
  };

  const ACTIONS = {
    official_channel: 'Resmî kanal / 186 / EDAŞ',
    free_tool: 'Ücretsiz hesaplayıcı veya karar aracı',
    maintenance: 'Bakım, test veya küçük düzeltme',
    existing_equipment: 'Mevcut ekipmanı doğru kullanma',
    product: 'Yeni tak-çalıştır ürün',
    electrician: 'Yetkili elektrikçi veya servis',
    professional_service: 'Ücretli profesyonel değerlendirme'
  };

  const OUTCOMES = {
    resolved: 'Tam çözüldü',
    partial: 'Kısmen çözüldü',
    unresolved: 'Çözülmedi',
    safety: 'Güvenlik riski oluştu'
  };

  const RECURRENCES = {
    none: 'Tekrar etmedi',
    once: 'Bir kez tekrar etti',
    multiple: 'Birden fazla tekrar etti'
  };

  const PURCHASES = {
    no_purchase: 'Satın alma gerekmedi',
    existing: 'Mevcut ürün yeterli oldu',
    new_product: 'Yeni ürün kullanıldı',
    paid_service: 'Profesyonel hizmet kullanıldı',
    not_applicable: 'Ürün kararı yok'
  };

  const ALIASES = {
    source: {
      'karar-motoru': 'decision_engine',
      'kesinti-atolyesi': 'outage_workshop',
      'hesaplayici': 'calculator',
      'urun-secimi': 'product_center',
      'rehber': 'guide',
      'profesyonel': 'professional'
    },
    category: {
      outage: 'outage_official',
      external: 'outage_official',
      meter: 'outage_official',
      panel: 'indoor_fault',
      internet: 'backup_power',
      mobile: 'product_selection',
      electronics: 'protection',
      lighting: 'product_selection',
      cold_chain: 'backup_power',
      long_outage: 'backup_power',
      generator: 'backup_power',
      inverter: 'solar_storage',
      surge_strip: 'protection',
      mini_ups: 'backup_power',
      power_station: 'backup_power',
      powerbank: 'product_selection',
      emergency_light: 'product_selection',
      smoke_alarm: 'product_selection',
      smart_plug: 'product_selection',
      ev_cable: 'ev_charging',
      ups_battery: 'backup_power'
    }
  };

  function hasOwn(object, key) {
    return Object.prototype.hasOwnProperty.call(object, key);
  }

  function normalizeEnum(value, allowed, fallback, aliases) {
    const raw = String(value || '').trim();
    const aliased = aliases && hasOwn(aliases, raw) ? aliases[raw] : raw;
    return hasOwn(allowed, aliased) ? aliased : fallback;
  }

  function sanitizeInput(input = {}) {
    return {
      source: normalizeEnum(input.source, SOURCES, 'guide', ALIASES.source),
      category: normalizeEnum(input.category, CATEGORIES, 'outage_official', ALIASES.category),
      action: normalizeEnum(input.action, ACTIONS, 'free_tool'),
      outcome: normalizeEnum(input.outcome, OUTCOMES, 'unresolved'),
      recurrence: normalizeEnum(input.recurrence, RECURRENCES, 'none'),
      purchase: normalizeEnum(input.purchase, PURCHASES, 'not_applicable')
    };
  }

  function routeAction(label, href, kind = 'primary') {
    return { label, href, kind };
  }

  function followupDaysFor(input) {
    if (input.outcome === 'safety') return 0;
    if (input.outcome === 'unresolved') return input.recurrence === 'multiple' ? 3 : 7;
    if (input.outcome === 'partial') return input.recurrence === 'multiple' ? 7 : 14;
    if (input.recurrence === 'multiple') return 14;
    if (input.category === 'outage_official') return 30;
    if (input.action === 'product' || input.purchase === 'new_product') return 30;
    return 90;
  }

  function deriveDecision(rawInput = {}) {
    const input = sanitizeInput(rawInput);
    const meta = CATEGORIES[input.category];
    const followupDays = followupDaysFor(input);
    const base = {
      input,
      categoryLabel: meta.label,
      revenueAllowed: false,
      followupDays,
      followupRoute: meta.monitor,
      actions: [],
      steps: []
    };

    if (input.outcome === 'safety') {
      return {
        ...base,
        key: 'safety_escalation',
        title: 'Ürün ve normal kontrol adımlarını durdurun',
        summary: 'Yeni ürün aramayın. Duman, alev, elektrik çarpması, kopmuş hat veya hızla artan ısı varsa güvenli uzaklığa çıkın ve 112’yi arayın; şebeke etkisi için 186 veya resmî EDAŞ kanalını kullanın.',
        actions: [
          routeAction('112’yi ara', 'tel:112', 'danger'),
          routeAction('Doğru resmî kanalı bul', '/karar-motoru', 'secondary')
        ],
        steps: ['Tehlikeli bölüme yaklaşmayın.', 'Enerjili ekipmana müdahale etmeyin.', 'Acil ve resmî kanal talimatlarını izleyin.']
      };
    }

    if (input.outcome === 'resolved') {
      if (input.purchase === 'new_product' || input.action === 'product') {
        return {
          ...base,
          key: 'resolved_product',
          title: 'Çözüm işe yaradı; yeni ürün aramayın',
          summary: 'Kullanılan ürün ihtiyacı karşıladıysa yeni bir satın alma rotası açılmaz. Etiket, kablo, pil, sıcaklık ve bakım koşullarını yeniden kontrol etmek için takip tarihi oluşturun.',
          actions: [
            routeAction('Bakım ve kontrol planı oluştur', meta.maintenance),
            routeAction('30 günlük kontrol ekle', '#followup', 'secondary')
          ],
          steps: ['Ürünün çalıştığı gerçek yük ve süreyi kaydedin.', 'Hasar, ısınma veya kapasite kaybını izleyin.', 'Yeni satın alma yerine bakım ve yeniden test uygulayın.']
        };
      }

      return {
        ...base,
        key: 'resolved_no_purchase',
        title: 'Sorun satın alma olmadan çözüldü',
        summary: 'Resmî kanal, mevcut ekipman, bakım veya ücretsiz araç yeterli oldu. Bu sonuç güvenli kullanıcı değeridir; yeni ürün önerilmez.',
        actions: [
          routeAction('Sonucu izleme planına ekle', meta.monitor),
          routeAction('Yeniden kontrol tarihi oluştur', '#followup', 'secondary')
        ],
        steps: ['Çözümün hangi koşulda işe yaradığını not yerine kapalı sonuç kaydıyla saklayın.', 'Sorun tekrar ederse aynı rotayı körlemesine tekrarlamayın.', 'Takip tarihinde ekipman ve belirti durumunu yeniden kontrol edin.']
      };
    }

    if (input.outcome === 'partial') {
      const actions = [routeAction('Teknik aracı yeniden aç', meta.tool)];
      if (meta.highRisk || input.recurrence === 'multiple') actions.push(routeAction('Profesyonel kapsamı hazırla', meta.professional, 'secondary'));
      return {
        ...base,
        key: 'partial_resolution',
        title: 'Kısmi çözüm var; kök neden doğrulanmadı',
        summary: 'Belirti azalmış olsa da sonuç kalıcı kabul edilmemeli. Ürün veya ayar değiştirmeden önce aynı koşulda ölçüm, test ve yeniden kontrol yapın.',
        actions,
        steps: ['Belirtinin hangi koşulda devam ettiğini kapalı kategoriyle kaydedin.', 'Ücretsiz teknik aracı güncel değerlerle yeniden çalıştırın.', 'Tekrar varsa yetkili uzman veya resmî kanala ilerleyin.']
      };
    }

    const repeated = input.recurrence === 'multiple';
    const highRisk = meta.highRisk || ['electrician', 'professional_service'].includes(input.action);
    const actions = [routeAction('Doğru teknik rotayı yeniden aç', meta.tool)];
    if (repeated || highRisk) actions.unshift(routeAction('Profesyonel ön değerlendirmeyi aç', meta.professional));
    else actions.push(routeAction('Takip kaydı oluştur', meta.monitor, 'secondary'));

    return {
      ...base,
      key: repeated ? 'unresolved_repeated' : 'unresolved',
      title: repeated ? 'Sorun tekrar ediyor; ürün denemesini durdurun' : 'Sorun çözülmedi; aynı adımı körlemesine tekrarlamayın',
      summary: repeated
        ? 'Birden fazla tekrar eden sorun, yanlış ürün seçimi veya yüzeysel müdahale ihtimalini artırır. Sabit tesisat, yüksek güç veya güvenlik kritik alanda profesyonel inceleme önceliklidir.'
        : 'Önce belirtiyi ve kullanılan rotayı yeniden sınıflandırın. Yeni ürün ancak teknik eksik açıkça doğrulanırsa değerlendirilmelidir.',
      actions,
      steps: ['Aynı ürünü, şalteri veya ayarı tekrar tekrar denemeyin.', 'Gözlemi güncel teknik araçla yeniden sınıflandırın.', repeated || highRisk ? 'Profesyonel veya resmî değerlendirme isteyin.' : '7 gün içinde sonucu yeniden kontrol edin.']
    };
  }

  function addDays(date, days) {
    return new Date(date.getTime() + days * DAY_MS);
  }

  function safeId(value, now) {
    const cleaned = String(value || '').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 48);
    return cleaned || `outcome_${now.getTime().toString(36)}`;
  }

  function normalizeRecord(rawInput = {}, nowValue = new Date()) {
    const now = nowValue instanceof Date ? nowValue : new Date(nowValue);
    const decision = deriveDecision(rawInput);
    const due = decision.followupDays > 0 ? addDays(now, decision.followupDays) : null;
    return {
      version: VERSION,
      id: safeId(rawInput.id, now),
      createdAt: now.toISOString(),
      dueAt: due ? due.toISOString() : null,
      source: decision.input.source,
      category: decision.input.category,
      action: decision.input.action,
      outcome: decision.input.outcome,
      recurrence: decision.input.recurrence,
      purchase: decision.input.purchase,
      decisionKey: decision.key,
      followupRoute: decision.followupRoute
    };
  }

  function isValidRecord(record) {
    return record && typeof record === 'object'
      && Number(record.version) === VERSION
      && hasOwn(SOURCES, record.source)
      && hasOwn(CATEGORIES, record.category)
      && hasOwn(ACTIONS, record.action)
      && hasOwn(OUTCOMES, record.outcome)
      && hasOwn(RECURRENCES, record.recurrence)
      && hasOwn(PURCHASES, record.purchase)
      && Number.isFinite(Date.parse(record.createdAt));
  }

  function pruneRecords(records, nowValue = new Date()) {
    const now = nowValue instanceof Date ? nowValue : new Date(nowValue);
    const cutoff = now.getTime() - TTL_DAYS * DAY_MS;
    const byId = new Map();
    (Array.isArray(records) ? records : []).forEach((record) => {
      if (!isValidRecord(record)) return;
      const created = Date.parse(record.createdAt);
      if (created < cutoff || created > now.getTime() + DAY_MS) return;
      const previous = byId.get(record.id);
      if (!previous || Date.parse(previous.createdAt) < created) byId.set(record.id, { ...record });
    });
    return [...byId.values()]
      .sort((a, b) => Date.parse(b.createdAt) - Date.parse(a.createdAt))
      .slice(0, MAX_RECORDS);
  }

  function upsertRecord(records, record, nowValue = new Date()) {
    return pruneRecords([record, ...(Array.isArray(records) ? records : [])], nowValue);
  }

  function percent(part, total) {
    return total ? Math.round((part / total) * 100) : 0;
  }

  function summarizeRecords(records, nowValue = new Date()) {
    const now = nowValue instanceof Date ? nowValue : new Date(nowValue);
    const clean = pruneRecords(records, now);
    const resolved = clean.filter((record) => record.outcome === 'resolved').length;
    const noPurchase = clean.filter((record) => record.purchase === 'no_purchase' || record.purchase === 'existing' || ['official_channel', 'maintenance', 'existing_equipment'].includes(record.action)).length;
    const repeated = clean.filter((record) => record.recurrence === 'multiple').length;
    const unresolved = clean.filter((record) => record.outcome === 'unresolved' || record.outcome === 'partial').length;
    const due = clean.filter((record) => record.dueAt && Date.parse(record.dueAt) <= now.getTime()).length;
    const categoryCounts = clean.reduce((acc, record) => {
      acc[record.category] = (acc[record.category] || 0) + 1;
      return acc;
    }, {});
    const topCategory = Object.keys(categoryCounts).sort((a, b) => categoryCounts[b] - categoryCounts[a])[0] || null;
    return {
      total: clean.length,
      resolved,
      noPurchase,
      repeated,
      unresolved,
      due,
      resolutionRate: percent(resolved, clean.length),
      noPurchaseRate: percent(noPurchase, clean.length),
      recurrenceRate: percent(repeated, clean.length),
      topCategory,
      topCategoryLabel: topCategory ? CATEGORIES[topCategory].label : 'Henüz kayıt yok'
    };
  }

  function yyyymmdd(value) {
    const date = value instanceof Date ? value : new Date(value);
    return `${date.getUTCFullYear()}${String(date.getUTCMonth() + 1).padStart(2, '0')}${String(date.getUTCDate()).padStart(2, '0')}`;
  }

  function escapeIcs(value) {
    return String(value || '').replace(/\\/g, '\\\\').replace(/\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;');
  }

  function buildCalendar(record, origin = 'https://alo186.com') {
    if (!isValidRecord(record) || !record.dueAt) return '';
    const start = yyyymmdd(record.dueAt);
    const end = yyyymmdd(addDays(new Date(record.dueAt), 1));
    const route = `${String(origin).replace(/\/$/, '')}${record.followupRoute}`;
    const description = `${CATEGORIES[record.category].label} sonucu yeniden kontrol edin. Sonuç: ${OUTCOMES[record.outcome]}. ALO186 kişisel veri veya resmî kayıt tutmaz. ${route}`;
    return [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Solution Outcome Follow-up//TR',
      'CALSCALE:GREGORIAN',
      'METHOD:PUBLISH',
      'BEGIN:VEVENT',
      `UID:${escapeIcs(record.id)}@alo186.com`,
      `DTSTAMP:${yyyymmdd(new Date())}T000000Z`,
      `DTSTART;VALUE=DATE:${start}`,
      `DTEND;VALUE=DATE:${end}`,
      'SUMMARY:ALO186 elektrik çözümünü yeniden kontrol et',
      `DESCRIPTION:${escapeIcs(description)}`,
      `URL:${escapeIcs(route)}`,
      'TRANSP:TRANSPARENT',
      'END:VEVENT',
      'END:VCALENDAR',
      ''
    ].join('\r\n');
  }

  function exportPayload(records, nowValue = new Date()) {
    const now = nowValue instanceof Date ? nowValue : new Date(nowValue);
    const clean = pruneRecords(records, now);
    return {
      schema: 'alo186-solution-outcomes-v1',
      exportedAt: now.toISOString(),
      privacy: 'Kişisel veri, serbest metin, adres, abonelik, ürün modeli, fiyat veya satıcı içermez.',
      summary: summarizeRecords(clean, now),
      records: clean
    };
  }

  return {
    VERSION,
    MAX_RECORDS,
    TTL_DAYS,
    SOURCES,
    CATEGORIES,
    ACTIONS,
    OUTCOMES,
    RECURRENCES,
    PURCHASES,
    sanitizeInput,
    deriveDecision,
    normalizeRecord,
    isValidRecord,
    pruneRecords,
    upsertRecord,
    summarizeRecords,
    buildCalendar,
    exportPayload
  };
});
