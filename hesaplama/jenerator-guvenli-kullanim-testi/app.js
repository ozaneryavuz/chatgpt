(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186GeneratorSafety=api;
  if(root&&root.document)api.init(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const runtimeRoot=typeof globalThis!=='undefined'?globalThis:{};
  const DISTANCE_MIN_M=6.1;
  const CATEGORY_LINKS={
    generator:{label:'Jeneratör ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=generator'},
    co_alarm:{label:'CO alarmı ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=co_alarm'},
    extension_cord:{label:'Dış ortam uzatma kablosu sınıfını aç',href:'../../akilli-urun-secimi?kategori=extension_cord'}
  };
  const TOOL_LINKS={
    sizing:{label:'Jeneratör güç hesabını aç',href:'../jenerator-gucu-secimi/'},
    cord:{label:'Uzatma kablosu uygunluk testini aç',href:'../uzatma-kablosu-uygunluk/'},
    alarms:{label:'Duman alarmı yerleşim testini aç',href:'../duman-alarmi-yerlesim-bakim-uygunluk/'},
    outcome:{label:'Çözüm sonucunu kaydet',href:'../cozum-sonucu/'}
  };

  const uniq=values=>[...new Set(values.filter(Boolean))];
  const num=value=>{
    const raw=String(value??'').trim();
    if(!raw)return null;
    const parsed=Number(raw.replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };

  function baseResult(status,title,summary){
    return {status,title,summary,issues:[],steps:[],commerceCategories:[],toolKeys:[],commerceClosed:true};
  }

  function evaluate(input={}){
    if(input.emergency){
      const result=baseResult('emergency','Acil: jeneratörü durdurun ve temiz havaya çıkın','CO alarmı veya zehirlenme/yangın/elektrik tehlikesi belirtisi varken hesap ve ticari yönlendirme yapılmaz.');
      result.issues.push('Jeneratörü güvenli biçimde kapatın; binaya geri dönmeyin ve egzoz kaynağına yaklaşmayın.');
      result.steps.push('Herkesi temiz havaya çıkarın. Belirti, bilinç değişikliği, nefes darlığı, yangın veya elektrik çarpması riski varsa 112’yi arayın.');
      result.steps.push('CO alarmını susturup kullanıma devam etmeyin; kaynak ve bina yetkili ekip tarafından kontrol edilmeden jeneratörü yeniden çalıştırmayın.');
      return result;
    }

    const hardStops=[];
    const evidence=[];
    const prerequisites=[];
    const steps=[];
    const commerce=[];
    const toolKeys=[];
    const distance=num(input.distanceM);

    if(input.placement==='indoor')hardStops.push('Jeneratör ev, bodrum veya başka bir kapalı alanda planlanıyor.');
    else if(input.placement==='garage_shed')hardStops.push('Garaj, depo, kulübe veya yarı kapalı alan karbonmonoksit için güvenli değildir; kapı açık olsa bile kullanılmamalıdır.');
    else if(input.placement==='porch_carport')hardStops.push('Balkon, veranda ve araç sundurması yapıya çok yakındır; tamamen açık dış ortam değildir.');
    else if(input.placement!=='open_outdoor')evidence.push('Tamamen açık dış ortam yerleşimi doğrulanmadı.');

    if(distance===null)evidence.push('En yakın kapı, pencere veya havalandırma açıklığına mesafe ölçülmedi.');
    else if(distance<DISTANCE_MIN_M)hardStops.push(`Açıklıklara mesafe ${distance.toLocaleString('tr-TR')} m; en az 6,1 m ön koşulu sağlanmıyor.`);

    if(input.exhaust==='toward')hardStops.push('Egzoz yapı, açıklık veya başka bir binaya doğru yöneliyor.');
    else if(input.exhaust!=='away')evidence.push('Egzozun yapı ve açıklıklardan uzağa yöneldiği doğrulanmadı.');

    if(input.weather==='wet')hardStops.push('Yağmur, su birikintisi veya ıslak elle kullanım elektrik çarpması riski oluşturuyor.');
    else if(!['dry','rated_canopy'].includes(input.weather))evidence.push('Yağmur/ıslaklık koruması üretici talimatıyla doğrulanmadı.');

    if(input.connection==='backfeed')hardStops.push('Prize veya uygunsuz kabloya ters besleme ölümcül geri besleme riski oluşturur.');
    else if(input.connection==='unknown')evidence.push('Elektrik bağlantı yöntemi bilinmiyor.');

    if(input.cord==='damaged')hardStops.push('Ezilmiş, ekli, gevşek, ısınmış veya yalıtımı hasarlı kablo kullanılamaz.');
    else if(input.cord==='indoor_light'){
      prerequisites.push('İnce, ev tipi, topraksız veya dış ortam sınıfı doğrulanmamış kablo kullanılmamalıdır.');
      commerce.push('extension_cord');
      toolKeys.push('cord');
    }else if(input.cord==='unknown'){
      evidence.push('Uzatma kablosunun topraklama, kesit, etiket ve dış ortam sınıfı bilinmiyor.');
      toolKeys.push('cord');
    }

    if(input.refuel==='hot_running')hardStops.push('Çalışan veya sıcak motora yakıt eklemek yangın riskidir.');
    else if(input.refuel!=='cooled_outdoors')evidence.push('Yakıt ikmalinin motor kapalı ve soğumuşken dışarıda yapılacağı doğrulanmadı.');

    if(hardStops.length){
      const result=baseResult('stop','Çalıştırmayın: kritik güvenlik koşulu sağlanmıyor','Bu yerleşim veya bağlantı biçiminde jeneratörü kullanmak karbonmonoksit, yangın ya da elektrik çarpması riski oluşturur.');
      result.issues=hardStops;
      result.steps=['Jeneratörü çalıştırmayın veya çalışıyorsa güvenli biçimde durdurun.','Yerleşimi tamamen açık dış ortama taşıyın; en yakın açıklığa en az 6,1 m mesafe ve egzozu yapıdan uzağa yönlendirme koşulunu sağlayın.','Geri besleme, hasarlı kablo, ıslak kullanım veya sıcak yakıt ikmali varsa ürün aramak yerine tehlikeyi giderin.'];
      return result;
    }

    if(input.medical){
      const result=baseResult('professional','Profesyonel süreklilik tasarımı gerekli','Tıbbi veya yaşam destek yükü taşınabilir jeneratör ve geçici kablo kararıyla güvenceye alınamaz.');
      result.issues=uniq([...evidence,...prerequisites,'Tıbbi yükte transfer süresi, yakıt sürekliliği, alarm, bakım, yedeklilik ve test planı birlikte doğrulanmalıdır.']);
      result.steps=['Yetkili elektrik ve ilgili tıbbi cihaz uzmanıyla kesintisiz güç mimarisi oluşturun.','Tek jeneratör veya tek CO alarmını yaşam destek güvencesi olarak kabul etmeyin.'];
      return result;
    }

    if(input.coAlarm==='none'){
      prerequisites.push('Evde çalışan CO alarmı yok; jeneratör çalıştırılmadan önce alarm kapsamı tamamlanmalıdır.');
      commerce.push('co_alarm');
      toolKeys.push('alarms');
    }else if(input.coAlarm==='partial'){
      prerequisites.push('CO alarmı yalnız bazı alanlarda var; her kat ve uyuma alanlarının dışı kapsanmıyor.');
      commerce.push('co_alarm');
      toolKeys.push('alarms');
    }else if(input.coAlarm!=='full'){
      evidence.push('CO alarmının kapsamı, bataryası ve test durumu bilinmiyor.');
      toolKeys.push('alarms');
    }

    if(input.coShutoff!=='yes')steps.push('Yeni jeneratör değerlendiriliyorsa üretici dokümanında CO otomatik durdurma özelliğini arayın; bu özellik doğru yerleşimin ve ev içi CO alarmının yerine geçmez.');

    if(input.connection==='transfer'){
      const result=baseResult('professional','Transfer sistemi ve bina bağlantısı uzman doğrulaması gerektirir','Yerleşim ve CO koşulları doğru olsa bile bina devreleri için transfer, nötr-toprak düzeni, koruma ve test birlikte değerlendirilmelidir.');
      result.issues=uniq([...evidence,...prerequisites]);
      result.steps=uniq(['Transfer sisteminin şebeke ve jeneratörü aynı anda bağlamadığını yetkili elektrik uzmanına doğrulatın.','Jeneratör üreticisinin nötr, topraklama ve RCD talimatlarını bina projesiyle birlikte kontrol edin.',...steps]);
      return result;
    }

    if(evidence.length){
      const result=baseResult('evidence_required','Önce eksik kanıtları tamamlayın','Bilinmeyen yerleşim, kablo, yakıt veya bağlantı bilgisi güvenli kullanım onayı değildir; ticari rota kapalıdır.');
      result.issues=uniq([...evidence,...prerequisites]);
      result.steps=uniq(['Mesafeyi ölçün, egzoz yönünü belirleyin ve üretici kılavuzundaki dış ortam/yağmur talimatını okuyun.','Kablo etiketini, topraklamayı, kesiti ve fiziksel durumu doğrulayın.',...steps]);
      result.toolKeys=uniq(toolKeys);
      return result;
    }

    if(prerequisites.length){
      const result=baseResult('prerequisite','Jeneratörü çalıştırmadan önce eksik güvenlik bileşenini tamamlayın','Temel dış ortam yerleşimi uygun görünse de CO alarmı veya geçici kablo ön koşulu tamamlanmadan jeneratör kullanılmamalıdır.');
      result.issues=uniq(prerequisites);
      result.steps=uniq(['Eksik bileşeni yalnız teknik sınıfı doğruladıktan sonra tamamlayın.','Bileşeni kurup test ettikten sonra bu aracı yeniden çalıştırın.',...steps]);
      result.commerceCategories=uniq(commerce);
      result.toolKeys=uniq(toolKeys);
      result.commerceClosed=result.commerceCategories.length===0;
      return result;
    }

    if(input.generatorStatus==='unknown'){
      const result=baseResult('evidence_required','Mevcut jeneratörün kapasitesini doğrulayın','Güvenli yerleşim, yanlış güç seçimini telafi etmez. Sürekli W, en ağır motor kalkışı ve rezerv bilinmeden ürün rotası açılmaz.');
      result.issues=['Mevcut jeneratörün sürekli ve kalkış gücü ihtiyacı karşılayıp karşılamadığı bilinmiyor.'];
      result.steps=uniq(['Jeneratör güç hesabını tamamlayın ve üretici etiketini doğrulayın.',...steps]);
      result.toolKeys=['sizing'];
      return result;
    }

    if(input.generatorStatus==='none'&&!input.sizingCompleted){
      const result=baseResult('evidence_required','Önce jeneratör güç hesabını tamamlayın','Güvenlik koşulları uygun görünse de sürekli ve kalkış gücü hesaplanmadan ürün sınıfı seçilmez.');
      result.issues=['Sürekli W, motor kalkış W ve kapasite rezervi hesabı tamamlanmadı.'];
      result.steps=uniq(['Jeneratör Gücü Ön Seçimi aracını tamamlayın.','Sonra üretici modelinin nominal ve maksimum gücünü, fazını, yakıtını ve CO özelliğini yeniden doğrulayın.',...steps]);
      result.toolKeys=['sizing'];
      return result;
    }

    if(input.generatorStatus==='owned_sized'){
      const result=baseResult('no_buy','Mevcut jeneratör yeterliyse yeni ürün almayın','Girilen koşullarda mevcut ürünün güç ihtiyacını karşıladığı belirtiliyor. Öncelik yeni ürün değil; yerleşim, alarm, kablo, bakım ve gerçek yük testidir.');
      result.steps=uniq(['Üretici bakım planını, yakıtı ve yük altında çalışma testini güncel tutun.','CO alarmını düzenli test edin; jeneratörü her kullanımda en az 6,1 m uzakta ve egzozu yapıdan uzağa yerleştirin.',...steps]);
      result.toolKeys=['outcome'];
      return result;
    }

    const result=baseResult('conditional_purchase','Güvenlik ön koşulları sağlandı; model seçimini güç hesabıyla sınırlandırın','Yerleşim ve kullanım koşulları uygun görünüyor. Bu sonuç ürün onayı değildir; yalnız güç hesabı tamamlanmış kullanıcı için jeneratör ürün sınıfına kontrollü geçiş açar.');
    result.steps=uniq(['Amazon sonucunda tam model, sürekli W, kalkış W, 230 V/50 Hz çıkış, CO durdurma özelliği, servis ve üretici talimatını yeniden doğrulayın.','Bina devresine bağlamayın; doğrudan yük kullanımında uygun dış ortam kablosu ve üretici talimatını izleyin.',...steps]);
    result.commerceCategories=['generator'];
    result.toolKeys=['sizing'];
    result.commerceClosed=false;
    return result;
  }

  function init(document){
    const form=document.getElementById('generatorSafetyForm');
    if(!form)return;
    const $=id=>document.getElementById(id);
    const resultEl=$('result');
    const gate=$('commerceGate');
    let lastResult=null;

    function collect(){
      return {
        emergency:$('emergency').checked,
        placement:$('placement').value,
        distanceM:$('distanceM').value,
        exhaust:$('exhaust').value,
        weather:$('weather').value,
        connection:$('connection').value,
        cord:$('cord').value,
        refuel:$('refuel').value,
        medical:$('medical').checked,
        coAlarm:$('coAlarm').value,
        coShutoff:$('coShutoff').value,
        generatorStatus:$('generatorStatus').value,
        sizingCompleted:$('sizingCompleted').checked
      };
    }

    function textList(targetId,items,emptyText){
      const target=$(targetId);
      target.innerHTML='';
      const values=items.length?items:[emptyText];
      for(const item of values){const li=document.createElement('li');li.textContent=item;target.appendChild(li);}
    }

    function renderToolLinks(keys){
      const wrap=$('toolLinks');wrap.innerHTML='';
      for(const key of uniq(keys)){
        const data=TOOL_LINKS[key];if(!data)continue;
        const link=document.createElement('a');link.className='button';link.href=data.href;link.textContent=data.label;wrap.appendChild(link);
      }
    }

    function gateReady(){return $('actualNeed').checked&&$('technicalCheck').checked&&$('affiliateAccept').checked;}

    function renderCommerce(categories){
      const wrap=$('commerceLinks');wrap.innerHTML='';
      for(const key of uniq(categories)){
        const data=CATEGORY_LINKS[key];if(!data)continue;
        const link=document.createElement('a');link.className='button primary';link.textContent=data.label;link.dataset.href=data.href;link.setAttribute('aria-disabled','true');link.tabIndex=-1;wrap.appendChild(link);
      }
      gate.classList.toggle('hidden',categories.length===0);
      updateGate();
    }

    function updateGate(){
      const ready=Boolean(lastResult&&!lastResult.commerceClosed&&gateReady());
      gate.querySelectorAll('a[data-href]').forEach(link=>{
        if(ready){link.href=link.dataset.href;link.removeAttribute('aria-disabled');link.tabIndex=0;}
        else{link.removeAttribute('href');link.setAttribute('aria-disabled','true');link.tabIndex=-1;}
      });
    }

    function render(result){
      lastResult=result;
      resultEl.className=`panel result status-${result.status}`;
      $('resultBadge').textContent={emergency:'ACİL',stop:'DURDUR',evidence_required:'KANIT GEREKLİ',prerequisite:'ÖN KOŞUL',professional:'UZMAN',no_buy:'SATIN ALMA YOK',conditional_purchase:'KOŞULLU GEÇİŞ'}[result.status]||'SONUÇ';
      $('resultTitle').textContent=result.title;
      $('resultSummary').textContent=result.summary;
      textList('issueList',result.issues,'Kritik eksik bildirilmedi.');
      textList('stepList',result.steps,'Üretici talimatını ve güncel koşulları yeniden doğrulayın.');
      renderToolLinks(result.toolKeys||[]);
      ['actualNeed','technicalCheck','affiliateAccept'].forEach(id=>$(id).checked=false);
      renderCommerce(result.commerceClosed?[]:(result.commerceCategories||[]));
      resultEl.focus({preventScroll:true});
      resultEl.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
      if(runtimeRoot.Alo186Track)runtimeRoot.Alo186Track('generator_safety_result',{status:result.status,commerce_categories:(result.commerceCategories||[]).join('|')||'none'});
    }

    form.addEventListener('submit',event=>{event.preventDefault();$('validation').textContent='';render(evaluate(collect()));});
    $('resetBtn').addEventListener('click',()=>{form.reset();lastResult=null;resultEl.className='panel result hidden';gate.classList.add('hidden');$('commerceLinks').innerHTML='';$('validation').textContent='';form.querySelector('input,select').focus();});
    ['actualNeed','technicalCheck','affiliateAccept'].forEach(id=>$(id).addEventListener('change',updateGate));
  }

  return {DISTANCE_MIN_M,CATEGORY_LINKS,TOOL_LINKS,evaluate,init};
});
