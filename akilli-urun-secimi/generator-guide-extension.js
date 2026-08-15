(() => {
  'use strict';

  const salesVersion='2026-07-30';
  const catalog=window.Alo186ProductCatalog;
  const newCategories=[
    {id:'hdmi_cable',name:'HDMI 2.1 görüntü ve oyun kablosu',mode:'direct',risk:'consumer',affiliatePolicy:'verified_direct',description:'Kaynak ve ekran HDMI sürümü, hedef çözünürlük/yenileme, eARC/VRR ihtiyacı ve kablo uzunluğu birlikte doğrulanır.',searchQuery:'HDMI 2.1 48Gbps 8K 60Hz 4K 120Hz kablo'},
    {id:'displayport_cable',name:'DisplayPort 1.4 monitör kablosu',mode:'direct',risk:'consumer',affiliatePolicy:'verified_direct',description:'Ekran kartı ve monitör DisplayPort sürümü, hedef çözünürlük/yenileme ve kablo uzunluğu birlikte doğrulanır.',searchQuery:'DisplayPort 1.4 32.4Gbps 8K 60Hz 4K 144Hz kablo'},
    {id:'usb_c_hdmi_cable',name:'USB-C - HDMI görüntü kablosu',mode:'direct',risk:'consumer',affiliatePolicy:'verified_direct',description:'USB-C portunun DisplayPort Alt Mode veya Thunderbolt görüntü çıkışı, HDMI hedefi, çözünürlük ve kablo yönü doğrulanmalıdır.',searchQuery:'USB C HDMI 4K 60Hz DisplayPort Alt Mode kablo'}
  ];
  const newProducts=[
    {id:'xiaomi-bhr4996gl-33w',category:'usb_c_charger',asin:'B09DDDLZQW',mpn:'BHR4996GL',name:'Xiaomi BHR4996GL 33 W USB-C + USB-A Şarj Adaptörü',brand:'Xiaomi',status:'verified_listing',verifiedAt:salesVersion,attributes:{maxOutputW:33,usbCPorts:1,usbAPorts:1,multiPort:true},strengths:['33 W etiket gücü','Bir USB-C ve bir USB-A port','İki farklı kablo tipi için tek adaptör'],limits:['İki port birlikte kullanıldığında güç dağılımı ürün sayfasından yeniden doğrulanmalı','Cihazın hızlı şarj protokolü ayrıca uyumlu olmalıdır','Kablo içeriği ve kablo akım sınıfı satın alma öncesi kontrol edilmelidir'],sourceNote:'ASIN, BHR4996GL model kodu, 33 W ve USB-C + USB-A port yapısı Amazon ürün sayfasından 30 Temmuz 2026 tarihinde doğrulandı; fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',url:catalog&&catalog.amazonProductUrl('B09DDDLZQW')},
    {id:'samsung-ep-ta800n-25w',category:'usb_c_charger',asin:'B00MN26FFC',mpn:'EP-TA800NBEGWW',name:'Samsung EP-TA800N 25 W USB-C PD/PPS Şarj Adaptörü',brand:'Samsung',status:'verified_listing',verifiedAt:salesVersion,attributes:{maxOutputW:25,usbCPorts:1,usbAPorts:0,pd3:true,pps:true,cableIncluded:false},strengths:['25 W USB-C çıkış sınıfı','USB Power Delivery 3.0','PPS desteği'],limits:['Şarj kablosu kutuya dahil değildir','Cihazın 25 W PD/PPS kabulü ve kablo sınıfı ayrıca doğrulanmalıdır','Amazon teknik tablosundaki model/parça alanı satın alma öncesi yeniden kontrol edilmelidir'],sourceNote:'ASIN, EP-TA800N model adı, 25 W, USB-C ve PD 3.0/PPS alanları Amazon ürün sayfasından 30 Temmuz 2026 tarihinde doğrulandı; fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',url:catalog&&catalog.amazonProductUrl('B00MN26FFC')},
    {id:'baseus-pudding-100w-12m',category:'usb_c_cable',asin:'B0CG7SZ299',name:'Baseus Pudding USB-C - USB-C 100 W 1,2 m Kablo',brand:'Baseus',status:'verified_listing',verifiedAt:salesVersion,attributes:{connectorA:'USB-C',connectorB:'USB-C',maxCurrentA:5,maxPowerW:100,lengthM:1.2,dataTransferMbps:480},strengths:['100 W / 5 A sınıfı','1,2 metre uzunluk','480 Mbps veri sınıfı'],limits:['240 W USB PD EPR ihtiyacı için uygun kabul edilmemeli','100 W için adaptör ve cihazın USB PD desteği gerekir','Video çıkışı veya yüksek hızlı USB veri kablosu olarak kabul edilmemelidir'],sourceNote:'ASIN, USB-C - USB-C, 100 W, 1,2 m ve 480 Mbps alanları ürün teknik listelemelerinden 30 Temmuz 2026 tarihinde doğrulandı; fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',url:catalog&&catalog.amazonProductUrl('B0CG7SZ299')},
    {id:'ugreen-dp14-2m',category:'displayport_cable',asin:'B088GQM9CV',name:'UGREEN DisplayPort 1.4 8K 60 Hz Kablo 2 m',brand:'UGREEN',status:'verified_listing',verifiedAt:salesVersion,attributes:{connectorA:'DisplayPort',connectorB:'DisplayPort',lengthM:2,displayPortVersion:'1.4',maxDataGbps:32.4,maxResolution:'8K@60Hz',max4KHz:144,hdr:true},strengths:['DisplayPort 1.4 sınıfı','32,4 Gbps bant genişliği','8K@60Hz ve 4K@144Hz sınıfı','2 metre uzunluk'],limits:['Gerçek çözünürlük ve yenileme hızı ekran kartı ile monitörün ortak sınırıdır','DSC, HDR, adaptif senkronizasyon ve renk derinliği cihazlara göre ayrıca doğrulanmalıdır'],sourceNote:'ASIN, DisplayPort 1.4, 2 m, 8K@60Hz, 4K@144Hz ve 32,4 Gbps alanları Amazon ürün sayfasından 30 Temmuz 2026 tarihinde doğrulandı; fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',url:catalog&&catalog.amazonProductUrl('B088GQM9CV')},
    {id:'ugreen-hdmi21-3m',category:'hdmi_cable',asin:'B0CFF9T3PS',mpn:'25911',name:'UGREEN 25911 HDMI 2.1 48 Gbps Kablo 3 m',brand:'UGREEN',status:'verified_listing',verifiedAt:salesVersion,attributes:{connectorA:'HDMI',connectorB:'HDMI',lengthM:3,hdmiVersion:'2.1',maxDataGbps:48,maxResolution:'8K@60Hz',max4KHz:240,earc:true,vrr:true,allm:true,hdr:true},strengths:['HDMI 2.1 Ultra High Speed sınıfı','48 Gbps bant genişliği','8K@60Hz ve 4K@240Hz sınıfı','eARC, VRR ve ALLM','3 metre uzunluk'],limits:['Gerçek çözünürlük, yenileme, HDR ve ses işlevleri kaynak ile ekranın ortak desteğiyle sınırlıdır','Kablo sertliği ve 3 m güzergâh cihaz konnektörüne mekanik yük bindirmemelidir'],sourceNote:'ASIN, 25911 model kodu, HDMI 2.1, 48 Gbps, 8K@60Hz, 4K@240Hz, eARC/VRR/ALLM ve 3 m alanları Amazon ürün sayfasından 30 Temmuz 2026 tarihinde doğrulandı; fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',url:catalog&&catalog.amazonProductUrl('B0CFF9T3PS')},
    {id:'daytona-hc01-usbc-hdmi-18m',category:'usb_c_hdmi_cable',asin:'B096G51911',mpn:'HC-01',name:'Daytona HC-01 USB-C - HDMI 4K 60 Hz Kablo 1,8 m',brand:'Daytona',status:'verified_listing',verifiedAt:salesVersion,attributes:{connectorA:'USB-C',connectorB:'HDMI',lengthM:1.8,maxResolution:'4K@60Hz',plugAndPlay:true},strengths:['USB-C - HDMI tek kablo','4K@60Hz sınıfı','1,8 metre uzunluk','Haricî sürücü gerektirmeyen kullanım'],limits:['Kaynak USB-C portu DisplayPort Alt Mode veya Thunderbolt görüntü çıkışı desteklemelidir','Telefon ve tabletlerin tüm USB-C portları görüntü vermez','HDR, ses ve HDCP uyumu kaynak ve ekranla sınırlıdır'],sourceNote:'ASIN, HC-01 model adı, USB-C - HDMI, 1,8 m ve 4K@60Hz alanları Amazon ürün sayfasından 30 Temmuz 2026 tarihinde doğrulandı; fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',url:catalog&&catalog.amazonProductUrl('B096G51911')},
    {id:'veggieg-z623-usbc-dp14-2m',category:'display_cable',asin:'B0DK6QPTFQ',mpn:'Z623',name:'VegGieg Z623 Çift Yönlü USB-C - DisplayPort 1.4 Kablo 2 m',brand:'VegGieg',status:'verified_listing',verifiedAt:salesVersion,attributes:{connectorA:'USB-C',connectorB:'DisplayPort',lengthM:2,displayPortVersion:'1.4',maxResolution:'8K@60Hz',max4KHz:144,bidirectional:true,hdr:true},strengths:['Çift yönlü USB-C / DisplayPort kullanım iddiası','8K@60Hz ve 4K@144Hz sınıfı','2 metre uzunluk'],limits:['Her iki yönde de kaynak cihazın görüntü çıkışını ve hedef cihazın girişini desteklemesi gerekir','USB-C portun görüntü yeteneği satın alma öncesi doğrulanmalıdır'],sourceNote:'ASIN, Z623 model adı, çift yönlü USB-C - DisplayPort 1.4, 2 m, 8K@60Hz ve 4K@144Hz alanları Amazon ürün sayfasından 30 Temmuz 2026 tarihinde doğrulandı; fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',url:catalog&&catalog.amazonProductUrl('B0DK6QPTFQ')},
    {id:'veggieg-dp14-2m',category:'displayport_cable',asin:'B0DN61ZDBQ',name:'VegGieg DisplayPort 1.4 8K 60 Hz Kablo 2 m',brand:'VegGieg',status:'verified_listing',verifiedAt:salesVersion,attributes:{connectorA:'DisplayPort',connectorB:'DisplayPort',lengthM:2,displayPortVersion:'1.4',maxDataGbps:32.4,maxResolution:'8K@60Hz',max4KHz:165,max2KHz:240},strengths:['DisplayPort 1.4 sınıfı','32,4 Gbps bant genişliği','8K@60Hz, 4K@165Hz ve 2K@240Hz sınıfı','2 metre uzunluk'],limits:['Gerçek görüntü modu ekran kartı ve monitörün ortak desteğine bağlıdır','Yüksek yenileme için çözünürlük, renk derinliği ve DSC koşulları ayrıca doğrulanmalıdır'],sourceNote:'ASIN, DisplayPort 1.4, 2 m, 32,4 Gbps, 8K@60Hz, 4K@165Hz ve 2K@240Hz alanları Amazon ürün sayfasından 30 Temmuz 2026 tarihinde doğrulandı; fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',url:catalog&&catalog.amazonProductUrl('B0DN61ZDBQ')}
  ];
  const purchaseCollections=[
    {id:'travel-65w',name:'Seyahat ve çoklu cihaz 65 W seti',description:'Telefon, tablet, uyumlu dizüstü ve taşınabilir enerji için adaptör, 100 W kablo ve powerbank üçlüsü.',productIds:['samsung-ep-t6530-trio-65w','baseus-crystal-shine-100w-2m','anker-prime-a1336'],checks:['Dizüstünün USB-C PD ile şarj kabul ettiğini doğrulayın.','65 W için uygun 5 A kablo kullanın.','Powerbank uçuş ve taşıma kurallarını seyahat öncesi kontrol edin.']},
    {id:'samsung-fast-charge',name:'Samsung 45 W hazır şarj seti',description:'Uyumlu Samsung cihazlar için 45 W adaptör, 5 A kablo ve kablosuz powerbank seçenekleri.',productIds:['anker-313-a2677','baseus-crystal-shine-100w-2m','samsung-eb-u2510x'],checks:['Telefonun Super Fast Charging 2.0 desteğini doğrulayın.','45 W için 5 A e-marker kablo gereklidir.','Powerbank kablolu ve kablosuz çıkış sınırlarını ayrı kontrol edin.']},
    {id:'desk-dock',name:'Tek kablolu çalışma masası seti',description:'Çoklu port şarj, USB-C hub ve yüksek çözünürlüklü monitör bağlantısı için çalışma masası üçlüsü.',productIds:['samsung-ep-t6530-trio-65w','ugreen-7in1-60515','ugreen-usbc-dp14-2m'],checks:['Dizüstü USB-C portunun görüntü ve PD geçişini desteklediğini doğrulayın.','Hub PD değeri adaptörün kutuya dahil olduğu anlamına gelmez.','Monitör bağlantı standardını ve hedef yenileme hızını kontrol edin.']},
    {id:'gaming-display',name:'Oyun ve yüksek yenileme görüntü seti',description:'DisplayPort ve HDMI 2.1 seçeneklerini aynı masada karşılaştırmak isteyen kullanıcılar için iki kablolu görüntü seti.',productIds:['ugreen-dp14-2m','ugreen-hdmi21-3m'],checks:['Ekran kartı ve monitörde ortak port standardını doğrulayın.','4K/8K ve yüksek yenileme aynı anda cihaz sınırlarıyla belirlenir.','HDMI eARC ihtiyacını görüntü kablosu ihtiyacından ayrı değerlendirin.']},
    {id:'mobile-presentation',name:'Mobil sunum ve toplantı seti',description:'USB-C görüntü çıkışlı cihazı HDMI ekrana bağlamak ve toplantı boyunca şarj etmek için kompakt üçlü.',productIds:['xiaomi-bhr4996gl-33w','daytona-hc01-usbc-hdmi-18m','baseus-pudding-100w-12m'],checks:['Telefon veya dizüstü USB-C portunun görüntü çıkışı desteklediğini doğrulayın.','33 W adaptörün cihaz için yeterli olup olmadığını kontrol edin.','HDMI ekranın hedef çözünürlük ve HDCP desteğini doğrulayın.']}
  ];

  function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}
  function productById(id){return catalog&&catalog.products.find(product=>product.id===id);}
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}

  function extendCatalog(){
    if(!catalog||catalog.__salesExpansion20260730)return;
    newCategories.forEach(category=>{if(!catalog.getCategory(category.id))catalog.categories.push(category);});
    newProducts.forEach(product=>{if(!catalog.products.some(item=>item.id===product.id||item.asin===product.asin))catalog.products.push(product);});
    const originalKnowledgeGraph=catalog.knowledgeGraph.bind(catalog);
    catalog.knowledgeGraph=options=>{
      const payload=originalKnowledgeGraph(options);
      const now=options&&options.now||new Date();
      const nodes=purchaseCollections.map(collection=>{
        const products=collection.productIds.map(productById).filter(product=>product&&catalog.verificationStatus(product,now).fresh);
        return {'@type':'ItemList','@id':`https://alo186.com/akilli-urun-secimi#collection-${collection.id}`,name:collection.name,description:collection.description,numberOfItems:products.length,itemListElement:products.map((product,index)=>({'@type':'ListItem',position:index+1,item:{'@id':catalog.productId(product)}}))};
      });
      payload['@graph'].push(...nodes);
      return payload;
    };
    catalog.purchaseCollections=purchaseCollections;
    catalog.__salesExpansion20260730=true;
    const script=document.getElementById('alo186-affiliate-knowledge-graph');
    if(script)script.textContent=JSON.stringify(catalog.knowledgeGraph());
  }

  extendCatalog();

  function salesRequirementMarkup(categoryId){
    if(categoryId==='usb_c_charger')return `<div class="form-grid sales-requirements"><label class="field"><span>Minimum tek port gücü</span><select data-sales-field="minOutputW"><option value="25">25 W — telefon</option><option value="33">33 W — hızlı telefon/tablet</option><option value="45" selected>45 W — SFC 2.0 / tablet</option><option value="65">65 W — uyumlu dizüstü</option></select></label><label class="field"><span>Minimum USB-C portu</span><select data-sales-field="minUsbCPorts"><option value="1" selected>1 USB-C</option><option value="2">2 USB-C</option></select></label><label class="check-item field full"><input data-sales-field="multiPort" type="checkbox"><span><b>Aynı anda birden fazla cihaz şarj edeceğim</b><br><small>Çoklu port güç paylaşımı tek port gücünden farklı olabilir.</small></span></label></div>`;
    if(categoryId==='usb_c_cable')return `<div class="form-grid sales-requirements"><label class="field"><span>Minimum güç sınıfı</span><select data-sales-field="minPowerW"><option value="60">60 W</option><option value="100" selected>100 W / 5 A</option></select></label><label class="field"><span>Minimum uzunluk</span><select data-sales-field="minLengthM"><option value="1">1 m</option><option value="1.2">1,2 m</option><option value="2" selected>2 m</option></select></label><label class="check-item field full"><input data-sales-field="dataTransfer" type="checkbox"><span><b>Veri aktarımı da gerekli</b><br><small>Şarj gücü, veri hızı ve görüntü çıkışı farklı özelliklerdir.</small></span></label></div>`;
    if(categoryId==='usb_c_hub')return `<div class="form-grid sales-requirements"><label class="field"><span>Minimum PD geçişi</span><select data-sales-field="minPdPassThroughW"><option value="65">65 W</option><option value="100" selected>100 W</option></select></label><label class="check-item field"><input data-sales-field="needHdmi" type="checkbox" checked><span><b>HDMI görüntü gerekli</b></span></label><label class="check-item field"><input data-sales-field="needEthernet" type="checkbox"><span><b>Ethernet gerekli</b></span></label></div>`;
    if(['display_cable','displayport_cable','hdmi_cable','usb_c_hdmi_cable'].includes(categoryId))return `<div class="form-grid sales-requirements"><label class="field"><span>Minimum uzunluk</span><select data-sales-field="minLengthM"><option value="1">1 m</option><option value="1.8" selected>1,8 m</option><option value="2">2 m</option><option value="3">3 m</option></select></label><label class="check-item field"><input data-sales-field="need4k" type="checkbox" checked><span><b>4K veya üstü görüntü gerekli</b><br><small>Port, kablo ve ekranın ortak sınırı geçerlidir.</small></span></label></div>`;
    return '';
  }

  function readSalesRequirements(categoryId){
    const root=document.getElementById('requirementFields');
    const value=name=>root&&root.querySelector(`[data-sales-field="${name}"]`);
    if(categoryId==='usb_c_charger')return {minOutputW:Number(value('minOutputW')?.value||25),minUsbCPorts:Number(value('minUsbCPorts')?.value||1),multiPort:Boolean(value('multiPort')?.checked)};
    if(categoryId==='usb_c_cable')return {minPowerW:Number(value('minPowerW')?.value||60),minLengthM:Number(value('minLengthM')?.value||1),dataTransfer:Boolean(value('dataTransfer')?.checked)};
    if(categoryId==='usb_c_hub')return {minPdPassThroughW:Number(value('minPdPassThroughW')?.value||65),needHdmi:Boolean(value('needHdmi')?.checked),needEthernet:Boolean(value('needEthernet')?.checked)};
    if(['display_cable','displayport_cable','hdmi_cable','usb_c_hdmi_cable'].includes(categoryId))return {minLengthM:Number(value('minLengthM')?.value||1.8),need4k:Boolean(value('need4k')?.checked)};
    return {};
  }

  function injectSalesRequirements(){
    const active=document.querySelector('.category-button[aria-pressed="true"]');
    const categoryId=active&&active.dataset.category;
    const markup=salesRequirementMarkup(categoryId);
    const target=document.getElementById('requirementFields');
    if(!markup||!target||target.querySelector('[data-sales-field]'))return;
    target.innerHTML=markup;
  }

  function wrapMatcher(){
    const matcher=window.Alo186ProductMatcher;
    if(!matcher||matcher.__salesRequirements20260730)return;
    const originalMatch=matcher.match.bind(matcher);
    const originalSummary=matcher.requirementsSummary.bind(matcher);
    matcher.match=(categoryId,requirements={},options={})=>originalMatch(categoryId,{...requirements,...readSalesRequirements(categoryId)},options);
    matcher.requirementsSummary=(categoryId,requirements={})=>originalSummary(categoryId,{...requirements,...readSalesRequirements(categoryId)});
    matcher.__salesRequirements20260730=true;
  }

  wrapMatcher();

  function collectionProducts(collection){
    const now=new Date();
    return collection.productIds.map(productById).filter(product=>product&&catalog.publicAffiliateEligible(product,{now})&&catalog.verificationStatus(product,now).fresh);
  }

  function renderPurchaseCollections(){
    const matcher=document.getElementById('matcher');
    if(!matcher||document.getElementById('purchase-ready-collections'))return;
    const available=purchaseCollections.map(collection=>({...collection,products:collectionProducts(collection)})).filter(collection=>collection.products.length>=2);
    const section=document.createElement('section');
    section.id='purchase-ready-collections';
    section.className='content-section purchase-ready-collections';
    section.innerHTML=`<div class="panel"><div class="section-title"><div><span class="eyebrow">Satın almaya hazır teknik setler</span><h2>Tek ürün değil, birlikte çalışması gereken parçaları karşılaştırın.</h2></div><span class="sales-count">${newProducts.length} yeni doğrulanmış ürün · ${available.length} set</span></div><p>Setler fiyat veya stok sıralaması değildir. Port, güç, protokol ve kablo yönü doğrulandıktan sonra ilgili Amazon ürün sayfalarını ayrı ayrı açar.</p><div class="sales-disclosure"><strong>Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum.</strong> Kullanıcıya ek maliyet yansımaz; her dış CTA satış ortaklığı bağlantısıdır.</div><div class="purchase-collection-grid">${available.map(collection=>`<article class="purchase-collection-card" data-sales-collection="${escapeHtml(collection.id)}"><span class="collection-label">${collection.products.length} parçalık set</span><h3>${escapeHtml(collection.name)}</h3><p>${escapeHtml(collection.description)}</p><ul>${collection.checks.map(item=>`<li>${escapeHtml(item)}</li>`).join('')}</ul><label class="collection-confirm"><input type="checkbox" data-collection-confirm><span>Port, güç ve protokol uyumunu ürün sayfasında yeniden doğrulayacağım.</span></label><div class="collection-products" hidden>${collection.products.map(product=>`<a class="btn btn-primary" data-collection-product="${escapeHtml(product.id)}" href="${escapeHtml(product.url)}" target="_blank" rel="sponsored nofollow noopener"><small>Satış ortaklığı bağlantısı</small>${escapeHtml(product.name)}</a>`).join('')}</div><p class="collection-status" role="status">Onay sonrası ürün bağlantıları açılır.</p></article>`).join('')}</div></div>`;
    matcher.before(section);
    section.querySelectorAll('[data-sales-collection]').forEach(card=>{
      const confirm=card.querySelector('[data-collection-confirm]');
      const products=card.querySelector('.collection-products');
      const status=card.querySelector('.collection-status');
      confirm.addEventListener('change',()=>{
        products.hidden=!confirm.checked;
        status.textContent=confirm.checked?'Teknik sınırlar kabul edildi; ürünleri ayrı ayrı inceleyin.':'Onay sonrası ürün bağlantıları açılır.';
        emit('sales_collection_qualified',{collection:card.dataset.salesCollection,qualified:confirm.checked});
      });
      card.querySelectorAll('[data-collection-product]').forEach(link=>link.addEventListener('click',()=>emit('sales_collection_product_clicked',{collection:card.dataset.salesCollection,product_id:link.dataset.collectionProduct,placement:'purchase_ready_collection'})));
    });
    emit('sales_collection_rendered',{collection_count:available.length,product_count:newProducts.length});
  }

  const companionMap={
    usb_c_charger:['usb_c_cable','powerbank'],usb_c_cable:['usb_c_charger','powerbank'],powerbank:['usb_c_charger','usb_c_cable'],usb_c_hub:['usb_c_charger','display_cable'],display_cable:['usb_c_hub','usb_c_charger'],displayport_cable:['hdmi_cable','usb_c_hub'],hdmi_cable:['displayport_cable','usb_c_hub'],usb_c_hdmi_cable:['usb_c_charger','usb_c_cable']
  };

  function renderCompanions(categoryId){
    let bar=document.getElementById('sales-companion-bar');
    const companions=companionMap[categoryId]||[];
    if(!companions.length){if(bar)bar.hidden=true;return;}
    if(!bar){
      bar=document.createElement('aside');
      bar.id='sales-companion-bar';
      bar.className='sales-companion-bar';
      bar.setAttribute('aria-live','polite');
      document.body.appendChild(bar);
    }
    bar.hidden=false;
    bar.innerHTML=`<div><b>Seti tamamlayın</b><span>Bu seçimle birlikte sık gereken teknik parçalar:</span></div><div>${companions.map(id=>{const category=catalog.getCategory(id);return category?`<button type="button" data-companion-category="${escapeHtml(id)}">${escapeHtml(category.name)}</button>`:'';}).join('')}</div>`;
    bar.querySelectorAll('[data-companion-category]').forEach(button=>button.addEventListener('click',()=>{
      document.querySelector(`[data-category="${button.dataset.companionCategory}"]`)?.click();
      document.getElementById('matcher')?.scrollIntoView({behavior:'smooth',block:'start'});
      emit('sales_cross_sell_clicked',{from_category:categoryId,to_category:button.dataset.companionCategory});
    }));
  }

  const checklist = [
    ['Sürekli ve kalkış gücü', 'Hesap sonucundaki asgari sürekli W ve kalkış W değerlerinin ikisini de ürün etiketinde doğrulayın.'],
    ['Gerilim, frekans ve faz', '230 V / 50 Hz ve monofaze ihtiyacınızı doğrulayın; trifaze seçim profesyonel projelendirme gerektirir.'],
    ['CO ve dış ortam güvenliği', 'Yakıtlı jeneratörü yalnız açık havada kullanın; CO algılama özelliği temel yerleşim kurallarının yerine geçmez.'],
    ['Bağlantı biçimi', 'Bina devreleri için prize ters besleme yapmayın; uygun transfer sistemi yetkili elektrikçi tarafından kurulmalıdır.'],
    ['İşletme koşulları', 'Gürültü, yakıt, çalışma süresi, rakım/sıcaklık düşümü, bakım ve yetkili servis koşullarını karşılaştırın.']
  ];

  function selectedGenerator() {
    const active = document.querySelector('[data-category="generator"][aria-pressed="true"]');
    return Boolean(active);
  }

  function checklistMarkup(marker) {
    return `<div class="guide-list generator-guide-extension" data-generator-guide="${marker}">${checklist.map(([title, text]) => `<div class="guide-item"><b>${escapeHtml(title)}</b><span>${escapeHtml(text)}</span></div>`).join('')}</div>`;
  }

  function injectRequirementChecklist() {
    if (!selectedGenerator()) return;
    const target = document.getElementById('requirementFields');
    if (!target || target.querySelector('[data-generator-guide]')) return;
    target.insertAdjacentHTML('beforeend', checklistMarkup('requirements'));
  }

  function injectResultChecklist() {
    if (!selectedGenerator()) return;
    const target = document.getElementById('guideResult');
    if (!target || target.querySelector('[data-generator-guide]')) return;
    const heading = target.querySelector('h3');
    if (heading) heading.insertAdjacentHTML('afterend', checklistMarkup('result'));
    else target.insertAdjacentHTML('afterbegin', checklistMarkup('result'));
  }

  function enablePostCalculationAffiliate() {
    const params = new URLSearchParams(location.search);
    if (!selectedGenerator() || params.get('hesaplandi') !== '1') return;
    const target = document.getElementById('guideResult');
    if (!target || !catalog) return;

    target.querySelectorAll('.decision-gate,.actions').forEach(node => node.remove());
    const searchUrl = catalog.searchUrl('generator');
    target.insertAdjacentHTML('beforeend', `<div class="decision-gate generator-post-calc"><b>Hesaplama tamamlandı; yine de ürün etiketini doğrulayın.</b><p>ALO186 marka veya model onayı vermez. Sonuçtaki sürekli ve kalkış W değerlerini, gerilim/fazı, CO güvenliğini, gürültüyü, yakıtı ve servis koşullarını satıcının güncel sayfasında yeniden kontrol edin.</p><label class="check-item"><input type="checkbox" data-generator-confirm><span><b>Hesap sonucumu ve yukarıdaki teknik kontrol listesini ürün sayfasında yeniden doğrulayacağım.</b><br><small>Fiyat, stok, satıcı, garanti ve nihai teknik özellik yalnız Amazon’un güncel sayfasında doğrulanır.</small></span></label><div class="actions"><a class="btn btn-primary disabled-link" data-generator-amazon aria-disabled="true" tabindex="-1" href="${escapeHtml(searchUrl)}" target="_blank" rel="sponsored nofollow noopener">Amazon’da teknik ifadelerle ara</a></div></div>`);

    const confirm = target.querySelector('[data-generator-confirm]');
    const link = target.querySelector('[data-generator-amazon]');
    if (!confirm || !link) return;
    confirm.addEventListener('change', () => {
      const enabled = confirm.checked;
      link.classList.toggle('disabled-link', !enabled);
      link.setAttribute('aria-disabled', enabled ? 'false' : 'true');
      link.tabIndex = enabled ? 0 : -1;
      emit('generator_affiliate_checklist_acknowledged', { acknowledged: enabled });
    });
    link.addEventListener('click', event => {
      if (link.getAttribute('aria-disabled') === 'true') {
        event.preventDefault();
        return;
      }
      emit('affiliate_category_clicked', { category: 'generator', placement: 'after_generator_calculation' });
    });
  }

  function afterSelection() {
    queueMicrotask(() => {
      injectSalesRequirements();
      injectRequirementChecklist();
      const active=document.querySelector('.category-button[aria-pressed="true"]');
      if(active)renderCompanions(active.dataset.category);
    });
  }

  function afterMatch() {
    queueMicrotask(() => {
      injectResultChecklist();
      enablePostCalculationAffiliate();
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    renderPurchaseCollections();
    const grid = document.getElementById('categoryGrid');
    const match = document.getElementById('matchBtn');
    if (grid) grid.addEventListener('click', event => {
      if(event.target.closest('[data-category]'))afterSelection();
    });
    if (match) match.addEventListener('click', afterMatch);
    injectSalesRequirements();
    injectRequirementChecklist();
    const active=document.querySelector('.category-button[aria-pressed="true"]');
    if(active)renderCompanions(active.dataset.category);
  });
})();
