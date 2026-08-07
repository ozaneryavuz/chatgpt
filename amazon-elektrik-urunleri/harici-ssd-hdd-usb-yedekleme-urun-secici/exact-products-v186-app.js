(() => {
  'use strict';

  const data=window.Alo186BackupExactProductsV186;
  const host=document.getElementById('exactBackupProducts');
  const status=document.getElementById('exactGateStatus');
  if(!data||!host||!status)return;

  const $=id=>document.getElementById(id);
  const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const gateIds=['exactNeedConfirm','exactSpecConfirm','exactAffiliateConfirm'];

  function gateOpen(){return gateIds.every(id=>Boolean($(id)?.checked));}
  function fresh(item){return data.verificationStatus(item,new Date()).fresh;}
  function emit(name,params={}){
    const safe={collection:'backup_exact_v186',...params};
    if(typeof window.Alo186Track==='function'){
      try{window.Alo186Track(name,safe);}catch(_error){}
    }
    const analytics=window.alo186Analytics;
    if(analytics&&typeof analytics.track==='function'){
      try{
        if(typeof analytics.getConsent!=='function'||analytics.getConsent()==='granted')analytics.track(name,safe);
      }catch(_error){}
    }
  }
  function list(items){return items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');}
  function action(item){
    if(!fresh(item))return '<span class="exact-shop disabled" aria-disabled="true">Teknik doğrulama tarihi yenileniyor</span>';
    if(!gateOpen())return '<span class="exact-shop disabled" aria-disabled="true">Üç onaydan sonra açılır</span>';
    return `<a class="exact-shop" data-exact-affiliate="${escapeHtml(item.id)}" href="${escapeHtml(item.amazonUrl)}" target="_blank" rel="sponsored nofollow noopener"><small>Amazon satış ortaklığı bağlantısı</small>Exact modeli Amazon’da yeniden doğrula</a>`;
  }
  function card(item){
    return `<article class="exact-card" data-category="${escapeHtml(item.category)}" id="exact-${escapeHtml(item.id)}">
      <div class="exact-meta">${escapeHtml(item.brand)} · ${escapeHtml(item.mpn)} · ASIN ${escapeHtml(item.asin)} · kontrol ${escapeHtml(item.verifiedAt)}</div>
      <h3>${escapeHtml(item.name)}</h3>
      <p class="exact-need"><strong>Çözdüğü ihtiyaç:</strong> ${escapeHtml(item.userNeed)}</p>
      <details><summary>Teknik kanıt, kullanım ve satın almama sınırı</summary><div>
        <h4>Doğrulanan teknik alanlar</h4><ul>${list(item.facts)}</ul>
        <h4>En uygun kullanım</h4><ul>${list(item.bestFor)}</ul>
        <h4>Satın almadan önce doğrulayın</h4><ul>${list(item.evidence)}</ul>
        <h4>Bu durumda almayın</h4><ul>${list(item.noBuyWhen)}</ul>
      </div></details>
      <a class="exact-source" href="${escapeHtml(item.technicalSource)}" target="_blank" rel="external noopener noreferrer">Üretici teknik kaynağını aç ↗</a>
      ${action(item)}
    </article>`;
  }
  function bindClicks(){
    host.querySelectorAll('[data-exact-affiliate]').forEach(link=>link.addEventListener('click',()=>emit('affiliate_backup_exact_clicked',{item_id:link.dataset.exactAffiliate,placement:'backup_selector'})));
  }
  function render(){
    const live=data.products.filter(fresh);
    host.innerHTML=live.map(card).join('');
    const open=gateOpen();
    status.textContent=open
      ? `${live.length} güncel model bağlantısı yalnız bu oturum için açıldı. Model, kapasite ve satıcıyı Amazon’da yeniden doğrulayın.`
      : 'Exact model bağlantıları kapalı. Mevcut ürün, teknik uyum ve satış ortaklığı onaylarını tamamlayın.';
    status.dataset.open=String(open);
    $('exactFreshCount').textContent=String(live.length);
    bindClicks();
  }
  function injectGraph(){
    const old=document.getElementById('alo186-backup-exact-kg-v186');
    if(old)old.remove();
    const script=document.createElement('script');
    script.id='alo186-backup-exact-kg-v186';
    script.type='application/ld+json';
    script.textContent=JSON.stringify(data.knowledgeGraph(new Date()));
    document.head.appendChild(script);
  }

  gateIds.forEach(id=>$(id)?.addEventListener('change',()=>{
    render();
    emit('affiliate_backup_exact_gate',{field:id,open:gateOpen()});
  }));
  render();
  injectGraph();
  emit('affiliate_backup_exact_viewed',{model_count:data.products.length,version:data.version});
})();
