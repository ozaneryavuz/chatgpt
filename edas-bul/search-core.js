(function(root,factory){
  const api=factory(root.Alo186Companies||(typeof require==='function'?require('./companies.js'):null));
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186Search=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(companyApi){
  if(!companyApi)throw new Error('Alo186Companies yüklenemedi.');
  const {normalize,provinceNames,companies,companyForProvince,provinceUrl,companyUrl}=companyApi;

  const intents=[
    {id:'emergency',type:'intent',name:'Acil elektrik tehlikesi',risk:'red',aliases:['elektrik carpti','elektrik carpmasi','yangin','duman','kivilcim','kablo yere dustu','kopmus kablo','direk devrildi','suya elektrik temas etti'],description:'Yaklaşmayın, güvenli alana geçin ve can güvenliği riski için 112’yi arayın.',primaryAction:{label:'112’yi ara',href:'tel:112'},secondaryAction:{label:'186’yı ara',href:'tel:186'}},
    {id:'fault-line',type:'intent',name:'Elektrik arıza hattı',risk:'normal',aliases:['186','elektrik kesintisi numarasi','elektrik ariza numarasi','edas numarasi','kesinti telefonu'],description:'Şebeke kesintisi, sokak aydınlatması ve dağıtım hattı arızalarında 186 kullanılır.',primaryAction:{label:'186’yı ara',href:'tel:186'}},
    {id:'street-light',type:'intent',name:'Sokak aydınlatması arızası',risk:'normal',aliases:['sokak lambasi','sokak aydinlatmasi','direk lambasi','aydınlatma arizasi'],description:'Sokak aydınlatması için 186 veya bölgenizin resmî dağıtım kanalı kullanılmalıdır.',primaryAction:{label:'186’yı ara',href:'tel:186'}},
    {id:'internal-fault',type:'intent',name:'Ev veya iş yeri iç tesisat arızası',risk:'yellow',aliases:['elektrikci','yalniz bende elektrik yok','bazi prizler calismiyor','kacak akim atiyor','sigorta atiyor'],description:'Sorun yalnız daire veya iş yerindeyse bina yönetimi ya da yetkili elektrikçiden destek alın. Yanık kokusu veya ısınma varsa müdahale etmeyin.',primaryAction:{label:'Karar motorunu aç',href:'https://alo186.com/elektrik-portali'}},
    {id:'outage',type:'intent',name:'Elektrik kesintisi sorgulama',risk:'normal',aliases:['elektrik kesintisi','kesinti sorgulama','elektrikler ne zaman gelecek','bugun kesinti var mi','planli kesinti'],description:'İl veya ilçenizi arayarak yetkili dağıtım şirketinin resmî kesinti ekranına ilerleyin.',primaryAction:{label:'Bölge ara',href:'#arama'}}
  ];

  function getProvinceId(item){return Number(item&&((item.provinceId??item.province_id??(item.province&&item.province.id))));}
  function similarity(a,b){
    a=normalize(a);b=normalize(b);if(a===b)return 1;if(!a||!b)return 0;
    const m=a.length,n=b.length,prev=Array(n+1).fill(0),cur=Array(n+1).fill(0);
    for(let j=0;j<=n;j++)prev[j]=j;
    for(let i=1;i<=m;i++){
      cur[0]=i;
      for(let j=1;j<=n;j++)cur[j]=Math.min(cur[j-1]+1,prev[j]+1,prev[j-1]+(a[i-1]===b[j-1]?0:1));
      for(let j=0;j<=n;j++)prev[j]=cur[j];
    }
    return 1-prev[n]/Math.max(m,n);
  }

  function fallbackProvinces(){return Object.entries(provinceNames).map(([id,name])=>({id:Number(id),name}));}

  function buildIndex(provinces,districts){
    provinces=Array.isArray(provinces)&&provinces.length?provinces:fallbackProvinces();
    districts=Array.isArray(districts)?districts:[];
    const provinceMap=new Map(provinces.map(p=>[Number(p.id),p]));
    const records=[];

    provinces.forEach(p=>{
      const id=Number(p.id),name=p.name||provinceNames[id],company=id===34?null:companyForProvince(id);
      records.push({type:'province',id:`province-${id}`,name,provinceId:id,provinceName:name,company,split:id===34,aliases:[name,`${name} elektrik kesintisi`,`${name} edas`]});
    });

    districts.forEach(d=>{
      const provinceId=getProvinceId(d),province=provinceMap.get(provinceId),name=d.name;
      if(!provinceId||!name||!province)return;
      const company=companyForProvince(provinceId,name);
      records.push({type:'district',id:`district-${d.id}`,name,provinceId,provinceName:province.name||provinceNames[provinceId],company,aliases:[name,`${name} elektrik kesintisi`,`${province.name||provinceNames[provinceId]} ${name}`]});
    });

    companies.forEach(c=>records.push({type:'company',id:`company-${c.id}`,name:c.name,company:c,aliases:[c.name,c.code,...(c.aliases||[])]}));
    intents.forEach(i=>records.push(i));
    return records;
  }

  function haystack(record){return normalize([record.name,...(record.aliases||[]),record.provinceName||'',record.company&&record.company.name||''].join(' '));}

  function scoreRecord(query,record){
    const q=normalize(query),h=haystack(record);if(!q)return 0;
    let score=0;
    if(q===normalize(record.name))score=110;
    else if((record.aliases||[]).some(a=>q===normalize(a)))score=105;
    else if(h.startsWith(q))score=90;
    else if(h.includes(q))score=80;
    else {
      const tokens=q.split(' ').filter(Boolean);
      if(tokens.length&&tokens.every(t=>h.includes(t)))score=74;
      else {
        const target=normalize(record.name);
        const sim=similarity(q,target);
        if(sim>=.78)score=60+sim*20;
      }
    }
    if(!score)return 0;
    if(record.type==='district')score+=8;
    if(record.type==='province')score+=6;
    if(record.type==='intent')score+=12;
    if(record.type==='company')score+=4;
    return score;
  }

  function search(query,index,limit=10){
    if(!normalize(query))return [];
    return index.map(record=>({record,score:scoreRecord(query,record)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.record.name.localeCompare(b.record.name,'tr')).slice(0,limit).map(x=>x.record);
  }

  function resultActions(record){
    if(record.type==='intent')return [record.primaryAction,record.secondaryAction].filter(Boolean);
    if(record.type==='company')return [{label:'Şirket ve resmî kanalları aç',href:companyUrl(record.company)},{label:'186’yı ara',href:'tel:186'}];
    if(record.type==='province'){
      if(record.split)return [{label:'İlçe seçerek yakayı belirle',href:'#arama'},{label:'186’yı ara',href:'tel:186'}];
      return [{label:`${record.provinceName} kesinti bilgilerini aç`,href:provinceUrl(record.provinceName)},{label:'186’yı ara',href:'tel:186'}];
    }
    if(record.type==='district')return [{label:'Resmî kesinti ve iletişim bilgilerini aç',href:provinceUrl(record.provinceName)},{label:'186’yı ara',href:'tel:186'}];
    return [];
  }

  function describe(record){
    if(record.type==='intent')return record.description;
    if(record.type==='company')return `${record.name}, ${record.company.provinceIds.map(id=>provinceNames[id]).join(', ')} bölgesinde elektrik dağıtım hizmetinden sorumludur.`;
    if(record.type==='province'&&record.split)return 'İstanbul Avrupa Yakası’nda BEDAŞ, Anadolu Yakası’nda AYEDAŞ yetkilidir. İlçe arayarak doğru şirketi belirleyin.';
    if(record.company)return `${record.name}${record.type==='district'?` / ${record.provinceName}`:''} için yetkili dağıtım şirketi ${record.company.name}’tır. Şebeke arızası için 186 kullanılmalıdır.`;
    return 'Yetkili dağıtım şirketini belirlemek için ilçe seçimi gerekir.';
  }

  return {intents,normalize,similarity,fallbackProvinces,buildIndex,search,scoreRecord,resultActions,describe,getProvinceId};
});
