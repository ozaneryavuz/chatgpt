(() => {
  'use strict';

  const core=window.Alo186DecisionShortlistCore;
  const catalog=window.Alo186ProductCatalog;
  const trustCore=window.Alo186TrustGrowthCore;
  if(!core||!catalog)return;

  const storageKey='alo186_product_shortlist_v1';
  const $=id=>document.getElementById(id);
  let vault=[];

  function emit(name,params={}){
    if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);
  }
  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
  function activeCategory(){return document.querySelector('[data-category][aria-pressed="true"]')?.dataset.category||'';}
  function readVault(){
    try{
      const parsed=JSON.parse(localStorage.getItem(storageKey)||'[]');
      const clean=core.normalizeVault(parsed);
      if(JSON.stringify(clean)!==JSON.stringify(parsed))localStorage.setItem(storageKey,JSON.stringify(clean));
      return clean;
    }catch(_error){return [];}
  }
  function writeVault(items){
    vault=core.normalizeVault(items);
    try{localStorage.setItem(storageKey,JSON.stringify(vault));return true;}
    catch(_error){return false;}
  }
  function productById(id){return catalog.products.find(product=>product.id===id)||null;}
  function snapshotFromCard(card){
    const link=card.querySelector('[data-product]');
    const product=productById(link?.dataset.product);
    if(!link||!product)return null;
    const verification=card.querySelector('.verification')?.textContent||'';
    const unknownText=card.querySelector('.unknowns')?.textContent.replace(/^Yeniden doğrulayın:\s*/i,'')||'';
    return core.sanitizeSnapshot({
      productId:product.id,
      asin:product.asin,
      categoryId:activeCategory()||product.category,
      productName:product.name,
      brand:product.brand,
      score:Number(link.dataset.score),
      confidence:card.querySelector('.score-row span')?.textContent.replace(/^Uygunluk · güven\s*/i,'')||'',
      verifiedAt:product.verifiedAt,
      sourceNote:verification||product.sourceNote,
      unknowns:unknownText?unknownText.split(/[.;]\s*/).filter(Boolean):[],
      attributes:product.attributes||{}
    });
  }
  function isSaved(productId){return vault.some(item=>item.productId===productId);}
  function augmentCards(){
    document.querySelectorAll('#directResult .product-card').forEach(card=>{
      const link=card.querySelector('[data-product]');
      if(!link)return;
      const productId=link.dataset.product;
      if(!card.querySelector('[data-shortlist-add]')){
        const button=document.createElement('button');
        button.type='button';
        button.className='btn btn-secondary shortlist-add';
        button.dataset.shortlistAdd=productId;
        button.textContent=isSaved(productId)?'Kısa listede':'Kısa listeye ekle';
        button.disabled=isSaved(productId);
        card.querySelector('.product-actions')?.prepend(button);
      }
      link.dataset.originalHref=link.dataset.originalHref||link.href;
      link.textContent='Satın alma kontrolünü aç';
      link.removeAttribute('target');
    });
  }
  function renderVault(){
    vault=readVault();
    const section=$('productShortlist');
    const list=$('productShortlistList');
    const table=$('productShortlistCompare');
    if(!section||!list||!table)return;
    if(!vault.length){section.classList.add('hidden');list.innerHTML='';table.innerHTML='';return;}
    section.classList.remove('hidden');
    list.innerHTML=vault.map(item=>`<article class="shortlist-card"><div><span class="eyebrow">${escapeHtml(item.brand||'Doğrulanmış kart')}</span><h3>${escapeHtml(item.productName)}</h3><p>Uygunluk: ${item.score??'—'}/100 · Teknik kontrol: ${escapeHtml(item.verifiedAt||'—')}</p><small>${core.daysUntilExpiry(item)} gün içinde yeniden kontrol edin.</small></div><div class="actions"><button type="button" class="btn btn-secondary" data-shortlist-recheck="${escapeHtml(item.categoryId)}">İhtiyacı yeniden kontrol et</button><button type="button" class="btn btn-secondary" data-shortlist-remove="${escapeHtml(item.productId)}">Sil</button></div></article>`).join('');
    const rows=core.comparisonRows(vault);
    const header=vault.map(item=>`<th scope="col">${escapeHtml(item.productName)}</th>`).join('');
    const body=rows.length?rows.map(row=>`<tr><th scope="row">${escapeHtml(row.label)}</th>${row.values.map(value=>`<td>${escapeHtml(value)}</td>`).join('')}</tr>`).join(''):'<tr><td colspan="4">Karşılaştırılabilir teknik alan bulunamadı; ürün sayfasındaki etiketleri yeniden doğrulayın.</td></tr>';
    table.innerHTML=`<div class="table-scroll"><table><thead><tr><th scope="col">Teknik alan</th>${header}</tr></thead><tbody>${body}</tbody></table></div><p class="shortlist-note">Karşılaştırma yalnız katalogda doğrulanmış teknik alanları gösterir. Fiyat, stok, satıcı, teslimat ve garanti bilgisi içermez.</p>`;
    document.querySelectorAll('[data-shortlist-add]').forEach(button=>{button.disabled=isSaved(button.dataset.shortlistAdd);button.textContent=button.disabled?'Kısa listede':'Kısa listeye ekle';});
  }
  function addToVault(card){
    const snapshot=snapshotFromCard(card);
    const status=$('productShortlistStatus');
    if(!snapshot){if(status)status.textContent='Ürün teknik özeti oluşturulamadı.';return;}
    if(vault.length>=core.limit&&!isSaved(snapshot.productId)){
      if(status)status.textContent=`Kısa liste en fazla ${core.limit} ürün tutar. Önce bir ürünü silin.`;
      emit('product_shortlist_blocked',{reason:'limit',category:snapshot.categoryId});
      return;
    }
    if(writeVault(core.upsert(vault,snapshot))){
      if(status)status.textContent='Ürün kısa listeye eklendi. Kayıt 30 gün yalnız bu tarayıcıda tutulur.';
      emit('product_shortlist_added',{category:snapshot.categoryId,product_id:snapshot.productId,count:vault.length});
      renderVault();
    }else if(status)status.textContent='Tarayıcı depolaması kapalı olduğu için kısa liste kaydedilemedi.';
  }
  function removeFromVault(productId){
    const item=vault.find(entry=>entry.productId===productId);
    writeVault(core.remove(vault,productId));
    renderVault();
    emit('product_shortlist_removed',{category:item?.categoryId||'unknown',product_id:productId,count:vault.length});
  }
  function clearVault(){
    try{localStorage.removeItem(storageKey);}catch(_error){/* no-op */}
    vault=[];renderVault();
    const status=$('productShortlistStatus');if(status)status.textContent='Kısa liste cihazınızdan silindi.';
    emit('product_shortlist_cleared');
  }
  function recheckCategory(categoryId){
    const button=document.querySelector(`[data-category="${CSS.escape(categoryId)}"]`);
    if(!button)return;
    button.click();
    document.getElementById('matcher')?.scrollIntoView({behavior:'smooth',block:'start'});
    emit('product_shortlist_recheck_opened',{category:categoryId});
  }
  function gateMarkup(product,href){
    const limits=product?.limits?.length?product.limits:['Ürün sayfasındaki teknik alanları yeniden doğrulayın.'];
    return `<div class="affiliate-decision-gate" data-affiliate-gate><h4>Satın alma bağlantısından önce son kontrol</h4><p><strong>Reklam / satış ortaklığı:</strong> Bu bağlantıdan nitelikli satın alım yapılırsa ALO186 komisyon kazanabilir; kullanıcıya ek maliyet yansımaz.</p><label class="check-item"><input type="checkbox" data-gate-need><span><b>Mevcut ekipmanım ihtiyacımı karşılamıyor veya ek ürün ihtiyacını doğruladım.</b><br><small>Satın almamak geçerli bir sonuçtur.</small></span></label><label class="check-item"><input type="checkbox" data-gate-technical><span><b>Teknik sınırları ürün sayfasında yeniden kontrol edeceğim.</b><small class="gate-limits"><span>Özellikle:</span><ul>${limits.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul></small></span></label><label class="check-item"><input type="checkbox" data-gate-affiliate><span><b>Bağlantının satış ortaklığı bağlantısı olduğunu anlıyorum.</b><br><small>Fiyat, stok, satıcı, teslimat ve garanti Amazon’da doğrulanır.</small></span></label><div class="actions"><a class="btn btn-primary disabled-link" data-gate-open href="${escapeHtml(href)}" target="_blank" rel="sponsored nofollow noopener" aria-disabled="true" tabindex="-1">Amazon ürün sayfasını aç</a><button type="button" class="btn btn-secondary" data-gate-no-purchase>Şimdilik satın alma</button></div><p class="gate-status" role="status"></p></div>`;
  }
  function blockedMarkup(result,productId){
    return `<div class="affiliate-decision-gate affiliate-confidence-block" data-affiliate-confidence-block><h4>Doğrudan ürün bağlantısı açılmadı</h4><p>${escapeHtml(result.message||'Teknik karar tamamlanmadan ürün bağlantısı gösterilmez.')}</p><div class="actions"><button type="button" class="btn btn-primary" data-confidence-save>Teknik ihtiyacı cihazımda sakla</button><button type="button" class="btn btn-secondary" data-confidence-recheck>Teknik minimumlara dön</button></div><small>Ürün kısa listede tutulabilir; ancak eksik teknik veri veya yeterli mevcut ekipman varken ticari bağlantı açılmaz.</small><p class="gate-status" role="status">Engel nedeni: ${escapeHtml(result.reason||'trust_gate')}.</p><input type="hidden" value="${escapeHtml(productId)}" data-confidence-product></div>`;
  }
  function trustAssessment(card){
    const viaUi=window.Alo186TrustGrowth?.evaluateCard?.(card);
    if(viaUi)return viaUi;
    if(!trustCore)return {allowed:true,reason:'legacy_gate',message:''};
    const snapshot=snapshotFromCard(card);
    return trustCore.affiliateEligibility({
      existingStatus:window.Alo186TrustGrowth?.getState?.().existingStatus||'none',
      confidence:snapshot?.confidence,
      unknowns:snapshot?.unknowns,
      score:snapshot?.score,
      verifiedAt:snapshot?.verifiedAt
    });
  }
  function renderConfidenceBlock(card,result,productId){
    let block=card.querySelector('[data-affiliate-confidence-block]');
    if(!block){
      card.querySelector('.product-actions')?.insertAdjacentHTML('beforeend',blockedMarkup(result,productId));
      block=card.querySelector('[data-affiliate-confidence-block]');
      block.querySelector('[data-confidence-save]')?.addEventListener('click',()=>{
        const save=$('saveBriefBtn');
        if(save){save.click();$('decisionBrief')?.scrollIntoView({behavior:'smooth',block:'nearest'});}
        else $('decisionBrief')?.scrollIntoView({behavior:'smooth',block:'nearest'});
      });
      block.querySelector('[data-confidence-recheck]')?.addEventListener('click',()=>$('requirements')?.scrollIntoView({behavior:'smooth',block:'start'}));
      emit('affiliate_confidence_blocked',{category:activeCategory(),product_id:productId,reason:result.reason||'trust_gate'});
    }
    block.scrollIntoView({behavior:'smooth',block:'nearest'});
  }
  function openAffiliateGate(link){
    const card=link.closest('.product-card');
    if(!card)return;
    const trust=trustAssessment(card);
    if(trust&&!trust.allowed){renderConfidenceBlock(card,trust,link.dataset.product);return;}
    card.querySelector('[data-affiliate-confidence-block]')?.remove();
    let gate=card.querySelector('[data-affiliate-gate]');
    if(!gate){
      const product=productById(link.dataset.product);
      card.querySelector('.product-actions')?.insertAdjacentHTML('beforeend',gateMarkup(product,link.dataset.originalHref||link.href));
      gate=card.querySelector('[data-affiliate-gate]');
      const checks=[gate.querySelector('[data-gate-need]'),gate.querySelector('[data-gate-technical]'),gate.querySelector('[data-gate-affiliate]')];
      const open=gate.querySelector('[data-gate-open]');
      const sync=()=>{
        const enabled=core.gateAllowed({needConfirmed:checks[0].checked,technicalConfirmed:checks[1].checked,affiliateConfirmed:checks[2].checked});
        open.classList.toggle('disabled-link',!enabled);
        open.setAttribute('aria-disabled',enabled?'false':'true');
        open.tabIndex=enabled?0:-1;
        gate.querySelector('.gate-status').textContent=enabled?'Kontroller tamamlandı. Bağlantı açılabilir.':'Üç kontrolü tamamlayın veya satın almadan çıkın.';
      };
      checks.forEach(check=>check.addEventListener('change',sync));
      open.addEventListener('click',event=>{
        if(open.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}
        emit('affiliate_verified_product_opened',{category:activeCategory(),product_id:link.dataset.product,gate:'existing_need_confidence_technical_disclosure'});
      });
      gate.querySelector('[data-gate-no-purchase]').addEventListener('click',()=>{
        gate.remove();
        emit('affiliate_no_purchase_selected',{category:activeCategory(),product_id:link.dataset.product});
      });
      emit('affiliate_verified_product_gate_opened',{category:activeCategory(),product_id:link.dataset.product});
    }
    gate.scrollIntoView({behavior:'smooth',block:'nearest'});
  }
  function bindEvents(){
    document.addEventListener('click',event=>{
      const add=event.target.closest?.('[data-shortlist-add]');
      if(add){addToVault(add.closest('.product-card'));return;}
      const remove=event.target.closest?.('[data-shortlist-remove]');
      if(remove){removeFromVault(remove.dataset.shortlistRemove);return;}
      const recheck=event.target.closest?.('[data-shortlist-recheck]');
      if(recheck){recheckCategory(recheck.dataset.shortlistRecheck);return;}
      const productLink=event.target.closest?.('#directResult [data-product]');
      if(productLink){
        event.preventDefault();
        event.stopImmediatePropagation();
        openAffiliateGate(productLink);
      }
    },true);
    $('clearProductShortlistBtn')?.addEventListener('click',clearVault);
  }
  function bindObserver(){
    const result=document.getElementById('directResult');
    if(!result)return;
    const observer=new MutationObserver(()=>{augmentCards();renderVault();window.Alo186TrustGrowth?.refresh?.();});
    observer.observe(result,{subtree:true,childList:true});
  }

  document.addEventListener('DOMContentLoaded',()=>{
    vault=readVault();
    bindEvents();
    bindObserver();
    augmentCards();
    renderVault();
  });
})();
