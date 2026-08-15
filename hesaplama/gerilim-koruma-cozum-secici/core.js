(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186VoltageProtectionSelector=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const solutions={
    emergency:{label:'Acil güvenlik ve enerjiyi güvenli biçimde ayırma',note:'Duman, yanık kokusu, ark, elektrik çarpması veya ısınan pano ürün seçimiyle çözülemez.',nextStepUrl:'https://alo186.com/karar-motoru/',nextStepLabel:'Acil yönlendirmeyi aç',productCategory:null},
    medical_plan:{label:'Üretici onaylı profesyonel güç kalitesi planı',note:'Tıbbi veya yaşam destek cihazında genel ürün önerisi güvenli değildir.',nextStepUrl:'https://alo186.com/hesaplama/yedek-guc-cozum-secici/',nextStepLabel:'Profesyonel yedek güç ön değerlendirmesini aç',productCategory:null},
    neutral_risk:{label:'Nötr / bağlantı arızası için acil teknik kontrol',note:'Bazı lambaların aşırı parlak, bazılarının sönük olması nötr veya bağlantı problemiyle ilişkili olabilir.',nextStepUrl:'https://alo186.com/karar-motoru/',nextStepLabel:'186 mı, elektrikçi mi kararını aç',productCategory:null},
    utility_report:{label:'Dağıtım şirketi kaydı + tesisat doğrulaması',note:'Bina veya komşularda görülen gerilim/kesinti olayı önce resmî dağıtım kanalında kayda alınmalıdır.',nextStepUrl:'https://alo186.com/edas-bul',nextStepLabel:'Bölgemdeki EDAŞ kanalını bul',productCategory:null},
    installation_check:{label:'Bina / daire iç tesisat kontrolü',note:'Tek oda, tek devre veya bina içi sınırlı sorunlarda ürün almadan önce bağlantı ve koruma ölçümü gerekir.',nextStepUrl:'https://alo186.com/karar-motoru/',nextStepLabel:'Güvenli kontrol sırasını aç',productCategory:null},
    device_service:{label:'Cihaz veya adaptör teknik servisi',note:'Sorun yalnız bir cihazda ve şebeke ölçümü normalse, koruma ürünü yerine cihaz/adaptör incelemesi öne çıkar.',nextStepUrl:'https://alo186.com/haberler/parafudr-gerilim-koruma-rolesi-farki',nextStepLabel:'Koruma cihazlarının görev farkını öğren',productCategory:null},
    spd_layers:{label:'Katmanlı aşırı gerilim koruması',note:'Çok kısa süreli yıldırım veya anahtarlama darbelerinde SPD/parafudr kademeleri değerlendirilir.',nextStepUrl:'https://alo186.com/hesaplama/parafudr-risk-testi/',nextStepLabel:'Parafudr risk testini aç',productCategory:'surge_strip'},
    ups_avr:{label:'UPS / AVR ile kesintisiz elektronik yük koruması',note:'Bilgisayar, modem ve ağ cihazı yeniden başlıyorsa geçiş süresi, W/VA ve AVR aralığı birlikte değerlendirilir.',nextStepUrl:'https://alo186.com/hesaplama/yedek-guc-cozum-secici/',nextStepLabel:'UPS ve yedek güç çözümünü karşılaştır',productCategory:null},
    voltage_regulator:{label:'Tek cihaz için otomatik voltaj regülasyonu ön değerlendirmesi',note:'Yetkili ölçümle doğrulanmış, tekrarlayan düşük/yüksek gerilimde yalnız monofaze fişli elektronik yük için düşünülebilir.',nextStepUrl:'https://alo186.com/haberler/parafudr-gerilim-koruma-rolesi-farki',nextStepLabel:'Regülatör, röle, SPD ve UPS farkını aç',productCategory:null},
    voltage_monitoring:{label:'Gerilim izleme ve profesyonel koruma tasarımı',note:'Birden fazla cihazı veya sabit tesisatı etkileyen sürekli düşük/yüksek gerilim ürün aramasından önce ölçüm ve kayıt gerektirir.',nextStepUrl:'https://alo186.com/haberler/parafudr-gerilim-koruma-rolesi-farki',nextStepLabel:'Gerilim rölesi ve SPD farkını öğren',productCategory:null},
    diagnose_first:{label:'Önce olayın süresini ve kapsamını ayırın',note:'Belirti tek başına doğru cihazı seçmeye yetmez; şebeke, tesisat ve cihaz kaynakları ayrılmalıdır.',nextStepUrl:'https://alo186.com/karar-motoru/',nextStepLabel:'Belirtiye göre güvenli yönlendirmeyi aç',productCategory:null}
  };
  const allowed={symptom:['outage_restart','dim','bright','mixed','flicker','surge','single_device','unknown'],duration:['instant','seconds','minutes','continuous','unknown'],scope:['one_device','one_room','whole_home','building','neighbors'],measurement:['none','normal','low','high','fluctuating'],loadType:['electronics','motor','fixed','unknown'],powerBand:['under300','under1000','over1000','unknown'],phase:['single','three','unknown'],continuity:['none','must_stay_on','brief_ok'],existing:['none','surge_strip','panel_spd','voltage_relay','ups_avr','unknown']};
  function enumValue(value,key,fallback){return allowed[key].includes(value)?value:fallback;}
  function analyze(raw){
    const input={symptom:enumValue(raw.symptom,'symptom','unknown'),duration:enumValue(raw.duration,'duration','unknown'),scope:enumValue(raw.scope,'scope','whole_home'),measurement:enumValue(raw.measurement,'measurement','none'),loadType:enumValue(raw.loadType,'loadType','unknown'),powerBand:enumValue(raw.powerBand,'powerBand','unknown'),phase:enumValue(raw.phase,'phase','unknown'),continuity:enumValue(raw.continuity,'continuity','none'),existing:enumValue(raw.existing,'existing','unknown'),emergency:Boolean(raw.emergency),medical:Boolean(raw.medical)};
    const reasons=[],limits=[],checks=[];
    let recommendation='diagnose_first';
    if(input.emergency){recommendation='emergency';reasons.push('Duman, yanık kokusu, ark, çarpılma veya anormal ısınma doğrudan can ve yangın riskidir.','Bu durumda ürün karşılaştırması yapmak güvenli değildir.');}
    else if(input.medical){recommendation='medical_plan';reasons.push('Tıbbi veya yaşam destek cihazlarında genel UPS, regülatör ya da priz tipi koruma önerisi yeterli değildir.','Cihaz üreticisinin güç kalitesi, transfer süresi, alarm ve yedek süre gereksinimi doğrulanmalıdır.');}
    else if(input.symptom==='mixed'){recommendation='neutral_risk';reasons.push('Aynı anda bazı lambaların aşırı parlak, bazılarının sönük olması olağan bir regülasyon ihtiyacından farklıdır.','Nötr veya bağlantı arızası olasılığı nedeniyle hassas cihazlar korunmalı ve yetkili kontrol geciktirilmemelidir.');}
    else if(['building','neighbors'].includes(input.scope)){recommendation='utility_report';reasons.push('Belirtinin bina veya komşular düzeyinde görülmesi dağıtım şebekesi kaynağı olasılığını artırır.','Resmî kayıt numarası, olay zamanı ve etkilenen kapsam sonraki teknik incelemeyi güçlendirir.');}
    else if(input.scope==='one_room'){recommendation='installation_check';reasons.push('Tek oda veya tek devreyle sınırlı sorun, genel şebeke koruma ürününden önce iç tesisat kontrolü gerektirir.');}
    else if(input.symptom==='single_device'&&input.measurement==='normal'){recommendation='device_service';reasons.push('Sorun yalnız bir cihazda ve güvenli ölçüm sonucu normalse cihaz, adaptör veya bağlantı kablosu öncelikli şüphedir.');}
    else if(input.symptom==='surge'||(input.duration==='instant'&&['flicker','bright','dim'].includes(input.symptom))){recommendation='spd_layers';reasons.push('Çok kısa süreli olaylar, sürekli düşük/yüksek gerilimden farklı bir transient darbe sınıfıdır.','Pano tipi SPD ve cihaz yakını koruma birbirinin yerine değil, koordineli kademeler olarak değerlendirilir.');}
    else if(input.symptom==='outage_restart'||input.continuity==='must_stay_on'){recommendation='ups_avr';reasons.push('Elektronik cihazın yeniden başlaması, kesinti/geçiş süresi ile yedek enerji ihtiyacını birlikte gündeme getirir.','Line-interactive UPS’te AVR, orta seviyeli gerilim sapmalarını bataryaya geçmeden düzeltebilir; model aralığı ayrıca doğrulanır.');}
    else if(['low','high','fluctuating'].includes(input.measurement)){
      const safePlugRegulator=input.scope==='one_device'&&input.loadType==='electronics'&&input.phase==='single'&&['under300','under1000'].includes(input.powerBand);
      if(safePlugRegulator){recommendation='voltage_regulator';reasons.push('Yetkili ölçüm/kayıt, tek monofaze fişli elektronik yükte tekrarlayan gerilim sapması olduğunu gösteriyor.','Regülatörün sürekli VA/W sınırı ve giriş-çıkış aralığı cihaz etiketine göre doğrulanmalıdır.');}
      else{recommendation='voltage_monitoring';reasons.push('Sürekli veya tekrarlayan düşük/yüksek gerilim birden fazla yükü, motoru ya da sabit tesisatı etkileyebilir.','Eşik, gecikme, kontaktör, faz/nötr ve kısa devre koordinasyonu ölçümle tasarlanmalıdır.');}
    }else if(input.symptom==='single_device'){recommendation='device_service';reasons.push('Tek cihazdaki belirti, şebeke koruma ürünü almadan önce cihaz ve adaptör incelemesi gerektirir.');}
    else{recommendation='diagnose_first';reasons.push('Süre, kapsam veya güvenli ölçüm sonucu bilinmediği için cihaz sınıfı seçmek erken olur.','Önce komşu/bina etkisi, devre kapsamı ve olay süresi ayrılmalıdır.');}
    const professionalRequired=['emergency','medical_plan','neutral_risk','utility_report','installation_check','voltage_monitoring'].includes(recommendation)||input.phase!=='single'||input.loadType==='fixed'||input.loadType==='motor'||input.powerBand==='over1000';
    let commercialAllowed=false,productCategory=null;
    if(recommendation==='spd_layers'&&input.scope==='one_device'&&input.phase==='single'&&input.loadType==='electronics'&&['under300','under1000'].includes(input.powerBand)&&['none','unknown'].includes(input.existing)){commercialAllowed=true;productCategory='surge_strip';}
    if(input.existing==='surge_strip')limits.push('Mevcut priz tipi ürünün durum göstergesi, etiket değerleri ve kullanım ömrü kontrol edilmeden yenisi önerilmez.');
    if(input.existing==='panel_spd')limits.push('Pano SPD’si bulunması cihaz yakını koruma ihtiyacını otomatik olarak ortadan kaldırmaz; koordinasyon doğrulanır.');
    if(input.existing==='voltage_relay')limits.push('Gerilim rölesi transient yıldırım darbesini SPD gibi sınırlamaz.');
    if(input.existing==='ups_avr')limits.push('UPS/AVR, bina nötr arızası veya bütün tesisat için koruma tasarımının yerine geçmez.');
    if(recommendation==='spd_layers')limits.push('Priz tipi akım korumalı ürün, pano tipi SPD ve uygun PE/topraklama düzeninin yerine geçmez.','SPD sürekli yüksek/düşük gerilimi regülatör veya izleme rölesi gibi düzeltmez.');
    else if(recommendation==='voltage_regulator')limits.push('Regülatör elektrik kesintisinde yedek enerji sağlamaz.','Motor, kompresör, sabit tesisat veya bilinmeyen güçte genel ürün seçimi yapılmaz.');
    else if(recommendation==='ups_avr')limits.push('UPS kapasitesi W, VA, çalışma süresi, dalga biçimi ve transfer davranışıyla doğrulanır.','UPS pano tipi SPD, gerilim izleme rölesi veya tesisat ölçümünün yerine geçmez.');
    else if(recommendation==='utility_report')limits.push('ALO186 arıza kaydı almaz; kullanıcıyı bölgesindeki resmî dağıtım kanalına yönlendirir.');
    checks.push('Belirtinin tek cihazda mı, tek devrede mi, tüm binada mı ve komşularda mı görüldüğünü doğrulayın.','Ürün seçmeden önce olayın anlık darbe mi, sürekli gerilim sapması mı, kesinti mi olduğunu ayırın.');
    if(recommendation==='spd_layers')checks.push('SPD tipi, Uc, Up, In/Imax veya Iimp, kutup düzeni ve PE bağlantısını yetkili kişi doğrulasın.');
    if(recommendation==='voltage_regulator')checks.push('Cihazın sürekli W/VA değeri, başlangıç akımı ve regülatörün giriş/çıkış aralığını tam model dokümanında kontrol edin.');
    if(recommendation==='ups_avr')checks.push('Bağlı yükün kapanmaması gerekiyorsa transfer süresini ve gerçek runtime eğrisini doğrulayın.');
    if(['neutral_risk','installation_check','voltage_monitoring'].includes(recommendation))checks.push('Pano veya gerilim altındaki bağlantılara kullanıcı müdahalesi yapılmamalıdır.');
    if(recommendation==='utility_report')checks.push('Olay saatini ve resmî kayıt numarasını saklayın; komşu/bina etkisini kayda ekleyin.');
    const riskLevel={emergency:'Kritik',medical_plan:'Kritik',neutral_risk:'Yüksek',utility_report:'Yüksek',installation_check:'Yüksek',voltage_monitoring:'Yüksek',spd_layers:'Orta',ups_avr:'Orta',voltage_regulator:'Orta',device_service:'Düşük–orta',diagnose_first:'Belirsiz'}[recommendation];
    const distributionReport=['utility_report','neutral_risk'].includes(recommendation)&&['building','neighbors'].includes(input.scope);
    return {input,recommendation,solution:solutions[recommendation],reasons,limits,checks,riskLevel,professionalRequired,distributionReport,commercialAllowed,productCategory};
  }
  return {solutions,analyze};
});
