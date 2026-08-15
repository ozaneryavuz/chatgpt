(() => {
  'use strict';

  const form = document.getElementById('portableEvseForm');
  if (!form) return;

  const $ = (id) => document.getElementById(id);
  const gateIds = ['actualNeed', 'technicalCheck', 'affiliateCheck'];

  function rewriteCommerceLink() {
    queueMicrotask(() => {
      const links = $('productLinks')?.querySelectorAll('a[data-category="portable_evse"]') || [];
      links.forEach((link) => {
        link.href = '../../amazon-elektrik-urunleri/tasinabilir-evse-secimi/?source=tasinabilir-ev-sarj-priz';
        link.textContent = 'Taşınabilir EVSE teknik seçim rehberini aç';
        link.removeAttribute('target');
        link.removeAttribute('rel');
      });
    });
  }

  function clearOutput() {
    const result = $('result');
    const commerce = $('commerce');
    const nextTool = $('nextTool');

    if (result) {
      result.hidden = true;
      result.className = 'panel result';
    }
    if ($('resultBadge')) $('resultBadge').textContent = '';
    if ($('resultTitle')) $('resultTitle').textContent = '';
    if ($('resultSummary')) $('resultSummary').textContent = '';
    if ($('metrics')) $('metrics').innerHTML = '';

    if (nextTool) {
      nextTool.removeAttribute('href');
      nextTool.classList.add('hidden');
    }

    if (commerce) {
      commerce.classList.add('hidden');
      commerce.dataset.categories = '[]';
    }
    gateIds.forEach((id) => {
      const input = $(id);
      if (input) input.checked = false;
    });
    if ($('productLinks')) $('productLinks').innerHTML = '';

    if ($('outdoorEvidence')) $('outdoorEvidence').classList.add('hidden');
    if ($('existingFields')) $('existingFields').classList.add('hidden');
  }

  gateIds.forEach((id) => $(id)?.addEventListener('change', rewriteCommerceLink));

  form.addEventListener('reset', () => {
    window.setTimeout(() => {
      clearOutput();
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
      form.querySelector('select, input, button')?.focus({ preventScroll: true });
      if (window.Alo186Track) window.Alo186Track('portable_evse_socket_reset', { commercial_state: 'cleared' });
    }, 0);
  });

  window.Alo186PortableEvseState = { clearOutput, rewriteCommerceLink };
})();
