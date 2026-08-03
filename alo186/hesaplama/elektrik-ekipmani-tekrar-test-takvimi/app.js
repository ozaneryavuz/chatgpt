(() => {
  "use strict";

  const TASKS = Object.freeze({
    internet: {
      title: "Modem / ONT / mini UPS görev testi",
      description: "Gerilim, akım, konnektör, polarite, gerçek bağlı yük ve hedef internet süresini yeniden doğrulayın.",
      route: "/hesaplama/modem-internet-yedekleme/"
    },
    portable: {
      title: "Powerbank / telefon / USB-C şarj yolu testi",
      description: "Powerbank, kablo, port gücü ve gerçek telefon şarj sonucunu birlikte yeniden deneyin.",
      route: "/hesaplama/powerbank-usb-c-uygunluk/"
    },
    lighting: {
      title: "Acil aydınlatma görev testi",
      description: "Şarj durumunu, erişilebilirliği, gerçek kullanım alanını ve hedef çalışma süresini yeniden test edin.",
      route: "/hesaplama/acil-aydinlatma-sure-uygunluk/"
    },
    cold: {
      title: "Soğuk zincir ve sıcaklık planı kontrolü",
      description: "Kapı açma planını, termometreyi, alternatif konumu ve ilaç için profesyonel talimatı yeniden doğrulayın.",
      route: "/hesaplama/kesinti-hazirlik-plani/"
    },
    warning: {
      title: "Duman / karbonmonoksit erken uyarı testi",
      description: "Üretici test yöntemini, pil durumunu, son kullanma veya değiştirme tarihini ve alarm duyulabilirliğini doğrulayın.",
      route: "/hesaplama/ekipman-bakim-plani/"
    },
    backup: {
      title: "UPS / batarya / jeneratör görev testi",
      description: "Gerçek yük, hedef süre, batarya durumu, yakıt, transfer, alarm ve güvenli durdurma adımlarını kayıt altına alın.",
      route: "/hesaplama/ekipman-bakim-plani/"
    }
  });

  const VALID_INTERVALS = new Set([30, 90, 365]);
  const form = document.getElementById("retestForm");
  const equipment = document.getElementById("equipment");
  const interval = document.getElementById("interval");
  const evidence = document.getElementById("evidence");
  const result = document.getElementById("result");
  const resetButton = document.getElementById("resetButton");

  function emit(event, task, days, status) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event, retest_task: task, retest_days: days, evidence_class: status });
  }

  function addDays(date, days) {
    const next = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    next.setDate(next.getDate() + days);
    return next;
  }

  function icsDate(date) {
    return `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, "0")}${String(date.getDate()).padStart(2, "0")}`;
  }

  function timestamp(date) {
    return date.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
  }

  function escapeIcs(value) {
    return value.replace(/\\/g, "\\\\").replace(/\n/g, "\\n").replace(/,/g, "\\,").replace(/;/g, "\\;");
  }

  function buildIcs(taskKey, days) {
    const task = TASKS[taskKey];
    const created = new Date();
    const start = addDays(created, days);
    const end = addDays(start, 1);
    const uid = `alo186-retest-${taskKey}-${icsDate(start)}@alo186.com`;
    const description = `${task.description}\n\nMevcut güvenli çözüm yeterliyse yeni ürün almayın. Hasarlı ekipmanı kullanmayın. Ücretsiz kontrol: https://alo186.com${task.route}`;
    return [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//ALO186//Elektrik Ekipmanı Tekrar Test Takvimi//TR",
      "CALSCALE:GREGORIAN",
      "METHOD:PUBLISH",
      "BEGIN:VEVENT",
      `UID:${uid}`,
      `DTSTAMP:${timestamp(created)}`,
      `DTSTART;VALUE=DATE:${icsDate(start)}`,
      `DTEND;VALUE=DATE:${icsDate(end)}`,
      `SUMMARY:${escapeIcs(task.title)}`,
      `DESCRIPTION:${escapeIcs(description)}`,
      "TRANSP:TRANSPARENT",
      "END:VEVENT",
      "END:VCALENDAR",
      ""
    ].join("\r\n");
  }

  function downloadIcs(taskKey, days) {
    const blob = new Blob([buildIcs(taskKey, days)], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `alo186-${taskKey}-${days}-gun-tekrar-test.ics`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    emit("equipment_retest_calendar_download", taskKey, days, evidence.value);
  }

  function show(message, type = "info") {
    result.dataset.type = type;
    result.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.innerHTML = message;
    result.appendChild(paragraph);
    result.hidden = false;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const taskKey = equipment.value;
    const days = Number(interval.value);
    const status = evidence.value;

    if (!TASKS[taskKey] || !VALID_INTERVALS.has(days) || !status) {
      show("Görev, hatırlatma aralığı ve son test kanıtını seçin.", "error");
      return;
    }

    if (status === "damaged") {
      show("<strong>Takvim kaydı oluşturulmadı.</strong> Hasarlı, ıslak, şişmiş, yanık kokulu veya aşırı ısınan ekipmanı test etmeyin ya da kullanmaya devam etmeyin. Güvenli ayırma ve yetkili teknik inceleme gerekir.", "blocked");
      emit("equipment_retest_blocked", taskKey, days, status);
      return;
    }

    const task = TASKS[taskKey];
    const note = status === "failed"
      ? "Önce arızanın veya kapasite kaybının kök nedenini doğrulayın; belirsizliği doğrudan satın alma gerekçesine dönüştürmeyin."
      : status === "startup"
        ? "Yalnız açılış kontrolü yeterli değildir; hatırlatma tarihinde gerçek yük ve hedef süreyle deneyin."
        : status === "unknown"
          ? "Kayıt bulunmadığı için mevcut ekipmanı değiştirmeden önce gerçek görev testi yapın."
          : "Mevcut çözüm yeterliyse yeni ürün almayın; sonucu ve hedef süreyi kaydedin.";

    result.replaceChildren();
    const title = document.createElement("h3");
    title.textContent = `${days} günlük tekrar test hazır`;
    const copy = document.createElement("p");
    copy.textContent = `${task.title}: ${note}`;
    const actions = document.createElement("div");
    actions.className = "actions";
    const download = document.createElement("button");
    download.type = "button";
    download.textContent = "Takvime ekle (.ics)";
    download.addEventListener("click", () => downloadIcs(taskKey, days), { once: true });
    const guide = document.createElement("a");
    guide.className = "button secondary";
    guide.href = task.route;
    guide.textContent = "Ücretsiz test rehberini aç";
    actions.append(download, guide);
    result.append(title, copy, actions);
    result.hidden = false;
    emit("equipment_retest_plan_created", taskKey, days, status);
  });

  resetButton.addEventListener("click", () => {
    form.reset();
    result.hidden = true;
    result.replaceChildren();
    equipment.focus();
  });
})();
