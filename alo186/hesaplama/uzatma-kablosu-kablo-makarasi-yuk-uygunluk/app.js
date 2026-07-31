'use strict';
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root){root.ALO186ExtensionCord=api;if(root.document)api.mount(root.document);}
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const ROUTE='/hesaplama/uzatma-kablosu-kablo-makarasi-yuk-uygunluk/';
  const RHO=0.0175;
  const n=(value)=>Number(value);
  const finite=(value)=>Number.isFinite(n(value));
  const round=(value,digits=2)=>Number(n(value).toFixed(digits));

  function metrics(data){
    const voltage=n(data.voltage);
    const loadW=n(data.loadW);
    const ratedA=n(data.ratedA);
    const currentA=finite(voltage)&&voltage>0&&finite(loadW)&&loadW>=0?loadW/voltage:NaN;
    const ratedW=finite(voltage)&&voltage>0&&finite(ratedA)&&ratedA>0?voltage*ratedA:NaN;
    const lengthM=n(data.lengthM);
    const area=n(data.crossSection);
    const dropV=finite(currentA)&&finite(lengthM)&&lengthM>0&&finite(area)&&area>0
      ?2*lengthM*currentA*RHO/area:NaN;
    const dropPct=finite(dropV)&&finite(voltage)&&voltage>0?dropV/voltage*100:NaN;
    return {
      currentA:finite(currentA)?round(currentA,2):NaN,
      ratedW:finite(ratedW)?round(ratedW,0):NaN,
      voltageDropV:finite(dropV)?round(dropV,2):NaN,
      voltageDropPct:finite(dropPct)?round(dropPct,2):NaN,
    };
  }

  function decide(data){
    const m=metrics(data);
    const targetDrop=n(data.targetDropPct);
    const confirmations=Boolean(data.confirmNeed&&data.confirmLabel&&data.confirmAffiliate);
    if(data.danger)return {code:'danger',commerce:false,tone:'danger',title:'Kabloyu kullanmayı bırakın',summary:'Duman, erime, kıvılcım, elektrik çarpması, yanık kokusu, ıslaklık veya belirgin ısınmada ürün karşılaştırması yapılmaz. Enerjiyi güvenle kesin; gerekirse 112 ve yetkili elektrikçi rotasına geçin.'};
    if(data.maleToMale||data.connection==='backfeed')return {code:'backfeed',commerce:false,tone:'danger',title:'Erkek–erkek kablo ve ters besleme kesinlikle kullanılmaz',summary:'Jeneratör veya başka bir kaynakla prizden tesisata ters besleme; açıkta enerjili uç, elektrik çarpması ve yangın riski oluşturur. Uygun transfer düzeni yetkili elektrikçi tarafından kurulmalıdır.'};
    if(!data.physicalSafe)return {code:'physical',commerce:false,tone:'danger',title:'Önce mevcut kablo ve priz hasarını giderin',summary:'Ezilmiş, kesilmiş, bantla onarılmış, gevşek, kararmış veya ısınan kablo/fiş/priz yeni ürün seçimiyle güvenli hâle gelmez.'};
    if(data.mode==='active_outage')return {code:'active',commerce:false,tone:'warn',title:'Aktif kesintide yeni ürün teslimatı çözüm değildir',summary:'Mevcut güvenli düzeni etiket sınırları içinde kullanın. Jeneratörü uzatma kablosuyla binaya ters beslemeyin; sabit transfer gereksinimini profesyonel olarak planlayın.'};
    if(['ev','medical','fixed','heater'].includes(data.useClass))return {code:'excluded',commerce:false,tone:'warn',title:'Bu yük uzatma kablosu affiliate akışına uygun değil',summary:'Elektrikli araç, tıbbi/yaşam destek, sabit tesisat ve yüksek güçlü ısıtıcı yüklerinde uzatma veya makara kablo seçimi tüketici ürününe dönüştürülmez. Uygun sabit devre ve profesyonel değerlendirme gerekir.'};
    if(['chain','adapter_chain'].includes(data.connection))return {code:'chain',commerce:false,tone:'danger',title:'Zincirleme bağlantıyı kaldırın',summary:'Uzatmayı uzatmaya, çoklayıcıya veya adaptör zincirine bağlamayın. Daha yüksek etiketli son ürün sabit devre ve önceki bağlantıların sınırını büyütmez.'};
    if(data.connection==='reel'&&data.reelState!=='unwound')return {code:'coiled',commerce:false,tone:'danger',title:'Kablo makarasını tamamen açmadan yük bağlamayın',summary:'Sarılı veya kısmen sarılı makaranın izin verilen yükü ürün etiketine göre farklı olabilir. Tam açma ve üretici etiket doğrulaması tamamlanmadan sonuç veya ürün yolu açılmaz.'};
    if(data.environment==='outdoor'&&!data.outdoorRated)return {code:'outdoor',commerce:false,tone:'danger',title:'Dış ortam uygunluğu doğrulanmadı',summary:'Dış ortam, nem ve mekanik etki için üreticinin uygunluk işareti ve kullanım sınırı doğrulanmadan kabloyu kullanmayın.'};
    if(!data.earthRcdVerified)return {code:'protection',commerce:false,tone:'warn',title:'Topraklama ve kaçak akım korumasını doğrulayın',summary:'Topraklı fiş görünümü tek başına koruma kanıtı değildir. Özellikle dış ortam ve portatif alet kullanımında devre koruması yetkili test veya güvenilir kayıtla doğrulanmalıdır.'};
    if(!data.ratingVerified||!finite(m.currentA)||!finite(m.ratedW)||!finite(data.ratedA)||n(data.ratedA)<=0)return {code:'label',commerce:false,tone:'warn',title:'Etiket akımı ve üretici sınırı eksik',summary:'Kablo/makara üzerindeki amper veya watt sınırı okunmadan yalnız kesit tahminiyle güvenli kullanım sonucu verilmez.'};
    if(m.currentA>n(data.ratedA)+0.001||n(data.loadW)>m.ratedW+0.5)return {code:'overload',commerce:false,tone:'danger',title:'Yük etiket sınırını aşıyor',summary:`Yaklaşık ${m.currentA} A yük, doğrulanan ${n(data.ratedA)} A sınırını aşıyor. Daha büyük çoklayıcı eklemek çözüm değildir; yükü azaltın veya uygun sabit devre planlayın.`};
    if(!finite(data.crossSection)||n(data.crossSection)<=0||!finite(m.voltageDropPct))return {code:'drop_unknown',commerce:false,tone:'warn',title:'Uzunluk ve iletken kesitiyle gerilim düşümünü doğrulayın',summary:'Etiket sınırı aşılmasa bile uzun kabloda gerilim düşümü ve ısınma etkisi değerlendirilmelidir. Kesit yalnız kablo üzerindeki işaretten veya üretici belgesinden alınmalıdır.'};
    if(finite(targetDrop)&&targetDrop>0&&m.voltageDropPct>targetDrop)return {code:'drop',commerce:false,tone:'warn',title:'Girdiğiniz planlama gerilim düşümü hedefi aşılıyor',summary:`Yaklaşık düşüm %${m.voltageDropPct}. Bu değer bir uygunluk sertifikası değildir; kabloyu kısaltın, yükü azaltın veya yetkili elektrikçiyle uygun kesiti değerlendirin.`};
    if(data.existingSuitable)return {code:'no_buy',commerce:false,tone:'ok',title:'Mevcut uzatma düzeni yeterli — yeni ürün almayın',summary:`Yaklaşık ${m.currentA} A yük, doğrulanmış ${n(data.ratedA)} A etiket sınırı içinde; makara tam açık, fiziksel durum ve koruma şartları uygun. Yalnız daha yeni model için değiştirmeyin.`};
    if(confirmations&&['low_power','portable_tool'].includes(data.useClass))return {code:'qualified',commerce:true,tone:'warn',title:'Yalnız doğrulanmış eksik için ürün sınıfı açıldı',summary:'Tek parça, topraklı, doğru ortam sınıfında, etiket akımı ve iletken kesiti okunabilen; makara ise tam açılarak kullanılacak bir ürün sınıfını karşılaştırın.'};
    return {code:'verify',commerce:false,tone:'warn',title:'Önce mevcut düzeni gerçek yükle doğrulayın',summary:'Etiket, tam açma, fiziksel durum, topraklama/RCD ve gerilim düşümü hedefi tamamlanmadan yeni ürün yolu açılmaz.'};
  }

  function report(data){return {route:ROUTE,generatedAt:new Date().toISOString(),metrics:metrics(data),decision:decide(data),personalData:false,officialApproval:false};}
  function calendar(days=90){
    const start=new Date(Date.now()+Math.max(1,n(days)||90)*86400000);
    const end=new Date(start.getTime()+30*60000);
    const stamp=(date)=>date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Extension Cord Check//TR','BEGIN:VEVENT',`UID:extension-cord-${Date.now()}@alo186.com`,`DTSTAMP:${stamp(new Date())}`,`DTSTART:${stamp(start)}`,`DTEND:${stamp(end)}`,'SUMMARY:Uzatma kablosu ve makara güvenlik kontrolü','DESCRIPTION:Fiş, kablo, makara, etiket akımı, iletken kesiti, tam açma, topraklama-RCD ve gerçek yükü yeniden kontrol edin.','END:VEVENT','END:VCALENDAR'].join('\r\n');
  }
  function download(name,text,type){const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),0);}
  function read(doc){
    const value=(id)=>doc.getElementById(id)?.value;
    const checked=(id)=>Boolean(doc.getElementById(id)?.checked);
    return {danger:checked('danger'),maleToMale:checked('maleToMale'),physicalSafe:checked('physicalSafe'),mode:value('mode'),useClass:value('useClass'),connection:value('connection'),reelState:value('reelState'),environment:value('environment'),outdoorRated:checked('outdoorRated'),ratingVerified:checked('ratingVerified'),voltage:value('voltage'),loadW:value('loadW'),ratedA:value('ratedA'),lengthM:value('lengthM'),crossSection:value('crossSection'),targetDropPct:value('targetDropPct'),earthRcdVerified:checked('earthRcdVerified'),existingSuitable:checked('existingSuitable'),confirmNeed:checked('confirmNeed'),confirmLabel:checked('confirmLabel'),confirmAffiliate:checked('confirmAffiliate')};
  }
  function mount(doc){
    const form=doc.getElementById('extensionForm');if(!form)return;let last=null;
    form.addEventListener('submit',(event)=>{event.preventDefault();const data=read(doc);last=report(data);const d=last.decision;const m=last.metrics;const result=doc.getElementById('result');result.className=`result ${d.tone}`;result.innerHTML=`<h2>${d.title}</h2><p>${d.summary}</p><div class="metrics"><div class="metric"><span>Yaklaşık akım</span><strong>${Number.isFinite(m.currentA)?m.currentA+' A':'—'}</strong></div><div class="metric"><span>Etiket gücü</span><strong>${Number.isFinite(m.ratedW)?m.ratedW+' W':'—'}</strong></div><div class="metric"><span>Gerilim düşümü</span><strong>${Number.isFinite(m.voltageDropPct)?'%'+m.voltageDropPct:'—'}</strong></div><div class="metric"><span>Ticari yol</span><strong>${d.commerce?'Açık':'Kapalı'}</strong></div></div>`;doc.getElementById('affiliate').classList.toggle('hidden',!d.commerce);result.scrollIntoView({behavior:'smooth',block:'start'});});
    doc.getElementById('exportJson')?.addEventListener('click',()=>download('alo186-uzatma-kablosu-kontrolu.json',JSON.stringify(last||report(read(doc)),null,2),'application/json'));
    doc.getElementById('calendar')?.addEventListener('click',()=>download('alo186-uzatma-kablosu-kontrolu.ics',calendar(90),'text/calendar'));
  }
  return {ROUTE,RHO,metrics,decide,report,calendar,mount};
});