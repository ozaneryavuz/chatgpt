(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.AloContinuityPassport = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const VERSION = 1;
  const STORAGE_MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000;
  const FACILITY_TYPES = Object.freeze(["hotel", "site", "business", "other"]);
  const STATUS_VALUES = Object.freeze({ current: 1, due: 0.65, planned: 0.35, missing: 0 });
  const STATUS_LABELS = Object.freeze({
    current: "Güncel",
    due: "Yenileme zamanı",
    planned: "Planlandı",
    missing: "Yok"
  });

  const CRITICAL_LOADS = Object.freeze([
    { id: "life-safety", label: "Yangın, acil aydınlatma ve tahliye" },
    { id: "it-comms", label: "İletişim, internet, sunucu ve erişim" },
    { id: "cold-chain", label: "Soğuk oda, gıda, ilaç veya proses sıcaklığı" },
    { id: "water-pumps", label: "Su, hidrofor, atık su ve drenaj" },
    { id: "security", label: "Güvenlik, kartlı geçiş ve kamera" },
    { id: "operations", label: "Operasyonu durduran üretim veya hizmet yükü" },
    { id: "elevator-access", label: "Asansör ve erişilebilirlik" },
    { id: "other-critical", label: "Diğer kritik elektrik yükü" }
  ]);

  const BACKUP_SOURCES = Object.freeze([
    { id: "generator", label: "Jeneratör" },
    { id: "ups", label: "UPS" },
    { id: "battery-inverter", label: "Batarya / inverter" },
    { id: "power-station", label: "Taşınabilir güç istasyonu" },
    { id: "dual-feed", label: "İkinci besleme / alternatif şebeke" },
    { id: "none", label: "Yedek kaynak yok" }
  ]);

  const EVIDENCE_FIELDS = Object.freeze([
    {
      id: "critical_load_inventory",
      title: "Kritik yük envanteri",
      weight: 14,
      basePriority: "P0",
      reviewDays: 180,
      action: "Kritik yükleri P1/P2/P3 olarak sınıflandırın; güç, besleme noktası, kabul edilebilir kesinti ve hedef otonomiyi kaydedin."
    },
    {
      id: "single_line_diagram",
      title: "Tek hat şeması veya besleme ilişkisi",
      weight: 11,
      basePriority: "P1",
      reviewDays: 365,
      action: "Ana besleme, transfer, jeneratör/UPS ve kritik panoları gösteren sürümlü tek hat dokümanını saha etiketleriyle eşleştirin."
    },
    {
      id: "emergency_contacts",
      title: "Acil iletişim ve görev listesi",
      weight: 8,
      basePriority: "P1",
      reviewDays: 90,
      action: "112, 186, yönetim, teknik ekip ve yetkili servis ayrımını; birincil ve yedek görev sahipleriyle çevrimdışı erişilebilir hâle getirin."
    },
    {
      id: "capacity_record",
      title: "Yedek güç kapasite ve otonomi kaydı",
      weight: 14,
      basePriority: "P0",
      reviewDays: 180,
      action: "Sürekli ve kalkış yükünü, gerçek kW/kVA/Wh kapasitesini, yakıt veya batarya rezervini ve hedef çalışma süresini doğrulayın."
    },
    {
      id: "generator_ups_test",
      title: "Jeneratör / UPS / batarya test kaydı",
      weight: 12,
      basePriority: "P0",
      reviewDays: 90,
      action: "Yedek kaynağı yalnız alarm ekranıyla değil tarih, yük, süre, sonuç ve uygunsuzluk içeren kayıtlı test ile doğrulayın."
    },
    {
      id: "transfer_test",
      title: "Transfer ve geri dönüş test kaydı",
      weight: 11,
      basePriority: "P0",
      reviewDays: 90,
      action: "Transfer süresini, başarısız geçişi, nötr/faz davranışını ve normal kaynağa dönüşü yetkili ekip gözetiminde kaydedin."
    },
    {
      id: "protection_test",
      title: "Koruma ve açma testleri",
      weight: 9,
      basePriority: "P1",
      reviewDays: 180,
      action: "RCD, şalter, koruma rölesi, SPD göstergesi ve kritik devre korumalarını üretici ve mevzuat kapsamına göre test edin."
    },
    {
      id: "earthing_measurement",
      title: "Topraklama ve süreklilik ölçümü",
      weight: 8,
      basePriority: "P1",
      reviewDays: 365,
      action: "Topraklama direnci tek başına yeterli kabul edilmeden PE sürekliliği, RCD açma süresi ve ölçüm koşullarını kayıt altına alın."
    },
    {
      id: "outage_log",
      title: "Kesinti ve olay günlüğü",
      weight: 7,
      basePriority: "P2",
      reviewDays: 90,
      action: "Başlangıç, kapsam, müdahale, 186/servis kayıt numarası, maliyet, geçici çözüm ve kapanış bilgisini standartlaştırın."
    },
    {
      id: "recovery_drill",
      title: "Kurtarma tatbikatı ve yönetim gözden geçirmesi",
      weight: 6,
      basePriority: "P2",
      reviewDays: 365,
      action: "Masa başı veya kontrollü tatbikatta ilk 5/15/60 dakika görevlerini ölçün; bulguları sorumlu ve hedef tarihle kapatın."
    }
  ]);

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function uniqueAllowed(values, catalogue) {
    const allowed = new Set(catalogue.map((item) => item.id));
    return [...new Set(Array.isArray(values) ? values.filter((item) => allowed.has(item)) : [])];
  }

  function safeFacility(value) {
    return FACILITY_TYPES.includes(value) ? value : "other";
  }

  function validStatus(value) {
    return Object.prototype.hasOwnProperty.call(STATUS_VALUES, value) ? value : "missing";
  }

  function normalizeEvidence(input) {
    const source = input && typeof input === "object" ? input : {};
    const output = {};
    EVIDENCE_FIELDS.forEach((field) => {
      output[field.id] = validStatus(source[field.id]);
    });
    return output;
  }

  function priorityRank(priority) {
    return { P0: 0, P1: 1, P2: 2 }[priority] ?? 9;
  }

  function effectivePriority(field, status) {
    if (status === "current") return null;
    if (status === "due") {
      if (field.basePriority === "P0") return "P1";
      if (field.basePriority === "P1") return "P2";
      return "P2";
    }
    if (status === "planned") return field.basePriority;
    return field.basePriority;
  }

  function scoreEvidence(evidence) {
    const normalized = normalizeEvidence(evidence);
    const totalWeight = EVIDENCE_FIELDS.reduce((sum, field) => sum + field.weight, 0);
    const earned = EVIDENCE_FIELDS.reduce(
      (sum, field) => sum + field.weight * STATUS_VALUES[normalized[field.id]],
      0
    );
    return Math.round((earned / totalWeight) * 100);
  }

  function classification(score) {
    if (score >= 85) return { id: "controlled", label: "Kanıt kontrollü", tone: "good", summary: "Temel kanıt seti güçlü; yenileme tarihlerini ve tatbikat bulgularını yönetin." };
    if (score >= 65) return { id: "developing", label: "Gelişen", tone: "warn", summary: "Çekirdek kayıtlar var; P0/P1 boşluklarını kapanış kanıtıyla tamamlayın." };
    if (score >= 40) return { id: "fragile", label: "Kırılgan", tone: "danger", summary: "Kritik kanıtlar eksik veya güncel değil; önce P0 maddelerini tamamlayın." };
    return { id: "uncontrolled", label: "Kontrolsüz", tone: "danger", summary: "Kesinti sırasında karar ve kurtarma büyük ölçüde kişiye bağlı; temel kanıt dosyasını oluşturun." };
  }

  function addDays(date, days) {
    return new Date(date.getTime() + days * 24 * 60 * 60 * 1000);
  }

  function nextReviewDate(evidence, now) {
    const base = now instanceof Date && !Number.isNaN(now.getTime()) ? now : new Date();
    const normalized = normalizeEvidence(evidence);
    const candidates = EVIDENCE_FIELDS.map((field) => {
      const status = normalized[field.id];
      if (status === "missing") return addDays(base, 30);
      if (status === "planned") return addDays(base, 60);
      if (status === "due") return addDays(base, 30);
      return addDays(base, field.reviewDays);
    });
    return new Date(Math.min(...candidates.map((item) => item.getTime())));
  }

  function createGaps(evidence) {
    const normalized = normalizeEvidence(evidence);
    return EVIDENCE_FIELDS.map((field) => {
      const status = normalized[field.id];
      const priority = effectivePriority(field, status);
      if (!priority) return null;
      return {
        id: field.id,
        title: field.title,
        status,
        statusLabel: STATUS_LABELS[status],
        priority,
        action: field.action,
        weight: field.weight
      };
    }).filter(Boolean).sort((a, b) => {
      const priorityDiff = priorityRank(a.priority) - priorityRank(b.priority);
      if (priorityDiff) return priorityDiff;
      const statusRank = { missing: 0, planned: 1, due: 2 };
      return statusRank[a.status] - statusRank[b.status] || b.weight - a.weight;
    });
  }

  function backupAvailable(sources) {
    const safe = uniqueAllowed(sources, BACKUP_SOURCES);
    return safe.some((item) => item !== "none");
  }

  function evaluatePassport(input, options) {
    const data = input && typeof input === "object" ? input : {};
    const immediateDanger = data.immediateDanger === true;
    if (immediateDanger) {
      return {
        valid: false,
        emergency: true,
        revenueAllowed: false,
        route: "112",
        errors: []
      };
    }

    const facilityType = safeFacility(data.facilityType);
    const criticalLoads = uniqueAllowed(data.criticalLoads, CRITICAL_LOADS);
    const backupSources = uniqueAllowed(data.backupSources, BACKUP_SOURCES);
    const evidence = normalizeEvidence(data.evidence);
    const errors = [];
    if (!criticalLoads.length) errors.push("En az bir kritik yük kategorisi seçin veya kritik yük bulunmadığını doğrulayın.");
    if (!backupSources.length) errors.push("Mevcut yedek kaynak durumunu seçin.");

    const score = scoreEvidence(evidence);
    const gaps = createGaps(evidence);
    const hasCriticalLoads = criticalLoads.length > 0;
    const hasBackup = backupAvailable(backupSources);
    const structuralP0 = [];
    if (hasCriticalLoads && !hasBackup) {
      structuralP0.push({
        id: "critical_load_without_backup",
        title: "Kritik yük var, yedek kaynak yok",
        status: "missing",
        statusLabel: "Yok",
        priority: "P0",
        action: "Önce kabul edilebilir kesinti süresini ve kritik yük gücünü doğrulayın; satın alma kararı vermeden teknik seçenek ve geçiş ihtiyacını yetkili uzmanla planlayın.",
        weight: 20
      });
    }
    if (hasCriticalLoads && evidence.critical_load_inventory === "missing") {
      structuralP0.push({
        id: "critical_load_not_documented",
        title: "Kritik yük seçildi fakat envanter kanıtı yok",
        status: "missing",
        statusLabel: "Yok",
        priority: "P0",
        action: "Kritik yüklerin güç, öncelik, besleme noktası ve hedef otonomi kaydını oluşturun.",
        weight: 18
      });
    }

    const allGaps = [...structuralP0, ...gaps].filter(
      (item, index, array) => array.findIndex((other) => other.id === item.id) === index
    ).sort((a, b) => priorityRank(a.priority) - priorityRank(b.priority) || b.weight - a.weight);

    const now = options && options.now ? new Date(options.now) : new Date();
    const lifeSupport = data.lifeSupport === true;
    return {
      valid: errors.length === 0,
      emergency: false,
      revenueAllowed: true,
      errors,
      facilityType,
      criticalLoads,
      backupSources,
      evidence,
      score,
      classification: classification(score),
      gaps: allGaps,
      priorities: {
        P0: allGaps.filter((item) => item.priority === "P0"),
        P1: allGaps.filter((item) => item.priority === "P1"),
        P2: allGaps.filter((item) => item.priority === "P2")
      },
      nextReviewAt: nextReviewDate(evidence, now).toISOString(),
      professionalPlanRequired: lifeSupport || structuralP0.length > 0 || score < 40,
      lifeSupportSelected: lifeSupport,
      panelRecommended: score < 85 || allGaps.length > 0
    };
  }

  function createExport(result, options) {
    if (!result || !result.valid || result.emergency) throw new Error("Geçerli pasaport sonucu gerekli.");
    const generatedAt = options && options.generatedAt ? new Date(options.generatedAt) : new Date();
    const importedMaturity = options && options.importedMaturity && typeof options.importedMaturity === "object"
      ? sanitizeMaturityHandoff(options.importedMaturity)
      : null;
    return {
      schema: "https://alo186.com/schemas/electric-continuity-passport-v1.json",
      schemaVersion: VERSION,
      passportId: `alo186-passport-${generatedAt.getTime()}-${result.score}-${result.facilityType}`,
      generatedAt: generatedAt.toISOString(),
      nextReviewAt: result.nextReviewAt,
      facilityType: result.facilityType,
      criticalLoadCategories: [...result.criticalLoads],
      backupSourceClasses: [...result.backupSources],
      evidence: EVIDENCE_FIELDS.map((field) => ({
        id: field.id,
        title: field.title,
        status: result.evidence[field.id],
        statusLabel: STATUS_LABELS[result.evidence[field.id]],
        weight: field.weight
      })),
      evidenceScore: result.score,
      evidenceBand: result.classification.id,
      priorityGaps: result.gaps.map((item) => ({
        id: item.id,
        priority: item.priority,
        status: item.status,
        action: item.action
      })),
      importedMaturity,
      handoff: {
        target: "alo186-continuity-panel",
        compatibleVersion: 1,
        suggestedRoute: "https://alo186.com/isletme-surekliligi?passport=1"
      },
      privacy: {
        containsPersonalData: false,
        personalFieldsCollected: [],
        freeTextIncluded: false,
        lifeSupportFlagIncluded: false,
        immediateDangerFlagIncluded: false
      },
      disclaimer: "Ücretsiz ön değerlendirme ve kanıt envanteridir; sertifika, proje, uygunluk raporu veya resmî denetim değildir."
    };
  }

  function sanitizeMaturityHandoff(payload) {
    if (!payload || typeof payload !== "object") return null;
    const score = clamp(Math.round(Number(payload.score) || 0), 0, 100);
    const facilityType = safeFacility(payload.facilityType);
    const dimensions = Array.isArray(payload.dimensions)
      ? payload.dimensions.slice(0, 12).map((item) => ({
          id: String(item && item.id || "").replace(/[^a-z0-9_-]/gi, "").slice(0, 50),
          score: clamp(Math.round(Number(item && item.score) || 0), 0, 100)
        })).filter((item) => item.id)
      : [];
    return {
      source: "alo186-continuity-maturity-v1",
      facilityType,
      score,
      band: String(payload.band || "").replace(/[<>]/g, "").slice(0, 80),
      dimensions,
      privacy: { containsPersonalData: false }
    };
  }

  function sanitizeStorage(input, savedAt) {
    const data = input && typeof input === "object" ? input : {};
    const timestamp = savedAt ? new Date(savedAt) : new Date();
    return {
      version: VERSION,
      savedAt: timestamp.toISOString(),
      expiresAt: new Date(timestamp.getTime() + STORAGE_MAX_AGE_MS).toISOString(),
      facilityType: safeFacility(data.facilityType),
      criticalLoads: uniqueAllowed(data.criticalLoads, CRITICAL_LOADS),
      backupSources: uniqueAllowed(data.backupSources, BACKUP_SOURCES),
      evidence: normalizeEvidence(data.evidence),
      privacy: {
        containsPersonalData: false,
        lifeSupportFlagIncluded: false,
        immediateDangerFlagIncluded: false
      }
    };
  }

  function isStoredPayloadFresh(payload, now) {
    if (!payload || payload.version !== VERSION || !payload.expiresAt) return false;
    const current = now ? new Date(now) : new Date();
    const expiry = new Date(payload.expiresAt);
    return !Number.isNaN(expiry.getTime()) && expiry.getTime() > current.getTime();
  }

  return Object.freeze({
    VERSION,
    STORAGE_MAX_AGE_MS,
    FACILITY_TYPES,
    STATUS_VALUES,
    STATUS_LABELS,
    CRITICAL_LOADS,
    BACKUP_SOURCES,
    EVIDENCE_FIELDS,
    normalizeEvidence,
    scoreEvidence,
    classification,
    nextReviewDate,
    evaluatePassport,
    createExport,
    sanitizeMaturityHandoff,
    sanitizeStorage,
    isStoredPayloadFresh
  });
});
