(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.AloContinuityPassport = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const SCHEMA_VERSION = "1.0.0";
  const STORAGE_VERSION = 1;
  const STORAGE_MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000;
  const STATUS_VALUES = Object.freeze({ current: 1, due: 0.6, planned: 0.3, missing: 0 });
  const FACILITY_TYPES = Object.freeze(["hotel", "site", "business", "other"]);
  const PRIORITY_ORDER = Object.freeze({ P0: 0, P1: 1, P2: 2 });

  const CRITICAL_LOAD_CATEGORIES = Object.freeze([
    { id: "safety", label: "Yangın, acil aydınlatma ve güvenlik" },
    { id: "communications", label: "İletişim, internet ve bilgi sistemleri" },
    { id: "refrigeration", label: "Soğutma, gıda veya ilaç muhafazası" },
    { id: "water-pumps", label: "Su, hidrofor, drenaj veya pompa sistemleri" },
    { id: "access", label: "Geçiş, kartlı erişim, kapı veya bariyer" },
    { id: "operations", label: "Operasyon, üretim veya hizmet sürekliliği" },
    { id: "elevator", label: "Asansör ve tahliye destek sistemleri" },
    { id: "other-critical", label: "Diğer kritik yük kategorisi" }
  ]);

  const BACKUP_SOURCE_CLASSES = Object.freeze([
    { id: "generator", label: "Jeneratör" },
    { id: "ups", label: "UPS" },
    { id: "battery-inverter", label: "İnverter ve sabit batarya" },
    { id: "power-station", label: "Taşınabilir güç istasyonu" },
    { id: "solar-storage", label: "GES ve enerji depolama" },
    { id: "temporary", label: "Geçici veya kiralık yedek kaynak" }
  ]);

  const EVIDENCE = Object.freeze([
    {
      id: "critical-load-inventory",
      label: "Kritik yük envanteri",
      description: "Kesintide çalışması gereken yükler, öncelikleri ve hedef çalışma süreleri kayıtlı.",
      weight: 14,
      priority: "P0",
      reviewMonths: 6,
      action: "P1/P2/P3 kritik yük listesini, yaklaşık güçleri ve hedef otonomiyi tek tabloda oluşturun."
    },
    {
      id: "single-line-diagram",
      label: "Tek hat veya besleme şeması",
      description: "Ana kaynak, transfer, kritik panolar ve yedek beslemeler güncel dokümanda gösteriliyor.",
      weight: 10,
      priority: "P1",
      reviewMonths: 12,
      action: "Gerçek pano ve devre adlarıyla güncel tek hat veya eşdeğer besleme ilişkisi dokümanı hazırlatın."
    },
    {
      id: "emergency-contacts",
      label: "Acil iletişim ve görev listesi",
      description: "112, 186, yönetim ve yetkili teknik ekip ayrımı çevrimdışı erişilebilir durumda.",
      weight: 8,
      priority: "P1",
      reviewMonths: 6,
      action: "İlk 5/15/60 dakika görevlerini ve resmî/teknik iletişim rotalarını çevrimdışı erişilebilir yapın."
    },
    {
      id: "capacity-record",
      label: "Yedek güç kapasite kaydı",
      description: "Sürekli yük, kalkış gücü, kVA/kW, yakıt veya batarya otonomisi doğrulanmış.",
      weight: 12,
      priority: "P0",
      reviewMonths: 6,
      action: "Kritik yük toplamı, motor kalkışları, rezerv ve gerçekçi otonomi için kapasite hesabını doğrulatın."
    },
    {
      id: "generator-ups-test",
      label: "Jeneratör, UPS veya batarya testi",
      description: "Son test tarihi, yöntem, yük, süre ve sonuç kayıtlı.",
      weight: 12,
      priority: "P0",
      reviewMonths: 3,
      action: "Yedek kaynak için tarih, yük, süre, alarm ve başarısızlık alanlarını içeren kayıtlı test uygulayın."
    },
    {
      id: "transfer-test",
      label: "Transfer sistemi testi",
      description: "Otomatik veya manuel transfer güvenli kapsamda ve gerçekçi yükle test edilmiş.",
      weight: 10,
      priority: "P0",
      reviewMonths: 3,
      action: "Transfer gecikmesini, başarısız geçişi ve geri dönüşü güvenli prosedürle kayıt altına alın."
    },
    {
      id: "protection-test",
      label: "Koruma sistemi testi",
      description: "RCD, şalter, SPD, röle veya ilgili koruma fonksiyonlarının test kanıtı bulunuyor.",
      weight: 10,
      priority: "P1",
      reviewMonths: 6,
      action: "Koruma cihazlarını yetkili test cihazı ve uygun prosedürle doğrulatıp sonuçları saklayın."
    },
    {
      id: "grounding-measurement",
      label: "Topraklama ölçümü",
      description: "Ölçüm tarihi, yöntem, ölçüm noktası, sonuç ve değerlendirme kayıtlı.",
      weight: 8,
      priority: "P1",
      reviewMonths: 12,
      action: "Topraklama ve koruma sürekliliğini ölçüm noktası ve yöntem bilgisiyle kayıt altına alın."
    },
    {
      id: "outage-log",
      label: "Kesinti ve olay günlüğü",
      description: "Başlangıç, kapsam, müdahale, resmî kayıt ve kapanış zaman çizelgesi tutuluyor.",
      weight: 8,
      priority: "P2",
      reviewMonths: 3,
      action: "Her kesinti için standart zaman çizelgesi, 186/servis kayıt numarası ve kapanış sonucu tutun."
    },
    {
      id: "recovery-drill",
      label: "Kurtarma tatbikatı",
      description: "Teknik ve operasyon ekipleriyle kesinti/kurtarma senaryosu uygulanmış ve eksikler kapatılmış.",
      weight: 8,
      priority: "P1",
      reviewMonths: 12,
      action: "Masa başı veya kontrollü saha tatbikatı yapın; süre, görev ve iletişim eksiklerini aksiyona dönüştürün."
    }
  ]);

  function safeArray(value, allowed) {
    const source = Array.isArray(value) ? value : [];
    const allowedSet = new Set(allowed);
    return Array.from(new Set(source.filter((item) => allowedSet.has(item)))).sort();
  }

  function safeFacilityType(value) {
    return FACILITY_TYPES.includes(value) ? value : "other";
  }

  function safeStatus(value) {
    return Object.prototype.hasOwnProperty.call(STATUS_VALUES, value) ? value : "missing";
  }

  function addDays(date, days) {
    const result = new Date(date.getTime());
    result.setUTCDate(result.getUTCDate() + days);
    return result;
  }

  function addMonths(date, months) {
    const result = new Date(date.getTime());
    result.setUTCMonth(result.getUTCMonth() + months);
    return result;
  }

  function formatDate(date) {
    return date.toISOString().slice(0, 10);
  }

  function classifyScore(score) {
    const value = Math.max(0, Math.min(100, Math.round(Number(score) || 0)));
    if (value < 35) return { id: "insufficient", label: "Kanıt yetersiz", tone: "bad", summary: "Temel kayıt ve test kanıtları eksik; önce P0 boşluklarını kapatın." };
    if (value < 60) return { id: "developing", label: "Gelişiyor", tone: "warn", summary: "Bazı kanıtlar mevcut; güncellik, test ve ortak format boşlukları sürüyor." };
    if (value < 80) return { id: "controlled", label: "Kontrollü", tone: "warn", summary: "Çekirdek kanıt paketi oluşmuş; yenileme ve tatbikat disiplini güçlendirilmeli." };
    if (value < 95) return { id: "strong", label: "Güçlü", tone: "ok", summary: "Kanıt dosyası güçlü; az sayıdaki boşluğu kapatıp periyodik gözden geçirmeyi sürdürün." };
    return { id: "complete", label: "Tam ve güncel", tone: "ok", summary: "Tanımlı on kanıt alanının tamamı güncel. Sonuç sertifika veya uygunluk raporu değildir." };
  }

  function gapDueDays(evidence, status) {
    if (status === "current") return evidence.reviewMonths * 30;
    if (status === "due") return evidence.priority === "P0" ? 7 : 14;
    if (status === "planned") return evidence.priority === "P0" ? 14 : evidence.priority === "P1" ? 30 : 60;
    return evidence.priority === "P0" ? 7 : evidence.priority === "P1" ? 30 : 60;
  }

  function buildGap(evidence, status, now) {
    const dueDays = gapDueDays(evidence, status);
    const statusLabels = {
      due: "Yenileme zamanı",
      planned: "Planlandı",
      missing: "Yok"
    };
    return {
      id: evidence.id,
      label: evidence.label,
      priority: evidence.priority,
      status,
      statusLabel: statusLabels[status] || status,
      action: evidence.action,
      targetDate: formatDate(addDays(now, dueDays)),
      dueInDays: dueDays
    };
  }

  function normalizeEvidenceStatuses(input) {
    const source = input && typeof input === "object" ? input : {};
    const result = {};
    EVIDENCE.forEach((item) => { result[item.id] = safeStatus(source[item.id]); });
    return result;
  }

  function evaluatePassport(input, options) {
    const source = input || {};
    const now = options && options.now ? new Date(options.now) : new Date();
    if (Number.isNaN(now.getTime())) throw new Error("Geçersiz değerlendirme tarihi.");

    if (source.immediateDanger === true) {
      return {
        valid: true,
        emergency: true,
        score: null,
        revenueAllowed: false,
        professionalReviewRequired: true,
        message: "Yangın, duman, elektrik çarpması, kıvılcım veya düşmüş iletken varsa değerlendirmeyi bırakın ve 112'yi arayın."
      };
    }

    const facilityType = safeFacilityType(source.facilityType);
    const criticalLoadCategories = safeArray(
      source.criticalLoadCategories,
      CRITICAL_LOAD_CATEGORIES.map((item) => item.id)
    );
    const backupSourceClasses = safeArray(
      source.backupSourceClasses,
      BACKUP_SOURCE_CLASSES.map((item) => item.id)
    );
    const evidenceStatuses = normalizeEvidenceStatuses(source.evidenceStatuses);

    let earned = 0;
    let possible = 0;
    const evidenceResults = EVIDENCE.map((item) => {
      const status = evidenceStatuses[item.id];
      const points = item.weight * STATUS_VALUES[status];
      earned += points;
      possible += item.weight;
      return {
        id: item.id,
        label: item.label,
        description: item.description,
        weight: item.weight,
        priority: item.priority,
        reviewMonths: item.reviewMonths,
        status,
        statusScore: STATUS_VALUES[status],
        points: Number(points.toFixed(2)),
        nextReviewDate: status === "current" ? formatDate(addMonths(now, item.reviewMonths)) : formatDate(addDays(now, gapDueDays(item, status)))
      };
    });

    const score = Math.round((earned / possible) * 100);
    const gaps = evidenceResults
      .filter((item) => item.status !== "current")
      .map((item) => buildGap(EVIDENCE.find((entry) => entry.id === item.id), item.status, now));

    if (criticalLoadCategories.length > 0 && backupSourceClasses.length === 0) {
      gaps.push({
        id: "critical-load-without-backup",
        label: "Kritik yük için doğrulanmış yedek kaynak yok",
        priority: "P0",
        status: "missing",
        statusLabel: "Yok",
        action: "Kritik yüklerin güç, geçiş süresi ve otonomi ihtiyacına göre yedek kaynak stratejisini profesyonel olarak doğrulatın.",
        targetDate: formatDate(addDays(now, 7)),
        dueInDays: 7
      });
    }

    gaps.sort((a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority] || a.dueInDays - b.dueInDays || a.id.localeCompare(b.id));
    const groupedGaps = { P0: [], P1: [], P2: [] };
    gaps.forEach((gap) => groupedGaps[gap.priority].push(gap));

    const reviewDates = evidenceResults.map((item) => item.nextReviewDate).concat(gaps.map((item) => item.targetDate));
    const nextReviewDate = reviewDates.sort()[0] || formatDate(addDays(now, 90));
    const classification = classifyScore(score);
    const professionalReviewRequired = source.lifeSupportPresent === true || groupedGaps.P0.length > 0 || score < 60;

    return {
      valid: true,
      emergency: false,
      facilityType,
      criticalLoadCategories,
      backupSourceClasses,
      evidenceStatuses,
      evidence: evidenceResults,
      score,
      classification,
      gaps: groupedGaps,
      totalGapCount: gaps.length,
      nextReviewDate,
      professionalReviewRequired,
      lifeSupportPresentAtRuntime: source.lifeSupportPresent === true,
      panelRecommended: score < 95 || gaps.length > 0,
      revenueAllowed: true,
      methodology: {
        version: SCHEMA_VERSION,
        evidenceCount: EVIDENCE.length,
        scoring: "weighted-current-1-due-0.6-planned-0.3-missing-0",
        certification: false
      }
    };
  }

  function sanitizeMaturityReference(input) {
    if (!input || typeof input !== "object") return null;
    const score = Number(input.score);
    if (!Number.isFinite(score) || score < 0 || score > 100) return null;
    return {
      score: Math.round(score),
      band: String(input.band || input.maturityBand || "").slice(0, 80),
      generatedAt: typeof input.generatedAt === "string" ? input.generatedAt.slice(0, 40) : null,
      sourceSchemaVersion: String(input.schemaVersion || input.version || "unknown").slice(0, 30)
    };
  }

  function parseMaturityImport(payload) {
    if (!payload || typeof payload !== "object") return { valid: false, reason: "invalid_json" };
    const score = Number(payload.score);
    const privacy = payload.privacy;
    if (!Number.isFinite(score) || score < 0 || score > 100) return { valid: false, reason: "score_missing" };
    if (privacy && privacy.containsPersonalData === true) return { valid: false, reason: "personal_data_not_allowed" };
    return {
      valid: true,
      facilityType: safeFacilityType(payload.facilityType),
      maturityReference: sanitizeMaturityReference(payload),
      sourceType: payload.importId ? "handoff" : "export"
    };
  }

  function sanitizeStorage(input, now) {
    const source = input || {};
    return {
      version: STORAGE_VERSION,
      savedAt: Number(now) || Date.now(),
      facilityType: safeFacilityType(source.facilityType),
      criticalLoadCategories: safeArray(source.criticalLoadCategories, CRITICAL_LOAD_CATEGORIES.map((item) => item.id)),
      backupSourceClasses: safeArray(source.backupSourceClasses, BACKUP_SOURCE_CLASSES.map((item) => item.id)),
      evidenceStatuses: normalizeEvidenceStatuses(source.evidenceStatuses),
      maturityReference: sanitizeMaturityReference(source.maturityReference)
    };
  }

  function isStoredPayloadFresh(payload, now) {
    if (!payload || payload.version !== STORAGE_VERSION || !Number.isFinite(payload.savedAt)) return false;
    const age = (Number(now) || Date.now()) - payload.savedAt;
    return age >= 0 && age <= STORAGE_MAX_AGE_MS;
  }

  function createPassportExport(result, options) {
    if (!result || !result.valid || result.emergency) throw new Error("Geçerli pasaport sonucu olmadan export oluşturulamaz.");
    const source = options || {};
    const generatedAt = source.generatedAt || new Date().toISOString();
    const maturityReference = sanitizeMaturityReference(source.maturityReference);
    const actions = ["P0", "P1", "P2"].flatMap((priority) => result.gaps[priority].map((item) => ({
      id: item.id,
      priority: item.priority,
      label: item.label,
      status: item.status,
      action: item.action,
      targetDate: item.targetDate
    })));
    return {
      $schema: "https://www.alo186.com/schemas/electric-continuity-passport-v1.schema.json",
      schemaVersion: SCHEMA_VERSION,
      passportId: `alo186-passport-${String(generatedAt).replace(/[^0-9]/g, "").slice(0, 14)}-${result.score}`,
      generatedAt,
      nextReviewDate: result.nextReviewDate,
      facilityType: result.facilityType,
      criticalLoadCategories: result.criticalLoadCategories.slice(),
      backupSourceClasses: result.backupSourceClasses.slice(),
      evidence: result.evidence.map((item) => ({
        id: item.id,
        status: item.status,
        weight: item.weight,
        priority: item.priority,
        nextReviewDate: item.nextReviewDate
      })),
      score: result.score,
      maturityBand: result.classification.id,
      maturityBandLabel: result.classification.label,
      gaps: {
        P0: result.gaps.P0.map((item) => ({ id: item.id, label: item.label, status: item.status, targetDate: item.targetDate, action: item.action })),
        P1: result.gaps.P1.map((item) => ({ id: item.id, label: item.label, status: item.status, targetDate: item.targetDate, action: item.action })),
        P2: result.gaps.P2.map((item) => ({ id: item.id, label: item.label, status: item.status, targetDate: item.targetDate, action: item.action }))
      },
      maturityReference,
      handoff: {
        version: 1,
        target: "alo186-continuity-panel",
        recommended: result.panelRecommended,
        actions
      },
      privacy: {
        containsPersonalData: false,
        freeTextCollected: false,
        includesLifeSupportFlag: false,
        includesImmediateDangerFlag: false,
        localStorageDefaultEnabled: false
      },
      disclaimer: "Bu pasaport sertifika, elektrik projesi, uygunluk raporu, sigorta ekspertizi veya resmî denetim değildir; teknik kanıtlar yetkili uzman ve gerçek kayıtlarla doğrulanmalıdır."
    };
  }

  return Object.freeze({
    SCHEMA_VERSION,
    STORAGE_VERSION,
    STORAGE_MAX_AGE_MS,
    STATUS_VALUES,
    FACILITY_TYPES,
    CRITICAL_LOAD_CATEGORIES,
    BACKUP_SOURCE_CLASSES,
    EVIDENCE,
    safeFacilityType,
    normalizeEvidenceStatuses,
    classifyScore,
    evaluatePassport,
    parseMaturityImport,
    sanitizeMaturityReference,
    sanitizeStorage,
    isStoredPayloadFresh,
    createPassportExport
  });
});
