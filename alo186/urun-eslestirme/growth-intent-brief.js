(() => {
  'use strict';

  const vaultKey='alo186_product_briefs_v1';
  const vaultLimit=3;
  const retentionDays=30;
  const intentAliases={
    internet:'mini_ups',
    mobil:'powerbank',
    tasinabilir:'power_station',
    darbe:'surge_strip',
    yangin:'smoke_alarm',
    olcum:'outlet_tester'
  };
  let currentBrief=null;
  let refreshTimer=null;

  const $=id=>document.getElementById(id);

  function emit(name,params={}){
    if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);
  }

  function escapeHtml(value){
    return String(value??'').replace(/[&<>"']/g,ch=>({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[ch]));
  }

  function activeCategoryId(){
    return document.querySelector('[data-category][aria-pressed="true"]')?.dataset.category||null;
  }

  function selectCategory(category,source='intent_shortcut'){
    const button=document.querySelector(`[data-category="${CSS.escape(category)}"]`);
    if(!button)return false;
    button.click();
    emit('product_intent_shortcut_selected',{category,source});
    return true;
  }

  function bindIntentShortcuts(){
    document.querySelectorAll('[data-intent-category]').forEach(button=>{
      button.addEventListener('click',()=>selectCategory(button.dataset.intentCategory));
    });
    const query=new URLSearchParams(location.search).get('niyet');
    if(query&&intentAliases[query])window.setTimeout(()=>selectCategory(intentAliases[query],'query_intent'),0);
  }

  function captureFields(){
    const fields={};
    document.querySelectorAll('#requirementFields [data-field]').forEach(input=>{
      fields[input.dataset.field]={
        type:input.type||input.tagName.toLowerCase(),
        value:input.type==='checkbox'?Boolean(input.checked):String(input.value??'')
      };
    });
    return fields;
  }

  function restoreFields(fields={}){
    Object.entries(fields).forEach(([name,state])=>{
      const input=document.querySelector(`#requirementFields [data-field="${CSS.escape(name)}"]`);
      if(!input)return;
      if(input.type==='checkbox')input.checked=Boolean(state.value);
      else input.value=String(state.value??'');
      input.dispatchEvent(new Event('change',{bubbles:true}));
    });
  }

  function directCandidates(){
    return [...document.querySelectorAll('#directResult .product-card')].slice(0,3).map(card=>({
      name:card.querySelector('h3')?.textContent.trim()||'Teknik eşleşme',
      score:card.querySelector('.score-row strong')?.textContent.trim()||null,
      unknowns:card.querySelector('.unknowns')?.textContent.trim()||null,
      verification:card.querySelector('.verification')?.textContent.trim()||null
    }));
  }

  function visibleCriteria(){
    const guideItems=[...document.querySelectorAll('#guideResult .guide-item')].map(item=>{
      const title=item.querySelector('b')?.textContent.trim();
      const text=item.querySelector('span')?.textContent.trim();
      return [title,text].filter(Boolean).join(': ');
    }).filter(Boolean);
    if(guideItems.length)return guideItems;
    const candidates=directCandidates();
    const criteria=[];
    candidates.forEach(candidate=>{
      if(candidate.unknowns)criteria.push(`${candidate.name} — ${candidate.unknowns}`);
      if(candidate.verification)criteria.push(`${candidate.name} — ${candidate.verification}`);
    });
    return criteria.slice(0,8);
  }

  function buildBrief(){
    const categoryId=activeCategoryId();
    const result=$('results');
    if(!categoryId||!result||result.classList.contains('hidden'))return null;
    const categoryName=$('resultTitle')?.textContent.trim()||categoryId;
    const requirementSummary=$('requirementsChip')?.textContent.trim()||'Teknik minimumlar kullanıcı tarafından seçildi.';
    const resultSummary=$('resultText')?.textContent.trim()||'';
    const now=new Date();
    const reviewAt=new Date(now.getTime()+retentionDays*86400000);
    const mode=!$('guideResult')?.classList.contains('hidden')?'guide':'direct';
    return {
      schemaVersion:1,
      categoryId,
      categoryName,
      mode,
      requirementSummary,
      resultSummary,
      fields:captureFields(),
      criteria:visibleCriteria(),
      candidates:mode==='direct'?directCandidates():[],
      savedAt:now.toISOString(),
      reviewAt:reviewAt.toISOString(),
      disclosure:'ALO186 ürün satıcısı veya resmî kurum değildir. Fiyat, stok, satıcı, garanti ve nihai teknik özellik satıcının güncel sayfasında doğrulanmalıdır.'
    };
  }

  function briefText(brief){
    const lines=[
      'ALO186 Teknik İhtiyaç Özeti',
      `Kategori: ${brief.categoryName}`,
      `Teknik minimum: ${brief.requirementSummary}`,
      `Sonuç: ${brief.resultSummary}`,
      `Hazırlanma: ${formatDate(brief.savedAt)}`,
      `Yeniden kontrol: ${formatDate(brief.reviewAt)}`
    ];
    if(brief.criteria.length){
      lines.push('','Satın almadan önce doğrulanacak alanlar:');
      brief.criteria.forEach(item=>lines.push(`- ${item}`));
    }
    if(brief.candidates.length){
      lines.push('','ALO186 katalog eşleşmeleri:');
      brief.candidates.forEach(item=>lines.push(`- ${item.name}${item.score?` (${item.score})`:''}${item.unknowns?` — ${item.unknowns}`:''}`));
    }
    lines.push('',brief.disclosure,'Bu özet fiyat teklifi, uygunluk belgesi veya satın alma önerisi değildir.');
    return lines.join('\n');
  }

  function renderBrief(){
    const section=$('decisionBrief');
    if(!section)return;
    currentBrief=buildBrief();
    if(!currentBrief){section.classList.add('hidden');return;}
    $('briefCategory').textContent=currentBrief.categoryName;
    $('briefRequirement').textContent=currentBrief.requirementSummary;
    $('briefResult').textContent=currentBrief.resultSummary;
    $('briefReviewDate').textContent=formatDate(currentBrief.reviewAt);
    const list=$('briefCriteria');
    list.innerHTML=currentBrief.criteria.length?currentBrief.criteria.map(item=>`<li>${escapeHtml(item)}</li>`).join(''):'<li>Ürün sayfasındaki teknik minimumları ve kullanım sınırlarını yeniden doğrulayın.</li>';
    section.classList.remove('hidden');
  }

  function formatDate(value){
    const date=new Date(value);
    return Number.isFinite(date.getTime())?new Intl.DateTimeFormat('tr-TR',{day:'2-digit',month:'long',year:'numeric'}).format(date):'—';
  }

  function readVault(){
    try{
      const parsed=JSON.parse(localStorage.getItem(vaultKey)||'[]');
      if(!Array.isArray(parsed))return [];
      const now=Date.now();
      const clean=parsed.filter(item=>item&&item.categoryId&&new Date(item.reviewAt).getTime()>now).slice(0,vaultLimit);
      if(clean.length!==parsed.length)localStorage.setItem(vaultKey,JSON.stringify(clean));
      return clean;
    }catch(_error){return [];}
  }

  function writeVault(items){
    try{localStorage.setItem(vaultKey,JSON.stringify(items.slice(0,vaultLimit)));return true;}
    catch(_error){return false;}
  }

  function briefSignature(brief){
    return JSON.stringify([brief.categoryId,brief.fields]);
  }

  function saveCurrentBrief(){
    if(!currentBrief)return;
    const items=readVault().filter(item=>briefSignature(item)!==briefSignature(currentBrief));
    items.unshift({...currentBrief,savedAt:new Date().toISOString(),reviewAt:new Date(Date.now()+retentionDays*86400000).toISOString()});
    if(writeVault(items)){
      renderVault();
      $('briefStatus').textContent=`Teknik ihtiyaç dosyanıza eklendi. En fazla ${vaultLimit} kayıt, ${retentionDays} gün cihazınızda tutulur.`;
      emit('product_brief_saved',{category:currentBrief.categoryId,vault_count:Math.min(items.length,vaultLimit)});
    }else $('briefStatus').textContent='Tarayıcı depolaması kapalı olduğu için kayıt yapılamadı.';
  }

  function renderVault(){
    const section=$('briefVault');
    const list=$('briefVaultList');
    if(!section||!list)return;
    const items=readVault();
    if(!items.length){section.classList.add('hidden');list.innerHTML='';return;}
    list.innerHTML=items.map((item,index)=>`<article class="brief-vault-card"><div><span class="eyebrow">${escapeHtml(formatDate(item.savedAt))}</span><h3>${escapeHtml(item.categoryName)}</h3><p>${escapeHtml(item.requirementSummary)}</p><small>Yeniden kontrol: ${escapeHtml(formatDate(item.reviewAt))}</small></div><div class="actions"><button type="button" class="btn btn-primary" data-brief-load="${index}">Yeniden aç</button><button type="button" class="btn btn-secondary" data-brief-delete="${index}">Sil</button></div></article>`).join('');
    list.querySelectorAll('[data-brief-load]').forEach(button=>button.addEventListener('click',()=>loadBrief(Number(button.dataset.briefLoad))));
    list.querySelectorAll('[data-brief-delete]').forEach(button=>button.addEventListener('click',()=>deleteBrief(Number(button.dataset.briefDelete))));
    section.classList.remove('hidden');
  }

  function loadBrief(index){
    const item=readVault()[index];
    if(!item||!selectCategory(item.categoryId,'saved_brief'))return;
    window.setTimeout(()=>{
      restoreFields(item.fields||{});
      $('matchBtn')?.click();
      emit('product_brief_restored',{category:item.categoryId});
    },0);
  }

  function deleteBrief(index){
    const items=readVault();
    const removed=items.splice(index,1)[0];
    writeVault(items);
    renderVault();
    emit('product_brief_deleted',{category:removed?.categoryId||'unknown'});
  }

  function clearVault(){
    try{localStorage.removeItem(vaultKey);}catch(_error){/* no-op */}
    renderVault();
    emit('product_brief_vault_cleared');
  }

  async function copyBrief(){
    if(!currentBrief)return;
    const text=briefText(currentBrief);
    try{
      await navigator.clipboard.writeText(text);
      $('briefStatus').textContent='Teknik özet panoya kopyalandı.';
    }catch(_error){
      const area=document.createElement('textarea');
      area.value=text;area.setAttribute('readonly','');area.style.position='fixed';area.style.opacity='0';
      document.body.appendChild(area);area.select();document.execCommand('copy');area.remove();
      $('briefStatus').textContent='Teknik özet panoya kopyalandı.';
    }
    emit('product_brief_copied',{category:currentBrief.categoryId});
  }

  function downloadBrief(){
    if(!currentBrief)return;
    const safeCategory=currentBrief.categoryId.replace(/[^a-z0-9_-]/gi,'-');
    const blob=new Blob([JSON.stringify(currentBrief,null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;link.download=`alo186-${safeCategory}-teknik-ihtiyac.json`;document.body.appendChild(link);link.click();link.remove();
    URL.revokeObjectURL(url);
    $('briefStatus').textContent='Kişisel veri içermeyen JSON özeti indirildi.';
    emit('product_brief_downloaded',{category:currentBrief.categoryId});
  }

  function printBrief(){
    if(!currentBrief)return;
    document.body.classList.add('print-brief-mode');
    const cleanup=()=>document.body.classList.remove('print-brief-mode');
    window.addEventListener('afterprint',cleanup,{once:true});
    window.print();
    window.setTimeout(cleanup,1000);
    emit('product_brief_printed',{category:currentBrief.categoryId});
  }

  function applyNoMatchGate(){
    const link=document.querySelector('#directResult [data-filtered-search]');
    if(!link||link.dataset.trustGated==='true')return;
    link.dataset.trustGated='true';
    link.classList.add('disabled-link');
    link.setAttribute('aria-disabled','true');
    link.tabIndex=-1;
    const label=document.createElement('label');
    label.className='check-item no-match-confirm';
    label.innerHTML='<input type="checkbox" data-unverified-search-confirm><span><b>Doğrulanmış eşleşme olmadığını anlıyorum.</b><br><small>Filtreli arama bir ürün önerisi değildir; teknik minimumları ve satıcı bilgisini ürün sayfasında yeniden doğrulayacağım.</small></span>';
    link.parentNode.insertBefore(label,link);
    const checkbox=label.querySelector('input');
    checkbox.addEventListener('change',()=>{
      const enabled=checkbox.checked;
      link.classList.toggle('disabled-link',!enabled);
      link.setAttribute('aria-disabled',enabled?'false':'true');
      link.tabIndex=enabled?0:-1;
      emit('affiliate_unverified_search_acknowledged',{category:activeCategoryId(),acknowledged:enabled});
    });
    emit('affiliate_exposure_blocked',{category:activeCategoryId(),reason:'no_verified_match_requires_ack'});
  }

  function scheduleRefresh(){
    window.clearTimeout(refreshTimer);
    refreshTimer=window.setTimeout(()=>{
      applyNoMatchGate();
      renderBrief();
    },0);
  }

  function bindResultObserver(){
    const results=$('results');
    if(!results)return;
    const observer=new MutationObserver(scheduleRefresh);
    observer.observe(results,{subtree:true,childList:true,attributes:true,attributeFilter:['class','aria-disabled']});
    document.addEventListener('click',event=>{
      const link=event.target.closest?.('[data-filtered-search]');
      if(link&&link.getAttribute('aria-disabled')==='true'){
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    },true);
  }

  function bindBriefActions(){
    $('saveBriefBtn')?.addEventListener('click',saveCurrentBrief);
    $('copyBriefBtn')?.addEventListener('click',copyBrief);
    $('downloadBriefBtn')?.addEventListener('click',downloadBrief);
    $('printBriefBtn')?.addEventListener('click',printBrief);
    $('clearBriefVaultBtn')?.addEventListener('click',clearVault);
  }

  document.addEventListener('DOMContentLoaded',()=>{
    bindIntentShortcuts();
    bindResultObserver();
    bindBriefActions();
    renderVault();
  });
})();
