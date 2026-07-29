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
        "slug": "kacak-akim-rolesi-selektivite-tip-s-zaman-gecikmesi",
        "required": [
            "Tip S", "IΔn", "tam seçicilik", "zaman gecikmesi",
            "SI ile S aynı değildir", "30 mA", "satın almayı zorunlu kılmaz",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/kacak-akim-rolesi-acma-suresi-rampa-testi-nasil-olculur",
            "/haberler/kacak-akim-rolesi-tip-f-tip-b-inverter-vfd-isi-pompasi",
            "/hesaplama/kacak-akim-rolesi-olay-gunlugu/",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["abb.com", "se.com"],
    },
    {
        "slug": "ges-dc-parafudr-ucpv-uocmax-topraklama-secimi",
        "required": [
            "UCPV", "UOCMAX", "IscPV", "koruma modu", "topraklama düzeni",
            "IEC 61643-31", "Y devresi", "satın almayı zorunlu kılmaz",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/parafudr-tip-1-tip-2-tip-3-paratoner-secimi",
            "/haberler/parafudr-yedek-sigorta-sccr-kisa-devre-koordinasyonu",
            "/haberler/parafudr-kirmizi-gosterge-uzaktan-kontak-degisim",
            "/haberler/ges-inverter-riso-dusuk-izolasyon-direnci-arizasi",
            "/hesaplama/teknik-sartname-talep-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["iec.ch", "dehn-international.com"],
    },
    {
        "slug": "jenerator-ters-guc-reverse-power-alarmi-ansi-32",
        "required": [
            "Reverse power", "ANSI 32", "motoring", "prime mover",
            "CT polaritesi", "negatif kW", "evrensel ayar değildir",
            "satın almayı zorunlu kılmaz", "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/jenerator-calisiyor-ama-ats-yuku-transfer-etmiyor",
            "/haberler/jenerator-ats-3-kutup-4-kutup-anahtarlanan-notr",
            "/haberler/jenerator-wet-stacking-dusuk-yuk-load-bank-testi",
            "/hesaplama/jenerator-ats-test-gunlugu/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["se.com", "deif.com"],
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
    assert manifest["version"] >= 61, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 135, len(article_routes)
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

    rcd = (REPO_ROOT / "alo186/haberler/kacak-akim-rolesi-selektivite-tip-s-zaman-gecikmesi/index.html").read_text(encoding="utf-8").casefold()
    pv = (REPO_ROOT / "alo186/haberler/ges-dc-parafudr-ucpv-uocmax-topraklama-secimi/index.html").read_text(encoding="utf-8").casefold()
    generator = (REPO_ROOT / "alo186/haberler/jenerator-ters-guc-reverse-power-alarmi-ansi-32/index.html").read_text(encoding="utf-8").casefold()
    assert "yalnız üst röleyi daha yüksek ma" in rcd and "si ile s aynı değildir" in rcd
    assert "yalnız “1000 v dc” etiketine göre" in pv and "yalnız daha yüksek ucpv" in pv
    assert "negatif kw her zaman mekanik arıza değildir" in generator and "yüzde 5 / 10 saniye" in generator
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
