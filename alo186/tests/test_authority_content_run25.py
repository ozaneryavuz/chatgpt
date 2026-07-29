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
        "slug": "harmonik-thd-tdd-pcc-olcum-farki",
        "required": [
            "Total Harmonic Distortion",
            "Total Demand Distortion",
            "Point of Common Coupling",
            "maximum demand current",
            "individual harmonic spectrum",
            "IEEE 519-2022",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler",
            "/haberler/detuned-reaktor-aktif-harmonik-filtre-farki",
            "/haberler/notr-akimi-faz-akimindan-yuksek-neden-olur",
            "/hesaplama/teknik-sartname-talep-paketi/",
            "/hesaplama/elektrik-kanit-envanteri/",
        ],
        "source_hosts": [
            "standards.ieee.org",
            "product-help.schneider-electric.com",
            "eaton.com",
            "abb.com",
        ],
    },
    {
        "slug": "ges-pid-potansiyel-kaynakli-degradasyon-nasil-anlasilir",
        "required": [
            "potential-induced degradation",
            "PID-s shunting",
            "PID-p polarization",
            "PID recovery",
            "electroluminescence imaging",
            "I-V curve tracing",
            "IEC TS 62804-1:2025",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ges-string-akimi-dusuk-mppt-uretim-farki",
            "/haberler/ges-panel-hotspot-bypass-diyot-termal-kamera",
            "/haberler/ges-inverter-izolasyon-direnci-dusuk-hatasi",
            "/hesaplama/inverter-uygunluk/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["webstore.iec.ch", "research-hub.nrel.gov", "solar.huawei.com"],
    },
    {
        "slug": "kacak-akim-rolesi-acma-suresi-rampa-testi-nasil-olculur",
        "required": [
            "RCD trip time",
            "ramp current test",
            "residual operating current",
            "0 degree and 180 degree test",
            "selective type S RCD",
            "IEC 61557-6:2019",
            "automatic RCD test sequence",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/kacak-akim-rolesi-test-dugmesi-ne-siklikla",
            "/haberler/kacak-akim-rolesi-tip-s-selektivite-nedir",
            "/haberler/kacak-akim-rolesi-tip-f-nedir-inverterli-cihazlar",
            "/haberler/ev-sarj-istasyonu-tip-b-rcd-rdc-dd-secimi",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["webstore.iec.ch", "fluke.com", "se.com"],
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
    assert manifest["version"] >= 52, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 117, len(article_routes)
    active_paths = {route["canonicalPath"] for route in article_routes}

    nearby_existing = {
        "/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler",
        "/haberler/detuned-reaktor-aktif-harmonik-filtre-farki",
        "/haberler/notr-akimi-faz-akimindan-yuksek-neden-olur",
        "/haberler/ges-string-akimi-dusuk-mppt-uretim-farki",
        "/haberler/ges-panel-hotspot-bypass-diyot-termal-kamera",
        "/haberler/ges-inverter-izolasyon-direnci-dusuk-hatasi",
        "/haberler/kacak-akim-rolesi-test-dugmesi-ne-siklikla",
        "/haberler/kacak-akim-rolesi-tip-s-selektivite-nedir",
        "/haberler/kacak-akim-rolesi-tip-f-nedir-inverterli-cihazlar",
    }
    assert nearby_existing.issubset(active_paths), nearby_existing - active_paths

    seen_canonical: set[str] = set()
    seen_titles: set[str] = set()
    seen_h1: set[str] = set()
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
        assert "Kaynaklar ve doğrulama" in html
        assert "Ticari sınır" in html or "Satın alma ve hizmet sınırı" in html
        assert "Bağımsız" in html
        assert "yetkili" in lower or "resmî" in lower
        assert "WebApplication" not in html
        assert "amazon.com" not in lower and "amazon.com.tr" not in lower
        assert not re.search(r"\bfiyat(?:ı)?\s*[:=]?\s*\d|\bstokta\b|\bpuanı\s*\d|\bgaranti\s*[:=]?\s*\d", lower)
        assert not re.search(r"<form\b|<input\b|<textarea\b", lower)
        assert not re.search(
            r"kesinlikle güvenlidir|her durumda güvenlidir|kesin çözüm|garantili kazanç|garantili tasarruf",
            lower,
        )

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
        assert len(article_schema.get("about", [])) >= 7
        assert all(item.get("@type") == "DefinedTerm" for item in article_schema["about"])
        faq = next(item for item in graphs if item.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
        assert all(item.get("@type") == "Question" for item in faq["mainEntity"])
        assert len(re.findall(r'<a href="https://', html)) >= 4
        assert canonical_path not in seen_canonical
        seen_canonical.add(canonical_path)

    harmonic = (REPO_ROOT / "alo186/haberler/harmonik-thd-tdd-pcc-olcum-farki/index.html").read_text(encoding="utf-8").casefold()
    pid = (REPO_ROOT / "alo186/haberler/ges-pid-potansiyel-kaynakli-degradasyon-nasil-anlasilir/index.html").read_text(encoding="utf-8").casefold()
    rcd = (REPO_ROOT / "alo186/haberler/kacak-akim-rolesi-acma-suresi-rampa-testi-nasil-olculur/index.html").read_text(encoding="utf-8").casefold()

    assert "akım thd yüzdesi tek başına harmonik filtre kararı değildir" in harmonic
    assert "düşük yükte" in harmonic and "ortak bağlantı noktası" in harmonic
    assert "pid, yalnız" in pid and "recovery özelliğini yalnız uyumluluk doğrulandıktan sonra" in pid
    assert "pid ile gölge, kir, hotspot" in pid
    assert "test düğmesine basıp cihazın açması, ölçümlü rcd kabulünün yerine geçmez" in rcd
    assert "tek bir evrensel sayı yayımlanamaz" in rcd and "0° ve 180°" in rcd

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "effectiveSourceArticleCount": len(article_routes),
        "newArticleCount": len(ARTICLES),
        "newCanonicalPaths": sorted(seen_canonical),
        "commercialClaimsAdded": False,
        "formsAdded": False,
        "intentSeparationChecked": True,
        "sourceVerificationDate": "2026-07-29",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
