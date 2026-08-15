(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const CHARGE_LOSS=1.20;
  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const baseResult=(status,title,summary,extra={})=>({
    status,title,summary,commercialAllowed:false,searchTerm:null,
    productClass:null,batteryWh:null,chargeHours:null,platformLabel:null,...extra
  });
  const safeText=(value,fallback='')=>String(value||fallback).trim().replace(/\s+/g,' ').slice(0,60);
  const approxEqual=(a,b)=>a!==null&&b!==null&&Math.abs(a-b)<=Math.max(1,Math.min(a,b)*0.12);

  function metrics(input={}){
    const toolVoltage=num(input.toolVoltage);
    const candidateVoltage=num(input.candidateVoltage);
    const candidateAh=num(input.candidateAh);
    const chargerCurrent=num(input.chargerCurrent);
    const batteryWh=candidateVoltage&&candidateAh?candidateVoltage*candidateAh:null;
    const chargeHours=candidateAh&&chargerCurrent&&chargerCurrent>0?(candidateAh/chargerCurrent)*CHARGE_LOSS:null;
    return {toolVoltage,candidateVoltage,candidateAh,chargerCurrent,batteryWh,chargeHours};
  }

  function productClassFor(goal){
    if(goal==='charger')return 'battery_charger';
    if(goal==='kit')return 'battery_charger_kit';
    return 'tool_battery';
  }

  function searchTerm(input,m){
    const brand=safeText(input.brand,'akülü el aleti');
    const platform=safeText(input.platform,'batarya platformu');
    const voltage=m.candidateVoltage||m.toolVoltage;
    const ah=m.candidateAh;
    const goal=input.goal||'battery';
    if(goal==='charger')return `${brand} ${platform} ${voltage||''}V orijinal akü şarj cihazı`;
    if(goal==='kit')return `${brand} ${platform} ${voltage||''}V ${ah||''}Ah akü şarj seti`;
    return `${brand} ${platform} ${voltage||''}V ${ah||''}Ah orijinal akülü el aleti bataryası`;
  }

  function calculate(input={}){
    const m=metrics(input);
    const enriched=(result)=>({...result,...m,platformLabel:safeText(input.platform)||null});

    if(input.emergency){
      return enriched(baseResult('emergency','Bataryadan uzaklaşın ve şarjı durdurun','Duman, alev, tıslama, yoğun ısı, kimyasal koku veya kıvılcım varsa bataryaya, şarj cihazına ve fişe dokunmayın. Güvenli alana çıkın; yangın, yaralanma veya yoğun dumanda 112 önceliklidir. Ticari yollar kapalıdır.'));
    }
    if(['swollen','cracked','leaking','burned','wet'].includes(input.batteryCondition||'')){
      return enriched(baseResult('stop_use','Hasarlı bataryayı kullanmayın veya şarj etmeyin','Şişmiş, çatlamış, sızdıran, yanmış ya da su almış lityum batarya yeniden denenmez. Yanmaz ve iletken olmayan güvenli ayırma, üretici talimatı ve yetkili atık/servis süreci gerekir.'));
    }
    if(input.batteryCondition!=='sound'){
      return enriched(baseResult('evidence_required','Bataryanın fiziksel durumunu doğrulayın','Kasa, mandal, terminal, yalıtım, etiket ve sıcaklık normal olmadan uyumluluk değerlendirmesi yapılmaz.'));
    }
    if(['damaged','corroded','bridged'].includes(input.terminals||'')){
      return enriched(baseResult('stop_use','Terminalleri kullanmayın','Eğilmiş, gevşek, aşırı oksitlenmiş veya metal parça ile köprülenme riski bulunan terminaller kısa devre ve ısınma riski taşır. Servis veya güvenli bertaraf gerekir.'));
    }
    if(input.terminals!=='clean'){
      return enriched(baseResult('evidence_required','Terminal durumunu kontrol edin','Terminaller temiz, kuru, eğilmemiş ve yabancı metal cisimlerden uzak olmalıdır.'));
    }
    if(['flammable','unattended','hotcold','wet'].includes(input.chargeArea||'')){
      return enriched(baseResult('stop_use','Bu ortamda şarj etmeyin','Yanıcı malzeme yanında, gözetimsiz, aşırı sıcak/soğuk veya ıslak ortamda şarj etmeyin. Üreticinin sıcaklık sınırlarında, kuru ve havalandırılan bir alanda şarj edin.'));
    }
    if(input.chargeArea!=='safe'){
      return enriched(baseResult('evidence_required','Şarj ortamını doğrulayın','Kuru, havalandırılan, yanıcı malzemeden uzak ve gözetimli bir şarj alanı seçin.'));
    }
    if(!['battery','second_battery','charger','kit','diagnose'].includes(input.goal||'')){
      return enriched(baseResult('evidence_required','İhtiyacı seçin','Yedek batarya, ikinci batarya, şarj cihazı, batarya-şarj seti veya arıza teşhisi aynı ürün kararı değildir.'));
    }
    if(input.goal==='diagnose'){
      return enriched(baseResult('professional','Önce arızanın kaynağını ayırın','Şarj olmama veya hızlı boşalma; batarya, şarj cihazı, terminal, sıcaklık, alet elektroniği ya da kullanım yükünden kaynaklanabilir. Bilinen sağlam batarya ve şarj cihazıyla çapraz test veya yetkili servis gerekir; affiliate kapalıdır.'));
    }
    if(!safeText(input.brand)||!safeText(input.platform)){
      return enriched(baseResult('evidence_required','Tam marka ve batarya platformunu bulun','Aletin, bataryanın ve şarj cihazının tam model kodu ile platform ailesi bilinmeden yalnız voltaj veya fiziksel oturma uyumluluk kanıtı değildir.'));
    }
    if(!['liion','nicd','nimh'].includes(input.chemistry||'')){
      return enriched(baseResult('evidence_required','Batarya kimyasını doğrulayın','Li-ion, NiCd ve NiMH bataryalar farklı şarj profilleri kullanır. Etiket ve üretici kılavuzundaki kimya açıkça doğrulanmalıdır.'));
    }
    if(input.adapterUse==='third_party'){
      return enriched(baseResult('stop_use','Üçüncü taraf batarya adaptörüyle şarj etmeyin','Markalar arası veya platformlar arası adaptör; BMS haberleşmesi, sıcaklık algısı, akım sınırı ve mekanik kilidi atlayabilir. Özellikle adaptör üzerinden şarj yapılmaz; ticari yönlendirme kapalıdır.'));
    }
    if(input.adapterUse==='oem'&&input.oemAdapterEvidence!=='yes'){
      return enriched(baseResult('evidence_required','OEM adaptörün tam model sınırlarını doğrulayın','Üretici adaptörleri bile yalnız belirli batarya, alet ve şarj cihazlarıyla çalışabilir. Tam model uyumluluk tablosu gerekir.'));
    }
    if(input.platformEvidence==='different'||input.platformEvidence==='physical'){
      return enriched(baseResult('stop_use','Fiziksel oturma veya aynı marka yeterli değildir','Aynı markada farklı voltaj/platformlar ve aynı gövdeye benzeyen ürünler elektronik olarak uyumsuz olabilir. Yalnız üreticinin tam model uyumluluk tablosu kabul edilir.'));
    }
    if(input.platformEvidence!=='exact'){
      return enriched(baseResult('evidence_required','Tam platform uyumluluğunu kanıtlayın','Alet, batarya ve şarj cihazının tam model kodları üretici kılavuzu veya resmî uyumluluk tablosunda birlikte doğrulanmalıdır.'));
    }
    if(m.toolVoltage===null||m.toolVoltage<=0||m.toolVoltage>120){
      return enriched(baseResult(m.toolVoltage&&m.toolVoltage>120?'professional':'evidence_required',m.toolVoltage&&m.toolVoltage>120?'120 V üzeri sistem bu aracın dışındadır':'Aletin nominal voltajını girin',m.toolVoltage&&m.toolVoltage>120?'Yüksek voltajlı endüstriyel batarya sistemleri üretici ve yetkili servis değerlendirmesi gerektirir.':'Alet etiketindeki nominal sistem voltajını girin; “MAX” pazarlama değeri ile nominal değer farklı olabilir.'));
    }
    if(m.candidateVoltage===null||m.candidateVoltage<=0){
      return enriched(baseResult('evidence_required','Aday bataryanın nominal voltajını girin','Batarya etiketindeki nominal voltajı ve platform adını birlikte doğrulayın.'));
    }
    if(!approxEqual(m.toolVoltage,m.candidateVoltage)){
      return enriched(baseResult('stop_use','Alet ve batarya voltaj sınıfı uyuşmuyor','Nominal voltajlar yüzde 12 toleransın dışında. “18 V nominal / 20 V MAX” gibi üreticiye özgü adlandırmalar yalnız resmî platform eşleşmesiyle kabul edilir; rastgele adaptör kullanılmaz.'));
    }
    if(m.candidateAh===null||m.candidateAh<=0||m.candidateAh>30){
      return enriched(baseResult(m.candidateAh&&m.candidateAh>30?'professional':'evidence_required',m.candidateAh&&m.candidateAh>30?'30 Ah üzeri paket bu aracın dışındadır':'Batarya kapasitesini girin',m.candidateAh&&m.candidateAh>30?'Büyük enerji paketleri taşıma, kısa devre ve termal yönetim açısından profesyonel değerlendirme gerektirir.':'Etiketteki Ah değerini girin. Daha yüksek Ah genellikle daha uzun çalışma sağlar; fakat ağırlık, akım yeteneği ve alet onayı ayrıca kontrol edilir.'));
    }
    if(input.toolDuty==='high'&&input.highOutputEvidence!=='yes'){
      return enriched(baseResult('evidence_required','Yüksek güçlü alet için çıkış sınıfını doğrulayın','Taşlama, kırıcı, zincir testere, yüksek torklu darbeli alet veya bahçe makinesinde yalnız Ah yeterli değildir. Üreticinin yüksek çıkış/hücre akım sınıfı ve alet model uyumu gerekir.'));
    }
    if(input.recallChecked==='recalled'){
      return enriched(baseResult('stop_use','Geri çağrılmış ürünü kullanmayın','Üreticinin veya ürün güvenliği otoritesinin geri çağırma/kullanımı durdurma talimatını izleyin. Yeniden şarj etmeyin ve ticari yönlendirmeye geçmeyin.'));
    }
    if(input.recallChecked!=='yes'){
      return enriched(baseResult('evidence_required','Tam model geri çağırma kontrolünü tamamlayın','Batarya ve şarj cihazının tam model kodu için üretici ve resmî ürün güvenliği duyurularını kontrol edin.'));
    }
    if(input.manualVerified!=='yes'){
      return enriched(baseResult('evidence_required','Üretici kılavuzunu doğrulayın','Alet, batarya ve şarj cihazı tam model kodları aynı resmî uyumluluk zincirinde görünmelidir.'));
    }
    if(input.traceability!=='yes'){
      return enriched(baseResult('evidence_required','Ürün ve satıcı izlenebilirliğini doğrulayın','Tam marka-model, seri/tarih kodu, fatura, üretici desteği ve sahte ürün riskine karşı izlenebilir kaynak gerekir.'));
    }
    if(input.certification!=='yes'){
      return enriched(baseResult('evidence_required','Tam model güvenlik belgesini doğrulayın','Yalnız CE baskısı veya pazar yeri açıklaması yeterli değildir. Şarj cihazı ve batarya için tam model uygunluk, koruma ve üretici belgeleri aranmalıdır.'));
    }

    if(['charger','kit'].includes(input.goal)){
      if(input.chargerMatch==='no'){
        return enriched(baseResult('stop_use','Bu şarj cihazı batarya için uygun değil','Şarj cihazının platform, kimya, sıcaklık algısı ve batarya model uyumu üretici tarafından onaylanmamış. Yalnız fişin veya kızak yapısının uyması yeterli değildir.'));
      }
      if(input.chargerMatch!=='exact'){
        return enriched(baseResult('evidence_required','Şarj cihazı uyumluluğunu doğrulayın','Şarj cihazının tam model kodu, batarya modeli, kimya ve platform üretici tablosunda birlikte yer almalıdır.'));
      }
      if(m.chargerCurrent===null||m.chargerCurrent<=0||m.chargerCurrent>30){
        return enriched(baseResult(m.chargerCurrent&&m.chargerCurrent>30?'professional':'evidence_required',m.chargerCurrent&&m.chargerCurrent>30?'30 A üzeri şarj bu aracın dışındadır':'Şarj akımını girin',m.chargerCurrent&&m.chargerCurrent>30?'Yüksek akımlı endüstriyel şarj düzeni özel koruma ve üretici onayı gerektirir.':'Şarj cihazı etiketindeki çıkış akımını girin; yaklaşık süre yalnız planlama amaçlıdır.'));
      }
      if(input.fastChargeAllowed!=='yes'){
        return enriched(baseResult(input.fastChargeAllowed==='no'?'stop_use':'evidence_required','Hızlı şarj iznini doğrulayın','Daha yüksek şarj akımı yalnız batarya modelinin ve üreticinin açık hızlı şarj desteğiyle kullanılabilir.'));
      }
    }

    if(input.existingStatus==='good'){
      if(input.goal==='battery'){
        return enriched(baseResult('no_buy','Mevcut batarya çalışıyorsa yenisini almayın','Mevcut batarya fiziksel olarak sağlam, üretici platformuna uyumlu ve gerçek işte ihtiyacı karşılıyorsa yalnız kapasite etiketi daha yüksek diye değiştirmeyin.'));
      }
      if(input.goal==='charger'){
        return enriched(baseResult('no_buy','Mevcut şarj cihazı yeterliyse yenisini almayın','Mevcut şarj cihazı tam model uyumlu, fiziksel olarak sağlam ve gözetimli şarj testini geçiyorsa yeni cihaz gerekmez.'));
      }
    }
    if(input.goal==='second_battery'&&input.workGap!=='yes'){
      return enriched(baseResult('no_buy','İkinci batarya ihtiyacı kanıtlanmadı','Mevcut batarya iş akışını karşılıyorsa yedek paket almak yerine şarj döngüsü ve görev planını kullanın.'));
    }
    if(['weak','not_charging'].includes(input.existingStatus||'')&&input.crossTest!=='yes'){
      return enriched(baseResult('test_existing','Bilinen sağlam batarya ve şarj cihazıyla çapraz test yapın','Hızlı boşalma veya şarj olmama tek başına batarya arızası değildir. Temiz terminaller, uygun sıcaklık ve bilinen sağlam eş cihazla kontrollü test yapılmadan ürün satın almayın.'));
    }
    if(input.supervisedTest!=='yes'){
      return enriched(baseResult('test_existing','Gözetimli şarj ve çalışma testini tamamlayın','Üretici sınırlarında ilk şarjı gözetimli yapın; anormal ısı, koku, ses, hata kodu, mandal gevşekliği ve beklenmeyen hızlı boşalmayı kontrol edin.'));
    }

    const cls=productClassFor(input.goal);
    const term=searchTerm(input,m);
    const title=input.goal==='charger'?'Tam platform uyumlu şarj cihazı sınıfı doğrulandı':input.goal==='kit'?'Batarya ve şarj seti sınıfı doğrulandı':'Tam platform uyumlu batarya sınıfı doğrulandı';
    const summary=`${safeText(input.brand)} ${safeText(input.platform)} için ${m.candidateVoltage} V, ${m.candidateAh} Ah aday paket yaklaşık ${m.batteryWh.toFixed(0)} Wh nominal enerji taşır.${m.chargeHours?` ${m.chargerCurrent} A çıkışta kaba şarj süresi yaklaşık ${m.chargeHours.toFixed(1)} saattir.`:''} Bu hesap çalışma süresi garantisi değildir; yalnız tam model üretici uyumluluğu, geri çağırma kontrolü ve gözetimli testle birlikte kullanılmalıdır.`;
    return enriched(baseResult('conditional_purchase',title,summary,{commercialAllowed:true,searchTerm:term,productClass:cls}));
  }

  function affiliateUrl(result){
    if(!result||!result.commercialAllowed||!result.searchTerm)return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(result.searchTerm)}&tag=${AFFILIATE_TAG}`;
  }

  function mount(doc){
    const form=doc.getElementById('batteryForm');
    if(!form)return;
    const ids=['batteryCondition','terminals','chargeArea','goal','brand','platform','chemistry','adapterUse','oemAdapterEvidence','platformEvidence','toolVoltage','candidateVoltage','candidateAh','toolDuty','highOutputEvidence','existingStatus','workGap','crossTest','chargerMatch','chargerCurrent','fastChargeAllowed','manualVerified','traceability','certification','recallChecked','supervisedTest'];
    const elements=Object.fromEntries(ids.map(id=>[id,doc.getElementById(id)]));
    const emergency=doc.getElementById('emergency');
    const resultBox=doc.getElementById('result');
    const status=doc.getElementById('status');
    const title=doc.getElementById('resultTitle');
    const summary=doc.getElementById('summary');
    const platformMetric=doc.getElementById('platformMetric');
    const energyMetric=doc.getElementById('energyMetric');
    const chargeMetric=doc.getElementById('chargeMetric');
    const next=doc.getElementById('nextStep');
    const commerce=doc.getElementById('commerce');
    const affiliate=doc.getElementById('affiliate');
    const confirms=[...doc.querySelectorAll('.confirm')];
    const jsonButton=doc.getElementById('downloadJson');
    const icsButton=doc.getElementById('downloadIcs');
    const printButton=doc.getElementById('printResult');
    let latest=null;
    const values=()=>({emergency:emergency.checked,...Object.fromEntries(ids.map(id=>[id,elements[id]?elements[id].value:null]))});
    const download=(name,type,text)=>{
      const blob=new Blob([text],{type});
      const url=URL.createObjectURL(blob);
      const a=doc.createElement('a');a.href=url;a.download=name;doc.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
    };
    const updateGate=()=>{
      const url=affiliateUrl(latest);
      const open=Boolean(url)&&confirms.every(c=>c.checked);
      affiliate.setAttribute('aria-disabled',String(!open));
      affiliate.tabIndex=open?0:-1;
      if(open)affiliate.href=url;else affiliate.removeAttribute('href');
    };
    const nextLabel=(result)=>({
      emergency:'112 / güvenli alan',stop_use:'Kullanımı ve şarjı durdurun',professional:'Yetkili servis / üretici',
      evidence_required:'Eksik teknik kanıtı tamamlayın',test_existing:'Mevcut seti kontrollü test edin',
      no_buy:'Mevcut ürünü kullanın',conditional_purchase:'Tam platform uyumlu ürün sınıfı'
    })[result.status]||'Teknik doğrulama';
    form.addEventListener('submit',(event)=>{
      event.preventDefault();
      latest=calculate(values());
      resultBox.hidden=false;resultBox.dataset.status=latest.status;
      status.textContent=latest.status.replaceAll('_',' ').toLocaleUpperCase('tr-TR');
      title.textContent=latest.title;summary.textContent=latest.summary;
      platformMetric.textContent=latest.platformLabel||'—';
      energyMetric.textContent=latest.batteryWh?`${latest.batteryWh.toLocaleString('tr-TR',{maximumFractionDigits:0})} Wh`:'—';
      chargeMetric.textContent=latest.chargeHours?`${latest.chargeHours.toLocaleString('tr-TR',{maximumFractionDigits:1})} saat`:'—';
      next.textContent=nextLabel(latest);
      commerce.hidden=!latest.commercialAllowed;
      confirms.forEach(c=>{c.checked=false;});
      updateGate();
      resultBox.focus();
    });
    confirms.forEach(c=>c.addEventListener('change',updateGate));
    form.addEventListener('reset',()=>setTimeout(()=>{
      latest=null;resultBox.hidden=true;commerce.hidden=true;confirms.forEach(c=>{c.checked=false;});updateGate();
    },0));
    jsonButton.addEventListener('click',()=>{
      if(!latest)return;
      const payload={tool:'ALO186 Akülü El Aleti Batarya ve Şarj Cihazı Uygunluk Testi',createdAt:new Date().toISOString(),personalData:false,result:latest,inputs:values(),disclaimer:'Ön seçimdir; tam model üretici uyumluluğu ve güvenlik talimatları önceliklidir.'};
      download('alo186-akulu-alet-batarya-teknik-fis.json','application/json;charset=utf-8',JSON.stringify(payload,null,2));
    });
    icsButton.addEventListener('click',()=>{
      if(!latest)return;
      const date=new Date();date.setUTCDate(date.getUTCDate()+120);const end=new Date(date);end.setUTCDate(end.getUTCDate()+1);
      const stamp=(x)=>`${x.getUTCFullYear()}${String(x.getUTCMonth()+1).padStart(2,'0')}${String(x.getUTCDate()).padStart(2,'0')}`;
      const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Akulu Alet Batarya Kontrolu//TR','BEGIN:VEVENT',`DTSTART;VALUE=DATE:${stamp(date)}`,`DTEND;VALUE=DATE:${stamp(end)}`,'SUMMARY:Akulu alet batarya ve sarj cihazi kontrolu','DESCRIPTION:Kasa, terminaller, mandal, sicaklik, geri cagirma, tam model uyumluluk, sarj suresi ve gercek is testini yeniden kontrol edin.','END:VEVENT','END:VCALENDAR'].join('\r\n');
      download('alo186-akulu-alet-120-gun-kontrol.ics','text/calendar;charset=utf-8',ics);
    });
    printButton.addEventListener('click',()=>root.print());
  }

  return {calculate,metrics,affiliateUrl,mount,constants:{AFFILIATE_TAG,CHARGE_LOSS}};
});