const assert=require('assert');
const fs=require('fs');
const path=require('path');

const repoRoot=path.resolve(__dirname,'../..');
const articles=[
  {
    slug:'ev-sarj-cihazi-icin-ev-tesisati-uygun-mu',
    required:['EPDK','IEC 60364-7-722','RDC-DD','yetkili'],
    cta:'/hesaplama/ev-sarj-suresi/'
  },
  {
    slug:'ges-elektrik-kesintisinde-calisir-mi',
    required:['anti-islanding','ada modu','batarya','yetkili'],
    cta:'/urun-rehberleri/ges-malzemeleri'
  },
  {
    slug:'jenerator-transfer-salteri-neden-gerekir',
    required:['geri besleme','transfer','erkek–erkek','yetkili'],
    cta:'/isletme-surekliligi'
  },
  {
    slug:'elektrik-kesintisi-cihaz-hasari-edas-basvurusu',
    required:['EPDK','10 iş günü','servis raporu','dağıtım şirketi'],
    cta:'/edas-bul'
  },
  {
    slug:'prizde-topraklama-var-mi-priz-test-cihazi',
    required:['toprak elektrodu','çevrim empedansı','RCD','yetkili'],
    cta:'/karar-motoru'
  },
  {
    slug:'saf-sinus-modifiye-sinus-inverter-farki',
    required:['aktif PFC','kalkış gücü','saf sinüs','tıbbi cihaz'],
    cta:'/hesaplama/ups-suresi/'
  },
  {
    slug:'kacak-akim-rolesi-tip-a-tip-ac-farki',
    required:['Tip AC','Tip A','RDC-DD','30 mA','yetkili elektrikçi'],
    cta:'/hesaplama/ev-sarj-uygunluk/'
  },
  {
    slug:'ev-tipi-enerji-depolama-kac-kwh-olmali',
    required:['kritik yük','kWh','kW','kullanılabilir kapasite','BMS'],
    cta:'/hesaplama/inverter-uygunluk/'
  },
  {
    slug:'harmonik-nedir-thd-cihazlari-nasil-etkiler',
    required:['THDv','THDi','nötr','PCC','aktif harmonik filtre'],
    cta:'/isletme-surekliligi'
  }
];

for(const article of articles){
  const file=path.join(repoRoot,'alo186/haberler',article.slug,'index.html');
  assert(fs.existsSync(file),`Makale bulunamadı: ${article.slug}`);
  const html=fs.readFileSync(file,'utf8');
  const canonical=`https://www.alo186.com/haberler/${article.slug}`;
  assert(html.toLowerCase().includes('<!doctype html>'));
  assert(html.includes(`rel="canonical" href="${canonical}"`),`Canonical eksik: ${article.slug}`);
  assert(html.includes('meta name="description"'),`Description eksik: ${article.slug}`);
  assert(html.includes('application/ld+json'),`JSON-LD eksik: ${article.slug}`);
  const jsonLd=[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  assert(jsonLd.length>0,`JSON-LD bulunamadı: ${article.slug}`);
  for(const match of jsonLd){
    const parsed=JSON.parse(match[1]);
    const graph=parsed['@graph']||[parsed];
    assert(graph.some(item=>item['@type']==='Article'),`Article schema eksik: ${article.slug}`);
    assert(graph.some(item=>item['@type']==='FAQPage'),`FAQPage schema eksik: ${article.slug}`);
  }
  assert(html.includes('../alo186-article.css'),`Ortak CSS eksik: ${article.slug}`);
  assert(html.includes(article.cta),`İç CTA eksik: ${article.slug}`);
  assert(html.includes('Bağımsız bilgi'),`Bağımsızlık ifadesi eksik: ${article.slug}`);
  assert(html.includes('Son doğrulama: 28 Temmuz 2026'),`Doğrulama tarihi eksik: ${article.slug}`);
  assert(html.includes('Kaynaklar ve doğrulama'),`Görünür kaynak bölümü eksik: ${article.slug}`);
  assert(!/<form\b/i.test(html),`Makale kişisel veri/form istememeli: ${article.slug}`);
  assert(!/amazon\.com\.tr/i.test(html),`Teknik makalede doğrudan Amazon URL'si olmamalı: ${article.slug}`);
  assert(!/fiyatı\s+\d|stokta|puanı\s+\d/i.test(html),`Doğrulanmamış ticari bilgi riski: ${article.slug}`);
  assert(!/kesinlikle güvenli|garanti eder|kesin çözer/i.test(html),`Aşırı kesin güvenlik iddiası riski: ${article.slug}`);
  for(const text of article.required){
    assert(html.toLocaleLowerCase('tr').includes(text.toLocaleLowerCase('tr')),`Zorunlu güvenlik/teknik ifade eksik (${text}): ${article.slug}`);
  }
  const h1=(html.match(/<h1\b/g)||[]).length;
  assert.strictEqual(h1,1,`Tek H1 olmalı: ${article.slug}`);
}

const css=path.join(repoRoot,'alo186/haberler/alo186-article.css');
assert(fs.existsSync(css),'Makale CSS dosyası eksik.');
const cssText=fs.readFileSync(css,'utf8');
assert(cssText.includes('@media(max-width:820px)'), 'Mobil breakpoint eksik.');
assert(cssText.includes(':focus-visible'), 'Klavye odak stili eksik.');
assert(cssText.includes('prefers-reduced-motion'), 'Azaltılmış hareket desteği eksik.');

const sitemap=fs.readFileSync(path.join(repoRoot,'alo186/sitemap.xml'),'utf8');
const routing=JSON.parse(fs.readFileSync(path.join(repoRoot,'alo186/deployment/routing-manifest.json'),'utf8'));
const portal=fs.readFileSync(path.join(repoRoot,'alo186/index.html'),'utf8');
for(const article of articles){
  const canonicalPath=`/haberler/${article.slug}`;
  assert(sitemap.includes(`https://www.alo186.com${canonicalPath}`),`Sitemap eksik: ${article.slug}`);
  assert(routing.routes.some(route=>route.canonicalPath===canonicalPath&&route.type==='article'),`Routing manifest eksik: ${article.slug}`);
  assert(portal.includes(`href="${canonicalPath}"`),`Portal kartı eksik: ${article.slug}`);
}

console.log('ALO186 içerik otoritesi makaleleri SEO, AEO, JSON-LD, erişilebilirlik, routing ve güvenlik testlerini geçti.');
