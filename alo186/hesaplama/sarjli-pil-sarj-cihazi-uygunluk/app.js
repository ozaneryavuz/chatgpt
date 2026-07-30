(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const AFFILIATE_TAG='alo186rehber-21';
  const CHEMISTRY={
    nimh:{voltage:1.2,factor:1.4,label:'Ni-MH'},
    nicd:{voltage:1.2,factor:1.4,label:'Ni-Cd'},
    li15:{voltage:1.5,factor:1.2,label:'1,5 V regüle Li-ion'},
    liion:{voltage:3.6,factor:1.2,label:'Li-ion'},
    lifepo4:{voltage:3.2,factor:1.2,label:'LiFePO₄'}
  };
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
    status,title,summary,commercialAllowed:false,searchTerm:null,productClass:null,
    nominalVoltage:null,totalEnergyWh:null,estimatedHours:null,chargeRateC:null,
    reviewDays:120,...extra
  });

  function metrics(input={}){
    const chemistry=CHEMISTRY[input.chemistry]||null;
    const capacityMah=num(input.capacityMah);
    const chargeCurrentMa=num(input.chargeCurrentMa);
    const cells=num(input.cells);
    const nominalVoltage=chemistry?chemistry.voltage:null;
    const totalEnergyWh=chemistry&&capacityMah&&cells?chemistry.voltage*(capacityMah/1000)*cells:null;
    const estimatedHours=chemistry&&capacityMah&&chargeCurrentMa?capacityMah/chargeCurrentMa*chemistry.factor:null;
    const chargeRateC=capacityMah&&chargeCurrentMa?chargeCurrentMa/capacityMah:null;
    return {
      nominalVoltage:round(nominalVoltage,2),
      totalEnergyWh:round(totalEnergyWh,2),
      estimatedHours:round(estimatedHours,1),
      chargeRateC:round(chargeRateC,2),
      capacityMah,chargeCurrentMa,cells
    };
  }
  function enrich(result,m){return {...result,...m};}

  function searchTerm(input,m){
    const model=(input.modelCode||'').trim();
    if(input.chemistry==='li15'){
      return `${model} 1.5 V şarjlı pil üretici onaylı şarj cihazı seti`.trim();
    }
    if(input.format==='9v'){
      return `9V Ni-MH akıllı pil şarj cihazı bağımsız kontrol otomatik kesme`;
    }
    const size=input.format==='aaa'?'AAA':input.format==='aa'?'AA':'AA AAA';
    return `${size} Ni-MH akıllı pil şarj cihazı bağımsız kanal eksi delta V sıcaklık ters kutup`;
  }

  function calculate(input={}){
    const m=metrics(input);
    const done=result=>enrich(result,m);

    if(input.emergency){
      return done(base('emergency','Pili ve şarj cihazını güvenle enerjisiz bırakın','Duman, alev, tıslama, patlama, keskin kimyasal koku veya hızla artan ısı varsa pile dokunmayın. Güvenli alana geçin; yangın, yaralanma veya yoğun dumanda 112 önceliklidir. Bütün ticari yollar kapalıdır.'));
    }
    if(['swollen','leaking','hot','damaged','rusted','wet'].includes(input.condition||'')){
      return done(base('stop_use','Bu pili veya şarj cihazını kullanmayın','Şişmiş, akmış, paslanmış, ezilmiş, yırtık kılıflı, ıslanmış ya da olağandışı ısınan hücre yeniden şarj edilmez. Kutupları kısa devre ettirmeden yerel atık ve geri dönüşüm prosedürünü izleyin.'));
    }
    if(input.condition!=='sound'){
      return done(base('evidence_required','Fiziksel durumu doğrulayın','Pil kılıfı, kutuplar, şarj yuvası, kablo ve adaptör sağlam, kuru, temiz ve ısınma izsiz olmalıdır.'));
    }
    if(['coin','button'].includes(input.format||'')){
      return done(base('stop_use','Düğme ve madeni para pilleri bu alışveriş akışının dışındadır','Yutulma riski nedeniyle çocuklardan tamamen uzak, kilitli saklama ve tam üretici uyumluluğu gerekir. Genel “şarj edilebilir CR2032” yönlendirmesi yapılmaz.'));
    }
    if(['18650','21700'].includes(input.format||'')){
      return done(base('professional','Gevşek 18650/21700 hücre için genel tüketici yönlendirmesi yapılmaz','Korumasız, yeniden sarılmış veya batarya paketinden ayrılmış gevşek lityum hücreler kısa devre, yangın ve patlama riski taşır. Yalnız cihaz üreticisinin kapalı, korumalı batarya paketi ve onaylı şarj sistemi kullanılmalıdır.'));
    }
    if(input.rechargeableMark==='no'||['alkaline','zinc','lithium_primary'].includes(input.chemistry||'')){
      return done(base('stop_use','Tek kullanımlık pili şarj etmeyin','Alkalin, çinko-karbon ve birincil lityum piller şarj edilebilir olarak işaretlenmedikçe şarj cihazına konulmaz. “Recondition/refresh” seçeneği tek kullanımlık pili güvenli biçimde şarj edilebilir yapmaz.'));
    }
    if(input.rechargeableMark!=='yes'){
      return done(base('evidence_required','Pilin şarj edilebilir işaretini doğrulayın','Pil üzerinde açık kimya, nominal voltaj, kapasite ve “rechargeable/şarj edilebilir” işareti bulunmalıdır.'));
    }
    if(!['aa','aaa','9v','proprietary'].includes(input.format||'')){
      return done(base('evidence_required','Pil biçimini seçin','Bu araç AA, AAA, 9 V Ni-MH ve üreticiye özgü 1,5 V şarjlı pil setleri içindir.'));
    }
    if(input.chemistry==='nicd'){
      return done(base('professional','Ni-Cd pil için eski sistem ve atık yönetimi kontrolü gerekir','Ni-Cd şarj profili Ni-MH ile aynı kabul edilmez. Tam cihaz kılavuzu, özel şarj cihazı ve yerel tehlikeli atık prosedürü olmadan ürün yönlendirmesi yapılmaz.'));
    }
    if(['liion','lifepo4'].includes(input.chemistry||'')){
      return done(base('professional','Açık lityum hücre şarjı bu tüketici aracının dışındadır','3,6/3,7 V Li-ion ile 3,2 V LiFePO₄ aynı şarj profili değildir. Koruma devresi, hücre üreticisi, şarj sonu gerilimi ve sıcaklık izleme profesyonel olarak doğrulanmalıdır.'));
    }
    if(!['nimh','li15'].includes(input.chemistry||'')){
      return done(base('evidence_required','Pil kimyasını etiketten doğrulayın','Ni-MH ile 1,5 V regüle Li-ion pil aynı şarj cihazında varsayılan olarak uyumlu değildir.'));
    }
    if(input.chemistry==='nimh'&&!['aa','aaa','9v'].includes(input.format)){
      return done(base('evidence_required','Ni-MH pil biçimini doğrulayın','AA, AAA veya 9 V Ni-MH için tam model uyumluluk tablosu gerekir.'));
    }
    if(input.chemistry==='li15'){
      if(input.format!=='proprietary'){
        return done(base('evidence_required','1,5 V Li-ion pili üreticiye özgü set olarak değerlendirin','USB-C uçlu veya özel şarj kutulu 1,5 V lityum piller, görünüşleri AA/AAA olsa da Ni-MH şarj cihazına konulmaz.'));
      }
      if(input.chargerType!=='manufacturer_specific'||!(input.modelCode||'').trim()){
        return done(base('evidence_required','Tam üretici-model eşleşmesi gerekir','1,5 V regüle lityum pil yalnız üreticinin aynı model ailesi için belirttiği şarj cihazı veya kabloyla şarj edilmelidir.'));
      }
    }
    if(input.chemistry==='nimh'&&!['smart_nimh','manufacturer_specific'].includes(input.chargerType||'')){
      return done(base('evidence_required','Ni-MH uyumlu akıllı şarj profili doğrulayın','Yalnız yuvası fiziksel olarak uyan “universal” veya zamanlayıcılı cihaz yeterli değildir. Tam modelde Ni-MH, doluluk algılama ve güvenlik kesmeleri doğrulanmalıdır.'));
    }
    if(input.supportedChemistry!==input.chemistry){
      return done(base('stop_use','Şarj cihazı ile pil kimyası eşleşmiyor','Ni-MH, 1,5 V regüle Li-ion, 3,6/3,7 V Li-ion ve LiFePO₄ profilleri birbirinin yerine kullanılamaz.'));
    }
    if(input.polarity!=='verified'){
      return done(base('evidence_required','Kutup yönünü ve yuva temasını doğrulayın','Artı/eksi yönü, yuva boyutu ve temas noktaları tam kılavuza göre yerleşmelidir; zorlayarak takmayın.'));
    }
    if(input.environment==='wet'||input.environment==='flammable'){
      return done(base('stop_use','Şarj ortamı uygun değil','Islak, çok sıcak, kapalı kutu içinde, yatak-koltuk üzerinde veya yanıcı malzeme yakınında şarj etmeyin. Sert, kuru, havalanan ve yanmaz yüzey kullanın.'));
    }
    if(input.environment!=='safe'){
      return done(base('evidence_required','Şarj ortamını doğrulayın','Şarj cihazı açıkta, havalanan, kuru ve yanmaz bir yüzeyde olmalıdır.'));
    }
    if(input.unattended==='yes'){
      return done(base('stop_use','Gözetimsiz veya uyurken şarj etmeyin','İlk kullanımda ve pil durumu belirsizken şarjı gözlemleyin; koku, aşırı ısı, şişme veya hata ışığında enerjiyi kesin.'));
    }
    if(input.unattended!=='no'){
      return done(base('evidence_required','Gözetimli şarj planını doğrulayın','Şarj sırasında evde ve uyanık olun; cihazı kapalı alanda veya çıkış yolunda bırakmayın.'));
    }

    const maxCurrent=num(input.maxChargeCurrentMa);
    if(m.capacityMah===null||m.capacityMah<=0||m.capacityMah>10000){
      return done(base('evidence_required','Pil kapasitesini etiketten girin','mAh değeri tam pil etiketinden alınmalıdır; pazarlama kapasitesi veya cihaz tüketimi değildir.'));
    }
    if(m.chargeCurrentMa===null||m.chargeCurrentMa<=0||m.chargeCurrentMa>5000){
      return done(base('evidence_required','Şarj yuvası akımını girin','Toplam adaptör akımı yerine, kullanılan yuva başına çıkış akımını tam model teknik bilgisinden alın.'));
    }
    if(maxCurrent===null||maxCurrent<=0){
      return done(base('evidence_required','Pilin izin verilen azami şarj akımını doğrulayın','Pil üreticisinin veri sayfası veya uyumluluk tablosu olmadan yalnız kapasiteye bakarak güvenli akım atanmaz.'));
    }
    if(m.cells===null||m.cells<1||m.cells>8){
      return done(base('evidence_required','Aynı anda şarj edilen pil sayısını girin','Şarj cihazının güç paylaşımı ve kanal düzeni takılan pil sayısıyla değişebilir.'));
    }
    if(m.chargeCurrentMa>maxCurrent){
      const term=searchTerm(input,m);
      return done(base('replace_candidate','Şarj akımı pil sınırını aşıyor',`${m.chargeCurrentMa} mA yuva akımı, üreticinin ${maxCurrent} mA azami değerini aşıyor. Bu eşleşmeyi kullanmayın; akımı otomatik veya açıkça uygun sınıra getiren tam model gerekir.`,{commercialAllowed:true,searchTerm:term,productClass:'battery_charger'}));
    }
    if(input.chemistry==='nimh'){
      if(input.protections!=='verified'){
        return done(base('evidence_required','Ni-MH güvenlik kesmelerini doğrulayın','Otomatik şarj sonu algılama, ters kutup/kuru pil algılama, kısa devre ve aşırı sıcaklık/zaman koruması tam modelde doğrulanmalıdır.'));
      }
      if(input.grouping==='mixed'&&input.independentChannels!=='yes'){
        return done(base('stop_use','Farklı pil çiftlerini ortak kanalda şarj etmeyin','Farklı kapasite, yaş, doluluk veya boyuttaki Ni-MH piller ancak her yuvası bağımsız izlenen bir şarj cihazında ayrı ayrı yönetilebilir.'));
      }
      if(input.grouping==='single'&&input.independentChannels!=='yes'){
        return done(base('evidence_required','Tek pil şarjı için bağımsız kanal gerekir','Bazı şarj cihazları yalnız eşleşmiş çiftleri kabul eder. Tek yuva kontrolü tam model kılavuzunda doğrulanmalıdır.'));
      }
      if(!['matched','mixed','single'].includes(input.grouping||'')){
        return done(base('evidence_required','Pil gruplamasını belirtin','Aynı cihazda kullanılan pilleri kapasite, yaş ve kullanım döngüsü açısından grup halinde yönetin.'));
      }
    }
    if(input.recallChecked==='recalled'){
      return done(base('stop_use','Geri çağrılmış pil veya şarj cihazını kullanmayın','Tam marka-model için resmî geri çağırma veya kullanım durdurma duyurusu varsa çözüm talimatını izleyin; ticari yol kapalıdır.'));
    }
    if(input.recallChecked!=='yes'){
      return done(base('evidence_required','Tam model geri çağırma kontrolünü tamamlayın','Üretici ve resmî ürün güvenliği kaynaklarını tam model numarasıyla kontrol edin.'));
    }
    if(input.certification!=='yes'){
      return done(base('evidence_required','Ürün güvenliği ve izlenebilirlik kanıtı gerekir','Şarj cihazında üretici, model, kılavuz ve IEC 60335-2-29 veya eşdeğer güvenlik kanıtı; pilde kimyaya uygun IEC 61951-2 ya da IEC 62133-2 kanıtı doğrulanmalıdır.'));
    }

    const term=searchTerm(input,m);
    const productClass=input.chemistry==='nimh'?'nimh_charger':'matched_li15_set';
    if(input.ownership==='owned'){
      if(input.existingStatus==='heats'||input.supervisedTest==='fail'){
        return done(base('stop_use','Mevcut pil veya şarj cihazı gerçek testte başarısız','Aşırı ısı, koku, şişme, hata ışığı, akma veya beklenmeyen kapanma varsa kullanımı durdurun. Kök neden belirlenmeden yeni pil takarak denemeye devam etmeyin.'));
      }
      if(input.existingStatus!=='good'||input.supervisedTest!=='pass'){
        return done(base('test_existing','Mevcut seti gözetimli şarj ve kullanım testinde doğrulayın','Üretici talimatına göre tek döngüde şarj süresini, yuva/pil sıcaklığını, hata göstergesini ve cihazdaki gerçek çalışma süresini kaydedin.'));
      }
      return done(base('no_buy','Mevcut pil ve şarj cihazı yeterli; yeni ürün almayın',`Kimya, biçim, ${m.chargeCurrentMa} mA yuva akımı, yaklaşık ${m.estimatedHours} saat ön şarj süresi, güvenlik kesmeleri, geri çağırma ve gözetimli test uygunsa yeni ürün aramayın.`));
    }
    if(input.ownership!=='candidate'){
      return done(base('evidence_required','Mevcut set mi aday ürün mü belirtin','Satın almama sonucu ile aday ürün ön seçimi ayrı değerlendirilir.'));
    }
    return done(base('conditional_purchase','Teknik ön koşullar karşılanıyor',`${CHEMISTRY[input.chemistry].label} pil için yaklaşık ${m.totalEnergyWh} Wh toplam enerji ve ${m.estimatedHours} saat ön şarj süresi hesaplandı. Bu süre garanti değildir; sıcaklık, pil yaşı, doluluk algılama ve üretici algoritması sonucu değiştirir. Satın almadan önce tam model uyumluluğu ve güvenlik kanıtlarını yeniden doğrulayın.`,{commercialAllowed:true,searchTerm:term,productClass}));
  }

  function affiliateUrl(result){
    if(!result||!result.commercialAllowed||!result.searchTerm)return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(result.searchTerm)}&tag=${AFFILIATE_TAG}`;
  }

  function mount(doc){
    const form=doc.getElementById('batteryForm');
    if(!form)return;
    const ids=['condition','format','chemistry','rechargeableMark','chargerType','supportedChemistry','modelCode','polarity','capacityMah','chargeCurrentMa','maxChargeCurrentMa','cells','independentChannels','protections','grouping','environment','unattended','recallChecked','certification','ownership','existingStatus','supervisedTest'];
    const resultBox=doc.getElementById('result');
    const commerce=doc.getElementById('commerce');
    const affiliate=doc.getElementById('affiliate');
    const confirmations=[...doc.querySelectorAll('.confirm')];
    let latest=null;
    const values=()=>({emergency:doc.getElementById('emergency').checked,...Object.fromEntries(ids.map(id=>[id,doc.getElementById(id).value]))});
    const statusText=status=>({
      emergency:'Acil güvenlik',stop_use:'Kullanımı durdurun',professional:'Profesyonel değerlendirme',
      evidence_required:'Kanıt gerekli',replace_candidate:'Uyumsuz aday',test_existing:'Önce gerçek test',
      no_buy:'Satın alma yok',conditional_purchase:'Koşullu ürün yolu'
    })[status]||'Sonuç';
    const nextText=status=>({
      emergency:'112 / güvenli alan',stop_use:'Enerjisiz bırakın',professional:'Yetkin batarya servisi',
      evidence_required:'Etiket ve kılavuz',replace_candidate:'Doğru şarj profili',test_existing:'Gözetimli döngü',
      no_buy:'Mevcut seti kullanın',conditional_purchase:'Tam model doğrulaması'
    })[status]||'Kontrol';
    const updateGate=()=>{
      const url=affiliateUrl(latest);
      const open=Boolean(url)&&confirmations.every(box=>box.checked);
      if(open){affiliate.href=url;affiliate.removeAttribute('aria-disabled');affiliate.tabIndex=0;}
      else{affiliate.removeAttribute('href');affiliate.setAttribute('aria-disabled','true');affiliate.tabIndex=-1;}
    };
    const download=(name,type,text)=>{
      const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const a=doc.createElement('a');
      a.href=url;a.download=name;doc.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
    };
    form.addEventListener('submit',event=>{
      event.preventDefault();latest=calculate(values());
      doc.getElementById('status').textContent=statusText(latest.status);
      doc.getElementById('resultTitle').textContent=latest.title;
      doc.getElementById('summary').textContent=latest.summary;
      doc.getElementById('voltageMetric').textContent=latest.nominalVoltage!==null?`${latest.nominalVoltage.toLocaleString('tr-TR')} V / hücre`:'—';
      doc.getElementById('energyMetric').textContent=latest.totalEnergyWh!==null?`${latest.totalEnergyWh.toLocaleString('tr-TR')} Wh`:'—';
      doc.getElementById('timeMetric').textContent=latest.estimatedHours!==null?`${latest.estimatedHours.toLocaleString('tr-TR')} saat`:'—';
      doc.getElementById('rateMetric').textContent=latest.chargeRateC!==null?`${latest.chargeRateC.toLocaleString('tr-TR')} C`:'—';
      doc.getElementById('nextMetric').textContent=nextText(latest.status);
      commerce.hidden=!latest.commercialAllowed;confirmations.forEach(box=>{box.checked=false;});updateGate();
      resultBox.hidden=false;resultBox.focus();
    });
    confirmations.forEach(box=>box.addEventListener('change',updateGate));
    form.addEventListener('reset',()=>setTimeout(()=>{latest=null;resultBox.hidden=true;commerce.hidden=true;confirmations.forEach(box=>{box.checked=false;});updateGate();},0));
    doc.getElementById('downloadJson').addEventListener('click',()=>{
      if(!latest)return;
      download('alo186-sarjli-pil-teknik-fis.json','application/json;charset=utf-8',JSON.stringify({
        tool:'ALO186 Şarjlı Pil ve Şarj Cihazı Uygunluk Testi',generatedAt:new Date().toISOString(),
        personalData:false,inputs:values(),result:latest,
        assumptions:{chargeTimeFactors:{nimh:1.4,li15:1.2},note:'Ön planlama katsayılarıdır; üretici algoritması önceliklidir.'}
      },null,2));
    });
    doc.getElementById('downloadIcs').addEventListener('click',()=>{
      if(!latest)return;
      const date=new Date();date.setUTCDate(date.getUTCDate()+latest.reviewDays);const end=new Date(date);end.setUTCDate(end.getUTCDate()+1);
      const stamp=d=>`${d.getUTCFullYear()}${String(d.getUTCMonth()+1).padStart(2,'0')}${String(d.getUTCDate()).padStart(2,'0')}`;
      const text=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Sarjli Pil Kontrolu//TR','BEGIN:VEVENT',`DTSTART;VALUE=DATE:${stamp(date)}`,`DTEND;VALUE=DATE:${stamp(end)}`,'SUMMARY:Sarjli pil ve sarj cihazi kontrolu','DESCRIPTION:Pil kilifi, akma-sisme, kimya, yuva akimi, geri cagirma, guvenlik kesmeleri ve gercek sarj testini kontrol edin.','END:VEVENT','END:VCALENDAR'].join('\r\n');
      download('alo186-sarjli-pil-120-gun-kontrol.ics','text/calendar;charset=utf-8',text);
    });
    doc.getElementById('printResult').addEventListener('click',()=>root.print());
  }
  return {calculate,metrics,affiliateUrl,mount,constants:{AFFILIATE_TAG,CHEMISTRY}};
});
