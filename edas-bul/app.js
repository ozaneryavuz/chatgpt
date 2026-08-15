const $=id=>document.getElementById(id);
const DATA_VERSION='2025';
const DATA_URLS={
  provinces:`https://api.turkiyeapi.dev/v2/datasets/${DATA_VERSION}/provinces.json`,
  districts:`https://api.turkiyeapi.dev/v2/datasets/${DATA_VERSION}/districts.json`
};
const CACHE_KEY=`alo186_geo_${DATA_VERSION}`;
const CACHE_TTL=30*24*60*60*1000;
let index=Alo186Search.buildIndex([],[]);
let visibleResults=[];
let activeIndex=-1;

function datasetArray(payload){return Array.isArray(payload)?payload:Array.isArray(payload&&payload.data)?payload.data:[];}
function slimProvinces(items){return items.map(x=>({id:Number(x.id),name:x.name})).filter(x=>x.id&&x.name);}
function slimDistricts(items){return items.map(x=>({id:Number(x.id),name:x.name,provinceId:Number(x.provinceId??x.province_id??(x.province&&x.province.id))})).filter(x=>x.id&&x.name&&x.provinceId);}

async function fetchJson(url,timeout=12000){
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),timeout);
  try{
    const response=await fetch(url,{signal:controller.signal,headers:{Accept:'application/json'}});
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }finally{clearTimeout(timer);}
}

function setDatasetState(kind,message){
  $('datasetBadge').textContent=message;
  $('datasetBadge').className=`dataset-badge ${kind||''}`.trim();
  $('datasetStatus').textContent=message;
}

function readCache(){
  try{
    const cached=JSON.parse(localStorage.getItem(CACHE_KEY)||'null');
    if(cached&&Date.now()-cached.savedAt<CACHE_TTL&&cached.provinces&&cached.districts)return cached;
  }catch(e){/* geçersiz önbelleği yok say */}
  return null;
}

function saveCache(provinces,districts){
  try{localStorage.setItem(CACHE_KEY,JSON.stringify({savedAt:Date.now(),provinces,districts}));}catch(e){/* depolama zorunlu değil */}
}

async function loadData(){
  const cached=readCache();
  if(cached){
    index=Alo186Search.buildIndex(cached.provinces,cached.districts);
    $('coverageStat').textContent=`${cached.provinces.length} il · ${cached.districts.length} ilçe`;
    setDatasetState('ok','Tam Türkiye verisi hazır');
    return;
  }
  try{
    const [provincePayload,districtPayload]=await Promise.all([fetchJson(DATA_URLS.provinces),fetchJson(DATA_URLS.districts)]);
    const provinces=slimProvinces(datasetArray(provincePayload));
    const districts=slimDistricts(datasetArray(districtPayload));
    if(provinces.length!==81||districts.length<950)throw new Error('Veri kapsamı beklenenden düşük.');
    index=Alo186Search.buildIndex(provinces,districts);
    saveCache(provinces,districts);
    $('coverageStat').textContent=`${provinces.length} il · ${districts.length} ilçe`;
    setDatasetState('ok','Tam Türkiye verisi hazır');
    Alo186Track('location_dataset_loaded',{province_count:provinces.length,district_count:districts.length,source:'turkiyeapi'});
  }catch(error){
    index=Alo186Search.buildIndex([],[]);
    $('coverageStat').textContent='81 il · 21 EDAŞ';
    setDatasetState('warn','İlçe verisi alınamadı; il ve şirket araması açık');
    $('sourceNote').textContent='İlçe verisi bağlantısı daha sonra yeniden denenecek.';
    Alo186Track('location_dataset_failed',{message:String(error&&error.message||error)});
  }
}

function typeLabel(record){
  if(record.type==='province')return 'İl';
  if(record.type==='district')return 'İlçe';
  if(record.type==='company')return 'Dağıtım şirketi';
  return record.risk==='red'?'Acil güvenlik':'İşlem';
}

function companyLabel(record){
  if(record.type==='province'&&record.split)return 'BEDAŞ / AYEDAŞ — ilçe seçimi gerekir';
  return record.company?record.company.name:'';
}

