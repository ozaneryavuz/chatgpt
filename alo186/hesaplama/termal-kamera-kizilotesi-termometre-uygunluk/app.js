(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const ELECTRICAL_TASKS=['electrical'];
  const PROFESSIONAL_SITES=['industrial','pv_ev'];

  const labelMap={
    ir_thermometer:'Kızılötesi termometre',
    phone_thermal_camera:'Telefon bağlantılı radyometrik termal kamera',
    handheld_thermal_camera:'El tipi radyometrik termal kamera',
    professional_thermography:'Yetkin kişiyle profesyonel termografi',
    none:'Yeni ürün gerekmiyor'
  };

  const baseResult=(status,title,summary,extra={})=>({
    status,title,summary,commercialAllowed:false,productClass:'none',searchTerm:null,searchUrl:null,
    requirements:[],revisitDays:90,...extra
  });

  function requiredClass(input){
    if(input.task==='spot'&&['single_temp','screening'].includes(input.outputNeed||'')&&input.trendNeed==='no'){
      return 'ir_thermometer';
    }
    if(input.task==='building'||input.task==='electronics'){
      if(input.outputNeed==='screening'&&input.trendNeed==='no')return 'phone_thermal_camera';
      return input.outputNeed==='single_temp'?'ir_thermometer':'phone_thermal_camera';
    }
    if(['electrical','mechanical','reporting'].includes(input.task||'')){
      return 'handheld_thermal_camera';
    }
    return null;
  }

  function classSearch(productClass){
    if(productClass==='ir_thermometer')return 'ayarlanabilir emissivite kızılötesi termometre yüzey sıcaklık ölçer';
    if(productClass==='phone_thermal_camera')return 'telefon termal kamera radyometrik ayarlanabilir emissivite';
    if(productClass==='handheld_thermal_camera')return 'radyometrik termal kamera manuel odak emissivite raporlama';
    return null;
  }

  function hasPatternNeed(input){
    return ['pattern','quantitative','report'].includes(input.outputNeed||'')||
      input.trendNeed==='yes'||['electrical','mechanical','reporting'].includes(input.task||'');
  }

  function evidenceGaps(input,productClass){
    const gaps=[];
    if(!input.surface||input.surface==='unknown')gaps.push('Hedef yüzeyin emissivite ve yansıma davranışını belirtin.');
    if(input.surface==='through_glass')gaps.push('Normal cam veya akriliği termal olarak şeffaf kabul etmeyin; hedefi doğrudan veya uygun IR penceresinden gözlemleyin.');
    if(input.surface==='reflective'&&input.emissivity!=='yes')gaps.push('Parlak metalde emissivite ve yansıyan görünür sıcaklık yöntemi doğrulanmalıdır.');
    if(input.surface==='ir_window'&&input.measurementParams!=='yes')gaps.push('IR penceresinin geçirgenlik verisini ve ölçüm düzeltmesini üretici belgesinden doğrulayın.');
    if(productClass!=='ir_thermometer'&&input.outputNeed!=='screening'){
      if(input.radiometric!=='yes')gaps.push('Nicel karşılaştırma için radyometrik görüntü kaydı gerekir.');
      if(input.emissivity!=='yes')gaps.push('Ayarlanabilir emissivite ve uygulama yöntemi gerekir.');
    }
    if(['quantitative','report'].includes(input.outputNeed||'')&&input.measurementParams!=='yes'){
      gaps.push('Nicel ölçümde yansıyan sıcaklık, mesafe ve ortam parametrelerini ayarlayabilen yöntem gerekir.');
    }
    if(input.outputNeed==='report'&&input.reporting!=='yes')gaps.push('Radyometrik dosya, not ve rapor dışa aktarımı gerekir.');
    if(hasPatternNeed(input)&&input.focus==='fail')gaps.push('Hedef net değilse sıcaklık karışır; göreve uygun odak ve hedef boyutu doğrulanmalıdır.');
    return gaps;
  }

  function existingMatches(input,required){
    if(input.existingType==='none')return false;
    const typeMatch=
      (required==='ir_thermometer'&&['ir_thermometer','phone_camera','handheld_camera'].includes(input.existingType))||
      (required==='phone_thermal_camera'&&['phone_camera','handheld_camera'].includes(input.existingType))||
      (required==='handheld_thermal_camera'&&input.existingType==='handheld_camera');
    if(!typeMatch)return false;
    if(input.condition!=='sound'||input.verification!=='yes'||input.fieldTest!=='pass'||input.recallChecked!=='yes')return false;
    if(required!=='ir_thermometer'){
      if(input.radiometric!=='yes'||input.emissivity!=='yes')return false;
      if(hasPatternNeed(input)&&!['manual','fixed'].includes(input.focus||''))return false;
    }
    if(['quantitative','report'].includes(input.outputNeed||'')&&input.measurementParams!=='yes')return false;
    if(input.outputNeed==='report'&&input.reporting!=='yes')return false;
    return true;
  }

  function calculate(input={}){
    if(input.emergency){
      return baseResult('emergency','Yaklaşmayın; ticari yollar kapalı','Duman, ark, kıvılcım, erime, yanık kokusu, patlama sesi, elektrik çarpması veya kontrolsüz yoğun ısı varsa termal görüntü almaya çalışmayın. Güvenli alan, enerjinin yetkili biçimde kesilmesi ve acil müdahale önceliklidir.');
    }
    if(input.condition==='damaged'){
      return baseResult('stop_use','Hasarlı ölçüm cihazını kullanmayın','Darbe, su, çatlak lens, aşırı ısınma veya güvensiz bağlantı bulunan cihazla ölçüm yapmayın. Ürünü şarj etmeyin veya enerjili ekipmana yaklaştırmayın; üretici ve yetkili servis talimatını izleyin.');
    }
    if(input.recallChecked==='recalled'){
      return baseResult('stop_use','Geri çağırılmış cihazı güvenilir kabul etmeyin','Tam marka-model için kullanım durdurma veya geri çağırma duyurusu varsa üretici ve resmî ürün güvenliği talimatını izleyin. Bu durumda affiliate yönlendirmesi kapalıdır.');
    }
    if(!input.competence||input.competence==='unknown'||!input.exposure||input.exposure==='unknown'||!input.activeWork||input.activeWork==='unknown'){
      return baseResult('evidence_required','Yetkinlik ve elektriksel sınırı tamamlayın','Ürün sınıfından önce kullanıcı yetkinliği, açık enerjili parçaya yaklaşma ihtimali ve incelemenin yalnız uzaktan gözlem olup olmadığı belirlenmelidir.');
    }
    if(input.exposure==='energized_exposed'||input.activeWork==='yes'){
      return baseResult('professional','Açık enerjili ekipmanda tüketici ürünü akışı kapalı','Kapak açma, açık enerjili iletkene yaklaşma veya çalışma ihtiyacı varsa yalnız yetkin kişi, belgeli iş prosedürü, uygun yaklaşma sınırı ve koruyucu donanımla değerlendirme yapılabilir. Termal kamera satın almak çalışma izni oluşturmaz.');
    }
    if(ELECTRICAL_TASKS.includes(input.task||'')&&input.competence!=='qualified'){
      return baseResult('professional','Elektriksel termografiyi yetkin kişiye bırakın','Pano, sigorta, bara, bağlantı veya kablo termografisi; yük durumu, elektriksel yaklaşma sınırı, ark riski ve takip ölçümleri nedeniyle genel kullanıcı veya yalnız temel bakım yetkinliğiyle affiliate sonucuna dönüştürülmez.');
    }
    if(PROFESSIONAL_SITES.includes(input.siteType||'')&&input.competence!=='qualified'){
      return baseResult('professional','Bu tesis için profesyonel termografi planı gerekir','Endüstriyel, GES, EV şarj, UPS veya yüksek enerjili sistemlerde cihaz satın almadan önce risk değerlendirmesi, ölçüm rotası, yük koşulu, raporlama ve yetkin personel planı gerekir.');
    }
    if(!input.task||input.task==='unknown'||!input.outputNeed||input.outputNeed==='unknown'||!input.trendNeed||input.trendNeed==='unknown'){
      return baseResult('evidence_required','Ölçüm görevini ve çıktıyı seçin','Tek nokta yüzey sıcaklığı, alan deseni, nicel trend ve radyometrik rapor farklı cihaz sınıfları gerektirir. Gereksiz yüksek sınıf ürün önermek için görev varsayılmaz.');
    }

    const required=requiredClass(input);
    if(!required){
      return baseResult('evidence_required','Göreve uygun cihaz sınıfı belirlenemedi','Görev ve çıktı seçimini yeniden kontrol edin. Termal kamera yalnız “daha gelişmiş” olduğu için otomatik önerilmez.');
    }

    if(input.surface==='through_glass'){
      return baseResult('evidence_required','Normal cam arkasından ölçümü güvenilir kabul etmeyin','Normal cam veya akrilik uzun dalga termal görüntülemede hedefi güvenilir biçimde göstermez. Doğrudan güvenli görüş, üretici verisi bilinen IR penceresi veya farklı bir ölçüm yöntemi gerekir.');
    }

    if(input.existingType!=='none'){
      if(input.condition!=='sound'){
        return baseResult('evidence_required','Mevcut cihazın fiziksel durumunu doğrulayın','Lens, gövde, bağlantı, batarya ve kablonun sağlam olduğunu doğrulamadan yeni ürün ihtiyacı veya mevcut cihaz yeterliliği belirlenemez.');
      }
      if(input.recallChecked!=='yes'){
        return baseResult('evidence_required','Tam model ürün güvenliği kontrolünü tamamlayın','Üretici ve resmî ürün güvenliği duyurularını tam marka-modelle kontrol edin. Pazar yeri ilanı güvenlik kanıtı değildir.');
      }
      if(input.verification==='fail'){
        return baseResult('stop_use','Ölçüm doğrulaması başarısız','Bilinen hedef veya üretici prosedürüyle tutarsız sonuç, donma veya bağlantı hatası varsa cihazı nicel karar için kullanmayın. Kalibrasyon/servis değerlendirmesi satın almadan önce gelir.');
      }
      if(input.verification!=='yes'){
        return baseResult('evidence_required','Yeni ürün almadan önce mevcut cihazı doğrulayın','Bilinen hedef veya üretici prosedürüyle işlev kontrolü yapın. Mevcut cihazın doğruluğu ve kararlılığı bilinmeden sırf yeni model olduğu için değişim önerilmez.');
      }
      if(input.fieldTest==='fail'){
        const requirements=evidenceGaps(input,required);
        return baseResult('conditional_purchase','Mevcut cihaz gerçek görevi karşılamıyor','Gerçek görev testinde hedef seçilemiyor, sonuç tekrarlanamıyor veya gerekli rapor üretilemiyorsa yalnız kanıtlanan eksik özellik için cihaz sınıfı değerlendirilebilir.',{
          commercialAllowed:requirements.length===0,productClass:required,searchTerm:classSearch(required),requirements
        });
      }
      if(input.fieldTest!=='pass'){
        return baseResult('test_existing','Yeni ürün almadan önce gerçek görev testini yapın','Aynı yük, mesafe, açı, emissivite ve odak ayarlarında tekrarlanabilir saha testi yapın. Mevcut cihaz görevi karşılıyorsa yeni ürün almayın.');
      }
    }

    const gaps=evidenceGaps(input,required);
    if(gaps.length){
      return baseResult('evidence_required','Ölçüm kanıtlarını tamamlayın','Yüzey ve nicel ölçüm parametreleri tamamlanmadan ürün yolu açılmaz. Eksik kanıtı daha yüksek fiyatlı veya daha yüksek çözünürlüklü cihaz satın alarak çözülmüş saymayın.',{
        productClass:required,requirements:gaps
      });
    }

    if(existingMatches(input,required)){
      return baseResult('no_buy','Mevcut cihaz yeterli — yeni ürün almayın','Mevcut cihaz görev sınıfını, fiziksel güvenliği, ürün güvenliği kontrolünü, gerekli ölçüm ayarlarını, raporlamayı ve tekrarlanabilir gerçek görev testini karşılıyor. Aynı yük ve ayarlarla trend kaydını sürdürün.',{
        productClass:'none',
        requirements:[
          'Aynı yük, mesafe, açı, emissivite ve odak ayarlarını kaydedin.',
          'Termal anomalinin kök nedenini elektriksel veya mekanik takip ölçümüyle doğrulayın.',
          '90 gün sonra fiziksel durum, ürün güvenliği ve trend karşılaştırmasını yenileyin.'
        ]
      });
    }

    if(input.existingType!=='none'&&input.fieldTest==='pass'){
      return baseResult('evidence_required','Mevcut cihazla özellik eşleşmesini tamamlayın','Gerçek test başarılı görünse de seçilen görev için radyometrik kayıt, emissivite, odak veya raporlama özelliklerinden biri doğrulanmadı. Önce tam model kılavuzunu kontrol edin; gereksiz satın alma yapmayın.',{
        productClass:required
      });
    }

    const requirements=[
      required==='ir_thermometer'
        ? 'Görüş alanı/hedef oranını, ayarlanabilir emissiviteyi ve yüzey sıcaklık aralığını tam model belgesinden doğrulayın.'
        : 'Termal çözünürlük, odak, radyometrik kayıt, emissivite ve raporlama işlevlerini gerçek hedefte doğrulayın.',
      'Ölçümü aynı yük, mesafe, açı ve ortam koşulunda tekrarlanabilir hâle getirin.',
      'Termal görüntüyü arıza teşhisi değil, takip ölçümü gerektiren bir tarama kanıtı olarak kullanın.'
    ];
    return baseResult('conditional_purchase',
      required==='ir_thermometer'?'Tek nokta görevi için sade cihaz sınıfı yeterli olabilir':'Gerçek görüntüleme açığı doğrulandı',
      required==='ir_thermometer'
        ? 'Görev yalnız erişilebilir tek yüzey noktasının yaklaşık sıcaklığıysa termal kamera yerine ayarlanabilir emissiviteli kızılötesi termometre daha düşük maliyetli ve yeterli olabilir.'
        : 'Alan deseni, trend veya radyometrik rapor ihtiyacı var ve mevcut uygun cihaz bulunmuyor. Yalnız gerekli özellikleri karşılayan teknik sınıfa geçin; çözünürlük veya NETD değerini tek başına satın alma gerekçesi yapmayın.',
      {commercialAllowed:true,productClass:required,searchTerm:classSearch(required),requirements}
    );
  }

  function affiliateUrl(searchTerm){
    const query=encodeURIComponent(searchTerm||'termal kamera');
    return `https://www.amazon.com.tr/s?k=${query}&tag=${AFFILIATE_TAG}`;
  }

  function text(id,doc){return doc.getElementById(id);}
  function value(id,doc){const el=text(id,doc);return el?el.value:null;}
  function checked(id,doc){const el=text(id,doc);return Boolean(el&&el.checked);}

  function readInput(doc){
    return {
      emergency:checked('emergency',doc),
      competence:value('competence',doc),exposure:value('exposure',doc),siteType:value('siteType',doc),
      activeWork:value('activeWork',doc),task:value('task',doc),outputNeed:value('outputNeed',doc),
      surface:value('surface',doc),trendNeed:value('trendNeed',doc),existingType:value('existingType',doc),
      condition:value('condition',doc),resolution:value('resolution',doc),radiometric:value('radiometric',doc),
      emissivity:value('emissivity',doc),measurementParams:value('measurementParams',doc),focus:value('focus',doc),
      reporting:value('reporting',doc),verification:value('verification',doc),fieldTest:value('fieldTest',doc),
      recallChecked:value('recallChecked',doc)
    };
  }

  function statusLabel(status){
    return ({
      emergency:'Acil',stop_use:'Kullanımı durdur',professional:'Profesyonel sınır',
      evidence_required:'Kanıt gerekli',test_existing:'Önce mevcut cihazı test et',
      no_buy:'Satın alma yok',conditional_purchase:'Koşullu teknik kategori'
    })[status]||'Sonuç';
  }

  function render(doc,result,input){
    const box=text('result',doc);
    box.hidden=false;box.dataset.status=result.status;
    text('statusBadge',doc).textContent=statusLabel(result.status);
    text('resultTitle',doc).textContent=result.title;
    text('resultSummary',doc).textContent=result.summary;
    text('productClass',doc).textContent=labelMap[result.productClass]||'Profesyonel değerlendirme';
    text('commerceState',doc).textContent=result.commercialAllowed?'Üç onaydan sonra koşullu':'Kapalı';
    const req=text('requirements',doc);
    req.innerHTML='';
    (result.requirements||[]).forEach(item=>{
      const p=doc.createElement('p');p.textContent=item;req.appendChild(p);
    });

    const gate=text('affiliateGate',doc);
    gate.hidden=!result.commercialAllowed;
    ['confirmNeed','confirmTech','confirmAffiliate'].forEach(id=>{text(id,doc).checked=false;});
    const link=text('affiliateLink',doc);
    link.href='#';link.classList.add('disabled');link.setAttribute('aria-disabled','true');
    link.dataset.searchTerm=result.searchTerm||'';

    box._aloResult=result;box._aloInput=input;
    box.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function updateGate(doc){
    const link=text('affiliateLink',doc);
    const open=checked('confirmNeed',doc)&&checked('confirmTech',doc)&&checked('confirmAffiliate',doc);
    if(open){
      link.href=affiliateUrl(link.dataset.searchTerm);
      link.classList.remove('disabled');link.setAttribute('aria-disabled','false');
    }else{
      link.href='#';link.classList.add('disabled');link.setAttribute('aria-disabled','true');
    }
  }

  function download(doc,name,type,content){
    const blob=new Blob([content],{type});
    const url=URL.createObjectURL(blob);
    const a=doc.createElement('a');a.href=url;a.download=name;doc.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }

  function buildIcs(result){
    const start=new Date();start.setDate(start.getDate()+(result.revisitDays||90));
    const y=start.getFullYear(),m=String(start.getMonth()+1).padStart(2,'0'),d=String(start.getDate()).padStart(2,'0');
    const dt=`${y}${m}${d}T090000`;
    const desc='Termal görüntüleme kontrolü: fiziksel durum ve geri çağırma; aynı yük/mesafe/açı/emissivite/odak; doğrulama hedefi; trend karşılaştırması; elektriksel güvenlik sınırı. Fiyat veya kampanya takibi değildir.';
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Termal Kontrol//TR','BEGIN:VEVENT',
      `UID:alo186-termal-${Date.now()}@alo186.com`,`DTSTART:${dt}`,`SUMMARY:Termal ölçüm güvenlik ve trend kontrolü`,
      `DESCRIPTION:${desc}`,'END:VEVENT','END:VCALENDAR'].join('\r\n');
  }

  function mount(doc){
    const form=text('thermalForm',doc);if(!form)return;
    form.addEventListener('submit',event=>{
      event.preventDefault();
      const input=readInput(doc);const result=calculate(input);render(doc,result,input);
    });
    ['confirmNeed','confirmTech','confirmAffiliate'].forEach(id=>text(id,doc).addEventListener('change',()=>updateGate(doc)));
    text('downloadJson',doc).addEventListener('click',()=>{
      const box=text('result',doc);if(!box._aloResult)return;
      const payload={
        generatedAt:new Date().toISOString(),source:'ALO186 bağımsız ön kontrol',
        input:box._aloInput,result:box._aloResult,
        commercialFieldsUsed:{price:false,stock:false,rating:false,seller:false,delivery:false,warranty:false},
        note:'Termografi raporu, elektriksel çalışma izni veya arıza teşhisi değildir.'
      };
      download(doc,'alo186-termal-uygunluk.json','application/json;charset=utf-8',JSON.stringify(payload,null,2));
    });
    text('downloadIcs',doc).addEventListener('click',()=>{
      const box=text('result',doc);if(!box._aloResult)return;
      download(doc,'alo186-termal-kontrol.ics','text/calendar;charset=utf-8',buildIcs(box._aloResult));
    });
    text('printResult',doc).addEventListener('click',()=>{
      const view=doc.defaultView;
      if(view&&typeof view.print==='function')view.print();
    });
  }

  return {calculate,requiredClass,evidenceGaps,existingMatches,affiliateUrl,buildIcs,mount,AFFILIATE_TAG};
});
