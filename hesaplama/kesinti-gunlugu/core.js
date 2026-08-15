(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.ALO186OutageJournalCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const VALID_KINDS = new Set(['planned', 'unplanned', 'unknown']);
  const VALID_SCOPES = new Set(['street', 'building', 'unit', 'unknown']);
  const VALID_USAGE = new Set(['home', 'site', 'business', 'hotel']);
  const VALID_VOLTAGE = new Set(['ag', 'og', 'unknown']);
  const VALID_AREA = new Set(['inside', 'outside', 'unknown']);

  const EPDK_THRESHOLDS = Object.freeze({
    inside: {
      ag: { unplanned: { hours: 48, count: 56 }, planned: { hours: 24, count: 6 } },
      og: { unplanned: { hours: 24, count: 56 }, planned: { hours: 16, count: 4 } }
    },
    outside: {
      ag: { unplanned: { hours: 72, count: 72 }, planned: { hours: 32, count: 8 } },
      og: { unplanned: { hours: 36, count: 72 }, planned: { hours: 24, count: 6 } }
    }
  });

  function clampInteger(value, min, max) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return min;
    return Math.min(max, Math.max(min, Math.round(numeric)));
  }

  function isIsoDate(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const date = new Date(`${value}T00:00:00Z`);
    return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
  }

  function normalizeEntry(raw) {
    if (!raw || !isIsoDate(raw.date)) throw new Error('Geçerli bir tarih girin.');
    const durationMinutes = clampInteger(raw.durationMinutes, 1, 43200);
    return {
      id: String(raw.id || `${raw.date}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`),
      date: raw.date,
      durationMinutes,
      kind: VALID_KINDS.has(raw.kind) ? raw.kind : 'unknown',
      scope: VALID_SCOPES.has(raw.scope) ? raw.scope : 'unknown',
      officialRecord: Boolean(raw.officialRecord),
      deviceDamage: Boolean(raw.deviceDamage),
      createdAt: typeof raw.createdAt === 'string' ? raw.createdAt : new Date().toISOString()
    };
  }

  function normalizeSettings(raw) {
    const priorities = raw && raw.priorities ? raw.priorities : {};
    return {
      usage: VALID_USAGE.has(raw && raw.usage) ? raw.usage : 'home',
      voltage: VALID_VOLTAGE.has(raw && raw.voltage) ? raw.voltage : 'unknown',
      area: VALID_AREA.has(raw && raw.area) ? raw.area : 'unknown',
      priorities: {
        internet: Boolean(priorities.internet),
        lighting: Boolean(priorities.lighting),
        cold: Boolean(priorities.cold),
        pump: Boolean(priorities.pump),
        medical: Boolean(priorities.medical)
      }
    };
  }

  function sum(items, selector) {
    return items.reduce((total, item) => total + selector(item), 0);
  }

  function getThreshold(settings, kind) {
    if (!settings || settings.area === 'unknown' || settings.voltage === 'unknown') return null;
    return EPDK_THRESHOLDS[settings.area][settings.voltage][kind] || null;
  }

  function evaluateAnnualSignal(kindEntries, threshold) {
    if (!threshold) return { status: 'unknown', durationExceeded: false, countExceeded: false, threshold: null };
    const durationHours = sum(kindEntries, (entry) => entry.durationMinutes) / 60;
    const count = kindEntries.length;
    const durationExceeded = durationHours > threshold.hours;
    const countExceeded = count > threshold.count;
    return {
      status: durationExceeded || countExceeded ? 'review' : 'below',
      durationExceeded,
      countExceeded,
      threshold,
      actual: { hours: durationHours, count }
    };
  }

  function summarize(entries, options) {
    const settings = normalizeSettings(options && options.settings ? options.settings : {});
    const year = clampInteger(options && options.year ? options.year : new Date().getFullYear(), 2000, 2100);
    const normalized = (entries || []).map(normalizeEntry).filter((entry) => Number(entry.date.slice(0, 4)) === year);
    const byKind = {
      planned: normalized.filter((entry) => entry.kind === 'planned'),
      unplanned: normalized.filter((entry) => entry.kind === 'unplanned'),
      unknown: normalized.filter((entry) => entry.kind === 'unknown')
    };
    const totalMinutes = sum(normalized, (entry) => entry.durationMinutes);
    const longestMinutes = normalized.reduce((max, entry) => Math.max(max, entry.durationMinutes), 0);
    const longDurationEntries = normalized.filter((entry) => entry.durationMinutes > 720);
    const damageEntries = normalized.filter((entry) => entry.deviceDamage);
    const officialRecordCount = normalized.filter((entry) => entry.officialRecord).length;
    const annualSignals = {
      planned: evaluateAnnualSignal(byKind.planned, getThreshold(settings, 'planned')),
      unplanned: evaluateAnnualSignal(byKind.unplanned, getThreshold(settings, 'unplanned'))
    };
    return {
      year,
      settings,
      entries: normalized.sort((a, b) => b.date.localeCompare(a.date)),
      count: normalized.length,
      totalMinutes,
      totalHours: totalMinutes / 60,
      longestMinutes,
      plannedCount: byKind.planned.length,
      unplannedCount: byKind.unplanned.length,
      unknownCount: byKind.unknown.length,
      plannedMinutes: sum(byKind.planned, (entry) => entry.durationMinutes),
      unplannedMinutes: sum(byKind.unplanned, (entry) => entry.durationMinutes),
      longDurationEntries,
      damageEntries,
      officialRecordCount,
      annualSignals,
      hasCompensationReviewSignal:
        longDurationEntries.length > 0 || annualSignals.planned.status === 'review' || annualSignals.unplanned.status === 'review'
    };
  }

  function buildResilienceRoutes(summary) {
    const routes = [];
    const settings = summary.settings;
    const priorities = settings.priorities;
    const medical = priorities.medical;

    if (medical) {
      routes.push({
        id: 'medical-plan',
        label: 'Tıbbi cihaz üreticisi ve sağlık ekibiyle acil güç planını doğrulayın',
        href: 'https://alo186.com/hesaplama/kesinti-hazirlik-plani/',
        commercial: false,
        reason: 'Tıbbi yüklerde tüketici ürünü yönlendirmesi yerine üretici ve sağlık ekibi planı gerekir.'
      });
      return { commercialSuppressed: true, routes, showProductCenter: false };
    }

    if (priorities.internet && (summary.count > 0 || summary.totalMinutes >= 30)) {
      routes.push({
        id: 'modem-backup',
        label: 'Modem ve ONT için gerekli Wh, voltaj ve akımı hesaplayın',
        href: 'https://alo186.com/hesaplama/modem-internet-yedekleme/',
        commercial: false,
        reason: 'İnternet önceliği seçildi; ürün aramasından önce gerçek DC yükü hesaplanmalıdır.'
      });
    }

    if ((priorities.lighting || priorities.cold) && (summary.totalMinutes >= 120 || summary.count >= 2)) {
      routes.push({
        id: 'ups-duration',
        label: 'Kritik yüklerin UPS veya power station süresini hesaplayın',
        href: 'https://alo186.com/hesaplama/ups-suresi/',
        commercial: false,
        reason: 'Tekrarlayan veya uzun kesinti kaydı, enerji kapasitesi hesabını anlamlı hale getiriyor.'
      });
    }

    if ((priorities.pump || settings.usage === 'business' || settings.usage === 'hotel' || settings.usage === 'site') && summary.longestMinutes >= 180) {
      routes.push({
        id: 'generator-size',
        label: 'Sürekli ve kalkış gücüyle jeneratör ön seçimi yapın',
        href: 'https://alo186.com/hesaplama/jenerator-gucu-secimi/',
        commercial: false,
        reason: 'Pompa, işletme veya ortak alan yüklerinde kalkış gücü ve transfer düzeni ayrıca değerlendirilmelidir.'
      });
    }

    if (summary.damageEntries.length > 0) {
      routes.push({
        id: 'surge-risk',
        label: 'Parafudr ve katmanlı aşırı gerilim koruması riskini değerlendirin',
        href: 'https://alo186.com/hesaplama/parafudr-risk-testi/',
        commercial: false,
        reason: 'Cihaz hasarı işaretlendi; ürün almadan önce hasarın kaynağı ve koruma katmanları ayrılmalıdır.'
      });
    }

    return {
      commercialSuppressed: false,
      routes,
      showProductCenter: routes.length > 0 && (summary.totalMinutes >= 120 || summary.count >= 2 || summary.damageEntries.length > 0)
    };
  }

  function buildEvidenceChecklist(summary) {
    const items = [
      'Kesintinin başlangıç ve bitiş tarih-saatini kaydedin.',
      'Yetkili dağıtım şirketinin planlı kesinti veya arıza ekranını kontrol edin.',
      '186 veya resmî dijital kanaldan işlem yaptıysanız başvuru kaydını saklayın.',
      'Ekran görüntüsü, SMS veya resmî duyuruyu olay tarihiyle birlikte arşivleyin.'
    ];
    if (summary.damageEntries.length > 0) {
      items.push('Hasarlı cihazı çalıştırmayı denemeyin; yetkili servisten arıza nedeni ve onarım bedelini gösteren rapor alın.');
      items.push('Cihaz faturası, servis raporu ve olay kayıtlarını birlikte saklayın; EPDK tüketici bilgisinde cihaz hasarı talebi için 30 günlük süre düzenlenir.');
    }
    if (summary.longDurationEntries.length > 0) {
      items.push('12 saati aşan kayıt için dağıtım şirketinin uzun süreli kesinti tazminatı sürecini resmî kanaldan kontrol edin.');
    }
    items.push('Bu günlük yalnız sizin girdiğiniz kayıtlara dayanır; resmî kesinti veya tazminat kararı değildir.');
    return items;
  }

  function createExport(entries, settings) {
    return {
      schemaVersion: 1,
      exportedAt: new Date().toISOString(),
      privacy: 'Kayıt; ad, adres, abonelik numarası, telefon, e-posta veya serbest metin içermez.',
      settings: normalizeSettings(settings || {}),
      entries: (entries || []).map(normalizeEntry).map((entry) => ({
        date: entry.date,
        durationMinutes: entry.durationMinutes,
        kind: entry.kind,
        scope: entry.scope,
        officialRecord: entry.officialRecord,
        deviceDamage: entry.deviceDamage
      }))
    };
  }

  return {
    EPDK_THRESHOLDS,
    normalizeEntry,
    normalizeSettings,
    summarize,
    buildResilienceRoutes,
    buildEvidenceChecklist,
    createExport
  };
});
