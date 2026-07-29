from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ARTICLES = [
    {
        "slug": "enerji-depolama-bms-soc-kalibrasyon-sapma-drift",
        "required": [
            "Coulomb counting", "akım sensörü ofseti", "kullanılabilir enerji",
            "elle sıfırlamak", "sensör ve zaman doğrulaması",
            "satın almayı zorunlu kılmaz", "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/enerji-depolama-round-trip-efficiency-soh-kabul-testi",
            "/haberler/enerji-depolama-termal-runaway-off-gas-erken-uyari",
            "/haberler/vpp-temel-tuketim-baseline-performans-dogrulama",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["standards.ieee.org", "sandia.gov"],
    },
    {
        "slug": "ev-sarj-kablosu-soketi-isiniyor-termal-derating",
        "required": [
            "termal derating", "temas direnci", "I²R",
            "akımı otomatik azaltması", "evrensel bir dokunma sıcaklığı",
            "satın almayı zorunlu kılmaz", "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/elektrikli-arac-sarj-olmuyor-wallbox-neden-baslamiyor",
            "/haberler/ev-sarj-open-pen-kopuk-pen-korumasi",
            "/haberler/ev-sarj-ocpp-iso-15118-plug-charge-farki",
            "/hesaplama/ev-sarj-uygunluk/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["iec.ch", "tesla.com"],
    },
    {
        "slug": "parafudr-baglanti-kablosu-uzunlugu-v-baglanti-up-etkin-koruma",
        "required": [
            "u = L × di/dt", "0,5 m", "V/Kelvin",
            "etkin koruma seviyesi", "yalnız kablo kesitini büyütmek",
            "satın almayı zorunlu kılmaz", "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/parafudr-tip-1-tip-2-tip-3-paratoner-secimi",
            "/haberler/parafudr-yedek-sigorta-sccr-kisa-devre-koordinasyonu",
            "/haberler/parafudr-kirmizi-gosterge-uzaktan-kontak-degisim",
            "/haberler/ges-dc-parafudr-ucpv-uocmax-topraklama-secimi",
            "/hesaplama/teknik-sartname-talep-paketi/",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["iec.ch", "phoenixcontact.com", "dehn-international.com", "se.com"],
    },
]


def jsonld_graphs(html: str) -> list[dict]:
    graphs: list[dict] = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        payload = json.loads(raw)
        graph = payload.get("@graph") if isinstance(payload, dict) else None
        graphs.extend(graph if isinstance(graph, list) else [payload])
    return graphs


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 62, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 138, len(article_routes)
    all_paths = {route["canonicalPath"] for route in manifest["routes"]}

    expected_links = {link for article in ARTICLES for link in article["links"]}
    assert expected_links.issubset(all_paths), expected_links - all_paths

    seen_titles: set[str] = set()
    seen_h1: set[str] = set()
    new_paths: set[str] = set()

    for article in ARTICLES:
        slug = article["slug"]
        canonical_path = f"/haberler/{slug}"
        route = next((item for item in article_routes if item["canonicalPath"] == canonical_path), None)
        assert route, f"Routing eksik: {canonical_path}"
        assert route["source"] == f"alo186/haberler/{slug}/index.html"
        file_path = REPO_ROOT / route["source"]
        assert file_path.is_file(), file_path
        html = file_path.read_text(encoding="utf-8")
        lower = html.casefold()
        canonical = f"https://www.alo186.com{canonical_path}"

        assert "<!doctype html>" in lower
        assert f'rel="canonical" href="{canonical}"' in html
        assert '<meta name="description"' in html
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in html
        assert '../alo186-article.css' in html
        assert html.count("<h1>") == 1
        title_match = re.search(r"<title>(.*?)</title>", html, re.S)
        h1_match = re.search(r"<h1>(.*?)</h1>", html, re.S)
        assert title_match and h1_match
        title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        h1 = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()
        assert title not in seen_titles and h1 not in seen_h1
        seen_titles.add(title)
        seen_h1.add(h1)

        assert "Doğrudan cevap" in html
        assert "Ticari sınır" in html
        assert "bağımsız" in lower
        assert "yetkili" in lower or "resmî" in lower
        assert "Mevcut içerikten görev ayrımı" in html
        assert "WebApplication" not in html
        assert "amazon.com" not in lower and "amazon.com.tr" not in lower
        assert not re.search(r"\bfiyat(?:ı)?\s*[:=]?\s*\d|\bstokta\b|\bpuanı\s*\d|\bgaranti\s*[:=]?\s*\d", lower)
        assert not re.search(r"<form\b|<input\b|<textarea\b", lower)
        assert not re.search(r"kesinlikle güvenlidir|her durumda güvenlidir|kesin çözüm|garantili kazanç|garantili tasarruf", lower)

        for required in article["required"]:
            assert required.casefold() in lower, f"Zorunlu ifade eksik ({required}): {slug}"
        for link in article["links"]:
            assert link in html, f"İç bağlantı eksik ({link}): {slug}"
        for host in article["source_hosts"]:
            assert host in lower, f"Birincil kaynak alan adı eksik ({host}): {slug}"

        graphs = jsonld_graphs(html)
        types = {item.get("@type") for item in graphs if isinstance(item, dict)}
        assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(types), (slug, types)
        assert "Product" not in types and "Offer" not in types
        article_schema = next(item for item in graphs if item.get("@type") == "Article")
        assert article_schema["datePublished"] == "2026-07-29"
        assert article_schema["dateModified"] == "2026-07-29"
        assert article_schema["mainEntityOfPage"] == canonical
        assert len(article_schema.get("about", [])) >= 8
        assert all(item.get("@type") == "DefinedTerm" for item in article_schema["about"])
        faq = next(item for item in graphs if item.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
        assert all(item.get("@type") == "Question" for item in faq["mainEntity"])
        assert len(re.findall(r'<a href="https://', html)) >= 4
        new_paths.add(canonical_path)

    bess = (REPO_ROOT / "alo186/haberler/enerji-depolama-bms-soc-kalibrasyon-sapma-drift/index.html").read_text(encoding="utf-8").casefold()
    ev = (REPO_ROOT / "alo186/haberler/ev-sarj-kablosu-soketi-isiniyor-termal-derating/index.html").read_text(encoding="utf-8").casefold()
    spd = (REPO_ROOT / "alo186/haberler/parafudr-baglanti-kablosu-uzunlugu-v-baglanti-up-etkin-koruma/index.html").read_text(encoding="utf-8").casefold()
    assert "yazılım komutuyla yüzdeyi 100 yapmak kapasiteyi artırmaz" in bess
    assert "termal korumayı devre dışı bırakmak" in ev and "wallboxı hemen değiştirmek" in ev
    assert "katalogdaki gerilim koruma seviyesi" in spd and "daha yüksek ka spd seçmek" in spd
    assert len(new_paths) == 3, new_paths

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "effectiveSourceArticleCount": len(article_routes),
        "newArticleCount": len(ARTICLES),
        "newCanonicalPaths": sorted(new_paths),
        "commercialClaimsAdded": False,
        "formsAdded": False,
        "intentSeparationChecked": True,
        "sourceVerificationDate": "2026-07-29",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
