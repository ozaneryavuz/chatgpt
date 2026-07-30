(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const CHARGING_EFFICIENCY=0.90;
  const SINGLE_PHASE_V=230;
  const THREE_PHASE_V=400;
  const OUTLETS={
    schuko:{label:'Ev tipi topraklı priz',phase:'single',maxA:10,portable:true},
    cee_blue_16:{label:'CEE mavi 16 A',phase:'single',maxA:16,portable:true},
    cee_blue_32:{label:'CEE mavi 32 A',phase:'single',maxA:32,portable:true},
    cee_red_16:{label:'CEE kırmızı trifaze 16 A',phase:'three',maxA:16,portable:true},
    cee_red_32:{label:'CEE kırmızı trifaze 32 A',phase:'three',maxA:32,portable:true},
    wallbox:{label:'Sabit wallbox / şarj ünitesi',phase:'unknown',maxA:null,portable:false}
  };
  const CATEGORY_LABELS={portable_evse:'Taşınabilir EV şarj cihazı sınıfı'};

  const n=value=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const round=(value,digits=2)=>Math.round(value*(10**digits))/(10**digits);
  const makeResult=(status,title,summary,extra={})=>({status,title,summary,commercialAllowed:false,categories:[],...extra});

  function powerKw(phase,currentA){
    return phase==='three'
      ? Math.sqrt(3)*THREE_PHASE_V*currentA/1000
      : SINGLE_PHASE_V*currentA/1000;
  }

  function currentForKw(phase,kw){
    return phase==='three'
      ? kw*1000/(Math.sqrt(3)*THREE_PHASE_V)
      : kw*1000/SINGLE_PHASE_V;
  }

  function calculate(input={}){
    if(input.emergency){
      return makeResult('emergency','Şarjı durdurun ve enerjiyi güvenli biçimde kesin','Duman, kıvılcım, yanık kokusu, erime, su teması veya elektrik çarpması riski varsa fişe, araca ya da kabloya yaklaşmadan enerjiyi güvenli biçimde kestirin. Yangın veya yaralanma riski varsa 112’yi arayın.');
    }

    const socketCondition=input.socketCondition||'unknown';
    if(['warm','hot','loose','damaged'].includes(socketCondition)){
      return makeResult('stop_use','Prizi kullanmayın','Şarj sırasında ısınan, gevşek, kararmış, çatlamış veya hasarlı priz/kablo güvenli ürün seçimi konusu değildir. Şarjı durdurun; priz, bağlantı sıkılığı, iletken kesiti, koruma ve topraklama yetkili elektrikçi tarafından kontrol edilmeden devam etmeyin.');
    }

    const extensionUse=input.extensionUse||'unknown';
    if(['extension','reel','multi_adapter'].includes(extensionUse)){
      return makeResult('stop_use','Uzatma kablosu veya çoklayıcıyla EV şarj etmeyin','Taşınabilir EVSE doğrudan uygun, topraklı ve doğrulanmış prize bağlanmalıdır. Kablo makarası, çoklayıcı, dönüştürücü veya ev tipi uzatma kablosu sürekli yüksek akımda ısınma ve temas riski oluşturur.');
    }
    if(extensionUse==='unknown'){
      return makeResult('evidence_required','Bağlantı yolunu doğrulayın','Şarj cihazının doğrudan prize bağlandığını; arada uzatma, makara, çoklayıcı veya dönüştürücü bulunmadığını doğrulayın.');
    }

    const outletType=input.outletType||'unknown';
    if(outletType==='unknown'||!OUTLETS[outletType]){
      return makeResult('evidence_required','Priz tipini doğrulayın','Ev tipi topraklı priz, CEE mavi/kırmızı endüstriyel priz veya sabit wallbox seçeneklerinden gerçek bağlantı noktasını belirleyin.');
    }
    if(outletType==='wallbox'){
      return makeResult('wallbox_path','Wallbox ve tesisat uygunluk testiyle devam edin','Sabit wallbox seçimi taşınabilir EVSE’den farklıdır. Ana besleme, faz, eşzamanlı yük, dinamik yük yönetimi, kablo ve koruma düzenini EV Wallbox ve Tesisat Uygunluğu aracında değerlendirin.',{nextTool:'/hesaplama/ev-sarj-uygunluk/'});
    }

    if(input.dedicatedCircuit==='no'){
      return makeResult('professional','Paylaşımlı devrede taşınabilir şarj önermeyin','EV şarjı uzun süreli yüksek yük oluşturur. Aynı devrede başka priz veya cihaz bulunuyorsa devre kapasitesi, bağlantılar, gerilim düşümü ve seçicilik yetkili elektrikçi tarafından ölçülmeden ürün seçimine ilerlemeyin.');
    }
    if(input.dedicatedCircuit!=='yes'){
      return makeResult('evidence_required','Devrenin bağımsızlığını doğrulayın','Prizin ayrı hat, uygun kesit ve doğru koruma üzerinden beslendiğini yetkili elektrikçi veya güncel proje/ölçüm kaydıyla doğrulayın.');
    }

    if(input.protectiveEarth==='no'){
      return makeResult('stop_use','Koruma iletkeni doğrulanmadan şarj etmeyin','Topraklama piminin bulunması tek başına PE sürekliliği kanıtı değildir. Koruma iletkeni ve hata döngüsü yetkili ölçümle doğrulanmadan şarjı başlatmayın.');
    }
    if(input.protectiveEarth!=='yes'){
      return makeResult('evidence_required','PE sürekliliği ölçümü gerekli','Priz koruma iletkeni, bağlantı sürekliliği ve hata halinde otomatik açma koşulu ölçümle doğrulanmalıdır.');
    }

    if(input.protection==='none'){
      return makeResult('stop_use','EV şarj koruma zinciri eksik','Uygun RCD ve DC kaçak akım algılama düzeni belgelenmeden taşınabilir EVSE kullanılmamalıdır. Ürünün üzerindeki beyan, bina devresinin koruma ve topraklama kontrolünün yerine geçmez.');
    }
    if(!['type_a_6ma','type_b','documented_chain'].includes(input.protection)){
      return makeResult('evidence_required','RCD ve DC kaçak korumasını doğrulayın','Üretici kılavuzu ile tesisattaki RCD/DC kaçak algılama zincirini birlikte doğrulayın. “RCD var” ifadesi tip ve DC davranışı bilinmeden yeterli değildir.');
    }

    if(input.socketInspection==='no'){
      return makeResult('professional','Priz ve bağlantılar kontrol edilmeli','Priz, klemensler, kablo kesiti, sigorta, gerilim düşümü ve uzun süreli ısınma kontrolü yapılmadan sürekli EV yüküne başlamayın.');
    }
    if(input.socketInspection!=='yes'){
      return makeResult('evidence_required','Güncel priz kontrolü gerekli','Prizin fiziksel durumu ve uzun süreli yük uygunluğu yakın tarihli kontrol veya ölçümle doğrulanmalıdır.');
    }

    if(input.outdoorUse==='yes'&&input.ipVerified==='no'){
      return makeResult('stop_use','Dış ortam koruması doğrulanmadan kullanmayın','EVSE, fiş, priz ve bağlantı noktalarının üretici tarafından belirtilen IP/çevre koşulları doğrulanmadan yağmur, su birikintisi veya ıslak zeminde şarj etmeyin.');
    }
    if(input.outdoorUse==='yes'&&input.ipVerified!=='yes'){
      return makeResult('evidence_required','Dış ortam IP koşulunu doğrulayın','EVSE, priz ve konnektörün dış ortam, sıcaklık ve suya karşı kullanım sınırlarını ürün etiketi ve kılavuzdan doğrulayın.');
    }

    if(input.connectorVerified==='no'){
      return makeResult('evidence_required','Araç ve EVSE konnektör uyumu yok','Araç giriş tipi, kablo/EVSE konnektörü ve bölgesel gerilim-frekans uyumu eşleşmeden ürün seçimine ilerlemeyin.');
    }
    if(input.connectorVerified!=='yes'){
      return makeResult('evidence_required','Konnektör ve araç kabulünü doğrulayın','Araç kılavuzundaki AC giriş tipi, azami AC güç ve taşınabilir EVSE kullanım koşullarını doğrulayın.');
    }

    const outlet=OUTLETS[outletType];
    const dailyKm=n(input.dailyKm);
    const consumption=n(input.consumptionKwh100);
    const availableHours=n(input.availableHours);
    const vehicleAcMaxKw=n(input.vehicleAcMaxKw);
    const documentedCurrentA=n(input.documentedCurrentA);
    const evseMaxA=n(input.evseMaxA);

    if(dailyKm===null||dailyKm<=0||dailyKm>600)return makeResult('evidence_required','Günlük kilometreyi doğrulayın','Günlük hedefi 1–600 km aralığında girin.');
    if(consumption===null||consumption<8||consumption>50)return makeResult('evidence_required','Araç tüketimini doğrulayın','Araç ekranı veya üretici verisinden 8–50 kWh/100 km aralığında gerçekçi tüketim girin.');
    if(availableHours===null||availableHours<0.5||availableHours>24)return makeResult('evidence_required','Şarj penceresini doğrulayın','Prizin güvenle kullanılabileceği süreyi 0,5–24 saat aralığında girin.');
    if(vehicleAcMaxKw===null||vehicleAcMaxKw<1||vehicleAcMaxKw>22)return makeResult('evidence_required','Aracın AC kabul gücü gerekli','Araç kılavuzundaki azami AC şarj gücünü 1–22 kW aralığında girin.');
    if(documentedCurrentA===null||documentedCurrentA<6||documentedCurrentA>32)return makeResult('evidence_required','Belgelenmiş devre akımı gerekli','Yetkili kontrol sonucunda izin verilen sürekli akımı 6–32 A aralığında girin.');
    if(documentedCurrentA>outlet.maxA)return makeResult('evidence_required','Belgelenmiş akım priz sınıfını aşıyor',`${outlet.label} için girilen ${documentedCurrentA} A değeri aracın muhafazakâr ${outlet.maxA} A üst sınırını aşıyor. Priz ve adaptör sınıfını yeniden doğrulayın.`);
    if(evseMaxA===null||evseMaxA<6||evseMaxA>32)return makeResult('evidence_required','EVSE akım etiketi gerekli','Taşınabilir şarj cihazının ayarlanabilir/azami akımını 6–32 A aralığında girin.');
    if(evseMaxA>documentedCurrentA&&input.evseAdjustable==='no'){
      return makeResult('stop_use','EVSE akımı devre sınırına indirilemiyor','Taşınabilir EVSE, belgelenmiş devre akımını aşmayacak şekilde güvenilir biçimde sınırlandırılamıyorsa bu prizde kullanılmamalıdır.');
    }
    if(evseMaxA>documentedCurrentA&&input.evseAdjustable!=='yes')return makeResult('evidence_required','EVSE akım ayarını doğrulayın','EVSE’nin akımı devre sınırına sabitleyebildiğini üretici kılavuzundan doğrulayın.');

    const phase=outlet.phase;
    const vehicleMaxCurrentA=currentForKw(phase,vehicleAcMaxKw);
    const installationMaxA=Math.min(outlet.maxA,documentedCurrentA,vehicleMaxCurrentA);
    const usableCurrentA=Math.min(installationMaxA,evseMaxA);
    const availablePowerKw=powerKw(phase,usableCurrentA);
    const batteryEnergyKwh=dailyKm*consumption/100;
    const mainsEnergyKwh=batteryEnergyKwh/CHARGING_EFFICIENCY;
    const requiredAveragePowerKw=mainsEnergyKwh/availableHours;
    const requiredCurrentA=currentForKw(phase,requiredAveragePowerKw);
    const requiredHours=mainsEnergyKwh/availablePowerKw;
    const deliverableKm=availablePowerKw*availableHours*CHARGING_EFFICIENCY*100/consumption;
    const portableMeetsTarget=deliverableKm+0.01>=dailyKm;
    const installationCouldMeet=powerKw(phase,installationMaxA)*availableHours*CHARGING_EFFICIENCY*100/consumption+0.01>=dailyKm;
    const limitingFactor=usableCurrentA+0.01<installationMaxA?'evse':'installation';

    const metrics={
      outletLabel:outlet.label,phase,phaseLabel:phase==='three'?'Trifaze':'Monofaze',
      outletMaxA:outlet.maxA,documentedCurrentA,vehicleMaxCurrentA:round(vehicleMaxCurrentA,1),
      usableCurrentA:round(usableCurrentA,1),availablePowerKw:round(availablePowerKw,2),
      batteryEnergyKwh:round(batteryEnergyKwh,2),mainsEnergyKwh:round(mainsEnergyKwh,2),
      requiredAveragePowerKw:round(requiredAveragePowerKw,2),requiredCurrentA:round(requiredCurrentA,1),
      requiredHours:round(requiredHours,2),deliverableKm:Math.floor(deliverableKm+1e-6),
      portableMeetsTarget,installationCouldMeet,limitingFactor
    };

    if(input.scenario==='active'){
      return makeResult('active_event','Aktif şarjda güvenlik ve sıcaklık takibi önceliklidir',`${outlet.label} üzerinde yaklaşık ${metrics.usableCurrentA} A / ${metrics.availablePowerKw} kW kullanılabilir. Ürün teslimatı anlık çözüm değildir; priz, fiş ve EVSE’de olağandışı ısınma olursa şarjı durdurun.`,{metrics});
    }

    if(input.sourceStatus==='existing'){
      if(input.thermalTest==='failed'){
        return makeResult('stop_use','Mevcut EVSE ısınma testini geçmedi','Priz, fiş, kablo veya EVSE’de olağandışı ısınma görüldüyse daha güçlü cihaz satın almak çözüm değildir. Şarjı durdurun ve tesisat/bağlantıları kontrol ettirin.',{metrics});
      }
      if(input.thermalTest!=='success'||input.chargeTest!=='success'){
        return makeResult('evidence_required','Mevcut EVSE için gerçek şarj testi gerekli','Hesaplanan akımda kontrollü gerçek şarj, araç kabulü, hata vermeden çalışma ve fiş/priz sıcaklık kontrolü başarıyla doğrulanmalıdır.',{metrics});
      }
      if(portableMeetsTarget){
        return makeResult('no_buy','Mevcut taşınabilir EVSE yeterli — yeni ürün almayın',`Mevcut cihaz; ${metrics.usableCurrentA} A, yaklaşık ${metrics.availablePowerKw} kW ve ${availableHours} saatlik pencerede yaklaşık ${metrics.deliverableKm} km günlük enerji sağlayabiliyor. Priz ve kablo sıcaklığını düzenli kontrol edin.`,{metrics});
      }
      if(limitingFactor==='evse'&&installationCouldMeet){
        return makeResult('conditional_purchase','Mevcut EVSE akımı günlük hedef için yetersiz',`Tesisat ve araç yaklaşık ${round(installationMaxA,1)} A seviyesini destekliyor; mevcut EVSE ${evseMaxA} A ile sınırlı. Yalnız üretici kılavuzu, priz ve koruma zinciri bu akıma izin veriyorsa uygun taşınabilir EVSE sınıfına ilerleyin.`,{metrics,categories:['portable_evse'],commercialAllowed:true});
      }
      return makeResult('wallbox_path','Günlük hedef taşınabilir priz kapasitesini aşıyor',`${availableHours} saatte yaklaşık ${metrics.deliverableKm} km enerji sağlanabilir; hedef ${dailyKm} km. Daha güçlü taşınabilir cihaz aynı priz sınırını aşamaz. Wallbox, besleme ve yük yönetimini değerlendirin.`,{metrics,nextTool:'/hesaplama/ev-sarj-uygunluk/'});
    }

    if(!portableMeetsTarget){
      return makeResult('wallbox_path','Taşınabilir şarj günlük hedefi karşılamıyor',`${outlet.label} ve belgelenmiş akım sınırıyla yaklaşık ${metrics.availablePowerKw} kW güç ve ${availableHours} saatte ${metrics.deliverableKm} km enerji sağlanabilir. Hedef ${dailyKm} km için wallbox ve tesisat hesabına ilerleyin.`,{metrics,nextTool:'/hesaplama/ev-sarj-uygunluk/'});
    }

    return makeResult('conditional_purchase','Taşınabilir EVSE teknik sınıfı hesaplandı',`${outlet.label} için üst sınır ${outlet.maxA} A; bu senaryoda kullanılabilir değer ${metrics.usableCurrentA} A ve yaklaşık ${metrics.availablePowerKw} kW. ${availableHours} saatte yaklaşık ${metrics.deliverableKm} km enerji sağlanabilir. Yalnız bu sınırları, koruma zincirini ve konnektör uyumunu karşılayan ürün sınıfına ilerleyin.`,{metrics,categories:['portable_evse'],commercialAllowed:true});
  }

  const statusLabels={
    emergency:'Acil',stop_use:'Kullanmayın',professional:'Profesyonel',evidence_required:'Kanıt gerekli',
    wallbox_path:'Wallbox yolu',active_event:'Aktif şarj',no_buy:'Satın alma yok',conditional_purchase:'Koşullu ürün'
  };

  function readForm(doc){
    const id=name=>doc.getElementById(name);
    const value=name=>id(name)?.value;
    const checked=name=>Boolean(id(name)?.checked);
    return{
      emergency:checked('emergency'),scenario:value('scenario'),outletType:value('outletType'),
      socketCondition:value('socketCondition'),extensionUse:value('extensionUse'),outdoorUse:value('outdoorUse'),
      ipVerified:value('ipVerified'),dedicatedCircuit:value('dedicatedCircuit'),protectiveEarth:value('protectiveEarth'),
      protection:value('protection'),socketInspection:value('socketInspection'),documentedCurrentA:value('documentedCurrentA'),
      dailyKm:value('dailyKm'),consumptionKwh100:value('consumptionKwh100'),availableHours:value('availableHours'),
      vehicleAcMaxKw:value('vehicleAcMaxKw'),evseMaxA:value('evseMaxA'),evseAdjustable:value('evseAdjustable'),
      connectorVerified:value('connectorVerified'),sourceStatus:value('sourceStatus'),thermalTest:value('thermalTest'),
      chargeTest:value('chargeTest')
    };
  }

  function mount(doc){
    const form=doc.getElementById('portableEvseForm');
    if(!form)return;
    const $=id=>doc.getElementById(id);

    const toggle=()=>{
      $('outdoorEvidence').classList.toggle('hidden',$('outdoorUse').value!=='yes');
      $('existingFields').classList.toggle('hidden',$('sourceStatus').value!=='existing');
    };
    const clearOutput=()=>{
      const box=$('result');
      box.hidden=true;
      box.className='panel result';
      $('resultBadge').textContent='';
      $('resultTitle').textContent='';
      $('resultSummary').textContent='';
      $('metrics').innerHTML='';
      const next=$('nextTool');
      next.removeAttribute('href');
      next.classList.add('hidden');
      const commerce=$('commerce');
      commerce.classList.add('hidden');
      commerce.dataset.categories='[]';
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{$(id).checked=false;});
      $('productLinks').innerHTML='';
    };
    ['outdoorUse','sourceStatus'].forEach(id=>$(id)?.addEventListener('change',toggle));
    toggle();

    form.addEventListener('reset',()=>{
      clearOutput();
      if(root&&typeof root.setTimeout==='function')root.setTimeout(toggle,0);
      else toggle();
    });

    form.addEventListener('submit',event=>{
      event.preventDefault();
      const out=calculate(readForm(doc));
      const box=$('result');
      box.className=`panel result status-${out.status}`;
      box.hidden=false;
      $('resultBadge').textContent=statusLabels[out.status]||out.status;
      $('resultTitle').textContent=out.title;
      $('resultSummary').textContent=out.summary;
      const m=out.metrics;
      $('metrics').innerHTML=m?[
        ['Bağlantı',m.outletLabel],['Faz',m.phaseLabel],['Kullanılabilir akım',`${m.usableCurrentA} A`],
        ['Yaklaşık güç',`${m.availablePowerKw} kW`],['Şebekeden enerji',`${m.mainsEnergyKwh} kWh/gün`],
        ['Hedef için süre',`${m.requiredHours} saat`],['Şarj penceresinde menzil',`${m.deliverableKm} km`]
      ].map(([label,value])=>`<article><span>${label}</span><strong>${value}</strong></article>`).join(''):'';
      const next=$('nextTool');
      if(out.nextTool){next.href=out.nextTool;next.classList.remove('hidden');}else{next.removeAttribute('href');next.classList.add('hidden');}
      const commerce=$('commerce');
      commerce.classList.toggle('hidden',!out.commercialAllowed);
      commerce.dataset.categories=JSON.stringify(out.categories||[]);
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{$(id).checked=false;});
      $('productLinks').innerHTML='';
      box.scrollIntoView({behavior:'smooth',block:'start'});
      box.focus({preventScroll:true});
      if(root.Alo186Track)root.Alo186Track('portable_evse_socket_result',{status:out.status,outlet:m?.outletLabel||'none',categories:(out.categories||[]).join(',')});
    });

    const refreshGate=()=>{
      const commerce=$('commerce');
      const enabled=!commerce.classList.contains('hidden')&&['actualNeed','technicalCheck','affiliateCheck'].every(id=>$(id).checked);
      const categories=JSON.parse(commerce.dataset.categories||'[]');
      const target=$('productLinks');
      target.innerHTML='';
      if(!enabled)return;
      categories.forEach(category=>{
        const link=doc.createElement('a');
        link.className='button primary';
        link.href='../../akilli-urun-secimi?kaynak=tasinabilir-ev-sarj-priz&niyet=portable_evse';
        link.textContent='Teknik ürün merkezini aç';
        link.dataset.category=category;
        target.appendChild(link);
      });
    };
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>$(id)?.addEventListener('change',refreshGate));
  }

  return{calculate,mount,powerKw,currentForKw,OUTLETS,CATEGORY_LABELS,CHARGING_EFFICIENCY,SINGLE_PHASE_V,THREE_PHASE_V};
});
