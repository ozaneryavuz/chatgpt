'use strict';

const fs = require('node:fs');
const path = require('node:path');
const catalog = require(path.resolve(__dirname, '../urun-eslestirme/catalog.js'));

const nowInput = process.env.ALO186_REPORT_NOW || new Date().toISOString();
const now = new Date(nowInput);
if (Number.isNaN(now.getTime())) throw new Error(`Geçersiz ALO186_REPORT_NOW: ${nowInput}`);

const categoryTargets = {
  powerbank: 8, usb_c_charger: 8, usb_c_cable: 12, usb_c_hub: 8, display_cable: 8,
  surge_strip: 8, mini_ups: 6, emergency_light: 8, smoke_alarm: 5, co_alarm: 5,
  power_station: 5, generator: 3, inverter: 4, smart_plug: 6, ev_cable: 6,
  ups_battery: 6, extension_cord: 6, outlet_tester: 0
};

const demandBoost = {
  usb_c_cable: 24, usb_c_charger: 22, powerbank: 20, usb_c_hub: 18,
  display_cable: 16, emergency_light: 14, mini_ups: 13, smart_plug: 12,
  ev_cable: 11, surge_strip: 10, ups_battery: 8, extension_cord: 7,
  smoke_alarm: 6, co_alarm: 5, power_station: 4, inverter: 2, generator: 1
};

const verificationStatus = typeof catalog.verificationStatus === 'function'
  ? (product) => catalog.verificationStatus(product, now)
  : (product) => {
      const checked = new Date(product.verifiedAt);
      const ageDays = Number.isNaN(checked.getTime()) ? null : Math.max(0, Math.floor((now - checked) / 86400000));
      return { fresh: ageDays !== null && ageDays <= 45, ageDays };
    };

const publicAffiliateEligible = typeof catalog.publicAffiliateEligible === 'function'
  ? (product) => catalog.publicAffiliateEligible(product, { now })
  : (product) => {
      const category = catalog.categories.find((item) => item.id === product.category);
      return Boolean(category && category.affiliatePolicy === 'verified_direct' && verificationStatus(product).fresh);
    };

function preferredBatch(category) {
  if (category.affiliatePolicy === 'verified_direct') return { min: 8, max: 15, type: 'verified_direct' };
  if (category.affiliatePolicy === 'after_tool') return { min: 3, max: 8, type: 'tool_gated' };
  return { min: 0, max: 0, type: 'professional_only' };
}

function gateDescription(category) {
  if (category.affiliatePolicy === 'verified_direct') {
    return 'Düşük riskli ürün; doğrulanmış teknik alan, açık satış ortaklığı etiketi ve taze kayıtla doğrudan ürün merkezinde yayımlanabilir.';
  }
  if (category.affiliatePolicy === 'after_tool') {
    return 'Ürün kaydı Knowledge Graph’a alınabilir; mağaza yolu yalnız ücretsiz uygunluk aracı ve gerçek ihtiyaç kanıtından sonra açılır.';
  }
  return 'Tüketici satın alma CTA’sı açılmaz; yalnız profesyonel ölçüm, hizmet veya güvenli yönlendirme geliştirilir.';
}

const categories = catalog.categories.map((category) => {
  const products = catalog.products.filter((product) => product.category === category.id && product.status === 'verified_listing');
  const freshProducts = products.filter((product) => verificationStatus(product).fresh);
  const staleProducts = products.filter((product) => !verificationStatus(product).fresh);
  const publicProducts = freshProducts.filter(publicAffiliateEligible);
  const target = Object.prototype.hasOwnProperty.call(categoryTargets, category.id)
    ? categoryTargets[category.id]
    : category.affiliatePolicy === 'verified_direct' ? 8 : category.affiliatePolicy === 'after_tool' ? 4 : 0;
  const deficit = Math.max(0, target - freshProducts.length);
  const score = (category.affiliatePolicy === 'verified_direct' ? 45 : category.affiliatePolicy === 'after_tool' ? 24 : -80)
    + (demandBoost[category.id] || 0) + staleProducts.length * 28 + deficit * 12;
  return {
    id: category.id,
    name: category.name,
    affiliatePolicy: category.affiliatePolicy,
    risk: category.risk,
    verifiedCount: products.length,
    freshCount: freshProducts.length,
    staleCount: staleProducts.length,
    publicDirectCount: publicProducts.length,
    toolGatedCount: freshProducts.length - publicProducts.length,
    target,
    deficit,
    score,
    preferredBatch: preferredBatch(category),
    safetyGate: gateDescription(category),
    actionType: staleProducts.length > 0 ? 'reverify_stale' : deficit > 0 ? 'grow_catalog' : 'optimize_conversion'
  };
});

