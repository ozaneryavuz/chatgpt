(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186Companies=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const provinceNames={
    1:'Adana',2:'Adıyaman',3:'Afyonkarahisar',4:'Ağrı',5:'Amasya',6:'Ankara',7:'Antalya',8:'Artvin',9:'Aydın',10:'Balıkesir',
    11:'Bilecik',12:'Bingöl',13:'Bitlis',14:'Bolu',15:'Burdur',16:'Bursa',17:'Çanakkale',18:'Çankırı',19:'Çorum',20:'Denizli',
    21:'Diyarbakır',22:'Edirne',23:'Elazığ',24:'Erzincan',25:'Erzurum',26:'Eskişehir',27:'Gaziantep',28:'Giresun',29:'Gümüşhane',30:'Hakkari',
    31:'Hatay',32:'Isparta',33:'Mersin',34:'İstanbul',35:'İzmir',36:'Kars',37:'Kastamonu',38:'Kayseri',39:'Kırklareli',40:'Kırşehir',
    41:'Kocaeli',42:'Konya',43:'Kütahya',44:'Malatya',45:'Manisa',46:'Kahramanmaraş',47:'Mardin',48:'Muğla',49:'Muş',50:'Nevşehir',
    51:'Niğde',52:'Ordu',53:'Rize',54:'Sakarya',55:'Samsun',56:'Siirt',57:'Sinop',58:'Sivas',59:'Tekirdağ',60:'Tokat',
    61:'Trabzon',62:'Tunceli',63:'Şanlıurfa',64:'Uşak',65:'Van',66:'Yozgat',67:'Zonguldak',68:'Aksaray',69:'Bayburt',70:'Karaman',
    71:'Kırıkkale',72:'Batman',73:'Şırnak',74:'Bartın',75:'Ardahan',76:'Iğdır',77:'Yalova',78:'Karabük',79:'Kilis',80:'Osmaniye',81:'Düzce'
  };

  const companies=[
    {id:'toroslar',code:'TOROSLAR',name:'Toroslar EDAŞ',slug:'toroslar-edas',provinceIds:[1,27,31,79,33,80],aliases:['toroslar','toroslar edas','toroslar elektrik']},
    {id:'akedas',code:'AKEDAŞ',name:'AKEDAŞ',slug:'akedas',provinceIds:[2,46],aliases:['akedas','ak edas','akedaş']},
    {id:'oedas',code:'OEDAŞ',name:'Osmangazi EDAŞ',slug:'oedas',provinceIds:[3,11,26,43,64],aliases:['oedas','osmangazi edas','osmangazi elektrik']},
    {id:'aras',code:'ARAS',name:'ARAS EDAŞ',slug:'aras-edas',provinceIds:[4,24,25,36,69,75,76],aliases:['aras','aras edas','aras elektrik']},
    {id:'medas',code:'MEDAŞ',name:'MEDAŞ',slug:'medas',provinceIds:[68,70,40,42,50,51],aliases:['medas','meram edas','meram elektrik']},
    {id:'yedas',code:'YEDAŞ',name:'YEDAŞ',slug:'yedas',provinceIds:[5,19,52,55,57],aliases:['yedas','yesilirmak edas','yeşilırmak edaş']},
    {id:'baskent',code:'BAŞKENT',name:'Başkent EDAŞ',slug:'baskent-edas',provinceIds:[6,18,37,71,74,78,67],aliases:['baskent','başkent','baskent edas','başkent edaş']},
    {id:'aedas',code:'AEDAŞ',name:'Akdeniz EDAŞ',slug:'akdeniz-edas',provinceIds:[7,15,32],aliases:['aedas','akdeniz edas','akdeniz elektrik']},
    {id:'coruh',code:'ÇORUH',name:'Çoruh EDAŞ',slug:'coruh-edas',provinceIds:[8,28,29,53,61],aliases:['coruh','çoruh','coruh edas','çoruh edaş']},
    {id:'adm',code:'ADM',name:'ADM Elektrik',slug:'adm-elektrik',provinceIds:[9,20,48],aliases:['adm','adm elektrik','aydem dagitim','aydem dağıtım']},
    {id:'uedas',code:'UEDAŞ',name:'UEDAŞ',slug:'uedas',provinceIds:[10,16,17,77],aliases:['uedas','uludag edas','uludağ edaş','uludag elektrik']},
    {id:'dicle',code:'DİCLE',name:'Dicle Elektrik',slug:'dicle-elektrik',provinceIds:[72,21,47,56,63,73],aliases:['dicle','dicle elektrik','dicle edas']},
    {id:'fedas',code:'FIRAT',name:'Fırat EDAŞ',slug:'firat-edas',provinceIds:[12,23,44,62],aliases:['firat','fırat','firat edas','fırat edaş']},
    {id:'vedas',code:'VEDAŞ',name:'VEDAŞ',slug:'vedas',provinceIds:[13,30,49,65],aliases:['vedas','vangolu edas','vangölü edaş','van golu edas']},
    {id:'sedas',code:'SEDAŞ',name:'SEDAŞ',slug:'sedas',provinceIds:[14,41,54,81],aliases:['sedas','sakarya edas','sakarya elektrik']},
    {id:'tredas',code:'TREDAŞ',name:'TREDAŞ',slug:'tredas',provinceIds:[22,39,59],aliases:['tredas','trakya edas','trakya elektrik']},
    {id:'gdz',code:'GDZ',name:'GDZ Elektrik',slug:'gdz-elektrik',provinceIds:[35,45],aliases:['gdz','gdz elektrik','gediz elektrik','gediz edas']},
    {id:'kcetas',code:'KCETAŞ',name:'KCETAŞ',slug:'kcetas',provinceIds:[38],aliases:['kcetas','kcetaş','kayseri elektrik','kayseri ve civari']},
    {id:'cedas',code:'ÇEDAŞ',name:'Çamlıbel EDAŞ',slug:'cedas',provinceIds:[58,60,66],aliases:['cedas','çedaş','camlibel edas','çamlıbel edaş']},
    {id:'bedas',code:'BEDAŞ',name:'BEDAŞ',slug:'bedas',provinceIds:[34],districtMode:'istanbul_europe',aliases:['bedas','bogazici edas','boğaziçi edaş','istanbul avrupa']},
    {id:'ayedas',code:'AYEDAŞ',name:'AYEDAŞ',slug:'ayedas',provinceIds:[34],districtMode:'istanbul_asia',aliases:['ayedas','anadolu yakasi edas','anadolu yakası edaş','istanbul anadolu']}
  ];

  const istanbulEurope=['Arnavutköy','Avcılar','Bağcılar','Bahçelievler','Bakırköy','Başakşehir','Bayrampaşa','Beşiktaş','Beylikdüzü','Beyoğlu','Büyükçekmece','Çatalca','Esenler','Esenyurt','Eyüpsultan','Fatih','Gaziosmanpaşa','Güngören','Kağıthane','Küçükçekmece','Sarıyer','Silivri','Sultangazi','Şişli','Zeytinburnu'];
  const istanbulAsia=['Adalar','Ataşehir','Beykoz','Çekmeköy','Kadıköy','Kartal','Maltepe','Pendik','Sancaktepe','Sultanbeyli','Şile','Tuzla','Ümraniye','Üsküdar'];

  function normalize(value){
    return String(value||'').toLocaleLowerCase('tr-TR')
      .replace(/[ç]/g,'c').replace(/[ğ]/g,'g').replace(/[ı]/g,'i').replace(/[ö]/g,'o').replace(/[ş]/g,'s').replace(/[ü]/g,'u')
      .normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim();
  }

  const europeSet=new Set(istanbulEurope.map(normalize));
  const asiaSet=new Set(istanbulAsia.map(normalize));

  function companyForProvince(provinceId,districtName){
    provinceId=Number(provinceId);
    if(provinceId===34){
      const key=normalize(districtName);
      if(europeSet.has(key))return companies.find(c=>c.id==='bedas');
      if(asiaSet.has(key))return companies.find(c=>c.id==='ayedas');
      return null;
    }
    return companies.find(c=>c.provinceIds.includes(provinceId))||null;
  }

  function provinceSlug(name){
    return normalize(name).replace(/\s+/g,'-');
  }

  function companyUrl(company){
    return company?`https://alo186.com/dagitim-sirketleri/${company.slug}`:'https://alo186.com/elektrik-kesintisi';
  }

  function provinceUrl(provinceName){
    return `https://alo186.com/il/${provinceSlug(provinceName)}`;
  }

  return {provinceNames,companies,istanbulEurope,istanbulAsia,normalize,companyForProvince,provinceSlug,companyUrl,provinceUrl};
});
