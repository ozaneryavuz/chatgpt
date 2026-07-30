(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186LaundryBackup=api;
  if(root&&root.document)api.init(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const ROUTE='/hesaplama/camasir-bulasik-kurutma-makinesi-yedek-guc-uygunluk/';
  const CONTINUOUS_RESERVE=1.20;
  const SURGE_RESERVE=1.10;
  const INVERTER_EFFICIENCY=0.85;
  const USABLE_ENERGY=0.80;
  const SURGE_MULTIPLIER={washer:1.7,dishwasher:1.35,heat_pump_dryer:2.4,resistance_dryer:1.35,washer_dryer:1.8};
  const LABELS={
    emergency:'Acil',evidence_required:'Kanıt eksik',stop:'Uygun değil',professional:'Uzman gerekli',
    active_event:'Aktif kesinti',no_buy:'Yeni ürün alma',conditional:'Koşullu uygunluk'
  };
  const TOOL_LINKS={
    power_station:{label:'Power station kapasite testini aç',href:'../power-station-kapasite-eps-uygunluk/'},
    generator:{label:'Jeneratör güç hesabını aç',href:'../jenerator-gucu-secimi/'},
    inverter:{label:'İnverter ve batarya testini aç',href:'../inverter-uygunluk/'},
    extension:{label:'Uzatma kablosu uygunluğunu kontrol et',href:'../uzatma-kablosu-uygunluk/'},
    compare:{label:'Yedek güç çözümlerini karşılaştır',href:'../yedek-guc-cozum-secici/'},
    outlet:{label:'Priz ve grup priz uygunluğunu kontrol et',href:'../akim-korumali-grup-priz-uygunluk/'}
  };
  const CATEGORY_LINKS={
    power_station:{label:'Power station ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=power_station'},
    generator:{label:'Jeneratör ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=generator'},
    inverter:{label:'İnverter ve batarya ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=inverter'}
  };

  const number=value=>{
    const raw=String(value??'').trim().replace(',','.');
    if(!raw)return null;
    const parsed=Number(raw);
    return Number.isFinite(parsed)?parsed:null;
  };
  const round=(value,digits=0)=>Number(value.toFixed(digits));
  const uniq=values=>[...new Set(values.filter(Boolean))];
  const base=(status,title,summary)=>({status,title,summary,issues:[],steps:[],metrics:null,toolKeys:[],commerceCategories:[],commerceClosed:true});

  function calculations(input={}){
    const maxInputW=number(input.maxInputW);
    const energyRaw=number(input.energyKWh);
    const cycles=number(input.cycleCount);
    const otherW=number(input.otherW)??0;
    const multiplier=SURGE_MULTIPLIER[input.applianceType];
    if(!(maxInputW>0)||!(energyRaw>0)||!(cycles>0)||!multiplier)return null;
    const energyPerCycleKWh=input.energyFormat==='per_100'?energyRaw/100:energyRaw;
    const explicitSurge=number(input.explicitSurgeW);
    const applianceSurge=explicitSurge>0?explicitSurge:maxInputW*multiplier;
    const requiredContinuousW=(maxInputW+otherW)*CONTINUOUS_RESERVE;
    const requiredSurgeW=(applianceSurge+otherW)*SURGE_RESERVE;
    const cycleEnergyWh=energyPerCycleKWh*1000;
    const loadEnergyWh=cycleEnergyWh*cycles;
    const requiredWh=loadEnergyWh/INVERTER_EFFICIENCY/USABLE_ENERGY;
    return {
      maxInputW:round(maxInputW),otherW:round(otherW),
      requiredContinuousW:round(requiredContinuousW),requiredSurgeW:round(requiredSurgeW),
      energyPerCycleKWh:round(energyPerCycleKWh,3),cycleEnergyWh:round(cycleEnergyWh),
      cycles:round(cycles),loadEnergyWh:round(loadEnergyWh),requiredWh:round(requiredWh),
      surgeAssumed:!(explicitSurge>0),surgeMultiplier:explicitSurge>0?null:multiplier
    };
  }

  function evaluate(input={}){
    if(input.emergency){
      const result=base('emergency','Acil: cihazı ve enerji kaynağını kullanmayın','Duman, su kaçağı, erime, yanık kokusu, aşırı ısı veya elektrik çarpması riski varken hesap ve ticari yönlendirme yapılmaz.');
      result.issues=['Islak zemine, hasarlı kabloya veya enerjili cihaza yaklaşmayın.'];
      result.steps=['Güvenliyse enerjiyi ana noktadan kesin.','Yangın, yaralanma veya elektrik çarpması riski varsa 112’yi arayın.','Su kaçağı varsa elektrik güvenliği sağlanmadan vanaya veya cihaza müdahale etmeyin.'];
      return result;
    }

    if(input.applianceType==='industrial'||input.connection==='hardwired'){
      const result=base('professional','Endüstriyel, trifaze veya sabit bağlantılı cihaz için tüketici tipi kaynak seçmeyin','Ortak çamaşırhane, trifaze ve sabit bağlantılı cihazlarda kablo, koruma, transfer, nötr-toprak düzeni ve eşzamanlılık birlikte projelendirilmelidir.');
      result.issues=['Taşınabilir bir ürünün priz çıkışı sabit tesisat uygunluğu anlamına gelmez.'];
      result.steps=['Yetkili elektrik mühendisi veya elektrikçiye yük ve bağlantı düzenini doğrulatın.','Ters besleme, geçici adaptör veya pano içine kullanıcı müdahalesi yapmayın.'];
      result.toolKeys=['generator','inverter','compare'];
      return result;
    }

    if(input.connection==='extension'){
      const result=base('stop','Uzatma, çoklayıcı veya adaptör üzerinden çalıştırmayın','Beyaz eşyanın ısıtma, motor, pompa ve kompresör yükleri ek bağlantı noktalarında aşırı ısınma ve gerilim düşümü oluşturabilir.');
      result.issues=['Cihaz, kaynak üreticisi açıkça izin vermedikçe topraklı ve ayrı çıkışa doğrudan bağlanmalıdır.'];
      result.steps=['Uzatma veya çoklayıcı planını kaldırın.','Priz, koruma ve iletken uygunluğunu yetkili elektrikçiye doğrulatın.'];
      result.toolKeys=['extension','outlet'];
      return result;
    }

    if(input.waterDrain==='risk'){
      const result=base('stop','Su girişi ve drenaj güvenli değilken cihazı çalıştırmayın','Gevşek hortum, kaçak veya gider riski elektrik kaynağından bağımsız olarak su hasarı ve elektrik güvenliği riski oluşturur.');
      result.issues=['Yedek güç ürünü su ve drenaj sorununu çözmez.'];
      result.steps=['Hortum, vana, conta ve gideri üretici talimatına göre kontrol ettirin.','Kaçak giderilmeden çevrim başlatmayın.'];
      return result;
    }

    if(input.supervised==='no'){
      const result=base('stop','İlk yedek güç çevrimini gözetimsiz çalıştırmayın','Kaynak aşırı yükü, transfer hatası, fiş-priz ısınması, su kaçağı veya programın yarıda kalması fark edilmeyebilir.');
      result.issues=['Zamanlayıcılı veya evde kimse yokken ilk deneme uygun değildir.'];
      result.steps=['İlk tam çevrimi uyanıkken ve cihazın yanında yapın.','Isıtma, sıkma, pompa ve varsa kompresör aşamalarını ayrı ayrı gözlemleyin.'];
      return result;
    }

    if(input.powerEvidence==='energy_label_only'){
      const result=base('evidence_required','Enerji etiketi tek başına güç kaynağı seçtirmez','kWh/100 çevrim değeri batarya enerjisini tahmin etmeye yardımcı olur; anlık azami giriş W ve motor/kompresör tepe gücünü göstermez.');
      result.issues=['Tam model azami giriş gücü eksik.'];
      result.steps=['Cihaz etiketinden, kullanım kılavuzundan veya üretici teknik sayfasından azami giriş W değerini bulun.','Enerji etiketi değerini çevrim enerjisi için kullanın.'];
      result.toolKeys=['power_station'];
      return result;
    }

    const evidence=[];
    if(!['planning','active','existing'].includes(input.scenario))evidence.push('Kullanım senaryosu seçilmedi.');
    if(!SURGE_MULTIPLIER[input.applianceType])evidence.push('Cihaz sınıfı seçilmedi.');
    if(input.connection!=='dedicated')evidence.push('Topraklı ve ayrı doğrudan bağlantı doğrulanmadı.');
    if(input.waterDrain!=='secure')evidence.push('Su girişi ve drenaj güvenliği doğrulanmadı.');
    if(input.supervised!=='yes')evidence.push('İlk tam çevrimin gözetimli yapılacağı doğrulanmadı.');
    if(!['nameplate','measured'].includes(input.powerEvidence))evidence.push('Azami giriş gücünün kaynağı doğrulanmadı.');
    if(!['per_cycle','per_100'].includes(input.energyFormat))evidence.push('Enerji verisinin biçimi seçilmedi.');

    const maxInputW=number(input.maxInputW);
    const energyKWh=number(input.energyKWh);
    const cycleCount=number(input.cycleCount);
    const otherW=number(input.otherW);
    const explicitSurgeW=number(input.explicitSurgeW);
    if(!(maxInputW>=100)||maxInputW>5000)evidence.push('Azami giriş gücü 100–5.000 W aralığında doğrulanmadı.');
    if(!(energyKWh>0)||energyKWh>500)evidence.push('Enerji değeri pozitif ve geçerli aralıkta olmalıdır.');
    if(!(cycleCount>=1)||cycleCount>5)evidence.push('Çevrim sayısı 1–5 aralığında olmalıdır.');
    if(otherW!==null&&(otherW<0||otherW>1500))evidence.push('Diğer eşzamanlı yük 0–1.500 W aralığında olmalıdır.');
    if(explicitSurgeW!==null&&(explicitSurgeW<100||explicitSurgeW>12000))evidence.push('Tepe güç 100–12.000 W aralığında olmalıdır.');

    if(evidence.length){
      const result=base('evidence_required','Önce güç ve çevrim kanıtlarını tamamlayın','Beyaz eşya seçiminde anlık W ile çevrim kWh değeri birlikte doğrulanmadan ürün yolu açılmaz.');
      result.issues=evidence;
      result.steps=['Tam model azami giriş W değerini bulun.','Enerji etiketindeki kWh/100 çevrim değerini olduğu biçimde girin veya ölçülen çevrim kWh değerini kullanın.'];
      result.toolKeys=['power_station'];
      return result;
    }

    const metrics=calculations(input);
    if(!metrics)return base('evidence_required','Hesap için gerekli veri eksik','Sayısal bilgiler tamamlanmadan sonuç üretilemez.');

    const impracticalPortable=input.applianceType==='resistance_dryer'||input.applianceType==='washer_dryer'||metrics.requiredContinuousW>3300||metrics.requiredWh>5000;
    if(impracticalPortable){
      const result=base('professional','Taşınabilir power station yerine programı erteleyin veya profesyonel kaynak değerlendirin','Rezistanslı kurutma, birleşik yıkama-kurutma veya yüksek enerji ihtiyacı çoğu taşınabilir kaynağın pratik sınırını aşar.');
      result.metrics=metrics;
      result.issues=['Yüksek sürekli güç ve uzun çevrim enerjisi; priz, kablo, havalandırma ve kaynak işletmesini birlikte etkiler.'];
      result.steps=['Mümkünse şebeke dönene kadar yüksek enerji programını erteleyin.','Zorunlu süreklilikte profesyonel jeneratör veya sabit inverter-batarya çözümü için proje ve koruma değerlendirmesi yaptırın.'];
      result.toolKeys=['generator','inverter','compare'];
      return result;
    }

    if(input.scenario==='active'){
      const result=base('active_event','Aktif kesintide yalnız önceden test edilmiş mevcut kaynağı kullanın','Hesap gelecekteki hazırlık sınıfını gösterir; ürün teslimatı devam eden çevrim veya aktif kesinti için anlık çözüm değildir.');
      result.metrics=metrics;
      result.issues=['Geçici kablo, ters besleme veya ilk kez denenen kaynak kullanmayın.'];
      result.steps=['Önceden tam çevrim testinden geçmemiş bir kaynakla cihazı başlatmayın.','Kapı, su ve program durumunu güvenli biçimde yönetin; kesinti sonrası planı yeniden oluşturun.'];
      result.toolKeys=['compare'];
      return result;
    }

    if(input.sourceStatus==='existing'){
      const continuous=number(input.sourceContinuousW);
      const surge=number(input.sourceSurgeW);
      const wh=number(input.sourceWh);
      const batteryNeeded=['power_station','inverter','auto'].includes(input.sourceType);
      if(!(continuous>0)||!(surge>0)||(batteryNeeded&&!(wh>0))){
        const result=base('evidence_required','Mevcut kaynağın W, tepe W ve Wh değerlerini doğrulayın','Model adı veya pazarlama tepe değeri tek başına yeterli değildir.');
        result.metrics=metrics;
        result.issues=['Sürekli AC W, kısa süreli tepe W ve bataryalıysa nominal Wh değeri eksik.'];
        result.steps=['Aynı modelin üretici teknik sayfasını kontrol edin.'];
        return result;
      }
      const continuousOk=continuous>=metrics.requiredContinuousW;
      const surgeOk=surge>=metrics.requiredSurgeW;
      const whOk=!batteryNeeded||wh>=metrics.requiredWh;
      const waveformOk=input.waveform==='pure';
      const outputOk=input.outputSpec==='confirmed';
      const directOk=input.directOutput==='yes';
      const testOk=input.loadTest==='success';
      if(continuousOk&&surgeOk&&whOk&&waveformOk&&outputOk&&directOk&&testOk){
        const result=base('no_buy','Mevcut kaynak tüm kanıtları karşılıyorsa yeni ürün almayın','Girilen teknik değerler ve gözetimli tam çevrim testine göre mevcut kaynak yeterli görünüyor.');
        result.metrics=metrics;
        result.steps=['Fiş, priz, kaynak sıcaklığı ve su bağlantılarını her kullanımda kontrol edin.','Yeni program veya yük eklendiğinde hesabı tekrarlayın.'];
        result.toolKeys=['power_station'];
        return result;
      }
      const result=base('conditional','Mevcut kaynakta kapasite veya doğrulama açığı var','Eksik güç, enerji, dalga biçimi, bağlantı veya tam çevrim testi kapatılmadan güvenli uygunluk doğrulanamaz.');
      result.metrics=metrics;
      if(!continuousOk)result.issues.push(`Sürekli güç en az ${metrics.requiredContinuousW} W olmalı.`);
      if(!surgeOk)result.issues.push(`Tepe güç en az ${metrics.requiredSurgeW} W olmalı.`);
      if(!whOk)result.issues.push(`Bataryalı kaynak nominal olarak yaklaşık ${metrics.requiredWh} Wh veya üzeri olmalı.`);
      if(!waveformOk)result.issues.push('Saf sinüs çıkış doğrulanmadı.');
      if(!outputOk)result.issues.push('230 V / 50 Hz ve cihaz üreticisi uyumu doğrulanmadı.');
      if(!directOk)result.issues.push('Doğrudan, topraklı ve ayrı bağlantı doğrulanmadı.');
      if(!testOk)result.issues.push('Gözetimli tam çevrim testi başarıyla tamamlanmadı.');
      result.steps=['Eksik kanıtı ürün almadan önce kapatın.','Yeni kaynak düşünülüyorsa tam model teknik verilerini bu eşiklerle karşılaştırın.'];
      result.toolKeys=['power_station','compare'];
      if(!continuousOk||!surgeOk||!whOk){
        const preferred=input.sourceType==='generator'?'generator':input.sourceType==='inverter'?'inverter':'power_station';
        result.commerceCategories=[preferred];
        result.commerceClosed=false;
      }
      return result;
    }

    const result=base('conditional','Tek çevrim için alt teknik sınırlar hesaplandı','Bu sonuç ürün veya model onayı değildir; tam model üretici şartları ve gözetimli tam çevrim testi gereklidir.');
    result.metrics=metrics;
    if(metrics.surgeAssumed)result.issues.push(`Üretici tepe gücü girilmedi; ${metrics.surgeMultiplier}× konservatif varsayım kullanıldı.`);
    result.steps=['Kaynak sürekli W, tepe W ve nominal Wh değerlerini birlikte karşılaştırın.','Saf sinüs, 230 V / 50 Hz, doğrudan topraklı çıkış ve ilk tam çevrim testini doğrulayın.'];
    const preferred=input.sourceType==='generator'?'generator':input.sourceType==='inverter'?'inverter':'power_station';
    result.toolKeys=uniq([preferred,'compare']);
    result.commerceCategories=[preferred];
    result.commerceClosed=false;
    return result;
  }

  function readForm(doc){
    const ids=['scenario','applianceType','connection','waterDrain','supervised','powerEvidence','maxInputW','explicitSurgeW','energyFormat','energyKWh','cycleCount','otherW','sourceStatus','sourceType','sourceContinuousW','sourceSurgeW','sourceWh','waveform','outputSpec','directOutput','loadTest'];
    const data={emergency:Boolean(doc.getElementById('emergency')?.checked)};
    ids.forEach(id=>{const el=doc.getElementById(id);data[id]=el?el.value:'';});
    return data;
  }

  function metricCards(metrics){
    if(!metrics)return '';
    return [
      ['Sürekli AC alt sınırı',`${metrics.requiredContinuousW} W`],
      ['Tepe güç alt sınırı',`${metrics.requiredSurgeW} W`],
      ['Çevrim enerjisi',`${metrics.energyPerCycleKWh} kWh`],
      ['Nominal batarya alt sınırı',`${metrics.requiredWh} Wh`]
    ].map(([label,value])=>`<div><span>${label}</span><strong>${value}</strong></div>`).join('');
  }

  function safeText(value){return String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}

  function render(doc,result){
    const section=doc.getElementById('result');
    section.className=`panel result status-${result.status}`;
    doc.getElementById('statusBadge').textContent=LABELS[result.status]||result.status;
    doc.getElementById('resultTitle').textContent=result.title;
    doc.getElementById('resultSummary').textContent=result.summary;
    doc.getElementById('metrics').innerHTML=metricCards(result.metrics);
    doc.getElementById('issues').innerHTML=(result.issues.length?result.issues:['Belirgin ek risk kaydı yok.']).map(item=>`<li>${safeText(item)}</li>`).join('');
    doc.getElementById('steps').innerHTML=(result.steps.length?result.steps:['Sonucu tam model üretici verileriyle doğrulayın.']).map(item=>`<li>${safeText(item)}</li>`).join('');
    doc.getElementById('toolLinks').innerHTML=uniq(result.toolKeys).map(key=>TOOL_LINKS[key]).filter(Boolean).map(link=>`<a class="button" href="${link.href}">${link.label}</a>`).join('');
    const commerce=doc.getElementById('commerce');
    commerce.classList.toggle('hidden',result.commerceClosed||!result.commerceCategories.length);
    commerce.dataset.categories=result.commerceCategories.join(',');
    ['confirmGap','confirmSpecs','confirmAffiliate'].forEach(id=>{const box=doc.getElementById(id);if(box)box.checked=false;});
    doc.getElementById('commerceLinks').innerHTML='';
    section.hidden=false;
    section.focus({preventScroll:true});
    section.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    section.dataset.result=JSON.stringify({route:ROUTE,createdAt:new Date().toISOString(),...result});
  }

  function updateCommerce(doc){
    const ready=['confirmGap','confirmSpecs','confirmAffiliate'].every(id=>doc.getElementById(id)?.checked);
    const target=doc.getElementById('commerceLinks');
    if(!ready){target.innerHTML='<span class="muted">Üç şeffaflık onayı tamamlanmadan ürün bağlantısı açılmaz.</span>';return;}
    const keys=(doc.getElementById('commerce').dataset.categories||'').split(',').filter(Boolean);
    target.innerHTML=keys.map(key=>CATEGORY_LINKS[key]).filter(Boolean).map(link=>`<a class="button primary" href="${link.href}" rel="sponsored nofollow noopener">${link.label}</a>`).join('');
  }

  function downloadJson(doc){
    const raw=doc.getElementById('result')?.dataset.result;
    if(!raw)return;
    const blob=new Blob([JSON.stringify(JSON.parse(raw),null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob);
    const anchor=doc.createElement('a');
    anchor.href=url;anchor.download='alo186-beyaz-esya-yedek-guc-sonucu.json';anchor.click();
    setTimeout(()=>URL.revokeObjectURL(url),0);
  }

  function init(doc){
    const form=doc.getElementById('laundryForm');
    if(!form||form.dataset.ready==='true')return;
    form.dataset.ready='true';
    const sourceStatus=doc.getElementById('sourceStatus');
    const existingFields=doc.getElementById('existingFields');
    const syncExisting=()=>existingFields.classList.toggle('hidden',sourceStatus.value!=='existing');
    sourceStatus.addEventListener('change',syncExisting);syncExisting();
    form.addEventListener('submit',event=>{event.preventDefault();render(doc,evaluate(readForm(doc)));});
    doc.getElementById('resetBtn').addEventListener('click',()=>{form.reset();syncExisting();doc.getElementById('result').hidden=true;});
    ['confirmGap','confirmSpecs','confirmAffiliate'].forEach(id=>doc.getElementById(id)?.addEventListener('change',()=>updateCommerce(doc)));
    doc.getElementById('printBtn').addEventListener('click',()=>{if(typeof globalThis.print==='function')globalThis.print();});
    doc.getElementById('jsonBtn').addEventListener('click',()=>downloadJson(doc));
  }

  return {ROUTE,calculations,evaluate,init};
});
