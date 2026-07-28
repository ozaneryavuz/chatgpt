(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.AloContinuityMaturity = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const ANSWER_VALUES = Object.freeze({ no: 0, partial: 0.5, yes: 1 });
  const STORAGE_VERSION = 1;
  const STORAGE_MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000;

  const DIMENSIONS = Object.freeze([
    { id: "critical-loads", title: "Kritik yük envanteri", short: "Kritik yük" },
    { id: "documentation", title: "Tek hat, etiket ve dokümantasyon", short: "Dokümantasyon" },
    { id: "backup", title: "Yedek güç kapsamı ve otonomi", short: "Yedek güç" },
    { id: "testing", title: "Transfer, test ve tatbikat", short: "Test ve tatbikat" },
    { id: "maintenance", title: "Bakım ve kanıt kayıtları", short: "Bakım" },
    { id: "incident", title: "Olay yönetimi ve resmî kayıt", short: "Olay yönetimi" },
    { id: "ownership", title: "İletişim ve görev sahipliği", short: "Sahiplik" },
    { id: "improvement", title: "Maliyet, iyileştirme ve yönetim takibi", short: "İyileştirme" }
  ]);

  const QUESTIONS = Object.freeze([
    {
      id: "critical_inventory",
      dimension: "critical-loads",
      weight: 1.5,
      text: "Elektrik kesildiğinde çalışması gereken kritik yükler yazılı ve önceliklendirilmiş durumda.",
      action30: "Kritik yükleri P1, P2 ve P3 olarak sınıflandırın; yalnız gerçekten kesintide çalışması gereken yükleri P1 yapın.",
      action60: "Her P1 yük için besleme noktası, yaklaşık W/kW ve hedef çalışma süresini kaydedin.",
      action90: "Kritik yük listesini operasyon, güvenlik ve teknik ekip ile yılda en az bir kez gözden geçirin."
    },
    {
      id: "critical_owner",
      dimension: "critical-loads",
      weight: 1,
      text: "Her kritik yük için operasyon sahibi ve teknik sorumlu bellidir.",
      action30: "Her P1 yük için bir operasyon sahibi ve bir teknik sorumlu atayın.",
      action60: "İzin, vardiya ve ulaşılmazlık durumları için yedek sorumlu tanımlayın.",
      action90: "Sorumluluk listesini tatbikatta doğrulayın ve güncelleyin."
    },
    {
      id: "critical_runtime",
      dimension: "critical-loads",
      weight: 1,
      text: "Kritik yüklerin kabul edilebilir kesinti süresi ve hedef otonomisi tanımlıdır.",
      action30: "P1 yükler için kabul edilebilir kesinti süresini ve hedef otonomiyi belirleyin.",
      action60: "Hedef süreyi gerçek tüketim ve geçiş gecikmesiyle karşılaştırın.",
      action90: "Sezon, doluluk veya üretim değişimlerinde hedef süreyi yeniden değerlendirin."
    },
    {
      id: "single_line",
      dimension: "documentation",
      weight: 1.2,
      text: "Güncel tek hat şeması veya besleme ilişkisini gösteren eşdeğer doküman vardır.",
      action30: "Ana besleme, jeneratör/UPS, transfer ve kritik panoları gösteren güncel tek hat dokümanını hazırlatın.",
      action60: "Dokümanı saha etiketleri ve gerçek kablo/pano adlarıyla eşleştirin.",
      action90: "Her proje ve pano değişikliğinde revizyon numarasıyla güncelleme kuralı koyun."
    },
    {
      id: "labels",
      dimension: "documentation",
      weight: 1,
      text: "Ana panolar, kritik devreler, transfer kaynakları ve kesme noktaları anlaşılır biçimde etiketlidir.",
      action30: "Kritik pano, devre ve kaynakları standart adlarla etiketleyin.",
      action60: "Etiketleri tek hat, bakım planı ve olay görevleriyle aynı adlandırmaya taşıyın.",
      action90: "Saha turunda okunamayan, eksik veya yanlış etiketleri periyodik kontrol listesine ekleyin."
    },
    {
      id: "documents_access",
      dimension: "documentation",
      weight: 0.8,
      text: "Kesinti sırasında gerekli dokümanlara elektrik/internet olmasa da erişilebilir.",
      action30: "Tek hat, acil numaralar ve kritik görev listesinin çevrimdışı kopyasını oluşturun.",
      action60: "Kopyaların sürüm ve erişim yetkisini kontrol edin.",
      action90: "Tatbikatta dokümanların gerçekten bulunabildiğini test edin."
    },
    {
      id: "backup_coverage",
      dimension: "backup",
      weight: 1.5,
      text: "Yedek kaynak kapasitesi kritik yüklerin sürekli ve kalkış gücünü karşılayacak şekilde doğrulanmıştır.",
      action30: "P1 yüklerin sürekli W/kW ve motor kalkış ihtiyaçlarını tek tabloda toplayın.",
      action60: "Jeneratör, UPS veya batarya kapasitesini ölçüm ve üretici verisiyle doğrulatın.",
      action90: "Yeni yük eklendiğinde kapasite kontrolünü zorunlu değişiklik adımı yapın."
    },
    {
      id: "backup_autonomy",
      dimension: "backup",
      weight: 1.4,
      text: "Yakıt, batarya ve UPS otonomisi hedef kesinti süresiyle karşılaştırılmıştır.",
      action30: "Mevcut yakıt/batarya ile gerçekçi otonomi süresini hesaplayın.",
      action60: "Düşük doluluk, yaşlanma ve güvenli rezerv payını hesaba katın.",
      action90: "Gerçek olay ve test sürelerinden otonomi varsayımını güncelleyin."
    },
    {
      id: "backup_single_failure",
      dimension: "backup",
      weight: 1.1,
      text: "Tek bir arızanın bütün kritik yükleri devre dışı bırakacağı noktalar belirlenmiştir.",
      action30: "Tek jeneratör, tek transfer şalteri, tek UPS veya tek pano gibi ortak arıza noktalarını işaretleyin.",
      action60: "En kritik ortak arıza noktası için geçici işletme veya yedekleme prosedürü oluşturun.",
      action90: "Yatırım planını risk, olay maliyeti ve uygulanabilirlik sırasına göre yönetime sunun."
    },
    {
      id: "transfer_test",
      dimension: "testing",
      weight: 1.5,
      text: "Transfer sistemi gerçek yük altında ve kayıtlı biçimde periyodik test edilir.",
      action30: "Transfer testinin sorumlusunu, güvenli kapsamını ve kayıt formatını belirleyin.",
      action60: "Yetkili ekip ile kontrollü gerçek yük veya uygun test prosedürü uygulayın.",
      action90: "Başarısızlık, gecikme ve alarm bulgularını bakım ve yatırım planına bağlayın."
    },
    {
      id: "ups_battery_test",
      dimension: "testing",
      weight: 1.2,
      text: "UPS, batarya veya enerji depolama sistemi yalnız alarm ekranına değil kayıtlı kapasite/test sonucuna göre izlenir.",
      action30: "Son batarya/UPS test tarihini ve kullanılan yöntemi kaydedin.",
      action60: "Kritik sistemlerde üretici prosedürüne uygun kapasite veya yük testi planlayın.",
      action90: "Değişim kararını yalnız yaşa değil test sonucu, sıcaklık ve olay performansına bağlayın."
    },
    {
      id: "scenario_drill",
      dimension: "testing",
      weight: 1,
      text: "Kesinti senaryosu teknik ve operasyon ekipleriyle tatbik edilmiştir.",
      action30: "Masa başı kesinti senaryosu ve ilk 15 dakika görevlerini çalışın.",
      action60: "Uygun güvenlik koşullarında kontrollü transfer/olay tatbikatı yapın.",
      action90: "Tatbikat sonrası süre, eksik görev ve iletişim sorunlarını kapatın."
    },
    {
      id: "maintenance_plan",
      dimension: "maintenance",
      weight: 1.2,
      text: "Jeneratör, UPS, batarya, transfer, RCD/SPD ve kritik panolar için bakım/test planı vardır.",
      action30: "Kritik elektrik varlıklarının son ve sonraki bakım/test tarihlerini tek listede toplayın.",
      action60: "Üretici kılavuzu, kullanım saati ve ortam koşuluna göre periyotları doğrulayın.",
      action90: "Geciken bakım ve başarısız testleri yönetim göstergesine dönüştürün."
    },
    {
      id: "maintenance_evidence",
      dimension: "maintenance",
      weight: 1,
      text: "Bakım, test, ölçüm ve arıza kayıtları tarih, sonuç ve sorumluyla saklanır.",
      action30: "Her bakım/test için tarih, sonuç, uygunsuzluk ve sorumlu alanlarını zorunlu yapın.",
      action60: "Fotoğraf, ölçüm ve servis belgesini ilgili varlık kaydıyla ilişkilendirin.",
      action90: "Tekrarlayan arızaları ve kapanmayan bulguları yönetim raporunda izleyin."
    },
    {
      id: "spares",
      dimension: "maintenance",
      weight: 0.8,
      text: "Kritik yedek parça, sarf ve dış servis erişimi önceden planlanmıştır.",
      action30: "Kritik arıza halinde bekleme yaratacak parça ve servisleri listeleyin.",
      action60: "Minimum stok, tedarik süresi ve onaylı servis iletişimlerini doğrulayın.",
      action90: "Kullanılmayan stok ve kritik eksikleri olay geçmişine göre yeniden dengeleyin."
    },
    {
      id: "incident_playbook",
      dimension: "incident",
      weight: 1.4,
      text: "Kesinti başladığında uygulanacak ilk güvenlik, kapsam ve bildirim adımları yazılıdır.",
      action30: "İlk 5, 15 ve 60 dakika için güvenlik ve kapsam kontrol listesini hazırlayın.",
      action60: "112, 186, yönetim ve yetkili teknik ekip ayrımını senaryolarla doğrulayın.",
      action90: "Gerçek olay ve tatbikatlardan playbook'u sürümlü biçimde geliştirin."
    },
    {
      id: "incident_timeline",
      dimension: "incident",
      weight: 1,
      text: "Olay zamanı, gözlem, müdahale, resmî kayıt numarası ve kapanış bilgisi tutulur.",
      action30: "Kesinti başlangıcı, müdahale ve kapanış için standart zaman çizelgesi oluşturun.",
      action60: "186/servis kayıt numarası ve yapılan işlemleri olay kaydına bağlayın.",
      action90: "Olay sürelerini ve tekrar eden nedenleri aylık olarak karşılaştırın."
    },
    {
      id: "incident_close",
      dimension: "incident",
      weight: 0.9,
      text: "Olay kapatılmadan önce kritik görevlerin tamamlandığı ve geçici çözümlerin izlendiği doğrulanır.",
      action30: "P1 görevler tamamlanmadan olay kapanmasını engelleyen kontrol listesi belirleyin.",
      action60: "Geçici çözümleri sorumlu ve hedef tarihle kalıcı aksiyona dönüştürün.",
      action90: "Kapanış kalitesini ve tekrar olay oranını yönetim göstergesi yapın."
    },
    {
      id: "roles",
      dimension: "ownership",
      weight: 1.2,
      text: "Kesintide karar verecek, müdahale edecek ve bilgi verecek roller bellidir.",
      action30: "Karar, teknik müdahale, güvenlik ve iletişim rollerini isimden bağımsız görev olarak tanımlayın.",
      action60: "Vardiya ve izin durumları için yedek rol atayın.",
      action90: "Tatbikat ve gerçek olayda görev devir sürelerini ölçün."
    },
    {
      id: "contacts",
      dimension: "ownership",
      weight: 1,
      text: "EDAŞ, 112, yetkili elektrikçi, jeneratör/UPS servisi ve yönetim iletişimleri günceldir.",
      action30: "Resmî ve teknik iletişim listesini güncelleyin; ALO186'in kayıt mercii olmadığını ekibe açıklayın.",
      action60: "Mesai dışı erişim ve ikinci kişi numaralarını doğrulayın.",
      action90: "İletişim listesini periyodik test ve değişiklik sürecine bağlayın."
    },
    {
      id: "stakeholder_updates",
      dimension: "ownership",
      weight: 0.8,
      text: "Çalışan, misafir, sakin veya müşteri için kesinti iletişim şablonu ve onay akışı vardır.",
      action30: "Kısa durum, güvenlik ve tahmini sonraki güncelleme şablonları hazırlayın.",
      action60: "Kimlerin hangi kanaldan ve kimin onayıyla bilgilendirileceğini belirleyin.",
      action90: "Tatbikatta mesajın doğruluk ve hızını ölçün."
    },
    {
      id: "cost_tracking",
      dimension: "improvement",
      weight: 1,
      text: "Kesintinin hizmet, personel, stok, yakıt ve yeniden başlatma etkisi yaklaşık olarak kaydedilir.",
      action30: "Olay başına süre, yakıt, personel ve doğrudan kayıp kalemlerini kaydetmeye başlayın.",
      action60: "Yıllık kesinti maliyeti ile bakım ve yedek güç yatırımını karşılaştırın.",
      action90: "Yatırım önceliklerini yalnız satın alma fiyatına değil toplam sahip olma maliyetine bağlayın."
    },
    {
      id: "management_review",
      dimension: "improvement",
      weight: 1,
      text: "Elektrik sürekliliği göstergeleri yönetim tarafından düzenli gözden geçirilir.",
      action30: "Olay sayısı, toplam süre, başarısız test, geciken bakım ve açık P1 aksiyonlarını raporlayın.",
      action60: "Aylık veya çeyreklik gözden geçirme sorumlusu ve karar kaydı oluşturun.",
      action90: "Kapanan aksiyonların riski gerçekten azaltıp azaltmadığını doğrulayın."
    },
    {
      id: "lessons_learned",
      dimension: "improvement",
      weight: 1,
      text: "Her ciddi olay veya tatbikattan sonra kök neden, öğrenilen ders ve takip aksiyonu kaydedilir.",
      action30: "Ciddi olaylar için kısa kök neden ve öğrenilen ders şablonu kullanın.",
      action60: "Her aksiyona sorumlu, hedef tarih ve kapanış kanıtı ekleyin.",
      action90: "Tekrarlayan bulguları süreç, tasarım veya yatırım değişikliğine dönüştürün."
    }
  ]);

  function answerValue(value) {
    if (typeof value === "number" && value >= 0 && value <= 1) return value;
    return Object.prototype.hasOwnProperty.call(ANSWER_VALUES, value) ? ANSWER_VALUES[value] : null;
  }

  function validateAnswers(answers) {
    const missing = [];
    const invalid = [];
    QUESTIONS.forEach((question) => {
      const raw = answers ? answers[question.id] : undefined;
      if (raw === undefined || raw === null || raw === "") missing.push(question.id);
      else if (answerValue(raw) === null) invalid.push(question.id);
    });
    return { valid: missing.length === 0 && invalid.length === 0, missing, invalid };
  }

  function classifyScore(score) {
    const value = Math.max(0, Math.min(100, Number(score) || 0));
    if (value < 25) return { id: "fragile", label: "Kırılgan", tone: "bad", summary: "Kesintiye karşı temel kayıt, sorumluluk ve doğrulama katmanları eksik." };
    if (value < 50) return { id: "reactive", label: "Reaktif", tone: "bad", summary: "Bazı önlemler var; ancak sistem çoğunlukla olay olduktan sonra çalışıyor." };
    if (value < 70) return { id: "controlled", label: "Kontrollü", tone: "warn", summary: "Temel yapı kurulmuş; test, kanıt ve ortak arıza noktalarında boşluklar sürüyor." };
    if (value < 85) return { id: "resilient", label: "Dirençli", tone: "ok", summary: "Süreklilik sistemi büyük ölçüde çalışıyor; doğrulama ve iyileştirme disiplini güçlendirilebilir." };
    return { id: "advanced", label: "İleri", tone: "ok", summary: "Kayıt, test ve iyileştirme disiplini güçlü. Sonuç sertifikasyon veya uygunluk belgesi değildir." };
  }

  function buildPlan(answers, limit) {
    const gaps = QUESTIONS.map((question) => {
      const value = answerValue(answers[question.id]);
      return {
        id: question.id,
        dimension: question.dimension,
        text: question.text,
        value,
        weight: question.weight,
        priority: question.weight * (1 - value),
        actions: { day30: question.action30, day60: question.action60, day90: question.action90 }
      };
    })
      .filter((item) => item.value < 1)
      .sort((a, b) => b.priority - a.priority || a.id.localeCompare(b.id));

    const selected = gaps.slice(0, Math.max(1, Math.min(Number(limit) || 6, 9)));
    const plan = { day30: [], day60: [], day90: [] };
    selected.forEach((gap, index) => {
      const phase = index < 2 ? "day30" : index < 4 ? "day60" : "day90";
      plan[phase].push({
        questionId: gap.id,
        dimension: gap.dimension,
        action: gap.actions[phase],
        priority: Number(gap.priority.toFixed(3))
      });
    });
    if (selected.length === 0) {
      plan.day90.push({
        questionId: "continuous_review",
        dimension: "improvement",
        action: "Skoru gerçek olay, tatbikat, bakım bulgusu ve değişen kritik yüklerle 90 gün sonra yeniden doğrulayın.",
        priority: 0
      });
    }
    return { gaps, selected, plan };
  }

  function evaluateAssessment(answers, options) {
    const validation = validateAnswers(answers || {});
    if (!validation.valid) return { valid: false, validation };

    const dimensionTotals = {};
    DIMENSIONS.forEach((dimension) => {
      dimensionTotals[dimension.id] = { earned: 0, possible: 0, score: 0 };
    });

    let earned = 0;
    let possible = 0;
    QUESTIONS.forEach((question) => {
      const value = answerValue(answers[question.id]);
      const points = question.weight * value;
      earned += points;
      possible += question.weight;
      dimensionTotals[question.dimension].earned += points;
      dimensionTotals[question.dimension].possible += question.weight;
    });

    const score = Math.round((earned / possible) * 100);
    const dimensions = DIMENSIONS.map((dimension) => {
      const totals = dimensionTotals[dimension.id];
      return {
        id: dimension.id,
        title: dimension.title,
        short: dimension.short,
        score: Math.round((totals.earned / totals.possible) * 100),
        earned: Number(totals.earned.toFixed(2)),
        possible: Number(totals.possible.toFixed(2))
      };
    }).sort((a, b) => a.score - b.score || a.id.localeCompare(b.id));

    const planData = buildPlan(answers, options && options.planLimit);
    const criticalGapIds = ["critical_inventory", "backup_coverage", "transfer_test", "incident_playbook", "roles"];
    const criticalGaps = criticalGapIds.filter((id) => answerValue(answers[id]) < 0.5);
    const classification = classifyScore(score);

    return {
      valid: true,
      score,
      classification,
      dimensions,
      weakestDimensions: dimensions.slice(0, 3),
      criticalGaps,
      plan: planData.plan,
      priorityGaps: planData.selected,
      panelRecommended: score < 85 || planData.gaps.length >= 4,
      professionalReviewRecommended: score < 50 || criticalGaps.length > 0,
      methodology: {
        version: "1.0.0",
        questionCount: QUESTIONS.length,
        dimensionCount: DIMENSIONS.length,
        scoring: "weighted-0-0.5-1",
        certification: false
      }
    };
  }

  function sanitizeStorage(input, now) {
    const source = input || {};
    const safeAnswers = {};
    QUESTIONS.forEach((question) => {
      const value = source.answers && source.answers[question.id];
      if (answerValue(value) !== null) safeAnswers[question.id] = value;
    });
    const facilityTypes = ["hotel", "site", "business", "other"];
    return {
      version: STORAGE_VERSION,
      savedAt: Number(now) || Date.now(),
      facilityType: facilityTypes.includes(source.facilityType) ? source.facilityType : "other",
      answers: safeAnswers
    };
  }

  function isStoredPayloadFresh(payload, now) {
    if (!payload || payload.version !== STORAGE_VERSION || !Number.isFinite(payload.savedAt)) return false;
    const age = (Number(now) || Date.now()) - payload.savedAt;
    return age >= 0 && age <= STORAGE_MAX_AGE_MS;
  }

  function createExport(result, facilityType, generatedAt) {
    if (!result || !result.valid) throw new Error("Geçerli sonuç olmadan export oluşturulamaz.");
    return {
      schemaVersion: 1,
      generatedAt: generatedAt || new Date().toISOString(),
      facilityType: ["hotel", "site", "business", "other"].includes(facilityType) ? facilityType : "other",
      score: result.score,
      maturityBand: result.classification.label,
      dimensions: result.dimensions.map((item) => ({ id: item.id, title: item.title, score: item.score })),
      criticalGapCount: result.criticalGaps.length,
      plan: result.plan,
      disclaimer: "ALO186 olgunluk skoru bir ISO sertifikası, elektrik projesi, uygunluk raporu veya resmî denetim değildir."
    };
  }

  return Object.freeze({
    ANSWER_VALUES,
    DIMENSIONS,
    QUESTIONS,
    STORAGE_VERSION,
    STORAGE_MAX_AGE_MS,
    answerValue,
    validateAnswers,
    classifyScore,
    buildPlan,
    evaluateAssessment,
    sanitizeStorage,
    isStoredPayloadFresh,
    createExport
  });
});
