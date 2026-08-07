(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186DocumentationGrowthCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const schemaVersion=1;
  const reviewStorageKey='alo186:documentation-reviews:v1';
  const reviewLimit=6;
  const reviewDays=14;
  const retentionDays=45;
  const dayMs=86400000;

  const categorySpecs={
    powerbank:{label:'Powerbank',supplier:'portable',fields:[
      {id:'capacity_mah',label:'Nominal kapasite',attribute:'capacityMah',critical:true,question:'Nominal kapasite kaç mAh ve hücre enerjisi kaç Wh olarak etiketlenmiştir?'},
      {id:'energy_wh',label:'Enerji kapasitesi',attribute:'energyWh',critical:false,question:'Bataryanın nominal enerji değeri kaç Wh olarak belirtilmiştir?'},
      {id:'max_output_w',label:'Azami USB-C çıkışı',attribute:'maxOutputW',critical:true,question:'Tek port ve toplam kullanımda desteklenen USB-C PD çıkış profilleri ile azami güç nedir?'},
      {id:'usb_c_ports',label:'USB-C port sayısı',attribute:'usbCPorts',critical:false,question:'Kaç USB-C portu vardır ve çoklu port kullanımında güç nasıl paylaşılır?'},
      {id:'wireless',label:'Kablosuz şarj',attribute:'wireless',critical:false,question:'Kablosuz şarj destekleniyor mu; destekleniyorsa azami güç ve uyumlu standart nedir?'},
      {id:'display',label:'Durum göstergesi',attribute:'display',critical:false,question:'Kalan kapasite veya güç bilgisi ekran ya da göstergeyle görüntüleniyor mu?'}
    ]},
    surge_strip:{label:'Akım korumalı grup priz',supplier:'safety',fields:[
      {id:'outlets',label:'Priz sayısı',attribute:'outlets',critical:true,question:'Kullanılabilir priz sayısı ve prizlerin topraklı bağlantı yapısı nedir?'},
      {id:'joules',label:'Darbe enerjisi',attribute:'joules',critical:true,question:'Ürünün joule cinsinden darbe enerjisi değeri ve ilgili test standardı nedir?'},
      {id:'max_current_a',label:'Nominal sürekli akım',attribute:'maxCurrentA',critical:true,question:'Ürünün etiketindeki nominal sürekli akım değeri kaç amperdir?'},
      {id:'max_power_w',label:'Azami güç',attribute:'maxPowerW',critical:true,question:'230 V kullanım için etiketlenen azami sürekli güç kaç wattır?'},
      {id:'usb_ports',label:'USB çıkışı',attribute:'usbPorts',critical:false,question:'USB çıkışı varsa port sayısı, toplam güç ve desteklenen hızlı şarj protokolleri nelerdir?'},
      {id:'cable_m',label:'Kablo uzunluğu',attribute:'cableM',critical:false,question:'Kablo uzunluğu ve iletken kesiti nedir?'}
    ]},
    mini_ups:{label:'Modem / ONT mini UPS',supplier:'ups',fields:[
      {id:'output_voltage',label:'Çıkış gerilimi',critical:true,question:'Desteklenen 5 V, 9 V ve 12 V çıkışların her biri için azami akım değeri nedir?'},
      {id:'polarity_jack',label:'Jak ve polarite',critical:true,question:'DC jak ölçüleri ve merkez artı/eksi polarite bilgisi nedir?'},
      {id:'runtime_method',label:'Çalışma süresi yöntemi',critical:true,question:'Beyan edilen çalışma süresi hangi watt yükünde ve hangi çıkış geriliminde ölçülmüştür?'},
      {id:'transfer_behavior',label:'Geçiş davranışı',critical:true,question:'Şebeke kesildiğinde bağlı cihaz yeniden başlatmadan çalışmaya devam eder mi?'},
      {id:'battery_energy',label:'Batarya enerjisi',critical:false,question:'Bataryanın nominal Wh değeri ve kullanılan hücre kimyası nedir?'}
    ]},
    emergency_light:{label:'Acil aydınlatma',supplier:'safety',fields:[
      {id:'lumens_mode',label:'Aynı moddaki lümen',critical:true,question:'Her parlaklık modu için lümen değeri ayrı ayrı nedir?'},
      {id:'runtime_mode',label:'Aynı moddaki süre',critical:true,question:'Her parlaklık modu için beyan edilen çalışma süresi kaç saattir?'},
      {id:'auto_on',label:'Kesintide otomatik yanma',critical:false,question:'Şebeke kesildiğinde otomatik yanma özelliği var mı ve nasıl devreye girer?'},
      {id:'battery_status',label:'Pil göstergesi',critical:false,question:'Pil doluluk ve düşük pil durumu kullanıcıya nasıl gösterilir?'},
      {id:'environment',label:'Ortam sınırları',critical:true,question:'IP sınıfı, çalışma sıcaklığı ve iç/dış ortam kullanım sınırları nelerdir?'}
    ]},
    smoke_alarm:{label:'Duman alarmı',supplier:'safety',fields:[
      {id:'standard',label:'Ürün standardı',critical:true,question:'Ürünün EN 14604 uygunluk belgesinin kapsamı ve belge numarası nedir?'},
      {id:'sensor',label:'Sensör türü',critical:true,question:'Algılama teknolojisi fotoelektrik mi ve hangi yanlış alarm azaltma özellikleri vardır?'},
      {id:'service_life',label:'Ürün ömrü',critical:true,question:'Üretim tarihi, ürün ömrü ve ömür sonu uyarısı nasıl belirtilir?'},
      {id:'battery_warning',label:'Pil ve uyarı',critical:true,question:'Pil tipi, düşük pil uyarısı, test düğmesi ve susturma işlevi nelerdir?'},
      {id:'interconnect',label:'Birbirine bağlantı',critical:false,question:'Birden fazla alarm kablolu veya kablosuz olarak birbirine bağlanabilir mi?'}
    ]},
    power_station:{label:'Power station',supplier:'portable',fields:[
      {id:'usable_wh',label:'Kullanılabilir enerji',critical:true,question:'Nominal Wh yanında AC çıkışta ölçülen kullanılabilir enerji ve test yükü nedir?'},
      {id:'continuous_surge',label:'Sürekli ve tepe güç',critical:true,question:'Sürekli AC güç, tepe güç, tepe süresi ve aşırı yük kapanma davranışı nedir?'},
      {id:'waveform',label:'Dalga biçimi',critical:true,question:'AC çıkış saf sinüs mü; THD değeri hangi yük koşulunda ölçülmüştür?'},
      {id:'eps_transfer',label:'EPS geçişi',critical:true,question:'EPS/UPS modu varsa geçiş süresi, bypass limiti ve desteklenmeyen yükler nelerdir?'},
      {id:'battery_chemistry',label:'Batarya kimyası',critical:false,question:'Batarya kimyası, çevrim ömrü beyanı ve bu beyanın DoD/sıcaklık koşulları nelerdir?'},
      {id:'pv_input',label:'PV giriş sınırları',critical:false,question:'PV girişinde Voc, Vmp, akım, güç ve konektör sınırları nelerdir?'}
    ]},
    smart_plug:{label:'Akıllı priz ve enerji ölçer',supplier:'safety',fields:[
      {id:'continuous_current',label:'Sürekli akım',critical:true,question:'Nominal ve uzun süreli sürekli akım sınırı kaç amperdir?'},
      {id:'motor_permission',label:'Motor/kompresör sınırı',critical:true,question:'Motor veya kompresör yükleri için üreticinin izin verdiği kalkış akımı ve kullanım sınırı nedir?'},
      {id:'meter_accuracy',label:'Ölçüm doğruluğu',critical:true,question:'W ve kWh ölçüm doğruluğu, çözünürlüğü ve minimum ölçülebilir güç nedir?'},
      {id:'history',label:'Geçmiş kayıt',critical:false,question:'Geçmiş tüketim kaydı ne kadar süre tutulur ve dışa aktarılabilir mi?'},
      {id:'local_cloud',label:'Yerel/bulut çalışma',critical:false,question:'İnternet olmadan yerel kontrol mümkün mü; hesap veya bulut servisi zorunlu mu?'}
    ]},
    ev_cable:{label:'Type 2 EV şarj kablosu',supplier:'ev',fields:[
      {id:'phase_current',label:'Faz ve akım',critical:true,question:'Kablo monofaze/trifaze hangi akım ve güç sınıflarını destekler?'},
      {id:'connector_standard',label:'Konnektör standardı',critical:true,question:'Araç ve istasyon uçlarının Type 2 / IEC 62196 uyum bilgisi nedir?'},
      {id:'length_section',label:'Uzunluk ve kesit',critical:true,question:'Kablo uzunluğu, iletken kesitleri ve sıcaklık dayanım sınıfı nedir?'},
      {id:'ip_temperature',label:'IP ve sıcaklık',critical:true,question:'Bağlı ve kapaklı durumda IP sınıfı ile çalışma/saklama sıcaklıkları nelerdir?'},
      {id:'lock_cycle',label:'Kilit ve çevrim ömrü',critical:false,question:'Konnektör kilidi, mekanik takma-çıkarma çevrimi ve garanti dışı kullanım sınırları nelerdir?'}
    ]},
    ups_battery:{label:'UPS aküsü / kartuşu',supplier:'ups',fields:[
      {id:'exact_compatibility',label:'Tam model uyumu',critical:true,question:'Hangi UPS tam modelleri ve hangi üretici kartuş/set kodlarıyla resmî olarak uyumludur?'},
      {id:'voltage_capacity',label:'Gerilim ve kapasite',critical:true,question:'Blok gerilimi, Ah kapasitesi, toplam string gerilimi ve akü adedi nedir?'},
      {id:'chemistry_terminal',label:'Kimya ve terminal',critical:true,question:'Batarya kimyası, terminal tipi, fiziksel ölçüler ve montaj yönü nedir?'},
      {id:'replacement_policy',label:'Set değiştirme politikası',critical:true,question:'Tek blok değişimine izin veriliyor mu, yoksa bütün kartuş/string birlikte mi değiştirilmelidir?'},
      {id:'temperature_life',label:'Sıcaklık ve ömür',critical:false,question:'Tasarım ömrü hangi sıcaklık ve şarj koşullarında beyan edilmiştir?'}
    ]},
    generator:{label:'Taşınabilir jeneratör',supplier:'ups',professionalOnly:true,fields:[
      {id:'continuous_starting',label:'Sürekli ve kalkış gücü',critical:true,question:'Sürekli ve kalkış gücü, güç faktörü ve izin verilen yük adımı nedir?'},
      {id:'co_safety',label:'CO güvenliği',critical:true,question:'Karbonmonoksit algılama/kapatma sistemi ve açık alan mesafe talimatı nedir?'},
      {id:'earthing_neutral',label:'Nötr-toprak düzeni',critical:true,question:'Nötr-toprak bağlantı düzeni ve transfer sistemiyle kullanım talimatı nedir?'},
      {id:'fuel_runtime',label:'Yakıt ve süre',critical:false,question:'Farklı yük yüzdelerinde yakıt tüketimi ve çalışma süresi nedir?'},
      {id:'service',label:'Servis planı',critical:false,question:'Bakım aralığı, yedek parça ve yetkili servis kapsamı nedir?'}
    ]},
    inverter:{label:'İnverter ve batarya sistemi',supplier:'solar',professionalOnly:true,fields:[
      {id:'continuous_surge',label:'Sürekli ve tepe güç',critical:true,question:'Sürekli/tepe güç, tepe süresi ve desteklenen yük türleri nelerdir?'},
      {id:'dc_window',label:'DC giriş penceresi',critical:true,question:'DC gerilim, akım, BMS ve kısa devre koruma sınırları nelerdir?'},
      {id:'waveform_thd',label:'Dalga biçimi ve THD',critical:true,question:'Çıkış dalga biçimi ve THD hangi yükte doğrulanmıştır?'},
      {id:'transfer_bypass',label:'Transfer ve bypass',critical:true,question:'Transfer süresi, bypass gücü ve ayrı kaynak/topraklama koşulları nelerdir?'},
      {id:'compliance',label:'Standart kapsamı',critical:false,question:'Ürün uygunluk belgeleri hangi tam model ve çalışma modlarını kapsar?'}
    ]},
    outlet_tester:{label:'Priz / RCD test cihazı',supplier:'measurement',professionalOnly:true,fields:[
      {id:'indication_scope',label:'Gösterge kapsamı',critical:true,question:'Cihaz hangi bağlantı hatalarını gösterebilir ve hangi hataları gösteremez?'},
      {id:'rcd_test_current',label:'RCD test akımı',critical:true,question:'RCD test akımı, süre ölçümü ve uyumlu IΔn değerleri nelerdir?'},
      {id:'measurement_category',label:'Ölçüm kategorisi',critical:true,question:'IEC 61010 ölçüm kategorisi, azami gerilim ve koruma sınıfı nedir?'},
      {id:'calibration',label:'Kalibrasyon',critical:true,question:'Kalibrasyon/izlenebilirlik belgesi ve doğrulama aralığı nedir?'},
      {id:'limitations',label:'Yöntem sınırı',critical:false,question:'Cihazın topraklama direnci, izolasyon veya çevrim empedansı ölçemediği açıkça belirtiliyor mu?'}
    ]}
  };

  const forbiddenKeys=['name','fullName','email','phone','address','subscription','identity','plate','serialNumber','freeText','price','stock','seller','warranty','asin','url'];

  function safeCategory(value){const key=String(value||'');return Object.prototype.hasOwnProperty.call(categorySpecs,key)?key:'';}
  function present(value){return value!==null&&value!==undefined&&value!=='';}
  function dateOnly(value){const d=value instanceof Date?value:new Date(value);return Number.isNaN(d.getTime())?null:new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth(),d.getUTCDate()));}
  function ageDays(value,now=new Date()){const checked=dateOnly(value),today=dateOnly(now);return checked&&today?Math.max(0,Math.floor((today-checked)/dayMs)):null;}

  function assessProduct(product={},options={}){
    const category=safeCategory(product.category||options.category);
    const spec=categorySpecs[category];
    if(!spec)return{category:'',status:'unsupported',score:0,missing:[],criticalMissing:[],affiliateAllowed:false,questions:[]};
    const attributes=product.attributes&&typeof product.attributes==='object'?product.attributes:{};
    const fields=spec.fields.map(field=>({...field,available:field.attribute?present(attributes[field.attribute]):false}));
    const totalWeight=fields.reduce((sum,field)=>sum+(field.critical?2:1),0);
    const earned=fields.reduce((sum,field)=>sum+(field.available?(field.critical?2:1):0),0);
    const score=totalWeight?Math.round(earned/totalWeight*100):0;
    const missing=fields.filter(field=>!field.available);
    const criticalMissing=missing.filter(field=>field.critical);
    const maxAge=Number.isFinite(options.maxAgeDays)?options.maxAgeDays:45;
    const age=ageDays(product.verifiedAt,options.now||new Date());
    const stale=age===null||age>maxAge;
    const status=stale?'stale':criticalMissing.length?'blocked':missing.length?'conditional':'complete';
    return{
      category,label:spec.label,status,score,stale,ageDays:age,maxAgeDays:maxAge,
      missing:missing.map(field=>field.id),criticalMissing:criticalMissing.map(field=>field.id),
      questions:missing.map(field=>field.question),
      affiliateAllowed:!spec.professionalOnly&&!stale&&!criticalMissing.length,
      professionalOnly:Boolean(spec.professionalOnly),supplierCategory:spec.supplier
    };
  }

  function questionPack(category,missingCodes=[]){
    const key=safeCategory(category),spec=categorySpecs[key];
    if(!spec)return[];
    const selected=new Set((Array.isArray(missingCodes)?missingCodes:[]).map(String));
    const fields=selected.size?spec.fields.filter(field=>selected.has(field.id)):spec.fields;
    return fields.map(field=>({id:field.id,label:field.label,critical:Boolean(field.critical),question:field.question}));
  }

  function buildQuestionText(category,productLabel,missingCodes=[]){
    const key=safeCategory(category),spec=categorySpecs[key];
    if(!spec)return'';
    const questions=questionPack(key,missingCodes);
    const title=String(productLabel||spec.label).replace(/[<>\r\n]/g,' ').trim().slice(0,120);
    return[
      'ALO186 Marka Bağımsız Teknik Veri Soru Paketi','',
      `Kategori: ${spec.label}`,
      `Ürün/kart: ${title||'Belirtilmedi'}`,'',
      'Satın alma veya yayın öncesinde resmî üretici kaynağıyla yanıtlanması gereken sorular:',
      ...questions.map((item,index)=>`${index+1}. ${item.question}`),'',
      'Yanıt beklentisi: Tam model kodu, resmî veri sayfası/kılavuz bağlantısı, ölçüm veya standardın kapsamı ve desteklenmeyen kullanım senaryoları.','',
      'Bu liste fiyat, stok, puan, garanti veya ürün uygunluk onayı değildir. ALO186 EDAŞ, kamu kurumu, ürün satıcısı veya laboratuvar değildir.'
    ].join('\n');
  }

  function supplierRoute(category,missingCodes=[]){
    const key=safeCategory(category),spec=categorySpecs[key];
    if(!spec)return'/tedarikci-ve-uretici-isbirligi';
    const allowed=new Set(spec.fields.map(field=>field.id));
    const fields=[...new Set((Array.isArray(missingCodes)?missingCodes:[]).map(String).filter(code=>allowed.has(code)))].slice(0,8);
    const params=new URLSearchParams({source:'documentation_gap',category:spec.supplier,type:'document',readiness:'partial',goal:'accuracy'});
    if(fields.length)params.set('fields',fields.join(','));
    return `/tedarikci-ve-uretici-isbirligi?${params.toString()}`;
  }

  function hasForbiddenData(value){
    if(!value||typeof value!=='object')return false;
    return Object.keys(value).some(key=>forbiddenKeys.includes(key)||hasForbiddenData(value[key]));
  }

  function sanitizeReview(input={},now=new Date()){
    const category=safeCategory(input.category);if(!category)return null;
    const spec=categorySpecs[category],allowed=new Set(spec.fields.map(field=>field.id));
    const missing=[...new Set((Array.isArray(input.missing)?input.missing:[]).map(String).filter(code=>allowed.has(code)))].slice(0,8);
    const created=new Date(now),reviewAt=new Date(created.getTime()+reviewDays*dayMs),expiresAt=new Date(created.getTime()+retentionDays*dayMs);
    return{schemaVersion,id:`doc_${category}_${created.getTime().toString(36)}`,category,productId:String(input.productId||'category').replace(/[^a-zA-Z0-9_-]/g,'').slice(0,80)||'category',missing,createdAt:created.toISOString(),reviewAt:reviewAt.toISOString(),expiresAt:expiresAt.toISOString()};
  }

  function normalizeReviews(raw,now=new Date()){
    const current=new Date(now).getTime(),seen=new Set(),clean=[];
    for(const item of Array.isArray(raw)?raw:[]){
      if(!item||item.schemaVersion!==schemaVersion||!safeCategory(item.category)||hasForbiddenData(item))continue;
      if(!Number.isFinite(Date.parse(item.createdAt))||!Number.isFinite(Date.parse(item.reviewAt))||Date.parse(item.expiresAt)<=current)continue;
      const key=`${item.category}|${item.productId}`;if(seen.has(key))continue;seen.add(key);clean.push(item);if(clean.length===reviewLimit)break;
    }
    return clean.sort((a,b)=>Date.parse(a.reviewAt)-Date.parse(b.reviewAt));
  }

  function upsertReview(vault,record){return record?normalizeReviews([record,...normalizeReviews(vault)]):normalizeReviews(vault);}
  function removeReview(vault,id){return normalizeReviews(vault).filter(item=>item.id!==id);}
  function daysUntil(value,now=new Date()){const diff=Date.parse(value)-new Date(now).getTime();return Number.isFinite(diff)?Math.ceil(diff/dayMs):null;}

  function buildReviewIcs(record,origin='https://alo186.com'){
    if(!record||!Number.isFinite(Date.parse(record.reviewAt)))return'';
    const date=new Date(record.reviewAt),end=new Date(date.getTime()+dayMs),spec=categorySpecs[record.category];
    const ymd=d=>`${d.getUTCFullYear()}${String(d.getUTCMonth()+1).padStart(2,'0')}${String(d.getUTCDate()).padStart(2,'0')}`;
    const esc=v=>String(v||'').replace(/\\/g,'\\\\').replace(/\n/g,'\\n').replace(/,/g,'\\,').replace(/;/g,'\\;');
    const route=`${String(origin).replace(/\/$/,'')}/akilli-urun-secimi?kategori=${encodeURIComponent(record.category)}`;
    return['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Documentation Review//TR','CALSCALE:GREGORIAN','BEGIN:VEVENT',`UID:${esc(record.id)}@alo186.com`,`DTSTART;VALUE=DATE:${ymd(date)}`,`DTEND;VALUE=DATE:${ymd(end)}`,'SUMMARY:ALO186 teknik ürün belgesini yeniden kontrol et',`DESCRIPTION:${esc(`${spec.label} için eksik teknik alanları resmî üretici kaynağından yeniden kontrol edin. Fiyat veya stok takibi değildir. ${route}`)}`,`URL:${esc(route)}`,'TRANSP:TRANSPARENT','END:VEVENT','END:VCALENDAR',''].join('\r\n');
  }

  function exportPayload(reviews,now=new Date()){
    const clean=normalizeReviews(reviews,now);
    return{schema:'alo186-documentation-reviews-v1',exportedAt:new Date(now).toISOString(),privacy:'Kişisel veri, ASIN, haricî ürün URL’si, fiyat, stok, puan, satıcı veya garanti içermez.',records:clean};
  }

  return{schemaVersion,reviewStorageKey,reviewLimit,reviewDays,retentionDays,categorySpecs,safeCategory,assessProduct,questionPack,buildQuestionText,supplierRoute,hasForbiddenData,sanitizeReview,normalizeReviews,upsertReview,removeReview,daysUntil,buildReviewIcs,exportPayload};
});
