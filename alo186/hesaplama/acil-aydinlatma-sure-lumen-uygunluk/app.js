(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186EmergencyLighting=api;
  if(root&&root.document)api.init(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const PRESET_LUX={orientation:10,path:20,reading:100,outdoor:30};
  const CATEGORY_LINKS={
    emergency_light:{label:'Şarjlı acil aydınlatma sınıfını aç',href:'../../akilli-urun-secimi?kategori=emergency_light'},
    powerbank:{label:'Powerbank ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=powerbank'},
    power_station:{label:'Taşınabilir güç istasyonu sınıfını aç',href:'../../akilli-urun-secimi?kategori=power_station'}
  };
  const TOOL_LINKS={
    powerbank:{label:'Powerbank ve USB-C uygunluk testini aç',href:'../powerbank-usb-c-uygunluk/'},
    center:{label:'Hesaplama Merkezine dön',href:'../'},
    outcome:{label:'Çözüm sonucunu kaydet',href:'../cozum-sonucu/'}
  };
  const EFFICIENCY=0.85;
  const USABLE_FRACTION=0.80;
  const LIGHT_RESERVE=1.30;

  const uniq=values=>[...new Set(values.filter(Boolean))];
  const num=value=>{
    const raw=String(value??'').trim();
    if(!raw)return null;
    const parsed=Number(raw.replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const round=(value,digits=1)=>Number(value.toFixed(digits));

  function baseResult(status,title,summary){
    return {status,title,summary,issues:[],steps:[],metrics:null,commerceCategories:[],toolKeys:[],commerceClosed:true};
  }

  function batteryWh(input){
    if(input.sourceType==='wh')return num(input.batteryWh);
    if(input.sourceType==='mah'){
      const mah=num(input.batteryMah);
      const voltage=num(input.batteryVoltage);
      if(mah===null||voltage===null)return null;
      return mah*voltage/1000;
    }
    return null;
  }

  function evaluate(input={}){
    if(input.emergency){
      const result=baseResult('emergency','Acil: ürünü kullanmayın ve enerjiyi güvenli biçimde kesin','Duman, kıvılcım, erime, şişmiş batarya, sıvı sızıntısı, su teması veya elektrik çarpması riski varken hesap ve ticari yönlendirme yapılmaz.');
      result.issues=['Hasarlı ışık, adaptör, kablo, powerbank veya batarya yangın ve elektrik çarpması riski oluşturabilir.'];
      result.steps=['Güvenliyse enerjiyi kesin; ürünü şarj etmeyin ve yanıcı yüzeyden uzak tutun.','Yangın, yoğun duman, yaralanma veya elektrik çarpması riski varsa 112’yi arayın.'];
      return result;
    }

    if(input.medical){
      const result=baseResult('professional','Tıbbi veya yaşam destek yükü için profesyonel süreklilik tasarımı gerekir','Taşınabilir lamba, powerbank veya tüketici tipi güç istasyonu yaşam destek sürekliliği olarak kabul edilemez.');
      result.issues=['Kesintisiz güç, alarm, yedeklilik, batarya testi ve bakım planı birlikte tasarlanmalıdır.'];
      result.steps=['Tıbbi cihaz üreticisi ve yetkili elektrik uzmanıyla doğrulanmış yedek güç planı hazırlayın.'];
      return result;
    }

    if(input.regulated==='yes'){
      const result=baseResult('professional','Mevzuata tabi kaçış ve acil aydınlatma için proje doğrulaması gerekir','Bu araç bina kaçış yolu, merdiven, yangın güvenliği veya zorunlu acil aydınlatma projesinin uygunluğunu onaylamaz.');
      result.issues=['Sabit acil aydınlatma armatürleri, süre, lux dağılımı, test, bakım ve besleme mimarisi proje kapsamında doğrulanmalıdır.'];
      result.steps=['Yetkili proje ve yangın güvenliği uzmanıyla yürürlükteki şartları doğrulayın.','Bu aracı yalnız taşınabilir hazırlık ekipmanının yaklaşık süre hesabı için kullanın.'];
      return result;
    }

    const use=String(input.use||'');
    const area=num(input.areaM2);
    const customLux=num(input.targetLux);
    const targetLux=customLux??PRESET_LUX[use]??null;
    const count=num(input.lightCount);
    const lumensEach=num(input.lumensEach);
    const wattsEach=num(input.wattsEach);
    const targetHours=num(input.targetHours);
    const nominalWh=batteryWh(input);
    const evidence=[];
    const prerequisites=[];

    if(!PRESET_LUX[use])evidence.push('Kullanım senaryosu seçilmedi.');
    if(area===null||area<=0||area>500)evidence.push('Alan 0–500 m² aralığında doğrulanmadı.');
    if(targetLux===null||targetLux<=0||targetLux>1000)evidence.push('Planlama lux değeri 0–1000 lx aralığında doğrulanmadı.');
    if(count===null||count<1||count>100)evidence.push('Işık adedi 1–100 aralığında doğrulanmadı.');
    if(lumensEach===null||lumensEach<=0||lumensEach>100000)evidence.push('Bir ışığın lümen değeri doğrulanmadı.');
    if(wattsEach===null||wattsEach<=0||wattsEach>2000)evidence.push('Bir ışığın watt değeri doğrulanmadı.');
    if(targetHours===null||targetHours<=0||targetHours>72)evidence.push('Hedef çalışma süresi 0–72 saat aralığında doğrulanmadı.');
    if(nominalWh===null||nominalWh<=0||nominalWh>100000)evidence.push('Bataryanın nominal Wh değeri doğrulanmadı; mAh tek başına yeterli değildir.');

    if(input.environment==='wet'&&input.ipStatus!=='rated'){
      const result=baseResult('stop','Islak ortamda uygun koruma doğrulanmadan kullanmayın','Su teması veya ıslak ortam için ürünün üretici tarafından uygun koruma sınıfıyla belirtilmesi gerekir.');
      result.issues=['Ürünün ıslak ortam koruma sınıfı doğrulanmadı.'];
      result.steps=['Ürünü kuru alana taşıyın veya üretici belgesindeki ortam/IP sınırını doğrulayın.','Islak kablo, adaptör veya enerji kaynağını kullanmayın.'];
      return result;
    }
    if(['damp','outdoor'].includes(input.environment)&&input.ipStatus==='unknown')prerequisites.push('Nemli veya dış ortam için üretici koruma sınıfı bilinmiyor.');
    if(input.regulated==='unknown')prerequisites.push('Alanının mevzuata tabi kaçış/acil aydınlatma alanı olup olmadığı bilinmiyor.');

    if(evidence.length){
      const result=baseResult('evidence_required','Önce etiket ve kapasite bilgilerini tamamlayın','Lümen, watt, gerçek Wh, alan veya hedef süre bilinmeden güvenilir ürün sınıfı seçilemez; ticari rota kapalıdır.');
      result.issues=uniq([...evidence,...prerequisites]);
      result.steps=['Işık etiketindeki lümen ve watt değerini doğrulayın.','Batarya için Wh değerini kullanın; yalnız mAh verildiyse mAh × volt / 1000 ile nominal Wh hesaplayın.','Hedef kullanım süresini ve aydınlatılacak alanı belirleyin.'];
      result.toolKeys=['center'];
      return result;
    }

    if(prerequisites.length){
      const result=baseResult('prerequisite','Önce ortam ve kullanım sınıfını doğrulayın','Sayısal kapasite yeterli olsa bile ortam koruması veya mevzuata tabi alan bilgisi belirsizken ürün yönlendirmesi açılmaz.');
      result.issues=prerequisites;
      result.steps=['Üretici kılavuzundaki iç/dış ortam ve IP koşulunu doğrulayın.','Kaçış yolu veya ortak alan ise profesyonel proje gerekip gerekmediğini belirleyin.'];
      return result;
    }

    const requiredLumens=area*targetLux*LIGHT_RESERVE;
    const providedLumens=count*lumensEach;
    const totalWatts=count*wattsEach;
    const usableWh=nominalWh*USABLE_FRACTION;
    const estimatedRuntime=usableWh*EFFICIENCY/totalWatts;
    const requiredNominalWh=totalWatts*targetHours/EFFICIENCY/USABLE_FRACTION;
    const lumenRatio=providedLumens/requiredLumens;
    const runtimeRatio=estimatedRuntime/targetHours;
    const lightingOk=lumenRatio>=1;
    const runtimeOk=runtimeRatio>=1;
    const metrics={
      targetLux:round(targetLux),requiredLumens:round(requiredLumens),providedLumens:round(providedLumens),
      totalWatts:round(totalWatts),nominalWh:round(nominalWh),usableWh:round(usableWh),
      estimatedRuntime:round(estimatedRuntime,2),targetHours:round(targetHours,2),requiredNominalWh:round(requiredNominalWh),
      lumenCoveragePct:round(lumenRatio*100),runtimeCoveragePct:round(runtimeRatio*100)
    };

    if(area>100||totalWatts>500||providedLumens>20000){
      const result=baseResult('professional','Büyük alan veya yüksek güçlü sistem için yerleşim projesi gerekir','Toplam lümen veya güç taşınabilir tüketici hazırlığı sınırını aşıyor; ışık dağılımı, devre, batarya ve bakım birlikte projelendirilmelidir.');
      result.metrics=metrics;
      result.issues=['Tek toplam lümen değeri büyük alanda homojenlik, gölge, kaçış yönü ve armatür yerleşimini kanıtlamaz.'];
      result.steps=['Aydınlatma yerleşimini ve yedek enerji mimarisini yetkili uzmanla doğrulayın.'];
      return result;
    }

    if(lightingOk&&runtimeOk){
      const result=baseResult('no_buy','Mevcut çözüm hedefi karşılıyorsa yeni ürün almayın','Girilen etiket değerleri ve muhafazakâr kayıplarla mevcut ışık ve enerji kaynağı yaklaşık hedef lümen ile süreyi karşılıyor.');
      result.metrics=metrics;
      result.steps=['Gerçek kesinti öncesinde tam şarjla kontrollü süre testi yapın.','Batarya kapasitesi yaşlandıkça sonucu yeniden hesaplayın.','Işıkları gölge ve kamaşmayı azaltacak biçimde birden fazla noktaya dağıtın.'];
      result.toolKeys=['outcome'];
      return result;
    }

    const categories=[];
    const issues=[];
    if(!lightingOk){
      categories.push('emergency_light');
      issues.push(`Toplam ışık ${round(providedLumens)} lm; planlama ihtiyacı rezervle yaklaşık ${round(requiredLumens)} lm.`);
    }
    if(!runtimeOk){
      const energyCategory=totalWatts<=20?'powerbank':'power_station';
      categories.push(energyCategory);
      issues.push(`Tahmini çalışma süresi ${round(estimatedRuntime,2)} saat; hedef ${round(targetHours,2)} saat.`);
    }

    const result=baseResult('conditional_purchase','Gerçek eksik doğrulandı; yalnız eksik ürün sınıfını tamamlayın','Aydınlık veya çalışma süresi hedeflerinden en az biri karşılanmıyor. Bu sonuç belirli marka/model onayı değildir; yalnız teknik ürün sınıfına kontrollü geçiş sağlar.');
    result.metrics=metrics;
    result.issues=issues;
    result.steps=['Lümen açığında daha fazla cihaz yerine ışık dağılımını ve gerçek lümen değerini birlikte kontrol edin.','Enerji açığında gerekli nominal Wh değerini ve çıkış gücünü birlikte doğrulayın.','Amazon sonucunda tam model, Wh, sürekli W, USB/AC çıkış, şarj süresi, ortam sınırı ve üretici güvenlik talimatını yeniden kontrol edin.'];
    result.commerceCategories=uniq(categories);
    result.toolKeys=result.commerceCategories.includes('powerbank')?['powerbank']:['center'];
    result.commerceClosed=false;
    return result;
  }

  function init(doc){
    const form=doc.getElementById('lightingForm');
    if(!form)return;
    const get=id=>doc.getElementById(id);
    const resultEl=get('result');
    const gate=get('commerceGate');
    const productLinks=get('productLinks');
    let lastResult=null;

    function read(){
      return {
        emergency:get('emergency').checked,medical:get('medical').checked,regulated:get('regulated').value,
        use:get('use').value,areaM2:get('areaM2').value,targetLux:get('targetLux').value,
        lightCount:get('lightCount').value,lumensEach:get('lumensEach').value,wattsEach:get('wattsEach').value,
        sourceType:get('sourceType').value,batteryWh:get('batteryWh').value,batteryMah:get('batteryMah').value,
        batteryVoltage:get('batteryVoltage').value,targetHours:get('targetHours').value,
        environment:get('environment').value,ipStatus:get('ipStatus').value,currentEquipment:get('currentEquipment').value
      };
    }

    function metricHtml(metrics){
      if(!metrics)return '';
      const items=[
        ['Planlama ihtiyacı',`${metrics.requiredLumens.toLocaleString('tr-TR')} lm`],
        ['Mevcut ışık',`${metrics.providedLumens.toLocaleString('tr-TR')} lm`],
        ['Toplam güç',`${metrics.totalWatts.toLocaleString('tr-TR')} W`],
        ['Tahmini süre',`${metrics.estimatedRuntime.toLocaleString('tr-TR')} saat`],
        ['Gerekli nominal enerji',`${metrics.requiredNominalWh.toLocaleString('tr-TR')} Wh`],
        ['Süre karşılama',`%${metrics.runtimeCoveragePct.toLocaleString('tr-TR')}`]
      ];
      return `<div class="metrics">${items.map(([label,value])=>`<article><span>${label}</span><strong>${value}</strong></article>`).join('')}</div>`;
    }

    function render(value){
      lastResult=value;
      get('resultBadge').textContent=value.status.replaceAll('_',' ');
      get('resultTitle').textContent=value.title;
      get('resultSummary').textContent=value.summary;
      get('metricArea').innerHTML=metricHtml(value.metrics);
      get('issueList').innerHTML=value.issues.length?value.issues.map(item=>`<li>${item}</li>`).join(''):'<li>Kritik eksik kaydedilmedi.</li>';
      get('stepList').innerHTML=value.steps.map(item=>`<li>${item}</li>`).join('');
      get('toolLinks').innerHTML=(value.toolKeys||[]).map(key=>TOOL_LINKS[key]?`<a class="button" href="${TOOL_LINKS[key].href}">${TOOL_LINKS[key].label}</a>`:'').join('');
      resultEl.className=`panel result status-${value.status}`;
      resultEl.focus();
      gate.classList.toggle('hidden',value.commerceClosed||!value.commerceCategories.length);
      productLinks.innerHTML='';
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{get(id).checked=false;});
      get('openProducts').disabled=true;
    }

    function updateSourceFields(){
      const type=get('sourceType').value;
      get('whFields').classList.toggle('hidden',type!=='wh');
      get('mahFields').classList.toggle('hidden',type!=='mah');
    }

    function updatePreset(){
      const preset=PRESET_LUX[get('use').value];
      get('presetHint').textContent=preset?`Başlangıç planlama değeri: ${preset} lx. İsterseniz üretici/proje verisiyle değiştirin.`:'Senaryo seçildiğinde başlangıç değeri gösterilir.';
    }

    function updateGate(){
      const ok=['actualNeed','technicalCheck','affiliateCheck'].every(id=>get(id).checked);
      get('openProducts').disabled=!ok;
    }

    form.addEventListener('submit',event=>{event.preventDefault();render(evaluate(read()));});
    get('resetBtn').addEventListener('click',()=>{form.reset();updateSourceFields();updatePreset();resultEl.className='panel result hidden';gate.classList.add('hidden');});
    get('sourceType').addEventListener('change',updateSourceFields);
    get('use').addEventListener('change',updatePreset);
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>get(id).addEventListener('change',updateGate));
    get('openProducts').addEventListener('click',()=>{
      if(!lastResult||lastResult.commerceClosed)return;
      productLinks.innerHTML=lastResult.commerceCategories.map(key=>CATEGORY_LINKS[key]?`<a class="button primary" href="${CATEGORY_LINKS[key].href}">${CATEGORY_LINKS[key].label}</a>`:'').join('');
      productLinks.focus();
    });
    updateSourceFields();
    updatePreset();
  }

  return {evaluate,batteryWh,init,constants:{PRESET_LUX,EFFICIENCY,USABLE_FRACTION,LIGHT_RESERVE,CATEGORY_LINKS}};
});
