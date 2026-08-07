(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.Alo186PlanGrowthCore=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const DAY_MS=86400000;
const CATEGORY_LABELS={powerbank:'Powerbank',surge_strip:'Akım korumalı grup priz',mini_ups:'Modem/ONT mini UPS',emergency_light:'Acil aydınlatma',smoke_alarm:'Duman alarmı',power_station:'Power station',generator:'Jeneratör',inverter:'İnverter ve batarya',outlet_tester:'Priz/RCD test cihazı',smart_plug:'Akıllı priz ve enerji ölçer',ev_cable:'Type 2 EV kablosu',ups_battery:'UPS aküsü ve kartuşu'};
const OUTCOME_CATEGORY={powerbank:'product_selection',surge_strip:'protection',mini_ups:'backup_power',emergency_light:'product_selection',smoke_alarm:'product_selection',power_station:'backup_power',generator:'backup_power',inverter:'solar_storage',outlet_tester:'protection',smart_plug:'product_selection',ev_cable:'ev_charging',ups_battery:'backup_power'};
const PROFESSIONAL=new Set(['generator','inverter','outlet_tester']);
const REQUIREMENTS={
 powerbank:['Cihazın gerekli USB-C çıkış gücü (W)','Hedef gerçek şarj sayısı ve kullanılabilir Wh','Kablo ve şarj protokolü uyumu','Şişme, ısı ve port hasarı kontrolü'],
 surge_strip:['Toplam sürekli ve tepe yük (W/A)','Priz sayısı ve üretici etiket sınırı','Joule değeri, durum göstergesi ve aşırı akım koruması','İşlevsel topraklama ve doğrudan duvar bağlantısı'],
 mini_ups:['Modem/ONT gerilimi, polaritesi ve jak ölçüsü','Toplam watt ve hedef çalışma süresi','Geçişte yeniden başlama testi','Batarya ısısı ve gerçek runtime'],
 emergency_light:['Alan, aynı moddaki lümen ve hedef süre','Fiziksel düğme ve otomatik yanma ihtiyacı','Pil göstergesi ve düşük mod runtime','Gövde, kablo ve batarya güvenliği'],
 smoke_alarm:['Kat, uyuma odası ve ayrı uyuma alanı adedi','Ürün standardı ve tam model belgesi','Aylık test, düşük pil ve ömür sonu uyarısı','Yerleşim, bağlantı ve erişilebilirlik ihtiyacı'],
 power_station:['Sürekli W, tepe W ve hedef Wh','Saf sinüs, EPS geçişi ve bypass sınırı','AC/DC/solar giriş uyumu','Batarya kimyası, sıcaklık ve üretici yük onayı'],
 generator:['Kritik yük, sürekli ve kalkış gücü','Prime/standby sınıfı ve gerçek çalışma süresi','CO güvenliği, dış konum, yakıt ve bakım','Transfer, nötr-toprak ve yetkili kurulum planı'],
 inverter:['Sürekli/tepe W ve saf sinüs ihtiyacı','12/24/48 V DC sistem ve batarya akımı','BMS, DC sigorta, ayırıcı ve kablo kesiti','Sabit bağlantı ve yetkili proje sınırı'],
 outlet_tester:['Gösterge cihazının ölçebildiği ve ölçemediği alanlar','RCD nominal değeri ve üretici uyumu','Topraklama direnci, çevrim ve izolasyon için yetkili ölçüm','Hasarlı veya şüpheli prizde enerjili kullanıcı testi yasağı'],
 smart_plug:['Sürekli akım ve motor/kompresör kalkışı','W/kWh ölçüm çözünürlüğü ve kayıt süresi','Yerel kontrol veya bulut bağımlılığı','Gözetimsiz ısıtıcı kullanımı ve fiziksel ısı kontrolü'],
 ev_cable:['Araç ve istasyon soket tipi','Monofaze/trifaze ve 16/32 A sınıfı','Aracın gerçek AC şarj sınırı ve kablo uzunluğu','Konnektör, kilit, dış kılıf ve termal güvenlik'],
 ups_battery:['UPS tam modeli ve üretici kartuş/set kodu','Gerilim, Ah, kimya, terminal ve akü adedi','Seri/paralel set bütünlüğü','Self-test, gerçek runtime, şişme ve sıcaklık kontrolü']
};
const TOOL_ROUTES={powerbank:'/hesaplama/powerbank-usb-c-uygunluk/',surge_strip:'/hesaplama/akim-korumali-grup-priz-uygunluk/',mini_ups:'/hesaplama/modem-internet-yedekleme/',emergency_light:'/hesaplama/acil-aydinlatma-sure-uygunluk/',smoke_alarm:'/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/',power_station:'/hesaplama/power-station-kapasite-eps-uygunluk/',generator:'/hesaplama/jenerator-gucu-secimi/',inverter:'/hesaplama/inverter-uygunluk/',outlet_tester:'/karar-motoru',smart_plug:'/hesaplama/akilli-priz-enerji-olcer-uygunluk/',ev_cable:'/hesaplama/ev-sarj-kablosu-uygunluk/',ups_battery:'/hesaplama/ups-aku-degisim-uygunluk/'};
function safeArray(v){return Array.isArray(v)?v:[];}
function asDate(v){const d=v instanceof Date?v:new Date(v);return Number.isFinite(d.getTime())?d:null;}
function seasonKey(dateValue=new Date()){const d=asDate(dateValue)||new Date(),m=d.getMonth()+1;if([6,7,8].includes(m))return'summer';if([12,1,2].includes(m))return'winter';if([9,10,11].includes(m))return'storm';return'spring';}
function seasonalActions(dateValue=new Date()){
 const key=seasonKey(dateValue),map={
  summer:[
   {id:'summer-ev-heat',title:'EV kablosu ve prizi ısınma kontrolü',detail:'Yüksek ortam sıcaklığında konnektör, priz ve kablo termal belirtilerini kontrol edin; yeni kablo almadan önce gerçek darboğazı ayırın.',route:'/haberler/ev-sarj-kablosu-prizi-isiniyor-ne-yapilmali',category:'ev_cable',mode:'free'},
   {id:'summer-inverter-derating',title:'GES inverter sıcaklık ve havalandırma kontrolü',detail:'Öğle güç düşüşünü clipping, şebeke limiti ve temperature derating olarak ayırın.',route:'/haberler/ges-inverter-sicakta-guc-dusuruyor-temperature-derating',category:'inverter',mode:'free'},
   {id:'summer-backup',title:'Yaz kesintisi için gerçek yedek güç süresi',detail:'Klima dışındaki kritik yükleri ayırın; power station veya UPS seçmeden önce W, Wh ve tepe gücü hesaplayın.',route:'/hesaplama/yedek-guc-cozum-secici/',category:'power_station',mode:'qualified'}],
  winter:[
   {id:'winter-lfp',title:'LiFePO₄ bataryada soğuk şarj kontrolü',detail:'Minimum şarj sıcaklığı, BMS kesmesi ve ısıtıcı davranışı doğrulanmadan bataryayı şarja zorlamayın.',route:'/haberler/lifepo4-batarya-sogukta-sarj-edilir-mi',category:'inverter',mode:'free'},
   {id:'winter-ups',title:'UPS aküsü ve gerçek runtime testi',detail:'Takvim yaşından önce self-test, yük altındaki çalışma süresi ve tam kartuş uyumunu kontrol edin.',route:'/hesaplama/ups-aku-degisim-uygunluk/',category:'ups_battery',mode:'qualified'},
   {id:'winter-generator',title:'Jeneratör sezon öncesi güvenli çalışma provası',detail:'Yakıt, yağ, dış konum, CO güvenliği ve transfer planını yük vermeden önce doğrulayın.',route:'/hesaplama/elektrik-kesintisi-tatbikati/',category:'generator',mode:'professional'}],
  storm:[
   {id:'storm-spd',title:'Parafudr ve bağlantı yolu kontrolü',detail:'Yalnız kA etiketine değil, Uc/Up, yedek sigorta ve kısa bağlantı güzergâhına bakın.',route:'/haberler/parafudr-baglanti-kablosu-neden-kisa-olmali',category:'surge_strip',mode:'free'},
   {id:'storm-outage',title:'Kesinti günlüğü ve cihaz hasarı kanıtı',detail:'Kesinti zamanını, süreyi ve güvenli gözlemi kaydedin; cihaz hasarında 30 günlük resmî süreyi kaçırmayın.',route:'/hesaplama/kesinti-gunlugu/',category:'emergency_light',mode:'free'},
   {id:'storm-light',title:'Acil aydınlatma gerçek süre testi',detail:'En parlak mod değil, kullanılacak moddaki lümen ve runtime değerini doğrulayın.',route:'/hesaplama/acil-aydinlatma-sure-uygunluk/',category:'emergency_light',mode:'qualified'}],
  spring:[
   {id:'spring-rcd',title:'RCD test ve profesyonel ölçüm planı',detail:'Test düğmesi ile açma süresi/akımı ölçümünü birbirinden ayırın; tekrar eden açmada ürünü büyütmeyin.',route:'/haberler/kacak-akim-rolesi-test-dugmesi-ne-siklikla',category:'outlet_tester',mode:'professional'},
   {id:'spring-ges',title:'GES bakım ve havalandırma hazırlığı',detail:'İnverter açıklıkları, termal olaylar, izolasyon ve string kayıtlarını sıcak dönem öncesinde kontrol edin.',route:'/hesaplama/ekipman-bakim-plani/',category:'inverter',mode:'professional'},
   {id:'spring-ev',title:'EV şarj güç ve yük yönetimi kontrolü',detail:'Araç AC sınırı, faz, ana güç ve dinamik yük yönetimini yaz yükleri artmadan doğrulayın.',route:'/hesaplama/ev-sarj-uygunluk/',category:'ev_cable',mode:'qualified'}]
 };
 return{key,actions:map[key]};
}
function latestProductCategory(snapshot={}){
 const saved=snapshot.savedDecision&&CATEGORY_LABELS[snapshot.savedDecision.category]?snapshot.savedDecision:null;
 if(saved)return saved.category;
 const reviews=safeArray(snapshot.reviews).filter(r=>CATEGORY_LABELS[r.category]).sort((a,b)=>String(b.createdAt||'').localeCompare(String(a.createdAt||'')));
 return reviews[0]?reviews[0].category:null;
}
function recentOutcomeForCategory(snapshot,category,now=new Date()){
 const target=OUTCOME_CATEGORY[category],cutoff=now.getTime()-90*DAY_MS;
 return safeArray(snapshot.outcomes).filter(r=>r&&r.category===target&&asDate(r.createdAt)&&asDate(r.createdAt).getTime()>=cutoff).sort((a,b)=>Date.parse(b.createdAt)-Date.parse(a.createdAt))[0]||null;
}
function procurementBrief(snapshot={},nowValue=new Date()){
 const now=asDate(nowValue)||new Date(),category=latestProductCategory(snapshot);
 if(!category)return{available:false,category:null,label:'Henüz teknik alım kartı yok',status:'empty',requirements:[],route:'/akilli-urun-secimi',reviewAt:null,affiliateAllowed:false,professional:false};
 const outcome=recentOutcomeForCategory(snapshot,category,now),professional=PROFESSIONAL.has(category),label=CATEGORY_LABELS[category];
 const noBuy=Boolean(outcome&&(outcome.purchase==='no_purchase'||outcome.purchase==='existing'||['maintenance','existing_equipment','official_channel'].includes(outcome.action))&&outcome.outcome==='resolved');
 const blocked=Boolean(outcome&&(outcome.outcome==='safety'||outcome.outcome==='unresolved'||outcome.recurrence==='multiple'));
 const saved=snapshot.savedDecision&&snapshot.savedDecision.category===category?snapshot.savedDecision:null;
 const reviewAt=saved&&asDate(saved.reviewAt)?asDate(saved.reviewAt).toISOString():new Date(now.getTime()+30*DAY_MS).toISOString();
 let status='ready',route=`/akilli-urun-secimi?kategori=${encodeURIComponent(category)}`,affiliateAllowed=true;
 if(noBuy){status='no_buy';route=TOOL_ROUTES[category];affiliateAllowed=false;}
 else if(blocked||professional){status='professional';route=`/kurumsal-elektrik-surekliligi-on-degerlendirme?source=technical_brief&category=${encodeURIComponent(category)}`;affiliateAllowed=false;}
 return{available:true,category,label,status,requirements:REQUIREMENTS[category]||[],toolRoute:TOOL_ROUTES[category],route,reviewAt,affiliateAllowed,professional:status==='professional',disclosure:affiliateAllowed?'Ürün merkezindeki haricî bağlantılar satış ortaklığı bağlantısı olabilir; fiyat, stok, puan, satıcı ve garanti ilgili mağazada doğrulanır.':'Bu sonuç ticari ürün yönlendirmesi açmaz.'};
}
function sharePayload(plan={},seasonal=seasonalActions(),brief={available:false}){
 const tasks=safeArray(plan.tasks).slice(0,3).map((t,i)=>`${i+1}. ${String(t.title||'Kontrol').slice(0,120)}`);
 const season=seasonal.actions.slice(0,2).map((a,i)=>`${i+1}. ${a.title}`);
 const briefLine=brief.available?`Teknik alım kartı: ${brief.label} — ${brief.status==='no_buy'?'yeni ürün önerilmiyor':brief.status==='professional'?'profesyonel doğrulama gerekli':'teknik minimumları doğrula'}`:'Teknik alım kartı: henüz oluşturulmadı';
 return{title:'ALO186 Elektrik Planım',text:['ALO186 kişisel verisiz elektrik planı','',...(tasks.length?['Öncelikler:',...tasks]:['Bugün için açık görev görünmüyor.']),'','Mevsimsel hazırlık:',...season,'',briefLine,'','ALO186 EDAŞ veya kamu kurumu değildir. Acil tehlikede 112, şebeke arızasında 186 veya resmî EDAŞ kanalı.'].join('\n'),url:'https://alo186.com/hesaplama/elektrik-planim/'};
}
function reviewRecord(action,days=30,nowValue=new Date()){
 const now=asDate(nowValue)||new Date(),safeDays=[7,30,90,180].includes(Number(days))?Number(days):30;
 return{id:`seasonal-${action.id}-${now.toISOString().slice(0,10)}`,actionId:action.id,category:action.category,createdAt:now.toISOString(),reviewAt:new Date(now.getTime()+safeDays*DAY_MS).toISOString(),days:safeDays,version:1};
}
function sanitizeReviews(records,nowValue=new Date()){
 const now=asDate(nowValue)||new Date(),cutoff=now.getTime()-180*DAY_MS,seen=new Set();return safeArray(records).filter(r=>r&&r.version===1&&typeof r.id==='string'&&CATEGORY_LABELS[r.category]&&asDate(r.createdAt)&&asDate(r.reviewAt)&&asDate(r.createdAt).getTime()>=cutoff).sort((a,b)=>Date.parse(b.createdAt)-Date.parse(a.createdAt)).filter(r=>{if(seen.has(r.id))return false;seen.add(r.id);return true;}).slice(0,6);
}
return{CATEGORY_LABELS,OUTCOME_CATEGORY,REQUIREMENTS,TOOL_ROUTES,seasonKey,seasonalActions,latestProductCategory,procurementBrief,sharePayload,reviewRecord,sanitizeReviews};
});
