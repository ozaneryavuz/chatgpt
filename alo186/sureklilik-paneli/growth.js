(() => {
  'use strict';

  const STORAGE_KEY='alo186_continuity_pilot_v1';
  const $=id=>document.getElementById(id);
  const core=window.Alo186ContinuityGrowth;
  const store=window.Alo186ContinuityStore;
  let lastSnapshot='';

  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function state(){try{return store.hydrate(JSON.parse(localStorage.getItem(STORAGE_KEY)||'null'));}catch(error){return store.createState();}}
  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
  function download(name,content,type){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  async function copyText(text){if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(text);return;}const area=document.createElement('textarea');area.value=text;area.setAttribute('readonly','');area.style.position='fixed';area.style.opacity='0';document.body.appendChild(area);area.select();document.execCommand('copy');area.remove();}
  function setStatus(message){const target=$('growthStatus');if(target)target.textContent=message;}

  function ensureUi(){
    if(!core||!store||$('buyume'))return;
    const nav=document.querySelector('.continuity-nav');
    if(nav&&!nav.querySelector('a[href="#buyume"]')){const link=document.createElement('a');link.href='#buyume';link.textContent='Sonraki adım';const events=nav.querySelector('a[href="#olaylar"]');nav.insertBefore(link,events||null);}
    const section=document.createElement('section');section.id='buyume';section.className='module growth-module';section.setAttribute('aria-labelledby','growthTitle');section.innerHTML=`
      <div class="module-head"><div><span class="eyebrow">Güvenli büyüme ve tekrar ziyaret</span><h2 id="growthTitle">Bir sonraki doğru işi seçin; planı takvime ve pilot kapsamına dönüştürün.</h2><p>Önce ücretsiz görev veya araca ilerleyin. Satın alma bağlantısı bu bölümde bulunmaz; düşük riskli ürün rotaları yalnız ilgili araç içinde açık satış ortaklığı etiketiyle değerlendirilir.</p></div><span class="module-count" id="growthReadinessBadge">Ön hazırlık</span></div>
      <div class="growth-grid">
        <article class="subpanel growth-card"><span class="stage-pill">1 · Kullanıcı yolculuğu</span><h3>Şimdi yapılacak en değerli 3 iş</h3><p>Açık 30/60/90 günlük plan, önem ve süreye göre ücretsiz araçlara veya panel görevlerine bağlanır.</p><div id="growthNextActions" class="growth-action-list"></div><div class="growth-disclosure"><strong>Satış ortaklığı sınırı:</strong> Buradaki bağlantılar affiliate değildir. Ücretsiz bir araç ileride ürün rotası açarsa ticari niteliği bağlantıdan önce görünür biçimde açıklanır.</div></article>
        <article class="subpanel growth-card"><span class="stage-pill">2 · Tekrar ziyaret</span><h3>90 günlük planı takviminize ekleyin</h3><p id="growthCalendarSummary">Açık aksiyon ve test tarihleri hazırlanıyor.</p><div class="actions"><button class="btn btn-secondary" id="growthCalendarBtn" type="button">Takvim dosyası indir (.ics)</button></div><small>Kuruluş, lokasyon, varlık veya kişi adları takvim dosyasına yazılmaz. Hatırlatmalar resmî bakım belgesi değildir.</small></article>
        <article class="subpanel growth-card"><span class="stage-pill">3 · B2B dönüşüm</span><h3>Anonim SaaS pilot kapsamı oluşturun</h3><p id="growthReadinessText">Panel aktivasyonu hesaplanıyor.</p><ul id="growthMilestones" class="growth-milestones"></ul><div class="actions"><button class="btn btn-secondary" id="growthCopyBriefBtn" type="button">Anonim kapsamı kopyala</button><button class="btn btn-secondary" id="growthDownloadBriefBtn" type="button">JSON indir</button><a class="btn btn-primary growth-contact disabled" id="growthPilotContact" href="https://www.alo186.com/iletisim?konu=sureklilik-pilotu" aria-disabled="true" tabindex="-1">Pilot iletişimini aç</a></div><small>Özet; kuruluş/lokasyon adı, adres, telefon, e-posta, abonelik, serbest metin veya tıbbi seçim içermez. İletişim adımı isteğe bağlıdır.</small></article>
      </div><p id="growthStatus" class="growth-status" role="status" aria-live="polite"></p>`;
    const events=$('olaylar');if(events&&events.parentNode)events.parentNode.insertBefore(section,events);else document.querySelector('main')?.appendChild(section);
    $('growthCalendarBtn').addEventListener('click',exportCalendar);
    $('growthCopyBriefBtn').addEventListener('click',copyBrief);
    $('growthDownloadBriefBtn').addEventListener('click',downloadBrief);
    $('growthNextActions').addEventListener('click',event=>{const link=event.target.closest('[data-growth-action]');if(!link)return;emit('continuity_next_action_opened',{dimension:link.dataset.dimension||'unknown',route_type:link.dataset.routeType||'unknown',horizon_days:Number(link.dataset.horizonDays||0)});});
    $('growthPilotContact').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();setStatus('Pilot iletişimi için önce en az dört aktivasyon adımını tamamlayın.');return;}emit('continuity_pilot_contact_opened',{readiness:core.activationReadiness(state()).completed});});
  }

  function render(){
    ensureUi();if(!$('buyume')||!core||!store)return;
    const current=state(),readiness=core.activationReadiness(current),actions=core.nextBestActions(current,3),events=core.buildCalendarEvents(current);
    $('growthReadinessBadge').textContent=`${readiness.completed}/${readiness.total} · ${readiness.level}`;
    $('growthNextActions').innerHTML=actions.map((item,index)=>`<article class="growth-action"><div><span>${String(index+1).padStart(2,'0')} · ${escapeHtml(item.dimensionLabel)} · ${item.horizonDays} gün</span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.disclosure)}</small></div><a class="growth-action-link" data-growth-action data-dimension="${escapeHtml(item.dimension)}" data-route-type="${escapeHtml(item.kind)}" data-horizon-days="${item.horizonDays}" href="${escapeHtml(item.href)}">${escapeHtml(item.linkLabel)} →</a></article>`).join('');
    $('growthCalendarSummary').textContent=events.length?`${events.length} kişisel verisiz kontrol ve test hatırlatması hazır. Dosyayı telefon veya masaüstü takviminize ekleyebilirsiniz.`:'Önce 90 günlük plan veya test periyodu oluşturun; ardından takvim dosyası hazırlanır.';
    $('growthCalendarBtn').disabled=!events.length;
    $('growthReadinessText').textContent=`Aktivasyon ${readiness.percent}%: ${readiness.level}.${readiness.next?` Sonraki adım: ${readiness.next.title}.`:' Temel pilot kanıtları hazır.'}`;
    $('growthMilestones').innerHTML=readiness.milestones.map(item=>`<li class="${item.done?'done':''}"><span aria-hidden="true">${item.done?'✓':'○'}</span>${escapeHtml(item.title)}</li>`).join('');
    const contact=$('growthPilotContact');contact.classList.toggle('disabled',!readiness.ready);contact.setAttribute('aria-disabled',readiness.ready?'false':'true');contact.tabIndex=readiness.ready?0:-1;
  }

  function exportCalendar(){const current=state(),events=core.buildCalendarEvents(current);if(!events.length){setStatus('Takvim oluşturmak için önce açık aksiyon veya test periyodu ekleyin.');return;}download(`alo186-sureklilik-takvimi-${new Date().toISOString().slice(0,10)}.ics`,core.buildIcs(events),'text/calendar;charset=utf-8');setStatus(`${events.length} hatırlatma takvim dosyasına eklendi.`);emit('continuity_calendar_exported',{event_count:events.length,improvement_count:events.filter(x=>x.kind==='improvement').length,test_count:events.filter(x=>x.kind==='asset-test').length});}
  async function copyBrief(){try{const result=core.buildPilotBrief(state());await copyText(result.text);setStatus('Anonim pilot kapsamı panoya kopyalandı.');emit('continuity_pilot_brief_copied',{readiness:result.brief.readiness.completed,locations:result.brief.inventory.locations,actions:result.brief.inventory.improvementActions});}catch(error){setStatus('Kapsam kopyalanamadı; JSON indirme seçeneğini kullanın.');}}
  function downloadBrief(){const result=core.buildPilotBrief(state());download(`alo186-anonim-pilot-kapsami-${new Date().toISOString().slice(0,10)}.json`,JSON.stringify(result.brief,null,2),'application/json;charset=utf-8');setStatus('Anonim pilot kapsamı JSON olarak indirildi.');emit('continuity_pilot_brief_downloaded',{readiness:result.brief.readiness.completed,locations:result.brief.inventory.locations,actions:result.brief.inventory.improvementActions});}
  function check(){const snapshot=localStorage.getItem(STORAGE_KEY)||'';if(snapshot===lastSnapshot&&$('buyume'))return;lastSnapshot=snapshot;render();}

  document.addEventListener('DOMContentLoaded',()=>{ensureUi();check();document.addEventListener('click',()=>setTimeout(check,0));document.addEventListener('change',()=>setTimeout(check,0));window.addEventListener('storage',check);setInterval(check,1500);});
})();
