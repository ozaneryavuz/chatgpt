(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const n=value=>{if(value===null||value===undefined||value==='')return null;const parsed=Number(String(value).replace(',','.'));return Number.isFinite(parsed)?parsed:null;};
  const roundUp=(value,step=10)=>Math.ceil(value/step)*step;
  const result=(status,title,summary,extra={})=>({status,title,summary,commercialAllowed:false,...extra});

  function calculate(input={}){
    if(input.emergency)return result('emergency','Enerjiyi kesin ve sistemi kullanmayın','Duman, yanık kokusu, şişmiş akü, aşırı ısınma, su teması, açık iletken veya elektrik çarpması riski varsa cihaza yaklaşmadan güvenli enerjisiz bırakın; yangın veya yaralanma riski varsa 112’yi arayın.');
    if(input.securityCritical)return result('professional','Profesyonel süreklilik tasarımı gerekli','Yangın, geçiş kontrolü, sağlık, asansör, kamu alanı veya hukuki delil sürekliliği gibi kritik kamera sistemleri tüketici tipi ürün seçimiyle doğrulanamaz. Yedeklilik, kayıt bütünlüğü, ağ ve bakım planı birlikte projelendirilmelidir.');

    const topology=input.topology||'unknown';
    const cameraCount=n(input.cameraCount),cameraW=n(input.cameraW),recorderW=n(input.recorderW),switchOwnW=n(input.switchOwnW)??0,routerW=n(input.routerW)??0,monitorW=n(input.monitorW)??0,otherW=n(input.otherW)??0,targetHours=n(input.targetHours);
    if(topology==='unknown'||cameraCount===null||cameraW===null||recorderW===null||targetHours===null)return result('evidence_required','Etiket ve sistem topolojisi gerekli','Kamera adedi, gece/IR/PTZ dâhil kamera başına azami W, kayıt cihazı W, hedef süre ve besleme topolojisini doğrulamadan ürün sınıfı seçmeyin.');
    if(cameraCount<1||cameraCount>128||cameraW<=0||cameraW>120||recorderW<0||recorderW>1500||targetHours<=0||targetHours>72)return result('evidence_required','Girdi aralığını doğrulayın','Kamera adedi, cihaz gücü veya hedef süre beklenen planlama aralığının dışında. Üretici etiketi ve proje verisini kontrol edin.');

    const isPoe=topology==='poe_nvr',poeEfficiency=.85,cameraDeliveredW=cameraCount*cameraW,cameraInputW=isPoe?cameraDeliveredW/poeEfficiency:cameraDeliveredW,totalLoadW=cameraInputW+recorderW+switchOwnW+routerW+monitorW+otherW,requiredContinuousW=roundUp(totalLoadW*1.25,10);
    const sourceType=input.sourceType||'auto',dcMiniCandidate=!isPoe&&cameraCount<=2&&recorderW===0&&totalLoadW<=45&&targetHours<=8,recommendedCategory=sourceType==='auto'?(dcMiniCandidate?'mini_ups':'power_station'):sourceType,efficiency=recommendedCategory==='mini_ups'?.9:.85,usableFraction=recommendedCategory==='power_station'?.85:.8,requiredWh=roundUp(totalLoadW*targetHours/(efficiency*usableFraction),10),requiredPoeBudgetW=isPoe?roundUp(cameraDeliveredW/poeEfficiency*1.2,5):0,requiredPoePorts=isPoe?cameraCount:0;
    const metrics={cameraDeliveredW:Math.round(cameraDeliveredW*10)/10,totalLoadW:Math.round(totalLoadW*10)/10,requiredContinuousW,requiredWh,requiredPoeBudgetW,requiredPoePorts,recommendedCategory};

    if(cameraCount>32||totalLoadW>1500||input.installation==='fixed_rack'||input.redundancy==='required')return result('professional','Rack ve süreklilik projesi gerekli','Yüksek kamera adedi, sabit rack, yedeklilik şartı veya yüksek toplam güç; UPS topolojisi, akü kabini, selektivite, PoE yedekliliği, sıcaklık ve kayıt bütünlüğüyle birlikte profesyonel tasarım gerektirir.',{metrics});

    if(isPoe){
      const poeBudgetW=n(input.poeBudgetW),poePorts=n(input.poePorts);
      if(poeBudgetW===null||poePorts===null)return result('evidence_required','PoE switch bütçesi ve port sayısı gerekli',`En az ${requiredPoePorts} aktif port ve yaklaşık ${requiredPoeBudgetW} W toplam PoE bütçesi planlandı. Switch etiketindeki toplam PoE budget ve port başına sınıfı doğrulayın.`,{metrics});
      if(poePorts<requiredPoePorts||poeBudgetW<requiredPoeBudgetW){const gaps=[];if(poePorts<requiredPoePorts)gaps.push(`${requiredPoePorts-poePorts} port eksik`);if(poeBudgetW<requiredPoeBudgetW)gaps.push(`${Math.ceil(requiredPoeBudgetW-poeBudgetW)} W PoE bütçesi eksik`);return result('poe_gap','Önce PoE dağıtım açığını çözün',`${gaps.join(' ve ')}. Yedek enerji kapasitesi, kameraları besleyemeyen bir PoE switch sorununu çözmez. Switch port sınıfı, toplam budget ve gece modu yükünü doğrulayın.`,{metrics});}
    }

    if((input.scenario||'planning')==='active')return result('active_event','Aktif kesintide kayıt bütünlüğünü koruyun',`Yaklaşık ${requiredContinuousW} W sürekli güç ve ${requiredWh} Wh nominal enerji gerekiyor. Geçici ters besleme veya kontrolsüz kablo kullanmayın; mevcut güvenli kaynağın kalan süresini ve kayıt cihazının düzgün kapanmasını önceliklendirin.`,{metrics});

    if((input.sourceStatus||'none')==='existing'){
      const sourceContinuousW=n(input.sourceContinuousW),sourceWh=n(input.sourceWh);
      if(sourceContinuousW===null||sourceWh===null||input.outputVerified!=='yes'||input.blackoutTest!=='success')return result('evidence_required','Mevcut kaynağın teknik kanıtı eksik',`En az ${requiredContinuousW} W sürekli çıkış, ${requiredWh} Wh nominal enerji, uygun çıkış ve kontrollü kesinti testi birlikte doğrulanmalıdır.`,{metrics});
      const gaps=[];if(sourceContinuousW<requiredContinuousW)gaps.push(`${requiredContinuousW-sourceContinuousW} W sürekli güç`);if(sourceWh<requiredWh)gaps.push(`${requiredWh-sourceWh} Wh enerji`);
      if(gaps.length===0)return result('no_buy','Mevcut kaynak yeterli — yeni ürün almayın',`Mevcut kaynak yaklaşık ${requiredContinuousW} W sürekli güç ve ${requiredWh} Wh enerji eşiğini, çıkış doğrulamasını ve gerçek kesinti testini karşılıyor. Düzenli akü testi ve kayıt kontrolü yapın.`,{metrics});
      return result('conditional_purchase','Doğrulanmış kapasite açığı var',`${gaps.join(' ve ')} açığı bulunuyor. Yalnız hesaplanan sınıfa ilerleyin; ürün etiketinde gerçek W, Wh, çıkış ve çalışma sıcaklığını yeniden doğrulayın.`,{metrics,commercialAllowed:true});
    }
    return result('conditional_purchase','Yedek güç sınıfı hesaplandı',`Yaklaşık ${requiredContinuousW} W sürekli çıkış ve ${requiredWh} Wh nominal enerji gerekir${isPoe?`; ayrıca en az ${requiredPoePorts} PoE portu ve ${requiredPoeBudgetW} W toplam PoE bütçesi gerekir`:''}. Yalnız bu eşikleri karşılayan ürün sınıfına ilerleyin.`,{metrics,commercialAllowed:true});
  }

  const statusLabels={emergency:'Acil',professional:'Profesyonel',evidence_required:'Kanıt gerekli',poe_gap:'PoE açığı',active_event:'Aktif kesinti',no_buy:'Satın alma yok',conditional_purchase:'Koşullu ürün'};
  function readForm(doc){const id=name=>doc.getElementById(name),value=name=>id(name)?.value,checked=name=>Boolean(id(name)?.checked);return{emergency:checked('emergency'),securityCritical:checked('securityCritical'),scenario:value('scenario'),topology:value('topology'),installation:value('installation'),redundancy:value('redundancy'),cameraCount:value('cameraCount'),cameraW:value('cameraW'),recorderW:value('recorderW'),switchOwnW:value('switchOwnW'),routerW:value('routerW'),monitorW:value('monitorW'),otherW:value('otherW'),targetHours:value('targetHours'),poeBudgetW:value('poeBudgetW'),poePorts:value('poePorts'),sourceStatus:value('sourceStatus'),sourceType:value('sourceType'),sourceContinuousW:value('sourceContinuousW'),sourceWh:value('sourceWh'),outputVerified:value('outputVerified'),blackoutTest:value('blackoutTest')};}
  function mount(doc){
    const form=doc.getElementById('cameraForm');if(!form)return;const $=id=>doc.getElementById(id);
    const toggle=()=>{$('poeFields')?.classList.toggle('hidden',$('topology').value!=='poe_nvr');$('existingFields')?.classList.toggle('hidden',$('sourceStatus').value!=='existing');};['topology','sourceStatus'].forEach(id=>$(id)?.addEventListener('change',toggle));toggle();
    form.addEventListener('submit',event=>{event.preventDefault();const out=calculate(readForm(doc)),box=$('result');box.className=`panel result status-${out.status}`;box.hidden=false;$('resultBadge').textContent=statusLabels[out.status]||out.status;$('resultTitle').textContent=out.title;$('resultSummary').textContent=out.summary;const m=out.metrics;$('metrics').innerHTML=m?`<article><span>Kamera yükü</span><strong>${m.cameraDeliveredW} W</strong></article><article><span>Toplam giriş</span><strong>${m.totalLoadW} W</strong></article><article><span>Sürekli alt sınır</span><strong>${m.requiredContinuousW} W</strong></article><article><span>Nominal enerji</span><strong>${m.requiredWh} Wh</strong></article><article><span>PoE bütçesi</span><strong>${m.requiredPoeBudgetW||'—'}${m.requiredPoeBudgetW?' W':''}</strong></article>`:'';const commerce=$('commerce');commerce.classList.toggle('hidden',!out.commercialAllowed);commerce.dataset.category=m?.recommendedCategory||'';['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{$(id).checked=false;});$('productLink').setAttribute('aria-disabled','true');$('productLink').classList.add('disabled');box.scrollIntoView({behavior:'smooth',block:'start'});box.focus({preventScroll:true});if(root.Alo186Track)root.Alo186Track('camera_poe_backup_result',{status:out.status,category:m?.recommendedCategory||'none'});});
    const refreshGate=()=>{const commerce=$('commerce'),enabled=!commerce.classList.contains('hidden')&&['actualNeed','technicalCheck','affiliateCheck'].every(id=>$(id).checked),link=$('productLink');if(enabled){const category=commerce.dataset.category||'power_station';link.href=`../../akilli-urun-secimi?kategori=${encodeURIComponent(category)}&kaynak=kamera-nvr-poe`;link.removeAttribute('aria-disabled');link.classList.remove('disabled');}else{link.removeAttribute('href');link.setAttribute('aria-disabled','true');link.classList.add('disabled');}};
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>$(id)?.addEventListener('change',refreshGate));$('productLink')?.addEventListener('click',event=>{if($('productLink').getAttribute('aria-disabled')==='true')event.preventDefault();});
  }
  return{calculate,mount};
});
