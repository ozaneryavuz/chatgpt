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
        "slug": "ups-bypass-senkron-degil-kaynak-tolerans-disi",
        "required": ["bypass unavailable", "not synchronized", "source out of tolerance", "senkronizasyon penceresi", "slew rate", "free-running", "faz sırası", "Son doğrulama: 29 Temmuz 2026"],
        "links": ["/haberler/ups-eco-modu-cift-cevrim-transfer-suresi-kritik-yuk", "/haberler/ups-eco-modu-acik-olmali-mi", "/haberler/ups-cikis-kisa-devre-akimi-sigorta-selektivite", "/hesaplama/elektrik-kesintisi-tatbikati/", "/hesaplama/teknik-devir-kabul-paketi/", "/hizmetler/elektrik-surekliligi-izleme/"],
        "source_hosts": ["product-help.schneider-electric.com", "vertiv.com"],
    },
    {
        "slug": "ges-inverter-reaktif-guc-qu-cosphi-gerilim-destegi",
        "required": ["Q(U)", "cosφ(P)", "sabit reaktif güç", "görünür güç", "P/Q önceliği", "bağlantı noktası", "aktif üretimi", "Son doğrulama: 29 Temmuz 2026"],
        "links": ["/haberler/ges-inverter-sebeke-gerilimi-yuksek-hatasi", "/haberler/gunes-paneli-inverter-clipping-dc-ac-orani", "/haberler/ges-inverter-sicakta-guc-dusuruyor-temperature-derating", "/hesaplama/inverter-uygunluk/", "/hesaplama/teknik-devir-kabul-paketi/", "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/"],
        "source_hosts": ["manuals.fronius.com", "manuals.sma.de"],
    },
    {
        "slug": "parafudr-kirmizi-gosterge-uzaktan-kontak-degisim",
        "required": ["kırmızı durum penceresi", "uzaktan alarm kontağı", "yedek koruma", "değiştirilebilir kartuş", "faz gerilimi", "BMS/SCADA", "gerilimsiz", "Son doğrulama: 29 Temmuz 2026"],
        "links": ["/haberler/parafudr-tip-1-tip-2-tip-3-paratoner-secimi", "/hesaplama/elektrik-kanit-envanteri/", "/hesaplama/teknik-devir-kabul-paketi/", "/hesaplama/elektrikci-is-emri-ozeti/"],
        "source_hosts": ["se.com", "phoenixcontact.com"],
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
    assert manifest["version"] >= 54, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 120, len(article_routes)
    active_paths = {route["canonicalPath"] for route in article_routes}
    nearby_existing = {
        "/haberler/ups-eco-modu-cift-cevrim-transfer-suresi-kritik-yuk", "/haberler/ups-eco-modu-acik-olmali-mi", "/haberler/ups-cikis-kisa-devre-akimi-sigorta-selektivite",
        "/haberler/ges-inverter-sebeke-gerilimi-yuksek-hatasi", "/haberler/gunes-paneli-inverter-clipping-dc-ac-orani", "/haberler/ges-inverter-sicakta-guc-dusuruyor-temperature-derating",
        "/haberler/parafudr-tip-1-tip-2-tip-3-paratoner-secimi",
    }
    assert nearby_existing.issubset(active_paths), nearby_existing - active_paths

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
        seen_titles.add(title); seen_h1.add(h1)
        assert "Doğrudan cevap" in html
        assert "Ticari sınır" in html
        assert "bağımsız" in lower
        assert "yetkili" in lower or "resmî" in lower
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
        assert len(article_schema.get("about", [])) >= 7
        assert all(item.get("@type") == "DefinedTerm" for item in article_schema["about"])
        faq = next(item for item in graphs if item.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
        assert all(item.get("@type") == "Question" for item in faq["mainEntity"])
        assert len(re.findall(r'<a href="https://', html)) >= 4
        new_paths.add(canonical_path)

    ups = (REPO_ROOT / "alo186/haberler/ups-bypass-senkron-degil-kaynak-tolerans-disi/index.html").read_text(encoding="utf-8").casefold()
    pv = (REPO_ROOT / "alo186/haberler/ges-inverter-reaktif-guc-qu-cosphi-gerilim-destegi/index.html").read_text(encoding="utf-8").casefold()
    spd = (REPO_ROOT / "alo186/haberler/parafudr-kirmizi-gosterge-uzaktan-kontak-degisim/index.html").read_text(encoding="utf-8").casefold()
    assert "bypassı zorlamak yerine" in ups and "internetteki tek bir sayı bütün ups’lere uygulanamaz" in ups
    assert "ayar değişikliği, alarm susturma yöntemi değil commissioning işlemidir" in pv
    assert "her üretim düşüşü panel arızası değildir" in pv
    assert "yalnız renge bakarak bütün cihazı değiştirmek yerine" in spd
    assert "uzaktan kontak yalnız durum/alarm bilgisini" in spd
    print(json.dumps({"ok": True, "routingVersion": manifest["version"], "effectiveSourceArticleCount": len(article_routes), "newArticleCount": len(ARTICLES), "newCanonicalPaths": sorted(new_paths), "commercialClaimsAdded": False, "formsAdded": False, "intentSeparationChecked": True, "sourceVerificationDate": "2026-07-29"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
