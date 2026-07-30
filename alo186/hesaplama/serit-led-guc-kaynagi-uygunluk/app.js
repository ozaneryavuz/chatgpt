(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const COPPER_RHO=0.0175;
  const num=value=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const round=(value,digits=2)=>{
    if(value===null||value===undefined||!Number.isFinite(value))return null;
    const factor=10**digits;
    return Math.round(value*factor)/factor;
  };
  const base=(status,title,summary,extra={})=>({
    status,title,summary,commercialAllowed:false,productClass:null,searchTerm:null,searchUrl:null,
    loadW:null,loadA:null,requiredW:null,requiredA:null,currentPerFeedA:null,
    voltageDropV:null,voltageDropPct:null,revisitDays:180,requirements:[],...extra
  });

  function metrics(input={}){
    const voltage=num(input.stripVoltage);
    const wattsPerMeter=num(input.wattsPerMeter);
    const lengthMeters=num(input.lengthMeters);
    const reservePercent=num(input.reservePercent);
    const feedCount=num(input.feedCount);
    const cableLengthM=num(input.cableLengthM);
    const cableSectionMm2=num(input.cableSectionMm2);
    const reserve=reservePercent===null?0.20:reservePercent/100;
    const loadW=wattsPerMeter&&lengthMeters?wattsPerMeter*lengthMeters:null;
    const loadA=loadW&&voltage?loadW/voltage:null;
    const requiredW=loadW?loadW*(1+reserve):null;
    const requiredA=loadA?loadA*(1+reserve):null;
    const currentPerFeedA=loadA&&feedCount?loadA/feedCount:null;
    const loopResistance=cableLengthM&&cableSectionMm2?2*cableLengthM*COPPER_RHO/cableSectionMm2:null;
    const voltageDropV=currentPerFeedA&&loopResistance?currentPerFeedA*loopResistance:null;
    const voltageDropPct=voltageDropV&&voltage?voltageDropV/voltage*100:null;
    return {
      voltage,wattsPerMeter,lengthMeters,reservePercent:reservePercent===null?20:reservePercent,
      feedCount,cableLengthM,cableSectionMm2,
      loadW:round(loadW,1),loadA:round(loadA,2),requiredW:round(requiredW,1),
      requiredA:round(requiredA,2),currentPerFeedA:round(currentPerFeedA,2),
      voltageDropV:round(voltageDropV,2),voltageDropPct:round(voltageDropPct,1)
    };
  }

  function searchTermFor(productClass,m,input){
    if(productClass==='power_supply'){
      const watts=m.requiredW?Math.ceil(m.requiredW/10)*10:'uygun güç';
      return `${m.voltage||''}V sabit voltaj LED güç kaynağı en az ${watts}W IEC 61347-2-13`.trim();
    }
    if(productClass==='controller'){
      return `${m.voltage||''}V LED ${input.controllerType||'dimmer'} kontrolcü en az ${m.requiredA||''}A`.trim();
    }
    if(productClass==='low_voltage_distribution'){
      return `${m.voltage||''}V LED dağıtım konnektörü sigortalı çoklu besleme terminali`.trim();
    }
    return null;
  }

  function calculate(input={}){
    const m=metrics(input);
    const done=result=>({...result,...m});

    if(input.emergency){
      return done(base('emergency','Enerjiyi güvenle kesin; ticari yollar kapalı','Duman, kıvılcım, erime, keskin koku veya hızla artan ısı varsa sisteme dokunmayın. Güvenli biçimde enerjisiz bırakın; yangın veya yaralanmada 112 önceliklidir.'));
    }
    if(['burned','melted','wet','damaged','hot'].includes(input.condition||'')){
      return done(base('stop_use','Hasarlı şerit, sürücü veya bağlantıyı kullanmayın','Kararmış, erimiş, ıslanmış, ezilmiş ya da olağandışı ısınan parça yeniden enerjilendirilmez. Sorunun nedeni belirlenmeden yeni ürün bağlamak güvenli değildir.'));
    }
    if(input.condition!=='sound'){
      return done(base('evidence_required','Fiziksel durumu doğrulayın','Şerit, güç kaynağı, kontrolcü, kablo, konnektör ve montaj yüzeyi sağlam, kuru ve ısınma izsiz olmalıdır.'));
    }
    if(['fixed_mains','open_terminals','commercial','vehicle'].includes(input.installation||'')){
      return done(base('professional','Bu kurulum yetkin kişi ve proje sınırındadır','Sabit tesisat, açık 230 V terminal, ticari alan, araç elektriği veya pano içi bağlantı tüketici tipi ürün yönlendirmesine dönüştürülmez. Uygun koruma, kablolama ve devreye alma yetkin kişi tarafından yapılmalıdır.'));
    }
    if(input.installation!=='plug_in_low_voltage'){
      return done(base('evidence_required','Kurulum türünü doğrulayın','Bu araç yalnız kapalı gövdeli, fişli güç kaynağıyla beslenen düşük gerilimli şerit LED kurulumları içindir.'));
    }
    if(input.stripMode==='constant_current'){
      return done(base('professional','Sabit akım LED modülü için eşleşmiş sürücü gerekir','Sabit akım modüllerinde yalnız voltaj ve watt hesabı yeterli değildir. LED modülünün anma akımı, gerilim aralığı ve üreticinin sürücü eşleştirmesi doğrulanmalıdır.'));
    }
    if(input.stripMode!=='constant_voltage'){
      return done(base('evidence_required','Şerit LED sürme biçimini doğrulayın','Etikette sabit voltajlı 5/12/24/48 V şerit olduğu açıkça görülmeden güç kaynağı seçmeyin.'));
    }
    if(input.labelVerified!=='yes'){
      return done(base('evidence_required','Etiket ve teknik veriyi doğrulayın','Şerit gerilimi, tam parlaklıkta W/m değeri, kesim aralığı ve üretici besleme sınırı yalnız pazar yeri başlığından değil ürün etiketi veya veri sayfasından alınmalıdır.'));
    }
    if(!m.voltage||![5,12,24,48].includes(m.voltage)){
      return done(base('evidence_required','Şerit gerilimini doğrulayın','5 V, 12 V, 24 V veya 48 V sabit voltaj değeri etiketten okunmalıdır. Farklı gerilimler birbirinin yerine kullanılamaz.'));
    }
    if(!m.wattsPerMeter||m.wattsPerMeter<=0||m.wattsPerMeter>100){
      return done(base('evidence_required','Tam parlaklıktaki W/m değerini girin','RGB/RGBW ve adreslenebilir şeritlerde en yüksek eşzamanlı parlaklık tüketimini kullanın; yalnız tek renk tüketimini esas almayın.'));
    }
    if(!m.lengthMeters||m.lengthMeters<=0||m.lengthMeters>100){
      return done(base('evidence_required','Toplam şerit uzunluğunu girin','Kesilmiş bütün parçaların toplam metre değerini kullanın.'));
    }
    if(m.reservePercent<10||m.reservePercent>50){
      return done(base('evidence_required','Görünür güç payını yüzde 10–50 arasında seçin','Araç varsayılan yüzde 20 planlama payı kullanır. Üretici sıcaklık düşümü ve sürekli yük sınırı her zaman önceliklidir.'));
    }
    if(!m.feedCount||m.feedCount<1||m.feedCount>20){
      return done(base('evidence_required','Bağımsız besleme noktası sayısını girin','Tek uç, iki uç veya çoklu enjeksiyon planındaki gerçek besleme noktalarını girin.'));
    }
    if(!m.cableLengthM||m.cableLengthM<=0||m.cableLengthM>100||!m.cableSectionMm2||m.cableSectionMm2<=0||m.cableSectionMm2>35){
      return done(base('evidence_required','Besleme kablosu uzunluğu ve kesitini girin','Güç kaynağından bir besleme noktasına tek yön uzunluk ile bakır iletken kesiti gerekir.'));
    }
    if(m.voltageDropPct>3){
      return done(base('design_gap','Yaklaşık gerilim düşümü yüksek',`Bakır iletken varsayımıyla yaklaşık düşüm %${m.voltageDropPct}. Besleme noktası, kablo kesiti veya hat uzunluğu yeniden tasarlanmadan ürün bağlantısı açılmaz.`,{requirements:['Üreticinin azami şerit besleme uzunluğunu doğrulayın.','Daha kısa/çoklu besleme veya uygun kesit değerlendirin.']}));
    }
    if(input.feedPlanVerified!=='yes'){
      return done(base('evidence_required','Şerit üreticisinin besleme sınırını doğrulayın','Hesaplanan kablo düşümü uygun olsa bile şerit üzerindeki bakır yolların taşıma sınırı ayrıdır. Tek uç/iki uç/çoklu besleme düzenini tam model kılavuzundan doğrulayın.'));
    }
    if(input.environment==='wet_outdoor'&&input.ipEvidence!=='yes'){
      return done(base('evidence_required','Islak/dış ortam koruma sınıfını doğrulayın','Şerit, ek noktaları, güç kaynağı ve kontrolcü için ortamla uyumlu IP sınıfı, drenaj ve yoğuşma yönetimi gerekir.'));
    }
    if(input.environment==='enclosed'&&input.ventilation!=='yes'){
      return done(base('stop_use','Kapalı hacimde ısı yönetimi doğrulanmadı','Güç kaynağını ve şeridi ısı hapseden kapalı hacimde çalıştırmayın. Üretici sıcaklık sınırı, havalandırma ve montaj yüzeyi doğrulanmalıdır.'));
    }
    if(!['dry','wet_outdoor','enclosed'].includes(input.environment||'')){
      return done(base('evidence_required','Kullanım ortamını seçin','Kuru iç ortam, ıslak/dış ortam veya kapalı mobilya hacmi ayrımı gerekir.'));
    }
    if(input.thermalMount!=='verified'){
      return done(base('evidence_required','Isı dağıtım yöntemini doğrulayın','Yüksek güçlü şeritlerde üreticinin istediği alüminyum profil veya uygun montaj yüzeyi doğrulanmalıdır; bant yapışkanı tek başına ısı yönetimi kanıtı değildir.'));
    }
    if(input.recallChecked==='recalled'){
      return done(base('stop_use','Geri çağrılmış ürünü kullanmayın','Tam marka-model için kullanım durdurma veya geri çağırma kaydı varsa ürünü enerjilendirmeyin; üreticinin resmî sürecini izleyin.'));
    }
    if(input.recallChecked!=='yes'){
      return done(base('evidence_required','Tam marka-model ürün güvenliği kontrolü yapın','Güç kaynağı, kontrolcü ve şerit için üretici ile resmî ürün güvenliği duyurularını kontrol edin.'));
    }
    if(input.certification!=='yes'){
      return done(base('evidence_required','Üretici, model ve güvenlik kanıtını doğrulayın','Yalnız pazar yeri beyanı yeterli değildir. Güç kaynağı için tam model kılavuzu, anma değerleri ve uygulanabilir güvenlik standardı kanıtı gerekir.'));
    }

    const psuVoltage=num(input.psuVoltage);
    const psuW=num(input.psuW);
    const psuA=num(input.psuA);
    const controllerA=num(input.controllerA);
    const connectorA=num(input.connectorA);
    if(!psuVoltage||!psuW||!psuA){
      const term=searchTermFor('power_supply',m,input);
      return done(base('replace_candidate','Uygun güç kaynağı kanıtı eksik','Çıkış gerilimi, sürekli W ve sürekli A değerleri tam model etiketinden doğrulanmalıdır.',{commercialAllowed:true,productClass:'power_supply',searchTerm:term,requirements:[`${m.voltage} V sabit voltaj çıkış`, `En az ${m.requiredW} W ve ${m.requiredA} A sürekli kapasite`]}));
    }
    if(Math.abs(psuVoltage-m.voltage)>0.1){
      return done(base('stop_use','Güç kaynağı gerilimi şeritle eşleşmiyor',`${psuVoltage} V çıkış, ${m.voltage} V şerit için kullanılmaz. Yanlış gerilim LED ve kontrolcüye zarar verebilir.`));
    }
    if(psuW<m.requiredW||psuA<m.requiredA){
      const term=searchTermFor('power_supply',m,input);
      return done(base('replace_candidate','Güç kaynağı kapasitesi yetersiz',`Hesaplanan planlama ihtiyacı en az ${m.requiredW} W ve ${m.requiredA} A. Mevcut/aday güç kaynağı ${psuW} W ve ${psuA} A.`,{commercialAllowed:true,productClass:'power_supply',searchTerm:term,requirements:[`${m.voltage} V sabit voltaj`, `En az ${m.requiredW} W`, `En az ${m.requiredA} A`, 'Üretici sıcaklık düşümü ve sürekli yük sınırı doğrulanmalı']}));
    }
    if(input.controllerType!=='none'){
      if(!controllerA){
        const term=searchTermFor('controller',m,input);
        return done(base('replace_candidate','Kontrolcü akım değeri doğrulanmadı','Dimmer, RGB/RGBW veya adreslenebilir kontrolcü toplam yükü ve kanal düzenini taşımalıdır.',{commercialAllowed:true,productClass:'controller',searchTerm:term,requirements:[`En az ${m.requiredA} A toplam sürekli akım`, `${m.voltage} V ile tam uyum`, 'Kanal başına ve toplam akım sınırları ayrı doğrulanmalı']}));
      }
      if(controllerA<m.requiredA){
        const term=searchTermFor('controller',m,input);
        return done(base('replace_candidate','Kontrolcü kapasitesi yetersiz',`Kontrolcü ${controllerA} A; planlama ihtiyacı ${m.requiredA} A. Kanal başına ve toplam sınırlar doğrulanmadan kullanmayın.`,{commercialAllowed:true,productClass:'controller',searchTerm:term,requirements:[`En az ${m.requiredA} A toplam sürekli akım`, `${m.voltage} V uyum`]}));
      }
    }
    if(!connectorA||connectorA<m.currentPerFeedA*1.2){
      const term=searchTermFor('low_voltage_distribution',m,input);
      return done(base('replace_candidate','Besleme konnektörü veya dağıtım elemanı yetersiz',`Her besleme noktası yaklaşık ${m.currentPerFeedA} A taşıyor. Konnektör ve dağıtım elemanı için görünür payla en az ${round(m.currentPerFeedA*1.2,2)} A doğrulanmalıdır.`,{commercialAllowed:true,productClass:'low_voltage_distribution',searchTerm:term,requirements:['Akım sınıfı üretici verisinden doğrulanmış konnektör','Doğru kutup ve çekme gerilimi azaltma','Gerekli ise her kol için uygun koruma']}));
    }
    if(input.ownership==='owned'){
      if(input.fieldTest==='fail'){
        return done(base('stop_use','Gerçek yük testinde sorun var; kullanmayı bırakın','Titreme, renk sapması, gerilim çökmesi, konnektör veya güç kaynağında ısınma/koku varsa sistemi enerjisiz bırakın ve nedeni bulun. Yeni ürün bağlantısı otomatik çözüm sayılmaz.'));
      }
      if(input.fieldTest!=='pass'){
        return done(base('test_first','Önce gözetimli gerçek yük testi yapın','Bütün parçalar doğrulansa bile tam parlaklıkta üreticinin izin verdiği süre boyunca gerilim, titreme ve sıcaklık gözlenmeden yeni ürün önerilmez.'));
      }
      return done(base('no_buy','Mevcut sistem yeterli — yeni ürün almayın',`Yaklaşık yük ${m.loadW} W / ${m.loadA} A; mevcut güç kaynağı, kontrolcü, kablo ve konnektör planlama sınırlarını karşılıyor ve gerçek test başarılı. Periyodik ısı ve bağlantı kontrolü yapın.`));
    }
    return done(base('qualified','Teknik minimumlar doğrulandı; satın almadan önce tam modeli yeniden karşılaştırın',`Yaklaşık yük ${m.loadW} W / ${m.loadA} A; planlama kapasitesi ${m.requiredW} W / ${m.requiredA} A. Fiyat, stok, puan ve garanti bilgisi verilmez.`,{requirements:[`${m.voltage} V sabit voltaj`, `En az ${m.requiredW} W ve ${m.requiredA} A`, `Her besleme için yaklaşık ${m.currentPerFeedA} A`, `Yaklaşık kablo düşümü %${m.voltageDropPct}`]}));
  }

  function amazonUrl(term){
    if(!term)return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(term)}&tag=${AFFILIATE_TAG}`;
  }

  function read(doc){
    const value=id=>{
      const el=doc.getElementById(id);
      if(!el)return '';
      if(el.type==='checkbox')return el.checked;
      return el.value;
    };
    return {
      emergency:value('emergency'),condition:value('condition'),installation:value('installation'),
      stripMode:value('stripMode'),labelVerified:value('labelVerified'),stripVoltage:value('stripVoltage'),
      wattsPerMeter:value('wattsPerMeter'),lengthMeters:value('lengthMeters'),reservePercent:value('reservePercent'),
      feedCount:value('feedCount'),cableLengthM:value('cableLengthM'),cableSectionMm2:value('cableSectionMm2'),
      feedPlanVerified:value('feedPlanVerified'),environment:value('environment'),ipEvidence:value('ipEvidence'),
      ventilation:value('ventilation'),thermalMount:value('thermalMount'),recallChecked:value('recallChecked'),
      certification:value('certification'),psuVoltage:value('psuVoltage'),psuW:value('psuW'),psuA:value('psuA'),
      controllerType:value('controllerType'),controllerA:value('controllerA'),connectorA:value('connectorA'),
      ownership:value('ownership'),fieldTest:value('fieldTest')
    };
  }

  function escapeHtml(value){
    return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  }

  function render(doc,result){
    const output=doc.getElementById('result');
    if(!output)return;
    const metricsHtml=result.loadW!==null?`<div class="metrics">
      <span><b>${escapeHtml(result.loadW)} W</b> şerit yükü</span>
      <span><b>${escapeHtml(result.loadA)} A</b> toplam akım</span>
      <span><b>${escapeHtml(result.requiredW)} W</b> planlama gücü</span>
      <span><b>%${escapeHtml(result.voltageDropPct)}</b> yaklaşık kablo düşümü</span>
    </div>`:'';
    const req=(result.requirements||[]).map(item=>`<li>${escapeHtml(item)}</li>`).join('');
    output.className=`result status-${escapeHtml(result.status)}`;
    output.innerHTML=`<p class="status">${escapeHtml(result.status)}</p><h2>${escapeHtml(result.title)}</h2><p>${escapeHtml(result.summary)}</p>${metricsHtml}${req?`<ul>${req}</ul>`:''}`;
    output.hidden=false;

    const gate=doc.getElementById('affiliateGate');
    const link=doc.getElementById('affiliateLink');
    const checks=[...doc.querySelectorAll('[data-affiliate-check]')];
    checks.forEach(check=>{check.checked=false;});
    if(result.commercialAllowed&&result.searchTerm){
      gate.hidden=false;
      link.dataset.term=result.searchTerm;
      link.href='#';
      link.setAttribute('aria-disabled','true');
      link.textContent='Üç onayı tamamlayın';
    }else{
      gate.hidden=true;
      if(link){link.href='#';link.removeAttribute('data-term');}
    }
    doc.getElementById('exportJson').disabled=false;
    doc.getElementById('calendar').disabled=false;
    doc.getElementById('printResult').disabled=false;
    doc.defaultView.__alo186LedResult=result;
  }

  function download(doc,name,type,text){
    const blob=new Blob([text],{type});
    const url=URL.createObjectURL(blob);
    const a=doc.createElement('a');
    a.href=url;a.download=name;doc.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),0);
  }

  function ics(result){
    const start=new Date(Date.now()+result.revisitDays*86400000);
    const stamp=new Date();
    const fmt=d=>d.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');
    const end=new Date(start.getTime()+30*60000);
    return [
      'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Serit LED Kontrol//TR','CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',`UID:alo186-led-${Date.now()}@alo186.com`,`DTSTAMP:${fmt(stamp)}`,
      `DTSTART:${fmt(start)}`,`DTEND:${fmt(end)}`,
      'SUMMARY:Şerit LED güç ve bağlantı güvenliği kontrolü',
      'DESCRIPTION:Güç kaynağı ve konnektör ısısı; titreme; renk sapması; kablo/ek noktaları; IP contaları; ürün güvenliği duyuruları ve tam yük testi yeniden kontrol edilsin.',
      'END:VEVENT','END:VCALENDAR'
    ].join('\r\n');
  }

  function mount(doc){
    const form=doc.getElementById('ledForm');
    if(!form)return;
    form.addEventListener('submit',event=>{
      event.preventDefault();
      render(doc,calculate(read(doc)));
      doc.getElementById('result').focus();
    });
    doc.querySelectorAll('[data-affiliate-check]').forEach(check=>check.addEventListener('change',()=>{
      const link=doc.getElementById('affiliateLink');
      const checks=[...doc.querySelectorAll('[data-affiliate-check]')];
      const ready=checks.every(item=>item.checked);
      if(ready&&link.dataset.term){
        link.href=amazonUrl(link.dataset.term);
        link.removeAttribute('aria-disabled');
        link.textContent='Amazon Türkiye’de teknik sınıfı karşılaştır';
      }else{
        link.href='#';link.setAttribute('aria-disabled','true');link.textContent='Üç onayı tamamlayın';
      }
    }));
    doc.getElementById('affiliateLink').addEventListener('click',event=>{
      if(event.currentTarget.getAttribute('aria-disabled')==='true')event.preventDefault();
    });
    doc.getElementById('exportJson').addEventListener('click',()=>{
      const result=doc.defaultView.__alo186LedResult;
      if(!result)return;
      const payload={
        generatedAt:new Date().toISOString(),source:'ALO186 bağımsız bilgi platformu',
        route:'/hesaplama/serit-led-guc-kaynagi-uygunluk/',result,
        commercialFields:{price:false,stock:false,rating:false,seller:false,warranty:false}
      };
      download(doc,'alo186-serit-led-teknik-fis.json','application/json;charset=utf-8',JSON.stringify(payload,null,2));
    });
    doc.getElementById('calendar').addEventListener('click',()=>{
      const result=doc.defaultView.__alo186LedResult;
      if(result)download(doc,'alo186-serit-led-kontrol.ics','text/calendar;charset=utf-8',ics(result));
    });
    doc.getElementById('printResult').addEventListener('click',()=>doc.defaultView.print());
  }

  return {calculate,metrics,amazonUrl,ics,mount};
});
