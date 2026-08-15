(function () {
  "use strict";
  const catalog = window.ALO186NiMHBatteryChargerCatalogV242;
  if (!catalog) return;
  const readinessIds = ["gateChemistry", "gateCondition", "gateInput", "gateSlots", "gateDry", "gateNotCritical", "gateVariant"];
  const commerceIds = ["gateNeed", "gateAffiliate"];
  const status = document.getElementById("gateStatus");
  const links = Array.from(document.querySelectorAll("[data-affiliate-asin]"));
  function checked(id) { const el = document.getElementById(id); return Boolean(el && el.checked); }
  function lock(message) {
    links.forEach(function (link) { link.removeAttribute("href"); link.setAttribute("aria-disabled", "true"); link.dataset.state = "locked"; });
    status.textContent = message;
  }
  function update() {
    if (!readinessIds.every(checked)) return lock("Önce pil kimyası, fiziksel durum, giriş gücü, yuva kuralı, ortam ve varyant kontrollerini tamamlayın.");
    if (!commerceIds.every(checked)) return lock("Teknik kontrol geçti. Gerçek ihtiyaç ve satış ortaklığı açıklaması onaylanmadan mağaza bağlantısı açılmaz.");
    if (catalog.category.affiliatePolicy !== "after_tool" || catalog.category.professionalOnly) return lock("Bu kapsam doğrudan ürün bağlantısına uygun değildir.");
    let opened = 0;
    links.forEach(function (link) {
      const product = catalog.products.find(function (item) { return item.asin === link.dataset.affiliateAsin; });
      const url = product ? catalog.amazonProductUrl(product, new Date()) : null;
      if (!url) { link.removeAttribute("href"); link.setAttribute("aria-disabled", "true"); link.dataset.state = "stale"; return; }
      link.href = url;
      link.rel = "sponsored nofollow noopener";
      link.target = "_blank";
      link.removeAttribute("aria-disabled");
      link.dataset.state = "open";
      opened += 1;
    });
    status.textContent = opened ? "Kontroller tamamlandı. Amazon Türkiye sayfasında ASIN, pil kimyası, fiş tipi ve kutu içeriğini yeniden doğrulayın." : "Ürün doğrulaması güncel değil; mağaza bağlantıları kapalı.";
  }
  readinessIds.concat(commerceIds).forEach(function (id) { const el = document.getElementById(id); if (el) el.addEventListener("change", update); });
  lock("Mağaza bağlantıları güvenlik ve ihtiyaç kontrolleri tamamlanana kadar kapalıdır.");
})();
