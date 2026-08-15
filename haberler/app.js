(() => {
  'use strict';
  const search = document.querySelector('#article-search');
  const cards = [...document.querySelectorAll('[data-article-card]')];
  const buttons = [...document.querySelectorAll('[data-category]')];
  const status = document.querySelector('[data-result-count]');
  const empty = document.querySelector('[data-empty]');
  if (!search || !cards.length || !status) return;

  let category = 'all';
  const normalise = (value) => String(value || '')
    .toLocaleLowerCase('tr-TR')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/ı/g, 'i')
    .replace(/[^a-z0-9çğıöşü\s-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const apply = () => {
    const query = normalise(search.value);
    let visible = 0;
    cards.forEach((card) => {
      const matchesCategory = category === 'all' || card.dataset.category === category;
      const matchesQuery = !query || normalise(card.dataset.search).includes(query);
      const show = matchesCategory && matchesQuery;
      card.hidden = !show;
      if (show) visible += 1;
    });
    status.textContent = query || category !== 'all'
      ? `${visible} makale eşleşti.`
      : `${visible} teknik makale gösteriliyor.`;
    if (empty) empty.hidden = visible !== 0;
  };

  buttons.forEach((button) => button.addEventListener('click', () => {
    category = button.dataset.category || 'all';
    buttons.forEach((item) => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    apply();
  }));
  search.addEventListener('input', apply);
  apply();
})();
