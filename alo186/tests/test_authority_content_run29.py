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
        "slug": "notr-toprak-gerilimi-yuksek-nedenleri-olcum",
        "required": [
            "yük akımının nötr iletken empedansı", "N-PE köprüsü", "üçlü harmonikler",
            "tek bir volt sınırı yoktur", "yük altında", "istenmeyen nötr-toprak",
            "satın almayı zorunlu kılmaz", "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/harmonik-thd-tdd-pcc-olcum-farki",
            "/haberler/kacak-akim-rolesi-acma-suresi-rampa-testi-nasil-olculur",
            "/hesaplama/kacak-akim-rolesi-olay-gunlugu/",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["fluke.com", "eaton.com", "megger.com"],
    },
    {
        "slug": "jenerator-ats-3-kutup-4-kutup-anahtarlanan-notr",
        "required": [
            "sabit nötr", "anahtarlanan nötr", "örtüşmeli nötr", "ayrı türetilmiş",
            "break-before-make", "N-PE bağı", "Türkiye'de doğrudan mevzuat yerine geçmez",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/jenerator-calisiyor-ama-ats-yuku-transfer-etmiyor",
            "/haberler/ups-jenerator-boyutlandirma-thdi-guc-faktoru",
            "/hesaplama/jenerator-ats-test-gunlugu/",
            "/hesaplama/elektrik-kesintisi-tatbikati/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["se.com", "cat.com"],
    },
    {
        "slug": "ges-mc4-konnektor-capraz-eslestirme-krimp-hatasi",
        "required": [
            "çapraz eşleştirme", "MC4 compatible", "aynı üretici", "krimp",
            "kablo dış çapı", "kontak direnci", "tek taraflı parça değişimi",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ges-string-akimi-dusuk-mppt-uretim-farki",
            "/haberler/ges-panel-hotspot-bypass-diyot-termal-kamera",
            "/haberler/ges-pid-potansiyel-kaynakli-degradasyon-nasil-anlasilir",
            "/hesaplama/inverter-uygunluk/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["staubli.com", "iec.ch", "nlr.gov"],
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
    assert manifest["version"] >= 58, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 129, len(article_routes)
    all_paths = {route["canonicalPath"] for route in manifest["routes"]}

    nearby_existing = {
        "/haberler/harmonik-thd-tdd-pcc-olcum-farki",
        "/haberler/kacak-akim-rolesi-acma-suresi-rampa-testi-nasil-olculur",
        "/hesaplama/kacak-akim-rolesi-olay-gunlugu/",
        "/hesaplama/elektrik-kanit-envanteri/",
        "/hesaplama/teknik-devir-kabul-paketi/",
        "/hizmetler/elektrik-surekliligi-izleme/",
        "/haberler/jenerator-calisiyor-ama-ats-yuku-transfer-etmiyor",
        "/haberler/ups-jenerator-boyutlandirma-thdi-guc-faktoru",
        "/hesaplama/jenerator-ats-test-gunlugu/",
        "/hesaplama/elektrik-kesintisi-tatbikati/",
        "/haberler/ges-string-akimi-dusuk-mppt-uretim-farki",
        "/haberler/ges-panel-hotspot-bypass-diyot-termal-kamera",
        "/haberler/ges-pid-potansiyel-kaynakli-degradasyon-nasil-anlasilir",
        "/hesaplama/inverter-uygunluk/",
        "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
    }
    assert nearby_existing.issubset(all_paths), nearby_existing - all_paths

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

    neutral = (REPO_ROOT / "alo186/haberler/notr-toprak-gerilimi-yuksek-nedenleri-olcum/index.html").read_text(encoding="utf-8").casefold()
    ats = (REPO_ROOT / "alo186/haberler/jenerator-ats-3-kutup-4-kutup-anahtarlanan-notr/index.html").read_text(encoding="utf-8").casefold()
    mc4 = (REPO_ROOT / "alo186/haberler/ges-mc4-konnektor-capraz-eslestirme-krimp-hatasi/index.html").read_text(encoding="utf-8").casefold()
    assert "tek bir volt değerinden" in neutral and "rastgele n-pe köprüsü" in neutral
    assert "mutlaka 4 kutuplu" in ats and "yerel mevzuat" in ats
    assert "mekanik olarak birbirine oturması" in mc4 and "yalnız “mc4 compatible”" in mc4

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
