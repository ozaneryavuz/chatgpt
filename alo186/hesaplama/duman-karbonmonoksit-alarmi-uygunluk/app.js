(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const RESIDENTIAL=['home','apartment','rental','holiday'];
  const PROFESSIONAL=['hotel','commercial','industrial','common_area'];

  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const baseResult=(status,title,summary,extra={})=>({
    status,title,summary,commercialAllowed:false,searchTerm:null,searchUrl:null,
    smokeObligations:null,coObligations:null,coverageGap:null,productClass:null,...extra
  });

  function coverage(input){
    const levels=num(input.levels);
    const bedrooms=num(input.bedrooms);
    const sleepingAreas=num(input.sleepingAreas);
    const valid=levels!==null&&levels>=1&&levels<=10&&bedrooms!==null&&bedrooms>=0&&bedrooms<=20&&sleepingAreas!==null&&sleepingAreas>=1&&sleepingAreas<=10;
    if(!valid)return {valid:false,levels,bedrooms,sleepingAreas,smokeObligations:null,coObligations:null,coRequired:null};
    const coRequired=input.fuelSources!=='none'&&input.fuelSources!=='unknown';
    return {
      valid:true,levels,bedrooms,sleepingAreas,coRequired,
      smokeObligations:levels+bedrooms+sleepingAreas,
      coObligations:coRequired?levels+sleepingAreas:0
    };
  }

  const withCoverage=(result,c)=>({...result,
    smokeObligations:c.smokeObligations,
    coObligations:c.coObligations
  });

  function productFor(gap){
    if(gap==='smoke')return {productClass:'smoke_alarm',searchTerm:'EN 14604 ev tipi duman alarmı uzun ömürlü pil test susturma'};
    if(gap==='co')return {productClass:'co_alarm',searchTerm:'EN 50291-1 karbonmonoksit alarmı ev tipi pil yedekli test düğmeli'};
    return {productClass:'smoke_and_co',searchTerm:'EN 14604 duman alarmı EN 50291-1 karbonmonoksit alarmı ev tipi'};
  }

  function calculate(input={}){
    if(input.emergency){
      return baseResult('emergency','Hemen güvenli alana çıkın','Duman, yangın, doğal gaz kokusu, karbonmonoksit alarmı veya zehirlenme belirtisi varsa ürünü test etmeyin ve kaynağı aramayın. Herkesi dışarı çıkarın; can güvenliği için 112’yi, doğal gaz şüphesinde güvenli alandan 187’yi arayın. Bütün ticari yollar kapalıdır.');
    }
    if(['smoke','co','both'].includes(input.alarmState||'')||input.symptoms==='yes'){
      return baseResult('emergency','Alarmı susturup içeride kalmayın','Aktif duman/CO alarmı veya baş ağrısı, baş dönmesi, bulantı ve sersemlik gibi olası CO belirtilerinde binayı terk edin. Güvenli alandan 112’yi; doğal gaz kaynağı şüphesinde ayrıca 187’yi arayın. Affiliate yönlendirmesi yoktur.');
    }
    if(input.alarmState!=='none'||input.symptoms!=='no'){
      return baseResult('evidence_required','Aktif alarm ve belirti durumunu belirtin','Önceden planlama ile devam eden acil durum birbirinden ayrılmalıdır. Alarm çalıyor veya belirti varsa formu kullanmayın; dışarı çıkın.');
    }
    if(PROFESSIONAL.includes(input.occupancy||'')){
      return baseResult('professional','Bu kullanım profesyonel yangın algılama tasarımı gerektirir','Otel, ticari/Endüstriyel alan, bina ortak alanı veya merkezi panel sistemi; konut tipi tekil alarm affiliate akışıyla onaylanamaz. Risk analizi, proje, zonlama, yangın yönetmeliği ve yetkili tasarım gerekir.');
    }
    if(!RESIDENTIAL.includes(input.occupancy||'')){
      return baseResult('evidence_required','Konut kullanım türünü seçin','Araç yalnız ev, apartman dairesi, kiralık konut ve tatil konutu gibi bağımsız konut kullanımları içindir.');
    }
    if(input.accessibility==='hearing'){
      return baseResult('professional','İşitsel alarma ek erişilebilir uyarı planlayın','Sağır veya işitme güçlüğü bulunan kişiler için yalnız standart sesli alarm yeterli kabul edilmez. Uyumlu flaş, titreşimli yastık/uyandırma cihazı ve birbirine bağlı sistem profesyonelce doğrulanmalıdır; genel affiliate yolu kapalıdır.');
    }
    if(input.accessibility!=='standard'){
      return baseResult('evidence_required','Alarmın herkes tarafından fark edileceğini doğrulayın','Evdeki kişilerin sesli alarmı uykuda duyabilmesi ve tahliye planına erişebilmesi gerekir. İşitme desteği gerekiyorsa erişilebilir sistem değerlendirin.');
    }

    const c=coverage(input);
    if(!c.valid){
      return withCoverage(baseResult('evidence_required','Kat, yatak odası ve uyku alanı sayısını girin','Duman alarmı kapsamı için her kat, her yatak odası ve her ayrı uyku alanı ayrı kontrol edilir. Sayılar ürün adedi değildir; aynı konumun birden fazla kapsama görevini karşılayıp karşılamadığı yerleşim planıyla doğrulanır.'),c);
    }
    if(input.fuelSources==='unknown'){
      return withCoverage(baseResult('evidence_required','Karbonmonoksit kaynağı riskini doğrulayın','Kombi, soba, şömine, gazlı cihaz, bağlı garaj veya jeneratör olasılığını kontrol edin. CO alarmı duman alarmının yerine geçmez; gereksiz ürün önermek için kaynak riski varsayılmaz.'),c);
    }
    if(input.placementChecked==='no'){
      return withCoverage(baseResult('evidence_required','Yerleşimi üretici talimatına göre düzeltin','Alarmı buhar, pişirme dumanı, hava menfezi veya kör noktaya rastgele yerleştirmeyin. Tavan/duvar mesafesi, mutfak uzaklığı ve CO alarm montaj yüksekliği tam model talimatına göre doğrulanmalıdır.'),c);
    }
    if(input.placementChecked!=='yes'){
      return withCoverage(baseResult('evidence_required','Yerleşim kanıtını tamamlayın','Her alarmın tam model üretici talimatına göre yerleştirildiğini; duman alarmının pişirme cihazından uygun uzaklıkta olduğunu ve CO alarmının üretici montaj yüksekliğine uyduğunu doğrulayın.'),c);
    }

    const smokeAnswers=[input.smokeBedrooms,input.smokeOutside,input.smokeEveryLevel];
    if(smokeAnswers.some(value=>value==='unknown')){
      return withCoverage(baseResult('evidence_required','Duman alarmı kapsamını oda oda kontrol edin','Her yatak odasında, her ayrı uyku alanının dışında ve her katta çalışan duman alarmı olup olmadığını ayrı ayrı doğrulayın.'),c);
    }
    const smokeGap=smokeAnswers.some(value=>value==='no');

    let coGap=false;
    if(c.coRequired){
      const coAnswers=[input.coEveryLevel,input.coOutside];
      if(coAnswers.some(value=>value==='unknown')){
        return withCoverage(baseResult('evidence_required','CO alarmı kapsamını kontrol edin','Yakıt yakan cihaz, bağlı garaj veya jeneratör riski bulunan konutta her katta ve uyku alanlarının dışında çalışan CO alarmı olup olmadığını doğrulayın.'),c);
      }
      coGap=coAnswers.some(value=>value==='no');
    }

    if(['damaged','missing'].includes(input.condition||'')){
      return withCoverage(baseResult('stop_use','Çalışmayan veya hasarlı alarm koruma sağlamaz','Kırık, boyanmış, su görmüş, eksik, sökülmüş ya da havalandırma delikleri kapalı cihazı güvenilir kabul etmeyin. Aktif tehlike yoksa güvenli geçici plan ve uygun cihazla değişim hazırlayın; tehlike sırasında mağaza bağlantısı gösterilmez.'),c);
    }
    if(input.condition!=='sound'&&input.existingType!=='none'){
      return withCoverage(baseResult('evidence_required','Mevcut cihazın fiziksel durumunu kontrol edin','Kasa, sensör açıklıkları, sabitleme, pil bölmesi ve uyarı göstergeleri sağlam olmalıdır. Boyanmış veya üzeri kapatılmış alarm yeterli sayılmaz.'),c);
    }

    if(input.recallChecked==='recalled'){
      return withCoverage(baseResult('stop_use','Geri çağırılmış alarmı güvenilir kabul etmeyin','Tam marka-model için geri çağırma veya kullanım durdurma duyurusu varsa üretici ve resmî ürün güvenliği talimatını izleyin. Çalışan alternatif koruma olmadan alanı korumasız bırakmayın; bu durumda affiliate yönlendirmesi kapalıdır.'),c);
    }
    if(input.existingType!=='none'&&input.recallChecked!=='yes'){
      return withCoverage(baseResult('evidence_required','Tam model geri çağırma kontrolünü tamamlayın','Alarmın marka, model ve üretim bilgisiyle üretici ve resmî ürün güvenliği duyurularını kontrol edin. Pazar yeri listesi güvenlik kanıtı değildir.'),c);
    }

    const smokePresent=['smoke','combination','mixed'].includes(input.existingType||'');
    const coPresent=['co','combination','mixed'].includes(input.existingType||'');
    if(smokePresent){
      const age=num(input.smokeAgeYears);
      if(age===null||age<0){
        return withCoverage(baseResult('evidence_required','Duman alarmının üretim tarihini bulun','Duman alarmı için üretim tarihini veya değişim tarihini kontrol edin. Yaş bilinmeden mevcut cihaz yeterli sayılmaz.'),c);
      }
      if(age>=10){
        const p=productFor(coGap?'both':'smoke');
        return withCoverage(baseResult('replace_candidate','Duman alarmı hizmet ömrünü doldurmuş','Duman alarmı üretim tarihinden itibaren 10 yıl veya üreticinin daha kısa ömrü dolduysa test düğmesi çalışsa bile planlı değişim gerekir. Yeni cihazda tam model EN 14604 kanıtını ve yerleşim uygunluğunu doğrulayın.',{commercialAllowed:true,coverageGap:coGap?'both':'smoke',...p}),c);
      }
    }
    if(coPresent){
      if(input.coEndOfLife==='expired'){
        const p=productFor(smokeGap?'both':'co');
        return withCoverage(baseResult('replace_candidate','CO alarmı üretici değişim tarihini geçmiş','CO sensör ömrü modele göre değişir. Üreticinin “replace by/end of life” tarihi geçmişse cihazı güvenilir kabul etmeyin; yeni cihazda EN 50291-1 ve tam model belgeyi doğrulayın.',{commercialAllowed:true,coverageGap:smokeGap?'both':'co',...p}),c);
      }
      if(input.coEndOfLife!=='valid'){
        return withCoverage(baseResult('evidence_required','CO alarmı değişim tarihini doğrulayın','Tam model etiketi veya kılavuzundaki sensör ömrü ve “replace by/end of life” tarihini kontrol edin. Sabit bir yıl varsayımıyla gereksiz değişim yapılmaz.'),c);
      }
    }

    if(input.monthlyTest==='fail'){
      if(input.batteryMode==='replaceable'&&input.batteryRetest!=='yes'){
        return withCoverage(baseResult('maintenance_first','Önce doğru pili değiştirip yeniden test edin','Üreticinin belirttiği pili takın, pil temasını ve cihaz sabitlemesini kontrol edin, ardından test düğmesini yeniden çalıştırın. Başarılı olursa sırf düşük pil uyarısı nedeniyle yeni ürün almayın.'),c);
      }
      const gap=smokeGap&&coGap?'both':smokeGap?'smoke':coGap?'co':input.existingType==='co'?'co':input.existingType==='smoke'?'smoke':'both';
      const p=productFor(gap);
      return withCoverage(baseResult('replace_candidate','Alarm testten geçmedi','Doğru pil ve üretici prosedüründen sonra test başarısızsa cihaz koruma sağlamıyor kabul edilir. Aktif acil durum yokken, eksik güvenlik sınıfını tam model standardı ve geri çağırma kontrolüyle değiştirin.',{commercialAllowed:true,coverageGap:gap,...p}),c);
    }
    if(input.monthlyTest!=='pass'&&input.existingType!=='none'){
      return withCoverage(baseResult('test_existing','Yeni ürün almadan önce aylık testi yapın','Test düğmesini üretici talimatına göre çalıştırın; ses, ışık, birbirine bağlı cihazlar ve erişilebilir uyarılar birlikte doğrulanmalıdır. Aerosol veya açık alevle kontrol yapmayın.'),c);
    }

    if(input.powerBackup==='no'){
      return withCoverage(baseResult('evidence_required','Kesintide çalışacak güç yedeği yok','Şebekeye bağlı alarmda üretici tarafından öngörülen batarya yedeği bulunmalıdır. Yeni ürün almadan önce mevcut sistemin uygun yedek güç modülünü ve elektrikçi gereksinimini doğrulayın.'),c);
    }
    if(input.powerBackup!=='yes'&&input.existingType!=='none'){
      return withCoverage(baseResult('evidence_required','Güç kaynağı ve batarya yedeğini doğrulayın','Pilli, mühürlü uzun ömürlü veya şebekeye bağlı-batarya yedekli yapıyı tam model kılavuzundan doğrulayın.'),c);
    }

    if(smokePresent&&input.certSmoke!=='yes'){
      return withCoverage(baseResult('evidence_required','Duman alarmının EN 14604 kanıtını doğrulayın','Tam marka-model, üretici, kullanım kılavuzu ve EN 14604 performans/uygunluk belgesi izlenebilir olmalıdır. Yalnız CE işareti veya pazar yeri metni yeterli kanıt değildir.'),c);
    }
    if(coPresent&&input.certCo!=='yes'){
      return withCoverage(baseResult('evidence_required','CO alarmının EN 50291-1 kanıtını doğrulayın','Tam marka-modelin EN 50291-1 test ve performans kanıtını, üretici talimatını ve son kullanım/değişim bilgisini doğrulayın.'),c);
    }

    if(smokeGap||coGap){
      const gap=smokeGap&&coGap?'both':smokeGap?'smoke':'co';
      const p=productFor(gap);
      const explanation=gap==='both'
        ?'Hem duman hem CO kapsamasında eksik var. Tek birleşik ürün ancak iki standardı ayrı ayrı karşılıyor ve her iki sensör için doğru konuma yerleştirilebiliyorsa değerlendirilir; aksi hâlde ayrı cihazlar daha doğru olabilir.'
        :gap==='smoke'
          ?'Her yatak odası, ayrı uyku alanının dışı veya kat kapsamından en az biri eksik. Gerekli konuma uygun ev tipi duman alarmı sınıfını doğrulayın.'
          :'Yakıt/garaj/jeneratör riski bulunan konutta kat veya uyku alanı dışı CO kapsamı eksik. Duman alarmı bu boşluğu kapatmaz.';
      return withCoverage(baseResult('conditional_purchase','Gerçek alarm kapsamı açığı doğrulandı',`${explanation} Kapsama görevleri ürün adedi değildir; aynı cihazın birden fazla görevi karşılaması yerleşim ve üretici talimatına göre doğrulanarak gereksiz satın alma önlenir.`,{commercialAllowed:true,coverageGap:gap,...p}),c);
    }

    if(input.existingType==='none'){
      return withCoverage(baseResult('evidence_required','Mevcut alarm bilgileri çelişkili','Kapsama soruları tam görünse de mevcut cihaz türü “yok” seçilmiş. Oda oda çalışan alarmı, modelini ve standardını yeniden doğrulayın.'),c);
    }

    return withCoverage(baseResult('no_buy','Mevcut alarm kapsamı yeterli — yeni ürün almayın','Mevcut duman/CO alarm düzeni; oda-kat kapsamı, fiziksel durum, yaş/son kullanım, tam model geri çağırma, aylık test, güç yedeği ve ilgili standart kanıtlarını karşılıyor. Yeni ürün yerine aylık test ve tahliye planı tatbikatını sürdürün.',{coverageGap:'none'}),c);
  }

  function statusLabel(status){
    const map={emergency:'Acil tahliye',professional:'Profesyonel tasarım',evidence_required:'Kanıt gerekli',stop_use:'Koruma yetersiz',maintenance_first:'Önce bakım',test_existing:'Önce test',replace_candidate:'Planlı değişim',conditional_purchase:'Koşullu ürün yolu',no_buy:'Satın alma yok'};
    return map[status]||'Sonuç';
  }
  function nextStep(result){
    const map={emergency:'Dışarı çık · 112/187',professional:'Yetkili proje ve risk analizi',evidence_required:'Etiket/yerleşim kontrolü',stop_use:'Çalışan alternatif koruma',maintenance_first:'Pil değiştir ve test et',test_existing:'Aylık test düğmesi',replace_candidate:'Doğru standardı doğrula',conditional_purchase:'Eksik kapsama sınıfı',no_buy:'Aylık testi sürdür'};
    return map[result.status]||'Kanıtları kontrol edin';
  }
  function buildSearchUrl(term){
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(term)}&tag=${AFFILIATE_TAG}`;
  }
  function download(filename,text,type){
    const blob=new Blob([text],{type});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');
    a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
  }
  function icsDate(date){return date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}/,'');}

  function mount(doc){
    const form=doc.getElementById('alarmForm');
    if(!form)return;
    const resultBox=doc.getElementById('result');
    const commerce=doc.getElementById('commerce');
    const affiliate=doc.getElementById('affiliate');
    let lastResult=null;

    const read=()=>{
      const ids=['alarmState','symptoms','occupancy','accessibility','levels','bedrooms','sleepingAreas','fuelSources','placementChecked','smokeBedrooms','smokeOutside','smokeEveryLevel','coEveryLevel','coOutside','existingType','condition','smokeAgeYears','coEndOfLife','monthlyTest','batteryMode','batteryRetest','powerBackup','certSmoke','certCo','recallChecked'];
      const data={emergency:doc.getElementById('emergency').checked};
      ids.forEach(id=>{data[id]=doc.getElementById(id).value;});
      return data;
    };
    const render=(r)=>{
      lastResult=r;
      doc.getElementById('status').textContent=statusLabel(r.status);
      doc.getElementById('resultTitle').textContent=r.title;
      doc.getElementById('summary').textContent=r.summary;
      doc.getElementById('smokeMetric').textContent=r.smokeObligations!==null?`${r.smokeObligations} kapsama görevi`:'—';
      doc.getElementById('coMetric').textContent=r.coObligations!==null?(r.coObligations?`${r.coObligations} kapsama görevi`:'Kaynak riski doğrulanmadı'):'—';
      doc.getElementById('gapMetric').textContent=r.coverageGap==='none'?'Eksik yok':r.coverageGap==='smoke'?'Duman alarmı':r.coverageGap==='co'?'CO alarmı':r.coverageGap==='both'?'Duman + CO':'—';
      doc.getElementById('nextMetric').textContent=nextStep(r);
      resultBox.hidden=false;
      commerce.hidden=!r.commercialAllowed;
      affiliate.removeAttribute('href');affiliate.setAttribute('aria-disabled','true');affiliate.setAttribute('tabindex','-1');
      doc.querySelectorAll('.confirm').forEach(box=>{box.checked=false;});
      if(r.commercialAllowed&&r.searchTerm)r.searchUrl=buildSearchUrl(r.searchTerm);
      resultBox.focus();
    };
    form.addEventListener('submit',(event)=>{event.preventDefault();render(calculate(read()));});
    form.addEventListener('reset',()=>{setTimeout(()=>{resultBox.hidden=true;commerce.hidden=true;lastResult=null;},0);});
    doc.querySelectorAll('.confirm').forEach(box=>box.addEventListener('change',()=>{
      const ok=[...doc.querySelectorAll('.confirm')].every(item=>item.checked);
      if(ok&&lastResult&&lastResult.searchUrl){affiliate.href=lastResult.searchUrl;affiliate.removeAttribute('aria-disabled');affiliate.setAttribute('tabindex','0');}
      else{affiliate.removeAttribute('href');affiliate.setAttribute('aria-disabled','true');affiliate.setAttribute('tabindex','-1');}
    }));
    doc.getElementById('downloadJson').addEventListener('click',()=>{
      if(!lastResult)return;
      const payload={generatedAt:new Date().toISOString(),platform:'ALO186 bağımsız bilgi platformu',result:lastResult,notice:'Fiyat, stok, puan, satıcı, teslimat ve garanti verisi içermez. Alarm yerleşimi ve yerel kurallar üretici/yetkili merciden doğrulanmalıdır.'};
      download('alo186-duman-co-alarm-teknik-fis.json',JSON.stringify(payload,null,2),'application/json');
    });
    doc.getElementById('downloadIcs').addEventListener('click',()=>{
      if(!lastResult)return;
      const start=new Date();start.setDate(start.getDate()+30);start.setHours(10,0,0,0);
      const end=new Date(start.getTime()+30*60*1000);
      const body=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Duman ve CO Alarm Kontrolu//TR','BEGIN:VEVENT',`UID:alo186-smoke-co-${Date.now()}@alo186.com`,`DTSTAMP:${icsDate(new Date())}`,`DTSTART:${icsDate(start)}`,`DTEND:${icsDate(end)}`,'SUMMARY:Duman ve CO alarmı aylık güvenlik kontrolü','DESCRIPTION:Test düğmesi, pil/şebeke yedeği, cihaz yaşı veya replace-by tarihi, tam model geri çağırma, fiziksel durum, birbirine bağlı uyarı ve tahliye planını kontrol edin. Fiyat veya kampanya takibi değildir.','END:VEVENT','END:VCALENDAR'].join('\r\n');
      download('alo186-duman-co-alarm-30-gun-kontrol.ics',body,'text/calendar');
    });
    doc.getElementById('printResult').addEventListener('click',()=>window.print());
  }

  return {calculate,coverage,mount,buildSearchUrl};
});
