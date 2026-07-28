(function(root,factory){
  const api=factory(root.Alo186ProductCatalog||(typeof require==='function'?require('./catalog.js'):null));
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186ConversionGrowthCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog){
  'use strict';
  if(!catalog)throw new Error('Ürün kataloğu yüklenemedi.');

  const allowedEventKeys=['category','status','placement','affiliate_policy','search_profile','professional_route'];
  const forbiddenEventKeys=['name','email','phone','address','subscription','identity','plate','serialNumber','freeText','raw','requirements','existing','price','stock','seller','warranty'];

  const profiles={
    powerbank:{label:'Powerbank teknik araması',fields:[
      {id:'capacity',label:'Kapasite sınıfı',options:[['10000','10.000 mAh','10000 mAh'],['20000','20.000 mAh','20000 mAh'],['25000','25.000 mAh ve üzeri','25000 mAh']]},
      {id:'output',label:'USB-C çıkış gücü',options:[['25','25 W','USB C PD 25W'],['65','65 W','USB C PD 65W'],['100','100 W','USB C PD 100W']]},
      {id:'feature',label:'Ek ihtiyaç',options:[['none','Ek özellik yok',''],['wireless','Kablosuz şarj','wireless'],['display','Dijital ekran','digital display']]}
    ]},
    surge_strip:{label:'Akım korumalı grup priz teknik araması',fields:[
      {id:'outlets',label:'Priz sayısı',options:[['5','5 priz','5 priz'],['6','6 priz','6 priz'],['8','8 priz','8 priz']]},
      {id:'joules',label:'Minimum darbe enerjisi',options:[['900','900 J ve üzeri','900 joule'],['1000','1.000 J ve üzeri','1000 joule'],['2000','2.000 J ve üzeri','2000 joule']]},
      {id:'current',label:'Nominal akım',options:[['10','10 A','10A'],['16','16 A','16A']]}
    ]},
    mini_ups:{label:'Modem ve ONT mini UPS teknik araması',fields:[
      {id:'voltage',label:'Doğrulanmış çıkış gerilimi',options:[['5','5 V','5V'],['9','9 V','9V'],['12','12 V','12V']]},
      {id:'current',label:'Gerekli akım sınıfı',options:[['2','2 A','2A'],['3','3 A','3A'],['5','5 A','5A']]},
      {id:'load',label:'Yük yapısı',options:[['modem','Yalnız modem','modem'],['modem_ont','Modem + fiber ONT','modem ONT'],['network','Modem + ONT + küçük switch','modem ONT switch']]}
    ]},
    emergency_light:{label:'Acil aydınlatma teknik araması',fields:[
      {id:'lumens',label:'Aynı moddaki ışık akısı',options:[['100','100 lm ve üzeri','100 lumen'],['300','300 lm ve üzeri','300 lumen'],['500','500 lm ve üzeri','500 lumen']]},
      {id:'runtime',label:'Aynı moddaki çalışma süresi',options:[['3','3 saat','3 saat'],['8','8 saat','8 saat'],['12','12 saat','12 saat']]},
      {id:'mode',label:'Çalışma biçimi',options:[['manual','Fiziksel düğmeli','fiziksel düğme'],['automatic','Kesintide otomatik yanan','elektrik kesintisinde otomatik']]}
    ]},
    smoke_alarm:{label:'Duman alarmı teknik araması',fields:[
      {id:'standard',label:'Standart',options:[['en14604','EN 14604','EN 14604']]},
      {id:'sensor',label:'Sensör',options:[['photoelectric','Fotoelektrik','fotoelektrik']]},
      {id:'battery',label:'Pil yapısı',options:[['replaceable','Değiştirilebilir pil','düşük pil uyarısı'],['sealed10','10 yıllık kapalı pil','10 yıl pil']]}
    ]},
    power_station:{label:'Power station teknik araması',fields:[
      {id:'capacity',label:'Kapasite sınıfı',options:[['500','500 Wh','500Wh'],['1000','1.000 Wh','1000Wh'],['2000','2.000 Wh','2000Wh']]},
      {id:'power',label:'Sürekli AC güç',options:[['600','600 W','600W'],['1200','1.200 W','1200W'],['1800','1.800 W','1800W']]},
      {id:'feature',label:'Zorunlu teknik özellik',options:[['lifepo4','LiFePO₄','LiFePO4'],['eps','EPS geçişi','EPS'],['solar','Solar giriş','MPPT solar giriş']]}
    ]},
    smart_plug:{label:'Akıllı priz ve enerji ölçer teknik araması',fields:[
      {id:'current',label:'Sürekli akım sınıfı',options:[['10','10 A','10A'],['16','16 A','16A']]},
      {id:'meter',label:'Ölçüm ihtiyacı',options:[['instant','Anlık W ölçümü','watt ölçüm'],['history','kWh ve geçmiş kayıt','kWh geçmiş kayıt']]},
      {id:'control',label:'Kontrol tercihi',options:[['local','Yerel kontrol önceliği','yerel kontrol'],['wifi','Wi-Fi uygulama','WiFi']]}
    ]},
    ev_cable:{label:'Type 2 EV kablosu teknik araması',fields:[
      {id:'current',label:'Akım sınıfı',options:[['16','16 A','16A'],['32','32 A','32A']]},
      {id:'phase',label:'Faz yapısı',options:[['single','Monofaze','monofaze'],['three','Trifaze','trifaze 22kW']]},
      {id:'length',label:'Kablo uzunluğu',options:[['5','5 m','5 metre'],['7_5','7,5 m','7.5 metre'],['10','10 m','10 metre']]}
    ]}
  };

  const professionalProfiles={
    generator:{problem:'backup',backup:'generator',scope:'comparison'},
    inverter:{problem:'backup',backup:'solar_storage',scope:'comparison'},
    outlet_tester:{problem:'audit',backup:'none',scope:'site'},
    ups_battery:{problem:'backup',backup:'ups',scope:'remote'}
  };

  function getProfile(category){return profiles[String(category||'')]||null;}
  function isProfessional(category){return Boolean(professionalProfiles[String(category||'')]);}
  function optionToken(field,value){const option=(field.options||[]).find(item=>String(item[0])===String(value));return option?String(option[2]||'').trim():'';}
  function normalizeSelections(category,selections={}){const profile=getProfile(category);if(!profile)return{};const clean={};for(const field of profile.fields){const raw=String(selections[field.id]||field.options[0][0]);const exists=field.options.some(item=>String(item[0])===raw);clean[field.id]=exists?raw:String(field.options[0][0]);}return clean;}
  function buildQuery(category,selections={}){const profile=getProfile(category);const catalogCategory=catalog.getCategory(category);if(!profile||!catalogCategory)return'';const clean=normalizeSelections(category,selections);const tokens=[catalogCategory.searchQuery];for(const field of profile.fields){const token=optionToken(field,clean[field.id]);if(token)tokens.push(token);}return [...new Set(tokens.map(token=>String(token).trim()).filter(Boolean))].join(' ');}
  function buildAffiliateUrl(category,selections={}){const query=buildQuery(category,selections);return query?catalog.amazonSearchUrl(query):'';}
  function gateStatus(category,confirmations={}){
    const profile=getProfile(category);const catalogCategory=catalog.getCategory(category);
    if(!catalogCategory)return{allowed:false,reason:'unknown_category'};
    if(isProfessional(category)||catalogCategory.affiliatePolicy==='professional_only')return{allowed:false,reason:'professional_only'};
    if(!profile)return{allowed:false,reason:'no_safe_profile'};
    const toolRequired=catalogCategory.affiliatePolicy==='after_tool';
    const checklistRequired=catalogCategory.affiliatePolicy==='after_checklist';
    if(toolRequired&&!confirmations.toolConfirmed)return{allowed:false,reason:'tool_not_confirmed'};
    if(checklistRequired&&!confirmations.checklistConfirmed)return{allowed:false,reason:'checklist_not_confirmed'};
    if(!confirmations.existingInsufficient)return{allowed:false,reason:'existing_may_be_sufficient'};
    if(!confirmations.affiliateAccepted)return{allowed:false,reason:'affiliate_not_accepted'};
    return{allowed:true,reason:'qualified_search'};
  }
  function professionalRoute(category){const profile=professionalProfiles[String(category||'')];if(!profile)return'';const params=new URLSearchParams({source:'product_center',category:String(category),problem:profile.problem,backup:profile.backup,scope:profile.scope});return `/kurumsal-elektrik-surekliligi-on-degerlendirme?${params.toString()}`;}
  function sanitizeEvent(input={}){const clean={};if(!input||typeof input!=='object')return clean;for(const key of allowedEventKeys){const value=input[key];if(typeof value==='string')clean[key]=value.replace(/[<>]/g,'').slice(0,80);else if(typeof value==='boolean')clean[key]=value;}return clean;}
  function hasForbiddenEventData(input={}){if(!input||typeof input!=='object')return false;return Object.keys(input).some(key=>forbiddenEventKeys.includes(key)||(input[key]&&typeof input[key]==='object'&&hasForbiddenEventData(input[key])));}

  return{profiles,professionalProfiles,getProfile,isProfessional,normalizeSelections,buildQuery,buildAffiliateUrl,gateStatus,professionalRoute,sanitizeEvent,hasForbiddenEventData};
});
