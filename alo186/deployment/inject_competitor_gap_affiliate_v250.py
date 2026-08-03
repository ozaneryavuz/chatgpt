from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from .competitor_gap_affiliate_v250 import (
        apply_competitor_gap_affiliate_v250 as _apply_competitor_gap_affiliate_v250,
    )
    from .materialize_location_pages_v251 import materialize as _materialize_location_pages
except ImportError:
    from competitor_gap_affiliate_v250 import (
        apply_competitor_gap_affiliate_v250 as _apply_competitor_gap_affiliate_v250,
    )
    from materialize_location_pages_v251 import materialize as _materialize_location_pages

VERSION = 251
PORTAL_SSR_MARKER = 'data-alo186-decision-ssr-v251="true"'
AI_AGENTS = (
    "OAI-SearchBot",
    "GPTBot",
    "ChatGPT-User",
    "PerplexityBot",
    "ClaudeBot",
    "anthropic-ai",
    "Bytespider",
    "Google-Extended",
)


def robots(site: Path) -> dict[str, object]:
    """Write an explicit, auditable crawler policy while preserving sitemap rows."""

    path = Path(site) / "robots.txt"
    old = path.read_text(encoding="utf-8") if path.is_file() else ""
    sitemaps: list[str] = []
    for line in old.splitlines():
        normalized = line.strip()
        if normalized.lower().startswith("sitemap:") and normalized not in sitemaps:
            sitemaps.append(normalized)
    if not sitemaps:
        sitemaps = ["Sitemap: https://alo186.com/sitemap.xml"]

    rows: list[str] = []
    for agent in AI_AGENTS:
        rows.extend((f"User-agent: {agent}", "Allow: /", ""))
    rows.extend(("User-agent: *", "Allow: /", ""))
    rows.extend(sitemaps)
    path.write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")
    return {
        "explicitAllow": list(AI_AGENTS),
        "sitemaps": sitemaps,
        "trainingAndSearchPoliciesKeptSeparate": True,
    }


def _ensure_portal_ssr(site: Path) -> dict[str, object]:
    portal = next(
        (
            path
            for path in (
                Path(site) / "elektrik-portali/index.html",
                Path(site) / "index.html",
            )
            if path.is_file()
        ),
        None,
    )
    if portal is None:
        raise FileNotFoundError("Akıllı Yol SSR portalı bulunamadı")
    source = portal.read_text(encoding="utf-8", errors="strict")
    required = ("ALO186 Akıllı Yol", "Kişisel hazırlık kontrolü")
    if PORTAL_SSR_MARKER in source and all(token in source for token in required):
        return {
            "route": "/" + portal.relative_to(site).parent.as_posix().strip("/"),
            "status": "already-present",
            "decisionBranches": 4,
            "preparationChecks": 5,
            "javascriptRequired": False,
        }
    section = f'''
<section id="alo186-akilli-yol" class="panel" {PORTAL_SSR_MARKER} aria-labelledby="alo186-akilli-yol-baslik">
  <p class="eyebrow">JS çalışmadan okunabilen karar özeti</p>
  <h2 id="alo186-akilli-yol-baslik">ALO186 Akıllı Yol</h2>
  <p><strong>Önce tehlikeyi, sonra kesintinin kapsamını, en son hazırlık veya ürün ihtiyacını ayırın.</strong> Bu statik karar ağacı arıza teşhisi yapmaz ve kayıt oluşturmaz.</p>
  <ol class="checklist">
    <li><strong>Aktif tehlike:</strong> Elektrik çarpması, yangın, duman, kıvılcım veya kopmuş iletken varsa yaklaşmadan <a href="tel:112">112’yi arayın</a>. Ticari yol kapalıdır.</li>
    <li><strong>Çevrede de kesinti:</strong> Bina ortak alanı, komşular veya sokak da karanlıksa <a href="tel:186">186’yı arayın</a> ve <a href="/edas-bul/">yetkili EDAŞ’ı bulun</a>.</li>
    <li><strong>Yalnız sizde:</strong> Pano kapağını açmayın, şalteri tekrar tekrar kaldırmayın; bina yönetimi veya yetkili elektrikçiye ilerleyin.</li>
    <li><strong>Güvenli hazırlık:</strong> Aktif tehlike yoksa mevcut çözümü, gerçek W/VA/Wh ihtiyacını ve teknik uygunluğu kontrol edin; ancak bundan sonra ürün sınıfını değerlendirin.</li>
  </ol>
  <p><a class="cta" href="/karar-motoru/">Etkileşimli Akıllı Yol’u aç</a></p>

  <h3 id="kisisel-hazirlik-kontrolu">Kişisel hazırlık kontrolü</h3>
  <ol class="checklist" aria-labelledby="kisisel-hazirlik-kontrolu">
    <li>Evde veya işletmede aktif elektrik, gaz, karbonmonoksit, su teması ya da yangın tehlikesi var mı?</li>
    <li>Kesinti yalnız sizi mi, binayı mı, yoksa çevreyi mi etkiliyor?</li>
    <li>Mevcut UPS, jeneratör, aydınlatma veya güç istasyonu güvenli biçimde ihtiyacı karşılıyor mu?</li>
    <li>Kritik yükün gerçek çalışma gücü, tepe gücü ve hedef süresi doğrulandı mı?</li>
    <li>Üretici/servis onayı, topraklama, geçiş süresi ve gerçek kesinti testi tamamlandı mı?</li>
  </ol>
  <p><a href="/kesintiye-hazirlik-atolyesi/">Hazırlık planını oluştur</a> · <a href="/amazon-elektrik-urunleri/">Yalnız güvenli ve doğrulanmış ihtiyaçta ürün sınıflarını incele</a></p>
  <p class="fine"><strong>Satın almama sonucu:</strong> Mevcut güvenli çözüm ihtiyacı karşılıyorsa yeni ürün almayın. Aktif tehlikede veya arıza bildirimi sırasında Amazon bağlantısı gösterilmez.</p>
</section>'''
    if not re.search(r"</main\s*>", source, re.I):
        raise RuntimeError(f"Portal SSR enjeksiyonu için </main> bulunamadı: {portal}")
    source = re.sub(r"</main\s*>", section + "\n</main>", source, count=1, flags=re.I)
    portal.write_text(source, encoding="utf-8")
    return {
        "route": "/" + portal.relative_to(site).parent.as_posix().strip("/"),
        "status": "injected",
        "decisionBranches": 4,
        "preparationChecks": 5,
        "javascriptRequired": False,
        "activeDangerCommerceClosed": True,
        "buyNothingOutcomeVisible": True,
    }


def apply(repo: Path, site: Path, base_path: str = "") -> dict[str, object]:
    """Materialize SSR routes, then apply final-artifact schema and affiliate hardening."""

    del base_path
    repo, site = Path(repo), Path(site)
    materialization = _materialize_location_pages(repo, site)
    portal_ssr = _ensure_portal_ssr(site)
    report = _apply_competitor_gap_affiliate_v250(site)
    report["adapterVersion"] = VERSION
    report["locationPageMaterializationV251"] = materialization
    report["decisionPortalSsrV251"] = portal_ssr
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(
        json.dumps(
            apply(args.repo.resolve(), args.site.resolve(), args.base_path),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
