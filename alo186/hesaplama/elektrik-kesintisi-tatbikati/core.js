(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.AloOutageDrill = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const VERSION = 1;
  const FACILITY_TYPES = Object.freeze(["hotel", "site", "business", "other"]);
  const STATUS_SCORES = Object.freeze({ ready: 1, partial: 0.5, missing: 0 });
  const STATUS_LABELS = Object.freeze({ ready: "Hazır", partial: "Kısmen hazır", missing: "Eksik" });

  const SCENARIOS = Object.freeze([
    { id: "grid-outage", label: "Şebeke kesintisi ve yedek kaynağa geçiş", extraTask: "transfer-observation" },
    { id: "generator-failure", label: "Jeneratör başlamıyor veya transfer gerçekleşmiyor", extraTask: "authorized-escalation" },
    { id: "short-autonomy", label: "UPS veya batarya otonomisi beklenenden kısa", extraTask: "autonomy-recheck" },
    { id: "voltage-anomaly", label: "Kısmi faz kaybı veya gerilim anormalliği", extraTask: "unsafe-load-stop" },
    { id: "critical-load-loss", label: "Su, iletişim veya soğuk zincir kritik yükü kaybı", extraTask: "continuity-fallback" }
  ]);

  const CRITICAL_LOADS = Object.freeze([
    { id: "life-safety", label: "Yangın, acil aydınlatma ve tahliye" },
    { id: "communications", label: "İletişim, internet, sunucu ve erişim" },
    { id: "cold-chain", label: "Soğuk oda, gıda, ilaç veya proses sıcaklığı" },
    { id: "water", label: "Su, hidrofor, drenaj ve atık su" },
    { id: "security", label: "Güvenlik, kamera ve kartlı geçiş" },
    { id: "operations", label: "Operasyonu durduran üretim veya hizmet yükü" },
    { id: "elevator", label: "Asansör ve erişilebilirlik" },
    { id: "none", label: "Kritik yük yok / yalnız genel konfor yükleri" }
  ]);

  const BACKUP_SOURCES = Object.freeze([
    { id: "generator", label: "Jeneratör" },
    { id: "ups", label: "UPS" },
    { id: "battery-inverter", label: "Batarya / inverter" },
    { id: "power-station", label: "Taşınabilir güç istasyonu" },
    { id: "dual-feed", label: "İkinci besleme / alternatif şebeke" },
    { id: "none", label: "Yedek kaynak yok" }
  ]);

  const TASKS = Object.freeze([
    { id: "scope-check", window: "5", weight: 8, priority: "P0", title: "Kesintinin kapsamı güvenli biçimde doğrulandı", action: "Enerjili pano veya iletkene dokunmadan çevre, bina ve kritik yük kapsamını karşılaştırın." },
    { id: "hazard-check", window: "5", weight: 10, priority: "P0", title: "Can güvenliği tehlikesi kontrol edildi", action: "Duman, yangın, elektrik çarpması, kıvılcım ve düşmüş iletken varsa tatbikatı durdurup 112 rotasına geçin." },
    { id: "life-safety-status", window: "5", weight: 8, priority: "P0", title: "Yangın ve acil aydınlatma durumu doğrulandı", action: "Yalnız gösterge ve sorumlu ekip raporuyla yaşam güvenliği sistemlerinin durumunu kaydedin." },
    { id: "role-activation", window: "5", weight: 7, priority: "P0", title: "Birincil ve yedek görev sahipliği aktive edildi", action: "İsim toplamadan görev rolünün ve yedek rolün tanımlı olduğunu doğrulayın." },
    { id: "time-record", window: "5", weight: 5, priority: "P1", title: "Başlangıç zamanı ve senaryo kaydı açıldı", action: "Olay veya tatbikat başlangıcını standart kayıt yapısına işleyin." },
    { id: "backup-status", window: "15", weight: 8, priority: "P0", title: "Yedek kaynak durumu doğrulandı", action: "Gösterge, alarm veya yetkili ekip geri bildirimiyle yedek kaynağın hazır/başarısız durumunu kaydedin." },
    { id: "critical-load-status", window: "15", weight: 8, priority: "P0", title: "Kritik yüklerin çalışır/kayıp durumu sınıflandırıldı", action: "Kritik yük kategorilerini çalışıyor, sınırlı veya devre dışı olarak ayırın." },
    { id: "official-record", window: "15", weight: 6, priority: "P1", title: "186, yönetim veya yetkili servis kayıt rotası belirlendi", action: "Şebeke, bina içi tesisat ve ekipman sorumluluğunu ayırarak doğru resmî veya teknik kanalı kullanın." },
    { id: "load-priority", window: "15", weight: 6, priority: "P1", title: "Önceliksiz yükleri azaltma planı hazır", action: "Yalnız önceden tanımlı prosedürle kritik olmayan yüklerin durdurulma sırasını belirleyin." },
    { id: "offline-comms", window: "15", weight: 5, priority: "P1", title: "Çevrimdışı iletişim ve durum paylaşımı hazır", action: "Telefon, basılı liste veya alternatif kanalın erişilebilirliğini doğrulayın; bu araçta iletişim bilgisi girmeyin." },
    { id: "autonomy-estimate", window: "60", weight: 7, priority: "P0", title: "Yakıt, batarya veya UPS kalan otonomisi tahmin edildi", action: "Üretici verisi, test kaydı ve gerçek yükle kalan süreyi doğrulayın; varsayımı görünür tutun." },
    { id: "authorized-escalation", window: "60", weight: 6, priority: "P1", title: "Yetkili servis veya teknik ekip escalation rotası hazır", action: "Enerjili ekipmana müdahale etmeden yetkili ekip çağrı ve erişim koşullarını doğrulayın." },
    { id: "continuity-fallback", window: "60", weight: 6, priority: "P1", title: "Alternatif operasyon planı hazır", action: "Kritik hizmeti azaltılmış kapasiteyle sürdürme veya kontrollü durdurma planını seçin." },
    { id: "stakeholder-update", window: "60", weight: 5, priority: "P2", title: "Kullanıcı ve yönetim bilgilendirme şablonu hazır", action: "Doğrulanmamış süre vermeden kapsam, güvenlik ve sonraki güncelleme zamanını paylaşın." },
    { id: "closure-owner", window: "60", weight: 5, priority: "P2", title: "Kanıt, bulgu ve kapanış sorumluluğu tanımlı", action: "Tatbikat bulgularını sorumlu rol, hedef tarih ve kapanış kanıtıyla izleyin." }
  ]);

  const SCENARIO_TASKS = Object.freeze({
    "transfer-observation": { id: "transfer-observation", window: "15", weight: 6, priority: "P0", title: "Transfer ve geri dönüş davranışı gözlendi", action: "Transfer süresini ve başarısız geçişi yalnız yetkili ekip gözetiminde kaydedin." },
    "authorized-escalation": { id: "generator-manual-start-boundary", window: "15", weight: 6, priority: "P0", title: "Manuel çalıştırma yetki sınırı açık", action: "Yetkisiz kişinin jeneratör, ATS veya panoya müdahale etmesini engelleyin; yetkili ekip rotasını kullanın." },
    "autonomy-recheck": { id: "autonomy-recheck", window: "15", weight: 6, priority: "P0", title: "Gerçek yük ve batarya yaşına göre otonomi yeniden değerlendirildi", action: "Etiket kapasitesi yerine test kaydı ve gerçek yükle kullanılabilir süreyi güncelleyin." },
    "unsafe-load-stop": { id: "unsafe-load-stop", window: "5", weight: 6, priority: "P0", title: "Anormal gerilimde hassas yükleri güvenli durdurma sınırı tanımlı", action: "Kullanıcı müdahalesi yerine önceden onaylı prosedür ve yetkili ekip kararını uygulayın." },
    "continuity-fallback": { id: "critical-service-fallback", window: "15", weight: 6, priority: "P0", title: "Kritik hizmet için alternatif kaynak veya kontrollü durdurma planı hazır", action: "Su, iletişim veya soğuk zincir için süre ve sorumluluk sınırı olan fallback planını doğrulayın." }
  });

  function uniqueAllowed(values, catalogue) {
    const allowed = new Set(catalogue.map((item) => item.id));
    return [...new Set(Array.isArray(values) ? values.filter((item) => allowed.has(item)) : [])];
  }

  function hasMixedNone(values) {
    return values.includes("none") && values.length > 1;
  }

  function validStatus(value) {
    return Object.prototype.hasOwnProperty.call(STATUS_SCORES, value) ? value : "missing";
  }

  function scenarioById(id) {
    return SCENARIOS.find((item) => item.id === id) || SCENARIOS[0];
  }

  function activeTasks(scenarioId) {
    const scenario = scenarioById(scenarioId);
    return [...TASKS, SCENARIO_TASKS[scenario.extraTask]].filter(Boolean);
  }

  function normalizeStatuses(input, scenarioId) {
    const source = input && typeof input === "object" ? input : {};
    const output = {};
    activeTasks(scenarioId).forEach((task) => { output[task.id] = validStatus(source[task.id]); });
    return output;
  }

  function priorityRank(value) {
    return { P0: 0, P1: 1, P2: 2 }[value] ?? 9;
  }

  function statusRank(value) {
    return { missing: 0, partial: 1, ready: 2 }[value] ?? 9;
  }

  function nextDrillDate(score, now) {
    const base = now instanceof Date && !Number.isNaN(now.getTime()) ? now : new Date();
    const days = score >= 85 ? 180 : score >= 65 ? 90 : 30;
    return new Date(base.getTime() + days * 24 * 60 * 60 * 1000);
  }

  function band(score) {
    if (score >= 85) return { id: "controlled", label: "Tatbikat kontrollü", tone: "good", summary: "İlk 5/15/60 dakika akışı güçlü; bulguları kanıtla kapatın ve altı ay içinde tekrarlayın." };
    if (score >= 65) return { id: "developing", label: "Gelişen", tone: "warn", summary: "Temel akış var; P0 boşlukları kapatılmadan gerçek olay hazırlığı yeterli sayılmamalı." };
    if (score >= 40) return { id: "fragile", label: "Kırılgan", tone: "danger", summary: "Görev, iletişim veya yedek kaynak adımlarında kritik boşluklar var; 30 günlük iyileştirme planı oluşturun." };
    return { id: "uncontrolled", label: "Kontrolsüz", tone: "danger", summary: "İlk saat müdahalesi kişiye ve doğaçlamaya bağlı; önce P0 görevleri ve çevrimdışı plan oluşturulmalı." };
  }

  function evaluate(input, options) {
    const data = input && typeof input === "object" ? input : {};
    if (data.immediateDanger === true) {
      return { valid: false, emergency: true, route: "112", revenueAllowed: false, errors: [] };
    }

    const scenario = scenarioById(data.scenarioId);
    const facilityType = FACILITY_TYPES.includes(data.facilityType) ? data.facilityType : "other";
    const criticalLoads = uniqueAllowed(data.criticalLoads, CRITICAL_LOADS);
    const backupSources = uniqueAllowed(data.backupSources, BACKUP_SOURCES);
    const statuses = normalizeStatuses(data.taskStatuses, scenario.id);
    const errors = [];
    if (!criticalLoads.length) errors.push("Kritik yük durumunu seçin.");
    if (!backupSources.length) errors.push("Yedek kaynak durumunu seçin.");
    if (hasMixedNone(criticalLoads)) errors.push("“Kritik yük yok” seçeneğini diğer kritik yüklerle birlikte kullanmayın.");
    if (hasMixedNone(backupSources)) errors.push("“Yedek kaynak yok” seçeneğini diğer yedek kaynaklarla birlikte kullanmayın.");
    if (data.confirmTabletop !== true) errors.push("Çalışmanın planlı masa başı veya yetkili ekip gözetimindeki kontrollü tatbikat olduğunu doğrulayın.");
    if (errors.length) return { valid: false, emergency: false, revenueAllowed: false, errors };

    const tasks = activeTasks(scenario.id);
    const taskWeight = tasks.reduce((sum, task) => sum + task.weight, 0);
    const earned = tasks.reduce((sum, task) => sum + task.weight * STATUS_SCORES[statuses[task.id]], 0);
    let score = Math.round((earned / taskWeight) * 100);
    const structuralGaps = [];
    const noCritical = criticalLoads.length === 1 && criticalLoads[0] === "none";
    const noBackup = backupSources.includes("none") && backupSources.length === 1;

    if (!noCritical && noBackup) {
      score = Math.min(score, 49);
      structuralGaps.push({ id: "critical-without-backup", window: "5", priority: "P0", title: "Kritik yük var, yedek kaynak yok", status: "missing", statusLabel: "Eksik", action: "Kabul edilebilir kesinti süresini ve kritik yük gücünü doğrulayın; ekipman satın almadan önce teknik çözüm sınıfını planlayın." });
    }
    if (data.rolesAssigned !== true) {
      score = Math.min(score, 64);
      structuralGaps.push({ id: "roles-not-assigned", window: "5", priority: "P0", title: "Birincil ve yedek görev rolleri tanımlı değil", status: "missing", statusLabel: "Eksik", action: "İsim toplamadan her kritik görev için birincil ve yedek rol atayın." });
    }
    if (data.offlineContacts !== true) {
      structuralGaps.push({ id: "offline-contacts-missing", window: "15", priority: "P1", title: "Çevrimdışı iletişim listesi hazır değil", status: "missing", statusLabel: "Eksik", action: "112, 186, yönetim, teknik ekip ve servis kanallarını çevrimdışı erişilebilir hâle getirin." });
    }
    if (data.recordTemplate !== true) {
      structuralGaps.push({ id: "record-template-missing", window: "5", priority: "P1", title: "Standart olay/tatbikat kayıt şablonu yok", status: "missing", statusLabel: "Eksik", action: "Başlangıç, kapsam, görev, karar, kayıt numarası, maliyet ve kapanış alanlarını standartlaştırın." });
    }

    const gaps = tasks.map((task) => {
      const status = statuses[task.id];
      if (status === "ready") return null;
      return { id: task.id, window: task.window, priority: status === "partial" && task.priority === "P0" ? "P1" : task.priority, title: task.title, status, statusLabel: STATUS_LABELS[status], action: task.action };
    }).filter(Boolean).concat(structuralGaps).sort((a, b) => priorityRank(a.priority) - priorityRank(b.priority) || Number(a.window) - Number(b.window) || statusRank(a.status) - statusRank(b.status));

    const classification = band(score);
    const now = options && options.now instanceof Date ? options.now : new Date();
    const timeline = ["5", "15", "60"].map((window) => ({
      window,
      tasks: tasks.filter((task) => task.window === window).map((task) => ({ ...task, status: statuses[task.id], statusLabel: STATUS_LABELS[statuses[task.id]] }))
    }));
    const p0Count = gaps.filter((item) => item.priority === "P0").length;
    const p1Count = gaps.filter((item) => item.priority === "P1").length;
    const passportEvidenceSuggestions = {
      recovery_drill: p0Count === 0 ? "current" : "planned",
      emergency_contacts: data.rolesAssigned && data.offlineContacts ? "current" : "due",
      outage_log: data.recordTemplate ? "current" : "planned",
      generator_ups_test: statuses["backup-status"] === "ready" ? "current" : "due",
      transfer_test: statuses["transfer-observation"] === "ready" ? "current" : "due"
    };

    const handoff = {
      schema: "alo186.continuity-drill-handoff.v1",
      version: VERSION,
      createdAt: now.toISOString(),
      expiresAt: new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      facilityType,
      scenarioId: scenario.id,
      criticalLoads: criticalLoads.filter((item) => item !== "none"),
      backupSources: backupSources.filter((item) => item !== "none"),
      score,
      band: classification.id,
      gaps: gaps.map(({ id, window, priority, status }) => ({ id, window, priority, status })),
      passportEvidenceSuggestions
    };

    return {
      valid: true,
      emergency: false,
      revenueAllowed: true,
      version: VERSION,
      facilityType,
      scenario,
      criticalLoads,
      backupSources,
      statuses,
      score,
      classification,
      p0Count,
      p1Count,
      gaps,
      timeline,
      nextDrillDate: nextDrillDate(score, now),
      managerSummary: `${scenario.label} senaryosunda hazırlık skoru ${score}/100. ${p0Count} P0 ve ${p1Count} P1 boşluk bulundu. İlk öncelik: ${gaps[0] ? gaps[0].title : "bulguları kanıtla kapatmak"}.`,
      passportEvidenceSuggestions,
      handoff
    };
  }

  function exportPayload(result) {
    if (!result || result.valid !== true) throw new Error("Geçerli tatbikat sonucu gerekli.");
    return {
      schema: "alo186.electric-outage-drill.v1",
      version: VERSION,
      createdAt: result.handoff.createdAt,
      facilityType: result.facilityType,
      scenarioId: result.scenario.id,
      criticalLoads: result.criticalLoads.filter((item) => item !== "none"),
      backupSources: result.backupSources.filter((item) => item !== "none"),
      score: result.score,
      band: result.classification.id,
      timeline: result.timeline.map((group) => ({ window: group.window, tasks: group.tasks.map(({ id, status }) => ({ id, status })) })),
      gaps: result.gaps.map(({ id, window, priority, status }) => ({ id, window, priority, status })),
      nextDrillDate: result.nextDrillDate.toISOString(),
      passportEvidenceSuggestions: result.passportEvidenceSuggestions,
      handoff: result.handoff
    };
  }

  return {
    VERSION,
    FACILITY_TYPES,
    SCENARIOS,
    CRITICAL_LOADS,
    BACKUP_SOURCES,
    TASKS,
    SCENARIO_TASKS,
    STATUS_SCORES,
    activeTasks,
    evaluate,
    exportPayload,
    nextDrillDate
  };
});
