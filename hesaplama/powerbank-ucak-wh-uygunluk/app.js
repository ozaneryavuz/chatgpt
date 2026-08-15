(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  if(root) root.PowerbankFlightTool=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const round=(n,d=1)=>Number.isFinite(n)?Number(n.toFixed(d)):null;
  const num=(v)=>{const n=Number(v);return Number.isFinite(n)&&n>0?n:null;};
  const whFromMah=(mah,voltage)=>round((mah*voltage)/1000,1);
  function classify(input){
    const base={status:'verify',commercialAllowed:false,wh:null,title:'Doğrulama gerekli',summary:'Etiket ve havayolu kanıtlarını tamamlayın.',actions:[],facts:[]};
    if(input.condition==='damaged'||input.recall==='recalled') return {...base,status:'danger',title:'Kullanmayın ve uçuşa götürmeyin',summary:'Hasarlı veya geri çağrılmış lityum batarya ısınma ve yangın riski taşır.',actions:['Cihazı şarj etmeyin, delmeyin veya bastırmayın.','Üretici ya da yerel tehlikeli atık yönlendirmesini izleyin.','Aktif duman veya yangında acil görevlilere haber verin.']};
    if(input.useCase==='medical') return {...base,status:'professional',title:'Tıbbi kullanım için havayolu ve cihaz üreticisi planı gerekir',summary:'Tıbbi veya yaşam desteğiyle ilişkili cihazlarda genel tüketici powerbank önerisi güvenli değildir.',actions:['Cihaz üreticisinin onaylı batarya listesini kullanın.','Havayolundan yazılı taşıma ve kullanım koşulu alın.','Tek bataryaya bağlı olmayan klinik yedek plan oluşturun.']};
    if(input.condition!=='sound'||input.recall!=='clear') return {...base,title:'Önce fiziksel güvenlik ve geri çağırma kontrolü',summary:'Tam marka-model güvenlik kontrolü tamamlanmadan uçuş veya satın alma kararı vermeyin.',actions:['Gövde, port ve kabloda şişme, ezilme, ısı ve hasar kontrolü yapın.','Üreticinin resmî destek ve geri çağırma sayfasını kontrol edin.']};
    let wh=null;
    if(input.labelMode==='wh') wh=num(input.labelWh);
    if(input.labelMode==='mah'){
      const mah=num(input.capacityMah),v=num(input.cellVoltage);
      if(mah&&v) wh=whFromMah(mah,v);
    }
    if(!wh||input.labelMode==='marketing') return {...base,title:'Wh değeri güvenilir biçimde belirlenemedi',summary:'Yalnız mAh pazarlama değeri veya USB çıkış voltajı uçuş sınıflandırması için yeterli değildir.',actions:['Etiketteki Wh değerini bulun.','Wh yoksa mAh ile nominal hücre voltajını üretici belgesinden doğrulayın.','Okunamayan veya izlenemeyen ürünü uçuşa hazırlamayın.']};
    base.wh=wh;
    base.facts.push(`${wh} Wh hesaplandı/doğrulandı.`);
    if(wh>100) return {...base,status:'airline_block',wh,title:'100 Wh üzeri powerbank için ürün yolu kapalı',summary:'Powerbank kuralları genel batarya istisnalarından daha sıkı olabilir. Yazılı havayolu doğrulaması olmadan taşıma varsaymayın.',actions:['Uçuşu yapan havayolunun powerbank başlığını kontrol edin.','100–160 Wh genel batarya istisnasını powerbank için otomatik izin saymayın.','Türk Hava Yolları güncel kuralında 100 Wh üzeri powerbank yasaktır.']};
    if(input.airlineProfile==='thy'&&wh<=100) base.facts.push('THY profili: kabinde en çok iki powerbank, uçuşta kullanmama/şarj etmeme ve kısa devre koruması kontrolü.');
    if(input.airlineChecked==='no') return {...base,status:'airline_block',wh,title:'Havayolu kuralı bu ürünü kabul etmiyor',summary:'Genel internet bilgisi veya IATA özeti, uçuşu yapan havayolunun kararının yerine geçmez.',actions:["Powerbank'i uçuşa götürmeyin.",'Havayolundan alternatif taşıma veya onay prosedürü isteyin.']};
    if(input.airlineChecked!=='yes') return {...base,wh,title:'Havayolunun güncel resmî kuralını kontrol edin',summary:'100 Wh altında olmak tek başına biniş onayı değildir.',actions:['Uçuşu gerçekleştiren havayolunun resmî kısıtlamalar sayfasını açın.','Kabin bagajı, adet, kullanım ve saklama koşullarını doğrulayın.']};
    if(input.shortCircuit!=='yes') return {...base,wh,title:'Kısa devreye karşı taşıma hazırlığı eksik',summary:'Powerbank kabinde taşınsa bile terminallerin metal cisimlerle temas etmesi önlenmelidir.',actions:["Powerbank'i ayrı kılıf veya koruyucu ambalajda taşıyın.",'Bozuk kablo ve gevşek metal aksesuarları aynı bölmede bulundurmayın.']};
    if(input.timing==='active') return {...base,status:'active',wh,title:'Aktif yolculukta satış bağlantısı gösterilmiyor',summary:'Havalimanında çevrim içi ürün teslimatı çözüm değildir; havayolu görevlisinin güncel kararını izleyin.',actions:["Powerbank'i kabin görevlisine/güvenliğe sorarak beyan edin.","Kayıtlı bagaja vermeyin; kapıda bagaj alınırsa powerbank'i çıkarın."]};
    if(input.need==='none') return {...base,status:'no_buy',wh,title:'Yeni powerbank almayın',summary:'Gerçek bir yedek enerji ihtiyacı yoksa yalnız seyahat kaygısıyla yeni ürün almak gerekli değildir.',actions:['Mevcut cihazların şarjını yolculuk öncesi tamamlayın.','Güvenli ve kurala uygun mevcut çözümü kullanın.']};
    if(input.need!=='real') return {...base,wh,title:'Önce gerçek enerji ihtiyacını belirleyin',summary:'Kaç cihazın ne kadar süre şarj edileceği bilinmeden kapasiteyi büyütmeyin.',actions:['Telefon/tablet/bilgisayar için gereken şarj sayısını belirleyin.','Kapasite Wh ile tek port çıkış W değerini ayrı değerlendirin.']};
    const requiredW=num(input.requiredW),outputW=num(input.outputW);
    if(!requiredW) return {...base,wh,title:'Cihazın gerekli giriş gücü eksik',summary:'Özellikle USB-C dizüstü bilgisayarda powerbank kapasitesi yeterli olsa bile tek port çıkışı yetersiz olabilir.',actions:['Cihaz veya orijinal adaptör üzerindeki W değerini doğrulayın.','PD/PPS gibi protokol gereksinimini üretici belgesinden kontrol edin.']};
    if(input.existing==='yes'&&input.tested==='yes'&&outputW&&outputW>=requiredW) return {...base,status:'no_buy',wh,title:'Mevcut powerbank yeterli — yeni ürün almayın',summary:'Fiziksel güvenlik, havayolu kuralı, Wh sınırı, kısa devre koruması ve gerçek şarj testi birlikte karşılanıyor.',actions:['Uçuş öncesi etiketi ve kabloyu yeniden kontrol edin.','Havayolunun son dakika kural değişikliklerini doğrulayın.']};
    if(input.existing==='yes'&&input.tested==='not_tested') return {...base,wh,title:'Önce mevcut powerbank ile gerçek test yapın',summary:'Yeni ürün aramadan önce cihazı gereken kabloyla güvenli biçimde şarj edip çıkış gücünü doğrulayın.',actions:['Şarj sırasında aşırı ısınma ve bağlantı kopması olup olmadığını izleyin.','Laptop için tek port W ve protokol uyumunu doğrulayın.']};
    if(outputW&&outputW<requiredW) base.facts.push(`Mevcut tek port çıkışı ${outputW} W; cihaz ihtiyacı ${requiredW} W.`);
    return {...base,status:'qualified',commercialAllowed:true,wh,title:'Doğrulanmış teknik eksik var',summary:'Yeni ürün ancak 100 Wh sınırı, gerekli tek port gücü ve havayolu kuralı birlikte karşılanacaksa değerlendirilebilir.',actions:[`Etikette en çok 100 Wh ve en az ${requiredW} W tek port çıkışını doğrulayın.`,'Cihazın USB-C PD/PPS veya üreticiye özgü protokol gereksinimini kontrol edin.',"Powerbank'i kayıtlı bagaja koymayın ve havayolunun kullanım koşulunu izleyin."]};
  }
  function amazonUrl(requiredW){
    const q=`powerbank 100Wh USB-C PD ${Math.ceil(requiredW||20)}W`;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(q)}&tag=alo186rehber-21`;
  }
  function render(result,input){
    const factHtml=result.facts.length?`<div class="metric"><div><span>Doğrulanan enerji</span><strong>${result.wh??'—'} Wh</strong></div><div><span>Uçuş sınıfı</span><strong>${result.wh&&result.wh<=100?'≤100 Wh':'Kontrol'}</strong></div><div><span>Ticari yol</span><strong>${result.commercialAllowed?'Koşullu':'Kapalı'}</strong></div></div>`:'';
    const actions=`<ul>${result.actions.map(x=>`<li>${x}</li>`).join('')}</ul>`;
    let commerce='';
    if(result.commercialAllowed) commerce=`<div class="gate"><strong>Amazon Türkiye satış ortaklığı açıklaması</strong><span>Bağlantı satış ortaklığı bağlantısıdır. ALO186 ürün satıcısı değildir; fiyat, stok, puan, satıcı, teslimat ve garanti bilgisi yayımlamaz.</span><label><input id="gateNeed" type="checkbox"> Gerçek enerji veya çıkış gücü eksikliği bulundu.</label><label><input id="gateSpecs" type="checkbox"> Wh, tek port W, protokol ve havayolu kuralını ürün sayfasında yeniden kontrol edeceğim.</label><label><input id="gateAffiliate" type="checkbox"> Açılacak Amazon bağlantısının satış ortaklığı bağlantısı olduğunu anladım.</label><a id="amazonLink" class="action primary" href="#" aria-disabled="true">Teknik sınıfa göre Amazon aramasını aç</a></div>`;
    return `<h2>${result.title}</h2><p>${result.summary}</p>${factHtml}${actions}${commerce}<div class="buttons"><button id="downloadJson" type="button">JSON teknik fişi</button><button id="downloadIcs" type="button">7 gün sonra yeniden kontrol takvimi</button><button id="printResult" type="button">Yazdır / PDF</button></div><p class="notice">Bu sonuç biniş izni, ürün onayı veya havayolu kararı değildir. Uçuşu gerçekleştiren havayolunun güncel resmî kuralı önceliklidir.</p>`;
  }
  function makeJson(result,input){return JSON.stringify({generatedAt:new Date().toISOString(),tool:'ALO186 Powerbank Uçak Wh Uygunluk Testi',result:{status:result.status,wh:result.wh,commercialAllowed:result.commercialAllowed,title:result.title},inputs:{labelMode:input.labelMode,useCase:input.useCase,airlineProfile:input.airlineProfile,airlineChecked:input.airlineChecked,condition:input.condition,recall:input.recall},notice:'Kişisel veri içermez; resmî havayolu kuralı ve ürün etiketi yeniden doğrulanmalıdır.'},null,2)}
  function makeIcs(){const now=new Date(),future=new Date(now.getTime()+7*86400000);const fmt=d=>d.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Powerbank Flight Check//TR','BEGIN:VEVENT',`DTSTAMP:${fmt(now)}`,`DTSTART:${fmt(future)}`,'DURATION:PT20M','SUMMARY:Powerbank uçuş uygunluğunu yeniden kontrol et','DESCRIPTION:Wh etiketi, fiziksel durum, geri çağırma, kısa devre koruması ve havayolunun güncel resmî powerbank kuralını yeniden doğrula.','END:VEVENT','END:VCALENDAR'].join('\r\n')}
  function download(name,text,type){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;document.body.appendChild(a);a.click();URL.revokeObjectURL(a.href);a.remove();}
  function init(){
    if(typeof document==='undefined') return;
    const form=document.getElementById('flightForm'),box=document.getElementById('result');
    if(!form||!box) return;
    const value=id=>document.getElementById(id)?.value??'';
    form.addEventListener('submit',e=>{
      e.preventDefault();
      const input={condition:value('condition'),recall:value('recall'),timing:value('timing'),airlineChecked:value('airlineChecked'),airlineProfile:value('airlineProfile'),useCase:value('useCase'),labelMode:value('labelMode'),labelWh:value('labelWh'),capacityMah:value('capacityMah'),cellVoltage:value('cellVoltage'),outputW:value('outputW'),requiredW:value('requiredW'),existing:value('existing'),need:value('need'),tested:value('tested'),shortCircuit:value('shortCircuit')};
      const result=classify(input);
      box.hidden=false;box.dataset.status=result.status;box.innerHTML=render(result,input);box.scrollIntoView({behavior:'smooth',block:'start'});
      const link=document.getElementById('amazonLink');
      if(link){
        const update=()=>{const ok=['gateNeed','gateSpecs','gateAffiliate'].every(id=>document.getElementById(id).checked);link.setAttribute('aria-disabled',String(!ok));link.href=ok?amazonUrl(num(input.requiredW)):'#';link.rel='sponsored nofollow noopener';link.target='_blank';};
        ['gateNeed','gateSpecs','gateAffiliate'].forEach(id=>document.getElementById(id).addEventListener('change',update));
        link.addEventListener('click',ev=>{if(link.getAttribute('aria-disabled')==='true')ev.preventDefault();});update();
      }
      document.getElementById('downloadJson').addEventListener('click',()=>download('alo186-powerbank-ucus-kontrolu.json',makeJson(result,input),'application/json'));
      document.getElementById('downloadIcs').addEventListener('click',()=>download('alo186-powerbank-ucus-yeniden-kontrol.ics',makeIcs(),'text/calendar'));
      document.getElementById('printResult').addEventListener('click',()=>window.print());
    });
    form.addEventListener('reset',()=>{box.hidden=true;box.innerHTML='';delete box.dataset.status;});
  }
  if(typeof document!=='undefined'){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();}
  return {whFromMah,classify,amazonUrl,makeJson,makeIcs};
});
