from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402
from inject_article_growth import classify  # noqa: E402


def read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def test_routing_and_source_page() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    routes = [route for route in manifest["routes"] if route["canonicalPath"] == "/hesaplama/teknik-takip-listem/"]
    assert len(routes) == 1
    assert routes[0]["type"] == "tool"
    assert manifest["version"] >= 40

    html = read("alo186/hesaplama/teknik-takip-listem/index.html")
    app = read("alo186/hesaplama/teknik-takip-listem/app.js")
    injector = read("alo186/deployment/inject_article_growth.py")
    article_js = read("alo186/deployment/assets/article-growth.js")
    pipeline = read("alo186/deployment/inject_shortlist_growth.py")

    assert 'rel="canonical" href="https://www.alo186.com/hesaplama/teknik-takip-listem/"' in html
    assert "WebApplication" in html and "FAQPage" in html
    assert "yalnız bu tarayıcıda" in html
    assert "Mevcut sistem yeterliyse" in html
    assert "affiliate kanalına açılmaz" in html
    assert "amazon.com" not in html.casefold()
    assert 'type="email"' not in html.casefold()
    assert 'type="tel"' not in html.casefold()
    assert '<textarea' not in html.casefold()

    assert "alo186.articleFollowup.v1" in app
    assert "LIMIT = 12" in app and "TTL_DAYS = 365" in app
    assert "containsPersonalData: false" in app
    assert "JSON indir" in html and "Takvime aktar" in html
    assert "price" not in app and "stock" not in app and "rating" not in app
    assert "Alo186Track('technical_followup_exported'" in app

    assert "directAffiliateLinksAdded" in injector
    assert '"consumerLaneDisclosureRequired": True' in injector
    assert "data-alo186-inventory-strip" in injector
    assert "data-alo186-article-next-step" in injector
    assert "data-alo186-followup-entry-card" in injector
    assert "Makale sonraki-adım kapsamı eksik" in injector
    assert "amazon.com" not in injector.casefold()
    assert "localStorage" in article_js
    assert "article_followup_saved" in article_js
    assert "price" not in article_js and "stock" not in article_js

    assert pipeline.index("run_private_search(site, base_path)") < pipeline.index("run_article_growth(site, base_path)")


def test_lane_classification() -> None:
    official = classify("/haberler/elektrik-kesintisi-tazminati-nasil-alinir")
    assert official["lane"] == "official"
    assert official["primary"] == "/edas-bul"
    assert "affiliate bağlantısı gösterilmez" in official["boundary"]

    consumer = classify("/haberler/power-station-gunes-paneli-nasil-secilir")
    assert consumer["lane"] == "consumer"
    assert consumer["primary"] == "/hesaplama/power-station-kapasite-eps-uygunluk/"
    assert consumer["secondary"] == "/akilli-urun-secimi"
    assert "satış ortaklığı" in consumer["boundary"]
    assert "Mevcut ekipman yeterliyse satın almayın" in consumer["boundary"]

    ev_cable = classify("/haberler/tip-2-ev-sarj-kablosu-nasil-secilir")
    assert ev_cable["lane"] == "consumer"
    assert ev_cable["primary"] == "/hesaplama/ev-sarj-kablosu-uygunluk/"

    fixed = classify("/haberler/kacak-akim-rolesi-tip-a-tip-ac-farki")
    assert fixed["lane"] == "professional"
    assert fixed["primary"] == "/hesaplama/teknik-devir-kabul-paketi/"
    assert "affiliate bağlantısı açılmaz" in fixed["boundary"]

    vpp = classify("/haberler/vpp-sanal-guc-santrali-nedir")
    assert vpp["lane"] == "professional"
    assert vpp["primary"] == "/kurumsal-elektrik-surekliligi-on-degerlendirme"


def main() -> None:
    test_routing_and_source_page()
    test_lane_classification()
    print(json.dumps({
        "ok": True,
        "followupRoute": "/hesaplama/teknik-takip-listem/",
        "lanePolicies": ["official", "consumer", "professional"],
        "directAffiliateLinksAdded": 0,
        "followupLimit": 12,
        "followupTtlDays": 365,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
