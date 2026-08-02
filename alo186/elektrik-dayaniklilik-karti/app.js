(() => {
  "use strict";

  const STORAGE_KEY = "alo186_resilience_card_v1";
  const STORAGE_DAYS = 90;
  const QUESTION_IDS = ["lighting", "phone", "internet", "cold", "contact", "test", "official"];
  const LOCATION_TYPES = new Set(["home", "relative", "villa", "site", "business"]);

  const SCORE_MAP = {
    lighting: { ready: 15, partial: 7, no: 0 },
    phone: { ready: 12, partial: 6, no: 0 },
    internet: { ready: 14, not_needed: 14, uncertain: 5, no: 0 },
    cold: { ready: 15, not_needed: 15, partial: 6, no: 0 },
    contact: { ready: 12, partial: 5, no: 0 },
    test: { recent: 16, overdue: 6, never: 0 },
    official: { ready: 16, unsure: 6, no: 0 }
  };

  const MAX_SCORES = {
    lighting: 15,
    phone: 12,
    internet: 14,
    cold: 15,
    contact: 12,
    test: 16,
    official: 16
  };

  const BANDS = [
    {
      key: "critical",
      min: 0,
      max: 39,
      label: "Kritik açık",
      title: "Önce temel güvenlik ve iletişim boşluklarını kapatın.",
      copy: "Kartınız, kesinti sırasında güvenli hareketi veya koordinasyonu zorlaştırabilecek birden fazla temel açık gösteriyor. Ürün aramadan önce ilk üç görevi tamamlayın ve planı başka bir kişiyle paylaşın."
    },
    {
      key: "developing",
      min: 40,
      max: 69,
      label: "Geliştirilmeli",
      title: "Temel hazırlık var; kritik boşluklar hâlâ birlikte yönetilmiyor.",
      copy: "Bazı hazırlıklarınız mevcut ancak test, süre, resmî kanal veya sorumluluk paylaşımı eksik. İlk üç aksiyon tamamlandığında planınız daha güvenilir ve tekrar kullanılabilir hâle gelir."
    },
    {
      key: "ready",
      min: 70,
      max: 84,
      label: "Hazır",
      title: "İyi bir temeliniz var; planı test ve paylaşım ile güçlendirin.",
      copy: "Ana ihtiyaçların çoğu karşılanıyor. Kalan açıklar genellikle güncel test, görev süresi veya ikinci bir kişinin planı bilmesiyle ilgilidir."
    },
    {
      key: "resilient",
      min: 85,
      max: 100,
      label: "Dayanıklı",
      title: "Planınız güçlü; düzenli test ve ortak sahiplik ile koruyun.",
      copy: "Temel hazırlık alanlarının büyük bölümü karşılanıyor. Yeni ürün aramak yerine mevcut ekipmanı görev koşulunda test edin, sonucu paylaşın ve resmî kanal bilgisini güncel tutun."
    }
  ];

  const ACTIONS = {
    lighting: {
      title: "Acil aydınlatmayı gerçek görev süresiyle test edin",
      copy: "Gece hareket edeceğiniz alanları belirleyin; ışığın şarjını, erişilebilirliğini ve hedef çalışma süresini kontrol edin.",
      href: "/hesaplama/acil-aydinlatma-sure-uygunluk/",
      cta: "Aydınlatma süre testini aç"
    },
    phone: {
      title: "Telefon yedek şarj yolunu doğrulayın",
      copy: "Powerbank kapasitesi kadar port gücü, kablo ve gerçek şarj durumunu da birlikte test edin.",
      href: "/hesaplama/powerbank-usb-c-uygunluk/",
      cta: "USB-C uygunluk testini aç"
    },
    internet: {
      title: "Modem ve ONT enerji ihtiyacını birlikte hesaplayın",
      copy: "Gerilim, akım, konnektör, polarite ve hedef süre doğrulanmadan mini UPS seçmeyin.",
      href: "/hesaplama/modem-internet-yedekleme/",
      cta: "İnternet yedekleme hesabını aç"
    },
    cold: {
      title: "Soğuk zincir için süre ve alternatif adımı yazılı hâle getirin",
      copy: "Kapıyı açmama, sıcaklık takibi, alternatif konum ve ilaç için sağlık profesyoneli talimatını önceden belirleyin.",
      href: "/hesaplama/kesinti-hazirlik-plani/",
      cta: "Kesinti hazırlık planını aç"
    },
    contact: {
      title: "En az bir sorumlu veya yakını plana ekleyin",
      copy: "Kesinti başladığında kimin resmî kanalı kontrol edeceğini, kimin ekipmanı test edeceğini ve kimin bilgilendirileceğini belirleyin.",
      action: "share",
      cta: "Kartı sorumlu kişiyle paylaş"
    },
    test: {
      title: "Yedek ekipmanı 90 günlük görev testine alın",
      copy: "Jeneratör, UPS, powerbank, acil ışık veya bataryayı yalnız açılışla değil gerçek yük ve hedef süreyle deneyin.",
      href: "/hesaplama/ekipman-bakim-plani/",
      cta: "Bakım ve test planını aç"
    },
    official: {
      title: "Yetkili EDAŞ ve resmî kesinti ekranını kaydedin",
      copy: "112 can güvenliği içindir. Şebeke kesintisi ve arıza işlemleri için 186 veya bölgenizdeki EDAŞ'ın resmî kanalını kullanın.",
      href: "/edas-bul",
      cta: "EDAŞ bulucuyu aç"
    },
    maintenance: {
      title: "Güçlü planı üç ayda bir yeniden test edin",
      copy: "Bataryalar, kablolar, yakıt, erişim ve sorumlu kişi bilgisi zamanla değişir. Görev testini takvime bağlayın.",
      href: "/hesaplama/ekipman-bakim-plani/",
      cta: "Tekrar test planını aç"
    },
    share: {
      title: "Planı tek kişiden çıkarıp ortaklaştırın",
      copy: "Aynı konumu kullanan en az bir kişi bu kartı, resmî kanalı ve ilk aksiyonları bilsin.",
      action: "share",
      cta: "Kartı birlikte kullanacağım kişiye gönder"
    }
  };

  const form = document.getElementById("assessment");
  const locationType = document.getElementById("locationType");
  const dangerInput = document.getElementById("immediateDanger");
  const emergencyPanel = document.getElementById("emergencyPanel");
  const calculateButton = document.getElementById("calculateButton");
  const validation = document.getElementById("validation");
  const results = document.getElementById("results");
  const scoreCard = document.getElementById("scoreCard");
  const scoreValue = document.getElementById("scoreValue");
  const bandValue = document.getElementById("bandValue");
  const resultTitle = document.getElementById("resultTitle");
  const resultCopy = document.getElementById("resultCopy");
  const actionList = document.getElementById("actionList");
  const progressText = document.getElementById("progressText");
  const progressBar = document.getElementById("progressBar");
  const progress = document.querySelector(".progress");
  const rememberResult = document.getElementById("rememberResult");
  const savedPanel = document.getElementById("savedPanel");
  const sharedPanel = document.getElementById("sharedPanel");
  const sharedTitle = document.getElementById("sharedTitle");
  const sharedCopy = document.getElementById("sharedCopy");
  const shareStatus = document.getElementById("shareStatus");
  const businessHandoff = document.getElementById("businessHandoff");

  let lastPayload = null;
  let startEventSent = false;

  function emit(eventName, details = {}) {
    const allowed = {
      event: eventName,
      result_band: typeof details.result_band === "string" ? details.result_band : undefined,
      location_class: LOCATION_TYPES.has(details.location_class) ? details.location_class : undefined,
      share_channel: ["native", "clipboard", "print", "action"].includes(details.share_channel) ? details.share_channel : undefined
    };
    Object.keys(allowed).forEach((key) => allowed[key] === undefined && delete allowed[key]);
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(allowed);
  }

  function sendStartOnce() {
    if (startEventSent) return;
    startEventSent = true;
    emit("resilience_card_start", { location_class: locationType.value });
  }

  function bandFor(score) {
    return BANDS.find((band) => score >= band.min && score <= band.max) || BANDS[0];
  }

  function encodePayload(payload) {
    const bytes = new TextEncoder().encode(JSON.stringify(payload));
    let binary = "";
    bytes.forEach((byte) => { binary += String.fromCharCode(byte); });
    return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
  }

  function decodePayload(value) {
    try {
      const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
      const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
      const binary = atob(padded);
      const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
      const parsed = JSON.parse(new TextDecoder().decode(bytes));
      if (parsed.v !== 1 || !Number.isInteger(parsed.s) || parsed.s < 0 || parsed.s > 100) return null;
      if (!BANDS.some((band) => band.key === parsed.b)) return null;
      if (!Array.isArray(parsed.m) || parsed.m.length > 3 || parsed.m.some((id) => !ACTIONS[id])) return null;
      if (!LOCATION_TYPES.has(parsed.t)) return null;
      return parsed;
    } catch (_error) {
      return null;
    }
  }

  function shareUrl(payload) {
    const url = new URL(window.location.href);
    url.search = "";
    url.hash = `card=${encodePayload(payload)}`;
    return url.toString();
  }

  function checkedValue(name) {
    const input = form.querySelector(`input[name="${name}"]:checked`);
    return input ? input.value : null;
  }

  function collectAnswers() {
    const answers = {};
    QUESTION_IDS.forEach((id) => { answers[id] = checkedValue(id); });
    return answers;
  }

  function updateProgress() {
    const completed = QUESTION_IDS.filter((id) => Boolean(checkedValue(id))).length;
    progressText.textContent = `${completed} / ${QUESTION_IDS.length} alan tamamlandı`;
    progress.setAttribute("aria-valuenow", String(completed));
    progressBar.style.width = `${(completed / QUESTION_IDS.length) * 100}%`;
  }

  function validateAssessment() {
    document.querySelectorAll("fieldset.question-card.invalid").forEach((field) => field.classList.remove("invalid"));
    const missing = QUESTION_IDS.filter((id) => !checkedValue(id));
    missing.forEach((id) => form.querySelector(`[data-question="${id}"]`)?.classList.add("invalid"));

    if (dangerInput.checked) {
      validation.textContent = "Aktif tehlike işaretliyken dayanıklılık puanı oluşturulmaz. Güvenli uzaklaşın ve 112 yönünü kullanın.";
      validation.hidden = false;
      validation.focus();
      return false;
    }
    if (!LOCATION_TYPES.has(locationType.value) || missing.length) {
      validation.textContent = "Konum türünü ve yedi hazırlık alanının tamamını işaretleyin. Emin olmadığınız yerde “Bilmiyorum” veya kısmi seçeneğini kullanabilirsiniz.";
      validation.hidden = false;
      validation.focus();
      return false;
    }
    validation.hidden = true;
    return true;
  }

  function calculate(answers) {
    let score = 0;
    const deficits = [];
    QUESTION_IDS.forEach((id) => {
      const points = SCORE_MAP[id][answers[id]];
      score += points;
      const deficit = MAX_SCORES[id] - points;
      if (deficit > 0) deficits.push({ id, deficit, maximum: MAX_SCORES[id] });
    });
    deficits.sort((a, b) => b.deficit - a.deficit || b.maximum - a.maximum || a.id.localeCompare(b.id));
    const actionIds = deficits.slice(0, 3).map((item) => item.id);
    if (!actionIds.length) actionIds.push("maintenance", "share", "official");
    else if (actionIds.length === 1) actionIds.push("share", "maintenance");
    else if (actionIds.length === 2) actionIds.push("share");
    return { score, actionIds: actionIds.slice(0, 3) };
  }

  function actionCard(id, rank) {
    const action = ACTIONS[id];
    const element = document.createElement("article");
    element.className = "action-card";
    const rankElement = document.createElement("span");
    rankElement.className = "action-rank";
    rankElement.textContent = String(rank).padStart(2, "0");
    const title = document.createElement("h3");
    title.textContent = action.title;
    const copy = document.createElement("p");
    copy.textContent = action.copy;
    element.append(rankElement, title, copy);

    if (action.action === "share") {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `${action.cta} →`;
      button.addEventListener("click", () => {
        document.getElementById("shareActions").scrollIntoView({ behavior: "smooth", block: "center" });
        document.getElementById("shareButton").focus();
        emit("resilience_card_share", { result_band: lastPayload?.b, location_class: lastPayload?.t, share_channel: "action" });
      });
      element.append(button);
    } else {
      const link = document.createElement("a");
      link.href = action.href;
      link.textContent = `${action.cta} →`;
      if (id === "official") link.dataset.officialLink = "action";
      element.append(link);
    }
    return element;
  }

  function renderResult(payload, options = {}) {
    const band = BANDS.find((item) => item.key === payload.b) || bandFor(payload.s);
    lastPayload = payload;
    scoreValue.textContent = `${payload.s}/100`;
    bandValue.textContent = band.label;
    scoreCard.dataset.band = band.key;
    resultTitle.textContent = band.title;
    resultCopy.textContent = band.copy;
    actionList.replaceChildren(...payload.m.map((id, index) => actionCard(id, index + 1)));
    businessHandoff.hidden = !["site", "business"].includes(payload.t);
    results.hidden = false;

    if (options.focus !== false) {
      results.scrollIntoView({ behavior: options.instant ? "auto" : "smooth", block: "start" });
      results.focus({ preventScroll: true });
    }
  }

  function savePayload(payload) {
    if (!rememberResult.checked) {
      localStorage.removeItem(STORAGE_KEY);
      savedPanel.hidden = true;
      return;
    }
    const record = { payload, expiresAt: Date.now() + STORAGE_DAYS * 24 * 60 * 60 * 1000 };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(record));
    savedPanel.hidden = false;
  }

  function readSaved() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const record = JSON.parse(raw);
      if (!record || record.expiresAt < Date.now()) {
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }
      const payload = record.payload;
      if (!payload || payload.v !== 1 || !Number.isInteger(payload.s) || !ACTIONS[payload.m?.[0]]) return null;
      if (!LOCATION_TYPES.has(payload.t) || !BANDS.some((band) => band.key === payload.b)) return null;
      return payload;
    } catch (_error) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  }

  function showShareStatus(message) {
    shareStatus.textContent = message;
    window.setTimeout(() => {
      if (shareStatus.textContent === message) shareStatus.textContent = "";
    }, 7000);
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.append(area);
    area.select();
    const copied = document.execCommand("copy");
    area.remove();
    if (!copied) throw new Error("copy_failed");
  }

  async function shareCard() {
    if (!lastPayload) return;
    const band = BANDS.find((item) => item.key === lastPayload.b);
    const url = shareUrl(lastPayload);
    const data = {
      title: "ALO186 Elektrik Dayanıklılık Kartı",
      text: `Elektrik dayanıklılık sonucu: ${lastPayload.s}/100 · ${band.label}. İlk üç aksiyonu birlikte gözden geçirelim.`,
      url
    };
    try {
      if (navigator.share) {
        await navigator.share(data);
        emit("resilience_card_share", { result_band: lastPayload.b, location_class: lastPayload.t, share_channel: "native" });
        showShareStatus("Kart paylaşım menüsüne gönderildi.");
      } else {
        await copyText(url);
        emit("resilience_card_share", { result_band: lastPayload.b, location_class: lastPayload.t, share_channel: "clipboard" });
        showShareStatus("Güvenli sonuç bağlantısı kopyalandı.");
      }
    } catch (error) {
      if (error?.name !== "AbortError") showShareStatus("Paylaşım açılamadı. Bağlantıyı kopyalama seçeneğini kullanın.");
    }
  }

  function clearHash() {
    if (!window.location.hash) return;
    history.replaceState(null, "", `${window.location.pathname}${window.location.search}`);
  }

  function resetForNewCard(type = "") {
    form.reset();
    window.setTimeout(() => {
      locationType.value = type;
      results.hidden = true;
      sharedPanel.hidden = true;
      validation.hidden = true;
      clearHash();
      updateProgress();
      document.getElementById("assessment").scrollIntoView({ behavior: "smooth", block: "start" });
      locationType.focus();
    }, 0);
  }

  form.addEventListener("change", (event) => {
    if (event.target !== rememberResult) sendStartOnce();
    if (event.target === dangerInput) {
      emergencyPanel.hidden = !dangerInput.checked;
      calculateButton.disabled = dangerInput.checked;
      document.getElementById("questions").setAttribute("aria-disabled", dangerInput.checked ? "true" : "false");
      if (dangerInput.checked) emergencyPanel.focus();
    }
    updateProgress();
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendStartOnce();
    if (!validateAssessment()) return;
    const answers = collectAnswers();
    const calculated = calculate(answers);
    const band = bandFor(calculated.score);
    const payload = {
      v: 1,
      s: calculated.score,
      b: band.key,
      m: calculated.actionIds,
      t: locationType.value
    };
    renderResult(payload);
    savePayload(payload);
    emit("resilience_card_complete", { result_band: band.key, location_class: locationType.value });
  });

  form.addEventListener("reset", () => {
    window.setTimeout(() => {
      dangerInput.checked = false;
      emergencyPanel.hidden = true;
      calculateButton.disabled = false;
      validation.hidden = true;
      results.hidden = true;
      updateProgress();
    }, 0);
  });

  document.getElementById("shareButton").addEventListener("click", shareCard);
  document.getElementById("copyButton").addEventListener("click", async () => {
    if (!lastPayload) return;
    try {
      await copyText(shareUrl(lastPayload));
      emit("resilience_card_share", { result_band: lastPayload.b, location_class: lastPayload.t, share_channel: "clipboard" });
      showShareStatus("Güvenli sonuç bağlantısı kopyalandı.");
    } catch (_error) {
      showShareStatus("Bağlantı kopyalanamadı. Tarayıcının adres çubuğundaki bağlantıyı kullanın.");
    }
  });
  document.getElementById("printButton").addEventListener("click", () => {
    if (lastPayload) emit("resilience_card_share", { result_band: lastPayload.b, location_class: lastPayload.t, share_channel: "print" });
    window.print();
  });
  document.getElementById("relativeButton").addEventListener("click", () => {
    emit("resilience_card_relative_restart", { result_band: lastPayload?.b, location_class: lastPayload?.t });
    resetForNewCard("relative");
  });
  document.getElementById("editButton").addEventListener("click", () => {
    form.scrollIntoView({ behavior: "smooth", block: "start" });
    locationType.focus();
  });
  document.getElementById("startOwnCard").addEventListener("click", () => resetForNewCard(""));
  document.getElementById("restoreSaved").addEventListener("click", () => {
    const payload = readSaved();
    if (payload) {
      rememberResult.checked = true;
      renderResult(payload);
      emit("resilience_card_restore", { result_band: payload.b, location_class: payload.t });
    }
  });
  document.getElementById("deleteSaved").addEventListener("click", () => {
    localStorage.removeItem(STORAGE_KEY);
    savedPanel.hidden = true;
  });

  document.addEventListener("click", (event) => {
    const official = event.target.closest("[data-official-link]");
    if (official) emit("resilience_card_official_channel", { result_band: lastPayload?.b, location_class: lastPayload?.t });
    const business = event.target.closest("[data-business-handoff]");
    if (business) emit("resilience_card_business_handoff", { result_band: lastPayload?.b, location_class: lastPayload?.t });
  });

  const saved = readSaved();
  savedPanel.hidden = !saved;

  const hashMatch = window.location.hash.match(/^#card=([A-Za-z0-9_-]+)$/);
  if (hashMatch) {
    const payload = decodePayload(hashMatch[1]);
    if (payload) {
      const band = BANDS.find((item) => item.key === payload.b);
      sharedTitle.textContent = `${payload.s}/100 · ${band.label}`;
      sharedCopy.textContent = "Bu kartı paylaşan kişi, ilk üç hazırlık aksiyonunu sizinle birlikte gözden geçirmek istiyor.";
      sharedPanel.hidden = false;
      renderResult(payload, { instant: true, focus: false });
      window.setTimeout(() => sharedPanel.focus(), 0);
    } else {
      clearHash();
    }
  }

  updateProgress();
})();
