(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const LEAD_ACID_CHARGE_FACTOR=1.20;
  const PLANNING_C_RATE=0.10;
  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step)=>Math.ceil(value/step)*step;
  const baseResult=(status,title,summary,extra={})=>({status,title,summary,commercialAllowed:false,searchUrl:null,planningCurrentA:null,approxHours:null,...extra});
  const leadAcid=new Set(['flooded','calcium','agm','efb','gel']);

  function calculate(input={}){
    if(input.emergency){
      return baseResult('emergency','Aküyü şarj etmeyin veya takviye yapmayın','Duman, tıslama, kıvılcım, yoğun ısı, şişme, çatlak kasa, elektrolit kaçağı, asit teması ya da yangın belirtisinde aküye ve kutuplara yaklaşmayın. Güvenli alana çıkın; yangın, yaralanma veya yoğun duman varsa 112’yi arayın. Bütün ticari yollar kapalıdır.');
    }
    if(input.batteryCondition==='frozen')return baseResult('stop_use','Donmuş olabilecek aküyü şarj etmeyin','Donmuş akünün şarj veya takviye sırasında yırtılma ve patlama riski vardır. Aracı çalıştırmaya veya şarj etmeye çalışmayın; profesyonel yol yardım/servis değerlendirmesi alın.');
    if(input.batteryCondition==='damaged')return baseResult('stop_use','Hasarlı aküyü kullanmayın','Şişmiş, çatlamış, sızdıran, darbe veya su hasarı bulunan akü şarj edilmez ve takviye edilmez. Yetkili servis ve uygun atık süreci gerekir.');
    if(input.batteryCondition!=='sound')return baseResult('evidence_required','Akünün fiziksel durumunu doğrulayın','Kasanın sağlam, kuru, sızıntısız ve donmamış olduğunu doğrulamadan ürün seçmeyin.');
    if(input.ventilation==='no')return baseResult('stop_use','Kapalı ve havasız alanda şarj etmeyin','Kurşun-asit aküler şarj sırasında gaz çıkarabilir. Alev, kıvılcım ve sigaradan uzak, üretici talimatına uygun havalandırılmış ortam gerekir.');
    if(input.ventilation!=='yes')return baseResult('evidence_required','Şarj ortamını doğrulayın','Havalandırma, kuru zemin, alev/kıvılcım uzaklığı ve gözetim koşulları doğrulanmalıdır.');
    if(['heavy_24v','hybrid_ev'].includes(input.vehicleClass||''))return baseResult('professional','Bu araç sınıfı profesyonel/OEM prosedürü gerektirir','24 V ağır araçlar ile hibrit/elektrikli araçların 12 V yardımcı aküsü; bağlantı noktaları, elektronik modüller ve yüksek gerilim ayrımı nedeniyle araç üreticisinin prosedürü ve yetkili servis/yol yardım desteğiyle ele alınmalıdır. Affiliate yönlendirmesi kapalıdır.');
    if(!['motorcycle','passenger','light_commercial'].includes(input.vehicleClass||''))return baseResult('evidence_required','Araç sınıfını doğrulayın','Motosiklet, binek araç veya hafif ticari araç sınıfını belirtin.');
    if(input.activeBreakdown==='yes')return baseResult('active_breakdown','Aktif arızada ürün teslimatını çözüm saymayın','Araç şu anda çalışmıyorsa yanlış kutup, kıvılcım veya elektronik hasar riskine karşı araç kılavuzundaki prosedürü ve yol yardımını kullanın. Yeni ürün siparişi mevcut yol kenarı durumunu çözmez; ticari yönlendirme kapalıdır.');
    if(input.activeBreakdown!=='no')return baseResult('evidence_required','Aktif arıza durumunu belirtin','Hazırlık amacı ile yolda kalmış araç durumu ayrılmalıdır.');
    if(input.manualChecked!=='yes')return baseResult('evidence_required','Araç ve akü kılavuzunu doğrulayın','Üreticinin izin verdiği bağlantı noktaları, voltaj, akü kimyası, şarj/takviye yöntemi ve varsa akü yönetim sensörü doğrulanmadan ürün seçmeyin.');

    const voltage=num(input.voltage);
    const capacityAh=num(input.capacityAh);
    const soc=num(input.socPercent);
    const manufacturerMaxA=num(input.manufacturerMaxA);
    const chargerVoltage=num(input.chargerVoltage);
    const chargerCurrentA=num(input.chargerCurrentA);
    if(![6,12,24].includes(voltage||0))return baseResult('evidence_required','Akü voltajını etiketinden doğrulayın','6 V, 12 V veya 24 V nominal değerini akü ve araç kılavuzundan okuyun; tahmin etmeyin.');
    if(!leadAcid.has(input.chemistry||'')&&input.chemistry!=='lifepo4')return baseResult('evidence_required','Akü kimyasını doğrulayın','WET/MF, Ca/Ca, AGM, EFB, GEL veya LiFePO₄ bilgisi etiket ve araç kılavuzundan doğrulanmalıdır.');
    if(capacityAh===null||capacityAh<2||capacityAh>500)return baseResult('evidence_required','Akü kapasitesini Ah olarak doğrulayın','Etiketteki Ah değerini girin. CCA veya RC değeri Ah yerine kullanılmaz.');
    if(input.chemistry==='lifepo4'){
      return baseResult('professional','LiFePO₄ marş aküsünde tam model onayı gerekir','LiFePO₄ marş aküsü yalnız kendi BMS, düşük sıcaklık sınırı, üretici şarj profili ve araç uyumluluğu doğrulanarak şarj edilir. Kurşun-asit recondition/desulfation modu kullanılmaz; genel affiliate ürünü gösterilmez.');
    }
    if(input.purpose==='diagnose')return baseResult('evidence_required','Şarj cihazı akü sağlık testinin yerini tutmaz','Tekrarlayan boşalma; akü kapasitesi, alternatör/şarj sistemi, kaçak tüketim ve bağlantı direnci ölçümü gerektirir. Yeni şarj cihazı almadan önce kök nedeni ölçtürün.');
    if(!['maintain','recharge','prepare_jump'].includes(input.purpose||''))return baseResult('evidence_required','Kullanım amacını belirtin','Bakım, yeniden şarj veya acil çalıştırmaya hazırlık hedeflerinden birini seçin.');

    const planningCurrentA=roundUp(Math.min(capacityAh*PLANNING_C_RATE,manufacturerMaxA&&manufacturerMaxA>0?manufacturerMaxA:Infinity),0.5);
    const estimateHours=(amps)=>{
      if(input.purpose!=='recharge'||soc===null||soc<0||soc>=100||!amps||amps<=0)return null;
      return Math.round(((capacityAh*((100-soc)/100)*LEAD_ACID_CHARGE_FACTOR)/amps)*10)/10;
    };

    if(input.existingType==='none'){
      if(input.purpose==='prepare_jump'){
        return baseResult('conditional_purchase','12 V akıllı takviye cihazı sınıfını doğrulayın','Araç kılavuzu 12 V takviyeye izin veriyorsa; motor hacmi/yakıt türü üretici tablosuna uyan, ters kutup ve kıvılcım korumalı, izlenebilir güvenlik belgeli cihaz sınıfı değerlendirilebilir. Amazon sonucu teknik onay değildir.',{commercialAllowed:voltage===12,productClass:'jump_starter',planningCurrentA,searchTerm:'12V akıllı araç akü takviye cihazı ters kutup kıvılcım korumalı'});
      }
      const label=input.purpose==='maintain'?'akü bakım cihazı':'akıllı akü şarj cihazı';
      const chemistryLabel={flooded:'WET',calcium:'Ca/Ca',agm:'AGM',efb:'EFB',gel:'GEL'}[input.chemistry];
      return baseResult('conditional_purchase',`${voltage} V ${label} sınıfını doğrulayın`,`Planlama için yaklaşık ${planningCurrentA} A sınıfı görünür; akü üreticisinin azami akımı ve tam şarj profili her zaman önceliklidir. Otomatik regülasyon, doğru kimya modu, ters kutup/kıvılcım koruması ve izlenebilir belge aranmalıdır.`,{commercialAllowed:true,productClass:input.purpose==='maintain'?'maintainer':'smart_charger',planningCurrentA,approxHours:estimateHours(planningCurrentA),searchTerm:`${voltage}V ${chemistryLabel} akıllı akü şarj bakım cihazı ${planningCurrentA}A`});
    }

    if(input.existingType==='manual_charger')return baseResult('replace_candidate','Manuel regülasyonsuz cihazı gözetimsiz kullanmayın','Araç üreticisi açıkça izin vermedikçe manuel/regülasyonsuz şarj cihazı modern araç elektroniği ve AGM/EFB aküler için uygun kabul edilmez. Önce servis doğrulaması yapın; sonra otomatik akıllı şarj cihazı sınıfını değerlendirin.',{commercialAllowed:true,productClass:'smart_charger',planningCurrentA,approxHours:estimateHours(planningCurrentA),searchTerm:`${voltage}V ${input.chemistry.toUpperCase()} otomatik akıllı akü şarj cihazı ${planningCurrentA}A`});

    const expectedType=input.purpose==='prepare_jump'?'jump_starter':['smart_charger','maintainer'].includes(input.existingType)?input.existingType:null;
    if(!expectedType)return baseResult('evidence_required','Mevcut cihaz türü kullanım amacıyla eşleşmiyor','Bakım/şarj için otomatik şarj cihazı veya maintainer; acil çalıştırmaya hazırlık için araç kılavuzuna uygun takviye cihazı değerlendirilir.');
    if(chargerVoltage===null)return baseResult('evidence_required','Mevcut cihaz çıkış voltajını doğrulayın','Cihazın OUTPUT/nominal voltajını teknik etiketinden okuyun. Şebeke INPUT 230 V değeri kullanılmaz.');
    if(chargerVoltage!==voltage)return baseResult('stop_use','Voltaj uyuşmuyor; cihazı bağlamayın',`Akü ${voltage} V, mevcut cihaz ${chargerVoltage} V olarak girildi. Voltaj eşleşmeden şarj veya takviye yapılmaz.`);
    if(input.chemistryMode!=='yes')return baseResult(input.chemistryMode==='no'?'stop_use':'evidence_required','Akü kimyası modu doğrulanmadı','Mevcut cihazın tam olarak bu WET/Ca-Ca/AGM/EFB/GEL akü tipini desteklediği üretici kılavuzunda görülmelidir. Recondition modu AGM/EFB/GEL için otomatik olarak uygun sayılmaz.');
    if(input.purpose!=='prepare_jump'){
      if(chargerCurrentA===null||chargerCurrentA<=0)return baseResult('evidence_required','Mevcut cihazın şarj akımını doğrulayın','OUTPUT akımı amper olarak teknik etiketten okunmalıdır.');
      if(manufacturerMaxA!==null&&manufacturerMaxA>0&&chargerCurrentA>manufacturerMaxA)return baseResult('stop_use','Şarj akımı üretici sınırını aşıyor','Mevcut cihazın akımı akü üreticisinin izin verdiği azami değerden yüksek. Cihazı kullanmayın.');
      if((manufacturerMaxA===null||manufacturerMaxA<=0)&&chargerCurrentA>capacityAh*0.15)return baseResult('evidence_required','Yüksek şarj akımı için üretici kanıtı gerekir','Cihaz akımı 0,15C planlama eşiğinin üzerinde. Bu tek başına uygunsuzluk kanıtı değildir; ancak akü üreticisinin açık azami akım verisi olmadan kullanmayın.');
    }
    if(input.protections!=='yes')return baseResult('evidence_required','Ters kutup ve kıvılcım korumasını doğrulayın','Koruma işlevleri ürün teknik belgesinde ve kullanım kılavuzunda doğrulanmalıdır.');
    if(input.certification!=='yes')return baseResult('evidence_required','Ürün güvenlik belgesini doğrulayın','Şarj/takviye cihazının üretici, model, kılavuz ve izlenebilir uygunluk/güvenlik belgesi bulunmalıdır. Yalnız pazar yeri açıklamasına güvenmeyin.');
    if(input.temperatureCompensation!=='yes'&&input.purpose!=='prepare_jump')return baseResult('evidence_required','Sıcaklık davranışını doğrulayın','Akü kimyasına uygun sıcaklık kompanzasyonu veya üreticinin tanımladığı çalışma sıcaklığı doğrulanmalıdır.');
    if(input.supervisedTest!=='yes')return baseResult('test_existing','Önce mevcut cihazı gözetimli test edin','Teknik değerler uyumlu görünüyor. Klemens/kablo ısısı, hata göstergesi, şarjın tamamlanması ve araçtaki elektronik uyarılar gözetimli testte normal ise yeni ürün almayın; test tamamlanmadan mağaza bağlantısı açılmaz.',{planningCurrentA,approxHours:estimateHours(chargerCurrentA)});

    return baseResult('no_buy','Mevcut cihaz yeterliyse yeni ürün almayın','Voltaj, akü kimyası, akım sınırı, korumalar, güvenlik belgesi, sıcaklık davranışı ve gözetimli gerçek test doğrulandı. Mevcut cihazı üretici talimatına göre kullanın; gereksiz satın alma yapmayın.',{planningCurrentA,approxHours:estimateHours(chargerCurrentA)});
  }

  function affiliateUrl(result){
    if(!result||!result.commercialAllowed||!result.searchTerm)return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(result.searchTerm)}&tag=${AFFILIATE_TAG}`;
  }

  function mount(doc){
    const form=doc.getElementById('batteryForm');
    if(!form)return;
    const ids=['batteryCondition','ventilation','vehicleClass','purpose','activeBreakdown','manualChecked','voltage','chemistry','capacityAh','socPercent','manufacturerMaxA','existingType','chargerVoltage','chemistryMode','chargerCurrentA','protections','certification','temperatureCompensation','supervisedTest'];
    const el=Object.fromEntries(ids.map(id=>[id,doc.getElementById(id)]));
    const emergency=doc.getElementById('emergency');
    const resultBox=doc.getElementById('result');
    const status=doc.getElementById('status');
    const title=doc.getElementById('resultTitle');
    const summary=doc.getElementById('summary');
    const current=doc.getElementById('planningCurrent');
    const hours=doc.getElementById('chargeHours');
    const next=doc.getElementById('nextStep');
    const commerce=doc.getElementById('commerce');
    const affiliate=doc.getElementById('affiliate');
    const confirms=[...doc.querySelectorAll('.confirm')];
    const jsonButton=doc.getElementById('downloadJson');
    const icsButton=doc.getElementById('downloadIcs');
    const printButton=doc.getElementById('printResult');
    let latest=null;

    const values=()=>({
      emergency:emergency.checked,
      ...Object.fromEntries(ids.map(id=>[id,el[id]?el[id].value:null]))
    });
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
    const nextLabel=(r)=>({emergency:'112 / güvenli alan',stop_use:'Kullanımı durdurun',professional:'Yetkili servis / yol yardım',active_breakdown:'Yol yardım ve araç kılavuzu',evidence_required:'Eksik teknik kanıtı tamamlayın',test_existing:'Mevcut cihazı gözetimli test edin',no_buy:'Mevcut cihazı kullanın',conditional_purchase:'Doğrulanmış ürün sınıfı',replace_candidate:'Akıllı şarj cihazı sınıfı'})[r.status]||'Teknik doğrulama';

    form.addEventListener('submit',(event)=>{
      event.preventDefault();
      latest=calculate(values());
      resultBox.hidden=false;
      resultBox.dataset.status=latest.status;
      status.textContent=latest.status.replaceAll('_',' ').toLocaleUpperCase('tr-TR');
      title.textContent=latest.title;
      summary.textContent=latest.summary;
      current.textContent=latest.planningCurrentA?`${latest.planningCurrentA.toLocaleString('tr-TR')} A`:'—';
      hours.textContent=latest.approxHours?`≈ ${latest.approxHours.toLocaleString('tr-TR')} saat`:'—';
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
      const payload={tool:'ALO186 Araç Aküsü Şarj ve Takviye Uygunluk Testi',createdAt:new Date().toISOString(),personalData:false,result:latest,inputs:values(),disclaimer:'Ön seçimdir; araç ve akü üreticisi talimatı önceliklidir.'};
      download('alo186-arac-aku-teknik-fis.json','application/json;charset=utf-8',JSON.stringify(payload,null,2));
    });
    icsButton.addEventListener('click',()=>{
      if(!latest)return;
      const date=new Date();date.setUTCDate(date.getUTCDate()+180);
      const end=new Date(date);end.setUTCDate(end.getUTCDate()+1);
      const stamp=(x)=>`${x.getUTCFullYear()}${String(x.getUTCMonth()+1).padStart(2,'0')}${String(x.getUTCDate()).padStart(2,'0')}`;
      const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Arac Aku Kontrolu//TR','BEGIN:VEVENT',`DTSTART;VALUE=DATE:${stamp(date)}`,`DTEND;VALUE=DATE:${stamp(end)}`,'SUMMARY:Araç aküsü ve şarj cihazı yeniden kontrolü','DESCRIPTION:Akü fiziksel durumu, voltaj, kimya, şarj cihazı modu, kablolar, korumalar ve gözetimli testi yeniden doğrulayın.','END:VEVENT','END:VCALENDAR'].join('\r\n');
      download('alo186-arac-aku-kontrolu.ics','text/calendar;charset=utf-8',ics);
    });
    printButton.addEventListener('click',()=>root.print());
  }

  return {calculate,affiliateUrl,mount,constants:{AFFILIATE_TAG,LEAD_ACID_CHARGE_FACTOR,PLANNING_C_RATE}};
});