const topActions = categories
  .filter((category) => category.target > 0 || category.staleCount > 0)
  .sort((a, b) => b.score - a.score || b.deficit - a.deficit || a.name.localeCompare(b.name, 'tr'))
  .slice(0, 3)
  .map((category, index) => ({
    priority: index + 1,
    categoryId: category.id,
    categoryName: category.name,
    actionType: category.actionType,
    currentFreshProducts: category.freshCount,
    targetProducts: category.target,
    minimumNeeded: category.deficit,
    staleProducts: category.staleCount,
    preferredBatch: category.preferredBatch,
    safetyGate: category.safetyGate,
    implementation: category.affiliatePolicy === 'verified_direct'
      ? 'ASIN, marka, model/MPN, doğrulama tarihi, teknik alanlar ve sınırlar doğrulandıktan sonra Product, Brand, DefinedTerm, ItemList ve uygun olduğunda ProductGroup/isVariantOf ilişkileri ekle. Offer, fiyat, stok, puan ve garanti yayımlama.'
      : 'Ürün kayıtlarını teknik uygunluk aracına bağla; public Product düğümünde doğrudan mağaza URL’sini ancak nitelikli geçiş sözleşmesi izin veriyorsa kullan. Mevcut ürün yeterliyse satın almama sonucunu koru.'
  }));

const freshProducts = catalog.products.filter((product) => product.status === 'verified_listing' && verificationStatus(product).fresh);
const publicProducts = freshProducts.filter(publicAffiliateEligible);
const staleProducts = catalog.products.filter((product) => product.status === 'verified_listing' && !verificationStatus(product).fresh);

const report = {
  schemaVersion: 1,
  generatedAt: now.toISOString(),
  timezone: 'Europe/Istanbul',
  schedule: 'Her gün 09:15',
  trackingIssue: 301,
  catalogVerifiedAt: catalog.verifiedAt || null,
  verificationMaxAgeDays: catalog.verificationMaxAgeDays || 45,
  summary: {
    categories: catalog.categories.length,
    totalVerifiedProducts: catalog.products.filter((product) => product.status === 'verified_listing').length,
    freshProducts: freshProducts.length,
    staleProducts: staleProducts.length,
    publicDirectProducts: publicProducts.length,
    toolGatedProducts: freshProducts.length - publicProducts.length,
    professionalOnlyCategories: catalog.categories.filter((category) => category.affiliatePolicy === 'professional_only').length
  },
  topActions,
  categories,
  guardrails: {
    affiliateDisclosureRequired: true,
    sponsoredRelRequired: true,
    noBuyOutcomeRequired: true,
    hazardCommerceClosed: true,
    officialAffiliationClaimed: false,
    offerSchemaAllowed: false,
    unverifiedCommercialFieldsAllowed: false,
    excludedCommercialFields: ['price', 'stock', 'rating', 'review', 'seller', 'delivery', 'warranty', 'availability']
  }
};

function renderMarkdown(payload) {
  const date = new Intl.DateTimeFormat('tr-TR', {
    timeZone: 'Europe/Istanbul', year: 'numeric', month: '2-digit', day: '2-digit'
  }).format(now);
  const lines = [
    '<!-- alo186-daily-affiliate-growth -->',
    `## ALO186 günlük satış ve affiliate büyüme raporu — ${date}`,
    '',
    `- Taze doğrulanmış ürün: **${payload.summary.freshProducts}**`,
    `- Doğrudan yayımlanabilir ürün: **${payload.summary.publicDirectProducts}**`,
    `- Teknik uygunluk kapılı ürün: **${payload.summary.toolGatedProducts}**`,
    `- Yeniden doğrulanması gereken ürün: **${payload.summary.staleProducts}**`,
    '',
    '### En yüksek potansiyelli 3 aksiyon'
  ];
  for (const action of payload.topActions) {
    const batch = action.preferredBatch.max > 0
      ? `${action.preferredBatch.min}–${action.preferredBatch.max} ${action.preferredBatch.type === 'verified_direct' ? 'düşük riskli doğrulanmış ürün' : 'teknik uygunluk kapılı ürün'}`
      : 'Ürün ekleme yerine profesyonel hizmet dönüşümü';
    lines.push('', `${action.priority}. **${action.categoryName}**`,
      `   - Mevcut taze ürün: ${action.currentFreshProducts} · hedef: ${action.targetProducts} · asgari açık: ${action.minimumNeeded} · eski kayıt: ${action.staleProducts}`,
      `   - Tercih edilen doğrulama partisi: ${batch}`,
      `   - Güven kapısı: ${action.safetyGate}`,
      `   - Uygulama: ${action.implementation}`);
  }
  lines.push('', '### Zorunlu yayın sınırları',
    '- Amazon satış ortaklığı ilişkisi görünür olmalı ve dış bağlantılar `rel="sponsored nofollow noopener"` taşımalı.',
    '- Fiyat, stok, puan, yorum, satıcı, teslimat, garanti veya `Offer` schema yayımlanmamalı.',
    '- Tehlike, sabit tesisat belirsizliği ve uyumsuz teknik etiketlerde ticari yol kapanmalı.',
    '- Mevcut ürün güvenli ve yeterliyse satın almama sonucu korunmalı.', '',
    '_Bu rapor ürün eklemez; doğrulanacak ilk üç satış işini ve güven kapılarını issue #301 için önceliklendirir._');
  return `${lines.join('\n')}\n`;
}

function argValue(flag) {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : null;
}

const jsonPath = argValue('--json');
const markdownPath = argValue('--markdown');
const markdown = renderMarkdown(report);
if (jsonPath) fs.writeFileSync(jsonPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
if (markdownPath) fs.writeFileSync(markdownPath, markdown, 'utf8');
if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, markdown, 'utf8');
process.stdout.write(markdown);

module.exports = { report, renderMarkdown };