function renderResults(records,query){
  visibleResults=records;activeIndex=-1;
  $('searchResults').innerHTML='';
  $('zeroState').classList.toggle('hidden',records.length>0||!query);
  $('resultCount').textContent=query?(records.length?`${records.length} uygun sonuç gösteriliyor.`:'Eşleşme bulunamadı.'):'Arama yapmaya başlayın.';
  $('searchInput').setAttribute('aria-expanded',records.length?'true':'false');
  if(!records.length){
    if(query)$('reportMissing').href=`https://alo186.com/iletisim?konu=eksik-bolge&aranan=${encodeURIComponent(query)}`;
    return;
  }
  records.forEach((record,i)=>{
    const article=document.createElement('article');
    article.className=`search-result ${record.risk==='red'?'red':record.risk==='yellow'?'yellow':''}`.trim();
    article.tabIndex=-1;article.role='option';article.id=`search-option-${i}`;article.setAttribute('aria-selected','false');
    const actions=Alo186Search.resultActions(record);
    article.innerHTML=`<div class="result-top"><div><span class="result-type ${record.risk==='red'?'intent-red':''}">${typeLabel(record)}</span><h3>${escapeHtml(record.name)}${record.type==='district'?` <small>/ ${escapeHtml(record.provinceName)}</small>`:''}</h3></div></div><p>${escapeHtml(Alo186Search.describe(record))}</p>${companyLabel(record)?`<span class="company-chip">${escapeHtml(companyLabel(record))}</span>`:''}<div class="result-actions">${actions.map((a,j)=>`<a href="${escapeAttr(a.href)}" data-action-index="${j}" data-record-id="${escapeAttr(record.id)}">${escapeHtml(a.label)}</a>`).join('')}</div>`;
    article.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>Alo186Track('location_result_action_clicked',{query,record_type:record.type,record_id:record.id,action_label:a.textContent.trim(),company:record.company&&record.company.id||null})));
    article.addEventListener('click',e=>{if(e.target.tagName!=='A')setActive(i,true);});
    $('searchResults').appendChild(article);
  });
}

function escapeHtml(value){return String(value??'').replace(/[&<>"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));}
function escapeAttr(value){return escapeHtml(value).replace(/'/g,'&#39;');}

function runSearch(query){
  const q=query.trim();
  if(!q){renderResults([],q);return;}
  const results=Alo186Search.search(q,index,10);
  renderResults(results,q);
  Alo186Track(results.length?'location_search_results_shown':'location_search_zero_result',{query_normalized:Alo186Companies.normalize(q),result_count:results.length});
}

let timer;
$('searchInput').addEventListener('input',e=>{clearTimeout(timer);timer=setTimeout(()=>runSearch(e.target.value),120);});
$('searchInput').addEventListener('keydown',e=>{
  if(e.key==='ArrowDown'){e.preventDefault();setActive(Math.min(activeIndex+1,visibleResults.length-1),true);}
  if(e.key==='ArrowUp'){e.preventDefault();setActive(Math.max(activeIndex-1,0),true);}
  if(e.key==='Escape')clearSearch();
  if(e.key==='Enter'&&activeIndex>=0){e.preventDefault();const link=$(`search-option-${activeIndex}`).querySelector('a');if(link)link.click();}
});

function setActive(i,focus){
  activeIndex=i;
  document.querySelectorAll('.search-result').forEach((el,idx)=>el.setAttribute('aria-selected',idx===i?'true':'false'));
  if(i>=0){$('searchInput').setAttribute('aria-activedescendant',`search-option-${i}`);if(focus)$(`search-option-${i}`).focus();}
}

function clearSearch(){$('searchInput').value='';renderResults([],'');$('searchInput').focus();}
$('clearBtn').addEventListener('click',clearSearch);
document.querySelectorAll('[data-query]').forEach(btn=>btn.addEventListener('click',()=>{$('searchInput').value=btn.dataset.query;runSearch(btn.dataset.query);$('searchInput').focus();Alo186Track('location_quick_query_clicked',{query:btn.dataset.query});}));
$('showProvincesBtn').addEventListener('click',()=>{const provinces=index.filter(x=>x.type==='province').sort((a,b)=>a.name.localeCompare(b.name,'tr'));renderResults(provinces,'81 il');});

loadData().then(()=>{
  const params=new URLSearchParams(location.search),q=params.get('q');
  if(q){$('searchInput').value=q;runSearch(q);}
});
