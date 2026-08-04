(() => {
  'use strict';

  const STORAGE_KEY = 'alo186.outageJournal.v1';
  const BUSINESS_DAYS = 10;
  const SOURCE_URL = 'https://www.epdk.gov.tr/Detay/Icerik/12-3/1-elektrik-aboneligini-kendi-adima-almak-zorunda';
  const ARTICLE_URL = '/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu';
  const panel = document.getElementById('damageDeadlinePlanner');
  const summary = document.getElementById('damageDeadlineSummary');
  const entriesHost = document.getElementById('damageDeadlineEntries');
  const reminderButton = document.getElementById('damageReminderBtn');

  if (!panel || !summary || !entriesHost || !reminderButton) return;

  let currentDamageEntries = [];

  const parseLocalDate = (value) => {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value || ''));
    if (!match) return null;
    const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]), 12, 0, 0, 0);
    return Number.isNaN(date.getTime()) ? null : date;
  };

  const dateKey = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const formatDate = (date) => new Intl.DateTimeFormat('tr-TR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(date);

  const isWeekend = (date) => date.getDay() === 0 || date.getDay() === 6;

  const addBusinessDays = (startDate, count) => {
    const date = new Date(startDate.getTime());
    let added = 0;
    while (added < count) {
      date.setDate(date.getDate() + 1);
      if (!isWeekend(date)) added += 1;
    }
    return date;
  };

  const remainingCalendarDays = (deadline, today = new Date()) => {
    const start = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 12);
    const end = new Date(deadline.getFullYear(), deadline.getMonth(), deadline.getDate(), 12);
    return Math.ceil((end.getTime() - start.getTime()) / 86400000);
  };

  const loadDamageEntries = () => {
    try {
      const state = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
      if (!state || !Array.isArray(state.entries)) return [];
      return state.entries
        .filter((entry) => entry && entry.deviceDamage === true)
        .map((entry) => {
          const eventDate = parseLocalDate(entry.date);
          if (!eventDate) return null;
          return {
            id: String(entry.id || entry.date),
            eventDate,
            deadline: addBusinessDays(eventDate, BUSINESS_DAYS),
          };
        })
        .filter(Boolean)
        .sort((a, b) => a.deadline - b.deadline);
    } catch (_) {
      return [];
    }
  };

  const deadlineStatus = (entry) => {
    const remaining = remainingCalendarDays(entry.deadline);
    if (remaining < 0) return { className: 'expired', text: 'Planlama tarihi geçmiş görünüyor; yine de resmî kayıt oluşturup gerekçeli yanıt isteyin.' };
    if (remaining === 0) return { className: 'urgent', text: 'Yaklaşık planlama tarihi bugün. Resmî kanalı gecikmeden kullanın.' };
    if (remaining <= 3) return { className: 'urgent', text: `Yaklaşık ${remaining} takvim günü kaldı. Resmî başvuruyu geciktirmeyin.` };
    return { className: 'open', text: `Yaklaşık ${remaining} takvim günü kaldı.` };
  };

  const render = () => {
    currentDamageEntries = loadDamageEntries();
    panel.hidden = currentDamageEntries.length === 0;
    if (!currentDamageEntries.length) {
      summary.textContent = '';
      entriesHost.replaceChildren();
      reminderButton.disabled = true;
      return;
    }

    const earliest = currentDamageEntries[0];
    summary.innerHTML = `<strong>${currentDamageEntries.length} cihaz hasarı şüphesi için yerel süre planı hazır.</strong> En erken yaklaşık tarih <b>${formatDate(earliest.deadline)}</b>. Bu tarih yalnız hafta sonlarını dışlayan yardımcı bir hesaplamadır; resmî tatilleri otomatik hesaplamaz ve resmî uygunluk kararı değildir.`;
    entriesHost.innerHTML = currentDamageEntries.map((entry) => {
      const status = deadlineStatus(entry);
      return `<li class="damage-deadline-item ${status.className}"><span><b>Olay tarihi:</b> ${formatDate(entry.eventDate)}</span><span><b>10 iş günü için yardımcı tarih:</b> ${formatDate(entry.deadline)}</span><small>${status.text}</small></li>`;
    }).join('');
    reminderButton.disabled = false;
  };

  const escapeIcs = (value) => String(value)
    .replace(/\\/g, '\\\\')
    .replace(/\n/g, '\\n')
    .replace(/,/g, '\\,')
    .replace(/;/g, '\\;');

  const icsDate = (date) => `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`;

  const createReminder = () => {
    if (!currentDamageEntries.length) return;
    const earliest = currentDamageEntries[0];
    const reminderDate = new Date(earliest.deadline.getTime());
    reminderDate.setDate(reminderDate.getDate() - 1);
    while (isWeekend(reminderDate)) reminderDate.setDate(reminderDate.getDate() - 1);
    const endDate = new Date(reminderDate.getTime());
    endDate.setDate(endDate.getDate() + 1);
    const now = new Date();
    const stamp = `${now.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z')}`;
    const uid = `alo186-cihaz-hasari-${dateKey(earliest.eventDate)}-${dateKey(earliest.deadline)}@alo186.com`;
    const description = [
      'EPDK tüketici açıklamasındaki 10 iş günlük süre için yardımcı hatırlatmadır.',
      'Resmî tatiller otomatik hesaplanmamıştır. Sonucu dağıtım şirketinin resmî kanalı belirler.',
      `ALO186 rehberi: https://alo186.com${ARTICLE_URL}`,
      `EPDK kaynağı: ${SOURCE_URL}`,
    ].join('\n');
    const ics = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ALO186//Cihaz Hasarı Süre Planı v258//TR',
      'CALSCALE:GREGORIAN',
      'METHOD:PUBLISH',
      'BEGIN:VEVENT',
      `UID:${escapeIcs(uid)}`,
      `DTSTAMP:${stamp}`,
      `DTSTART;VALUE=DATE:${icsDate(reminderDate)}`,
      `DTEND;VALUE=DATE:${icsDate(endDate)}`,
      `SUMMARY:${escapeIcs('Cihaz hasarı resmî başvuru süresini kontrol et')}`,
      `DESCRIPTION:${escapeIcs(description)}`,
      `URL:${SOURCE_URL}`,
      'TRANSP:TRANSPARENT',
      'END:VEVENT',
      'END:VCALENDAR',
      '',
    ].join('\r\n');
    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `alo186-cihaz-hasari-hatirlatma-${dateKey(reminderDate)}.ics`;
    link.click();
    URL.revokeObjectURL(link.href);
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: 'outage_damage_deadline_reminder_created',
      damage_entry_count_bucket: currentDamageEntries.length > 1 ? 'multiple' : 'single',
    });
  };

  reminderButton.addEventListener('click', createReminder);
  window.addEventListener('storage', (event) => {
    if (event.key === STORAGE_KEY) render();
  });
  const journalRows = document.getElementById('entryRows');
  if (journalRows) new MutationObserver(render).observe(journalRows, { childList: true, subtree: true });
  render();
})();
