(() => {
  'use strict';

  const byId=id=>document.getElementById(id);

  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
  function formatDate(value){const date=new Date(value);return Number.isFinite(date.getTime())?new Intl.DateTimeFormat('tr-TR',{dateStyle:'medium'}).format(date):'Tarih yok';}
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}

  function injectStyles(){
    if(document.getElementById('evidenceLifecycleStyles'))return;
    const style=document.createElement('style');style.id='evidenceLifecycleStyles';style.textContent='.evidence-lifecycle{margin:44px 0;padding:24px;border:1px solid #b8c8e6;border-radius:22px;background:#f5f8ff}.evidence-lifecycle h2{margin:.35rem 0 .6rem;color:#071631}.evidence-lifecycle>p{color:#56667e}.evidence-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:18px}.evidence-card{padding:18px;border:1px solid #d7e1ef;border-left:7px solid #08745b;border-radius:16px;background:#fff}.evidence-card.expiring{border-left-color:#d19a00}.evidence-card.expired{border-left-color:#b42318}.evidence-card h3{margin:.3rem 0;color:#071631}.evidence-card p{margin:.35rem 0;color:#56667e}.evidence-card small{display:block;margin:.5rem 0}.evidence-empty{padding:20px;border:1px dashed #94a8c5;border-radius:16px;background:#fff;text-align:center}.evidence-status{display:inline-flex;padding:5px 9px;border-radius:999px;background:#dff5ec;color:#075843;font-size:.75rem;font-weight:900}.evidence-card.expiring .evidence-status{background:#fff0bd;color:#6e4900}.evidence-card.expired .evidence-status{background:#ffe1dc;color:#8b1b13}@media(max-width:760px){.evidence-grid{grid-template-columns:1fr}}';document.head.appendChild(style);
  }

  function ensureSection(){
    if(byId('technicalEvidenceLifecycle'))return byId('technicalEvidenceLifecycle');
    const section=document.createElement('section');section.id='technicalEvidenceLifecycle';section.className='evidence-lifecycle';section.innerHTML='<span class="eyebrow">Teknik kanıt · 45 günlük geçerlilik · tekrar ziyaret</span><h2>Teknik Doğrulama Cüzdanı</h2><p>Bir uygunluk aracından Akıllı Ürün Merkezi’ne geçtiğinizde yalnız kategori, araç yolu ve tarih cihazınızda tutulur. Ham hesap, ürün modeli, fiyat veya kişisel veri saklanmaz.</p><div id="technicalEvidenceGrid" class="evidence-grid" aria-live="polite"></div><p id="technicalEvidenceSummary" class="growth-status"></p>';
    const growth=document.querySelector('.growth-grid');if(growth)growth.insertAdjacentElement('afterend',section);else document.querySelector('main')?.appendChild(section);return section;
  }

  function render(){
    const wallet=window.Alo186EvidenceWallet;if(!wallet)return;
    injectStyles();ensureSection();const records=wallet.list(new Date());const grid=byId('technicalEvidenceGrid');if(!records.length){grid.innerHTML='<div class="evidence-empty"><strong>Henüz teknik doğrulama kaydı yok.</strong><p>Ürün aramadan önce ilgili ücretsiz uygunluk testini tamamlayın. Araçtan ürün merkezine geçtiğinizde kanıt otomatik oluşur.</p><a class="button primary" href="/hesaplama/">Ücretsiz araçları aç</a></div>';byId('technicalEvidenceSummary').textContent='Doğrulama kaydı yalnız teknik araçtan ürün merkezine geçişte oluşur.';return;}
    grid.innerHTML=records.map(item=>{const statusText=item.state==='current'?'Güncel':item.state==='expiring'?'Yakında doluyor':'Süresi doldu';const detail=item.state==='current'?`${item.daysLeft} gün daha geçerli.`:item.state==='expiring'?`${Math.max(0,item.daysLeft)} gün içinde ücretsiz aracı yeniden çalıştırın.`:'Yeni ürün karşılaştırmasından önce ücretsiz aracı yeniden çalıştırın.';const productRoute=`/akilli-urun-secimi?kategori=${encodeURIComponent(item.category)}`;return`<article class="evidence-card ${escapeHtml(item.state)}"><span class="evidence-status">${statusText}</span><h3>${escapeHtml(item.label)}</h3><p>${detail}</p><small>Son doğrulama: ${formatDate(item.record.completedAt)} · Bitiş: ${formatDate(item.record.expiresAt)}</small><div class="actions"><a class="button secondary" href="${escapeHtml(item.toolRoute)}" data-evidence-action="tool" data-category="${escapeHtml(item.category)}">Ücretsiz aracı aç</a>${item.state!=='expired'?`<a class="button primary" href="${productRoute}" data-evidence-action="product" data-category="${escapeHtml(item.category)}">Şeffaf ürün merkezine dön</a>`:''}</div></article>`;}).join('');
    const current=records.filter(item=>item.state==='current').length,expiring=records.filter(item=>item.state==='expiring').length,expired=records.filter(item=>item.state==='expired').length;byId('technicalEvidenceSummary').textContent=`${current} güncel, ${expiring} süresi yaklaşan, ${expired} süresi dolmuş teknik kanıt yalnız bu tarayıcıda tutuluyor.`;
    grid.querySelectorAll('[data-evidence-action]').forEach(link=>link.addEventListener('click',()=>emit('technical_evidence_lifecycle_opened',{category:link.dataset.category,status:link.dataset.evidenceAction,placement:'electrical_plan'})));
  }

  function loadWallet(){
    if(window.Alo186EvidenceWallet){render();return;}
    if(document.querySelector('script[data-plan-evidence-wallet]'))return;
    const script=document.createElement('script');script.src='../evidence-wallet.js';script.dataset.planEvidenceWallet='true';script.addEventListener('load',render,{once:true});document.head.appendChild(script);
  }

  function init(){loadWallet();window.addEventListener('alo186:evidence-updated',render);window.addEventListener('storage',event=>{if(event.key==='alo186:technical-evidence:v1')render();});}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
