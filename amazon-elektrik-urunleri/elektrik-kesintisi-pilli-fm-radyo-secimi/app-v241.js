(function () {
  "use strict";

  const catalog = window.ALO186BatteryFmRadioCatalogV241;
  if (!catalog) return;

  const readinessIds = [
    "gateDry",
    "gateBattery",
    "gateReception",
    "gateCord",
    "gateNotCritical",
    "gateVariant"
  ];
  const commerceIds = ["gateNeed", "gateAffiliate"];
  const allIds = readinessIds.concat(commerceIds);
  const status = document.getElementById("gateStatus");
  const links = Array.from(document.querySelectorAll("[data-affiliate-asin]"));

  function checked(id) {
    const element = document.getElementById(id);
    return Boolean(element && element.checked);
  }

  function lockLinks(message) {
    links.forEach(function (link) {
      link.removeAttribute("href");
      link.setAttribute("aria-disabled", "true");
      link.dataset.state = "locked";
    });
    status.textContent = message;
  }

  function update() {
    const toolPassed = readinessIds.every(checked);
    const commercePassed = commerceIds.every(checked);

    if (!toolPassed) {
      lockLinks("Önce pil, FM çekimi, kuru ortam, fiziksel durum ve model kontrollerini tamamlayın.");
      return;
    }
    if (!commercePassed) {
      lockLinks("Teknik kontrol geçti. Gerçek ihtiyaç ve satış ortaklığı açıklaması onaylanmadan mağaza bağlantısı açılmaz.");
      return;
    }
    if (catalog.category.affiliatePolicy !== "after_tool" || catalog.category.professionalOnly) {
      lockLinks("Bu kapsam doğrudan ürün bağlantısına uygun değildir.");
      return;
    }

    let opened = 0;
    links.forEach(function (link) {
      const product = catalog.products.find(function (item) {
        return item.asin === link.dataset.affiliateAsin;
      });
      const url = product ? catalog.amazonProductUrl(product, new Date()) : null;
      if (!url) {
        link.removeAttribute("href");
        link.setAttribute("aria-disabled", "true");
        link.dataset.state = "stale";
        return;
      }
      link.href = url;
      link.rel = "sponsored nofollow noopener";
      link.target = "_blank";
      link.removeAttribute("aria-disabled");
      link.dataset.state = "open";
      opened += 1;
    });
    status.textContent = opened
      ? "Kontroller tamamlandı. Amazon Türkiye bağlantıları açıldı; ürün sayfasında tam model ve ASIN'i yeniden doğrulayın."
      : "Ürün doğrulaması güncel değil; mağaza bağlantıları kapalı.";
  }

  allIds.forEach(function (id) {
    const element = document.getElementById(id);
    if (element) element.addEventListener("change", update);
  });

  lockLinks("Mağaza bağlantıları güvenlik ve ihtiyaç kontrolleri tamamlanana kadar kapalıdır.");
})();
