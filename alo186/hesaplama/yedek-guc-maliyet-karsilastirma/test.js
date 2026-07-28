"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const core = require("./core.js");

const baseAssumptions = {
  years: 5,
  outagesPerYear: 10,
  hoursPerOutage: 2,
  impactPerHour: 1000,
  continuousW: 500,
  scope: "plug",
  phase: "single",
  medical: false
};

function option(id, values = {}) {
  return {
    id,
    enabled: true,
    purchase: 10000,
    installation: 0,
    annualMaintenance: 0,
    annualOperating: 0,
    replacementYears: 0,
    replacementCost: 0,
    coveragePercent: 80,
    ...values
  };
}

assert.strictEqual(core.normalizedReplacementInterval(0.000001), 0.5, "Çok küçük yenileme aralığı güvenli alt sınıra çekilmeli");
assert.strictEqual(core.replacementCount(5, 5), 0, "Analiz döneminin sonundaki yenileme gereksiz sayılmamalı");
assert.strictEqual(core.replacementCount(6, 5), 1, "Dönem içindeki yenileme sayılmalı");

const replacementAwarePayback = core.calculatePaybackYears({
  horizonYears: 2,
  upfront: 10000,
  annualAvoidedImpact: 10000,
  annualRecurring: 0,
  replacementYears: 0.5,
  replacementCost: 2000
});
assert(replacementAwarePayback > 1.3 && replacementAwarePayback < 1.5, "Geri ödeme, dönem içindeki yenileme harcamalarını içermeli");

const ranked = core.compare(baseAssumptions, [
  option("ups", { purchase: 20000, coveragePercent: 90 }),
  option("powerStation", { purchase: 35000, coveragePercent: 80 })
]);
assert.strictEqual(ranked.ok, true);
assert.strictEqual(ranked.best.id, "ups", "Daha yüksek net farkı veren çözüm ilk sırada olmalı");
assert.strictEqual(ranked.noBuy, false);
assert.strictEqual(ranked.affiliateEligible, true, "Düşük riskli taşınabilir sonuç affiliate kapısına uygun olmalı");

const noBuy = core.compare({ ...baseAssumptions, impactPerHour: 10 }, [
  option("ups", { purchase: 100000 }),
  option("powerStation", { purchase: 120000 })
]);
assert.strictEqual(noBuy.ok, true);
assert.strictEqual(noBuy.noBuy, true, "Maliyet-fayda negatif olduğunda satın almama sonucu çıkmalı");
assert.strictEqual(noBuy.affiliateEligible, false, "Satın almama sonucunda affiliate kapısı açılmamalı");

const explicitZeroImpact = core.compare({ ...baseAssumptions, impactPerHour: 0 }, [
  option("ups", { purchase: 20000 }),
  option("powerStation", { purchase: 25000 })
]);
assert.strictEqual(explicitZeroImpact.ok, true, "Kullanıcının açıkça girdiği sıfır etki kabul edilmeli");
assert.strictEqual(explicitZeroImpact.noBuy, true);

const missingImpact = core.compare({ ...baseAssumptions, impactPerHour: null }, [
  option("ups", { purchase: 20000 }),
  option("powerStation", { purchase: 25000 })
]);
assert.strictEqual(missingImpact.ok, false, "Boş bırakılan saatlik etki sıfır gibi yorumlanmamalı");
assert(missingImpact.errors.some((message) => message.includes("saatlik tahmini etkisini")));

const fixed = core.compare({ ...baseAssumptions, scope: "fixed" }, [
  option("ups", { purchase: 20000 }),
  option("powerStation", { purchase: 25000 })
]);
assert.strictEqual(fixed.professional, true);
assert.strictEqual(fixed.affiliateEligible, false, "Sabit tesisat sonucunda affiliate kapısı kapalı olmalı");

const medical = core.compare({ ...baseAssumptions, medical: true }, [
  option("ups", { purchase: 20000 }),
  option("powerStation", { purchase: 25000 })
]);
assert.strictEqual(medical.professional, true);
assert.strictEqual(medical.affiliateEligible, false, "Tıbbi yükte ticari rota kapalı olmalı");

const generator = core.compare(baseAssumptions, [
  option("generator", { purchase: 10000, annualMaintenance: 500, annualOperating: 500, coveragePercent: 95 }),
  option("ups", { purchase: 90000, coveragePercent: 20 })
]);
assert.strictEqual(generator.best.id, "generator");
assert.strictEqual(generator.professional, true, "Jeneratör sonucu profesyonel doğrulama gerektirmeli");
assert.strictEqual(generator.affiliateEligible, false, "Jeneratör için affiliate gösterilmemeli");

const invalid = core.compare(baseAssumptions, [
  option("ups", { purchase: 0 }),
  option("powerStation", { purchase: 0 })
]);
assert.strictEqual(invalid.ok, false, "Kullanıcı maliyet verisi olmadan sıfır maliyet sonucu üretilmemeli");
assert(invalid.errors.some((message) => message.includes("satın alma, kurulum")));

const replacementOnly = core.compare(baseAssumptions, [
  option("ups", { purchase: 0, replacementYears: 10, replacementCost: 50000 }),
  option("powerStation", { purchase: 20000 })
]);
assert.strictEqual(replacementOnly.ok, false, "Analiz dönemi dışında kalan yenileme bedeli tek başına maliyet temeli sayılmamalı");

const stored = core.sanitizeForStorage({ ...baseAssumptions, medical: true }, [option("ups")], "2026-07-28T04:00:00.000Z");
assert.strictEqual(Object.prototype.hasOwnProperty.call(stored.assumptions, "medical"), false, "Tıbbi seçim kalıcı depolamaya yazılmamalı");

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const app = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const coreSource = fs.readFileSync(path.join(__dirname, "core.js"), "utf8");
assert(html.includes('rel="canonical" href="https://www.alo186.com/hesaplama/yedek-guc-maliyet-karsilastirma/"'));
assert(html.includes("Reklam / satış ortaklığı açıklaması"));
assert(html.includes("Güncel fiyat iddiası yok"));
assert(html.includes("satın almamanın"));
assert(html.includes("ALO186 örnek veya ortalama fiyat doldurmaz"));
assert(!/amazon\.(com|com\.tr)/i.test(html), "Araçta doğrudan Amazon URL'si olmamalı");
assert(!/<input[^>]+type="(?:text|email|tel)"/i.test(html), "Kişisel veri veya serbest metin alanı bulunmamalı");
assert(!/<input[^>]+(?:id|name)="(?:name|email|phone|address|company|contact|note)"/i.test(html), "Kimlik veya iletişim alanı bulunmamalı");
assert(app.includes("STORAGE_TTL_MS = 30 * 24 * 60 * 60 * 1000"));
assert(app.includes('return raw === "" ? null : Number(raw)'));
assert(coreSource.includes("delete assumptions.medical"));
assert(app.includes("backup_tco_no_buy_shown"));
assert(app.includes("backup_tco_product_center_opened"));

console.log("ALO186 yedek güç TCO testleri başarılı.");