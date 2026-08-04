(() => {
  'use strict';

  const STORAGE_KEY = 'alo186.outageJournal.v1';
  const CALENDAR_DAYS = 30;
  const SOURCE_URL = 'https://www.resmigazete.gov.tr/eskiler/2020/12/20201229M1-1.htm';
  const AMENDMENT_URL = 'https://www.resmigazete.gov.tr/eskiler/2025/10/20251023-5.htm';
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

  const addCalendarDays = (startDate, count) => {
    const date = new Date(startDate.getTime());
    date.setDate(date.getDate() + count);
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
            deadline: addCalendarDays(eventDate, CALENDAR_DAYS),
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
    if (remaining < 0) return { className: 'expired', text: 'Yaklaşık süre geçmiş görünüyor; yine de resmî kayıt oluşturup gerekçeli yanıt isteyin.' };
    if (remaining === 0) return { className: 'urgent', text: 'Yaklaşık son gün bugün. Resmî kanalı gecikmeden kullanın.' };
    if (remaining <= 3) return { className: 'urgent', text: `Yaklaşık ${remaining} gün kaldı. Resmî başvuruyu geciktirmeyin.` };
    return { className: 'open', text: `Yaklaşık ${remaining} gün kaldı.` };
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
    summary.innerHTML = `<strong>${currentDamageEntries.length} cihaz hasarı şüphesi için yerel süre planı hazır.</strong> En erken yaklaşık tarih <b>${formatDate(earliest.deadline)}</b>. Kalite Yönetmeliği Madde 26/1 kapsamında 30 takvim günü eklenerek hesaplanmıştır; resmî uygunluk veya tazminat kararı değildir.`;
    entriesHost.innerHTML = currentDamageEntries.map((entry) => {
      const status = deadlineStatus(entry);
      return `<li class="damage-deadline-item ${status.className}"><span><b>Olay tarihi:</b> ${formatDate(entry.eventDate)}</span><span><b>30 gün için yardımcı tarih:</b> ${formatDate(entry.deadline)}</span><small>${status.text}</small></li>`;
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
    const reminderDate = addCalendarDays(earliest.deadline, -3);
    const endDate = addCalendarDays(reminderDate, 1);
    const now = new Date();
    const stamp = now.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
    const uid = `alo186-cihaz-hasari-${dateKey(earliest.eventDate)}-${dateKey(earliest.deadline)}@alo186.com`;
    const description = [
      'Kalite Yönetmeliği Madde 26/1 kapsamındaki 30 günlük talep süresi için yardımcı hatırlatmadır.',
      'Hasarın dağıtım sisteminden kaynaklandığını ve sürecin sonucunu dağıtım şirketinin teknik incelemesi belirler.',
      `ALO186 rehberi: https://alo186.com${ARTICLE_URL}`,
      `Kalite Yönetmeliği: ${SOURCE_URL}`,
      `23 Ekim 2025 değişikliği: ${AMENDMENT_URL}`,
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
      `SUMMARY:${escapeIcs('Cihaz hasarı resmî talep süresini kontrol et')}`,
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
