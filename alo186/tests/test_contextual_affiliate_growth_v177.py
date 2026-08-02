from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

import inject_contextual_affiliate_growth_v177 as growth  # noqa: E402

PRODUCT_MAP_ROUTE = Path(
    "amazon-elektrik-urunleri/konuya-gore-urun-haritasi/index.html"
)
PRODUCT_MAP_SOURCE = (
    ROOT
    / "alo186/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/index.html"
)
PRODUCT_MAP_PLACEHOLDER = 'data-alo186-product-map-placeholder="true"'
PRODUCT_MAP_TITLE = "konuya göre elektrik ürünleri haritası"


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def validate_product_map(site: Path, base_path: str) -> None:
    path = site / PRODUCT_MAP_ROUTE
    assert path.is_file(), PRODUCT_MAP_ROUTE.as_posix()
    text = path.read_text(encoding="utf-8")
    visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).casefold()

    assert growth.MARKER in text
    assert growth.TAG in text
    assert PRODUCT_MAP_TITLE in visible
    assert growth.DISCLOSURE in text
    assert text.count('class="alo186-contextual-product"') == 3
    assert text.count("data-affiliate-gate=") == 3
    assert growth.public_url(base_path, "/" + growth.CSS_FILE) in text
    assert growth.public_url(base_path, "/" + growth.JS_FILE) in text
    assert not re.search(
        r'<a\b[^>]*href=["\']https?://(?:www\.)?(?:amazon\.com\.tr|amzn\.to)',
        text,
        re.IGNORECASE,
    )
    assert not re.search(
        r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"',
        text,
        re.IGNORECASE,
    )


def validate_site(site: Path, base_path: str) -> None:
    report = growth.audit(site, base_path)
    assert report["ok"] is True
    assert report["targetRouteCount"] == 40
    assert report["moduleCount"] == 40
    assert report["placementCount"] == 120
    assert report["productClassCount"] == 34
    assert report["gateCount"] == 3
    assert report["directStoreUrlsInHtml"] == 0
    assert report["highRiskDirectLinks"] == 0
    assert report["personalDataCollectionAdded"] is False
    assert report["productImagesAdded"] is False

    modules = cards = static_store_links = 0
    for route, keys in growth.PLACEMENTS.items():
        path = site / route
        assert path.is_file(), route
        text = path.read_text(encoding="utf-8")
        modules += text.count(growth.MARKER)
        cards += text.count('class="alo186-contextual-product"')
        static_store_links += len(
            re.findall(
                r'<a\b[^>]*href=["\']https?://(?:www\.)?amazon\.com\.tr',
                text,
                re.IGNORECASE,
            )
        )
        assert text.count("data-affiliate-gate=") == 3
        assert growth.DISCLOSURE in text
        assert growth.public_url(base_path, "/" + growth.CSS_FILE) in text
        assert growth.public_url(base_path, "/" + growth.JS_FILE) in text
        for key in keys:
            assert f'data-product-class="{key}"' in text
    assert modules == 40
    assert cards == 120
    assert static_store_links == 0

    validate_product_map(site, base_path)

    js = (site / growth.JS_FILE).read_text(encoding="utf-8")
    assert growth.TAG in js
    assert "window.alo186Analytics.track" in js
    assert "affiliate_context_view" in js
    assert "affiliate_gate_open" in js
    assert "affiliate_product_select" in js
    assert "sponsored nofollow noopener" in js
    assert "localStorage" not in js
    assert "document.cookie" not in js

    for release_name in ("alo186-release.json", "pages-release.json"):
        path = site / release_name
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        release = payload["contextualAffiliateGrowth"]
        assert release["version"] == 177
        assert release["targetRouteCount"] == 40
        assert release["placementCount"] == 120
        assert release["productClassCount"] == 34
        assert release["gateCount"] == 3
        assert release["directStoreUrlsInHtml"] == 0
        assert release["highRiskDirectLinks"] == 0
        assert release["priceStockRatingClaims"] is False
        assert release["productImagesAdded"] is False
        assert release["personalDataCollectionAdded"] is False
        assert release["existingProductFirst"] is True


assert PRODUCT_MAP_SOURCE.is_file()
assert PRODUCT_MAP_PLACEHOLDER in PRODUCT_MAP_SOURCE.read_text(encoding="utf-8")
assert len(growth.PLACEMENTS) == 40
assert len({key for keys in growth.PLACEMENTS.values() for key in keys}) == 34
assert all(len(keys) == 3 and len(set(keys)) == 3 for keys in growth.PLACEMENTS.values())
assert all(key in growth.PRODUCTS for keys in growth.PLACEMENTS.values() for key in keys)

with tempfile.TemporaryDirectory(prefix="alo186-contextual-affiliate-v177-") as folder:
    root = Path(folder)
    canonical = root / "canonical"
    run(
        [
            sys.executable,
            "alo186/deployment/build_static_site.py",
            "--output",
            str(canonical),
            "--commit",
            "contextual-affiliate-v177-test",
        ]
    )

    canonical_product_map = canonical / PRODUCT_MAP_ROUTE
    assert canonical_product_map.is_file(), (
        "v177 product map canonical artifact içinde değil; routing manifest/overlay eksik"
    )
    assert PRODUCT_MAP_PLACEHOLDER in canonical_product_map.read_text(encoding="utf-8")

    for name, base_path in (("custom", ""), ("project", "/chatgpt")):
        site = root / name
        shutil.copytree(canonical, site)
        run(
            [
                sys.executable,
                "alo186/deployment/prepare_github_pages.py",
                "--site",
                str(site),
                "--base-path",
                base_path,
                "--repository",
                "ozaneryavuz/chatgpt",
                "--commit",
                "contextual-affiliate-v177-test",
            ]
        )
        first = growth.run(site, base_path)
        assert first["injectedRouteCount"] == 40
        assert first["alreadyInjectedRouteCount"] == 0
        assert first["missingRouteCount"] == 0
        assert first["skippedExistingCommerceRouteCount"] == 0
        validate_site(site, base_path)

        second = growth.run(site, base_path)
        assert second["injectedRouteCount"] == 0
        assert second["alreadyInjectedRouteCount"] == 40
        assert second["placementCount"] == 120
        validate_site(site, base_path)

print(
    json.dumps(
        {
            "ok": True,
            "version": 177,
            "targetRouteCount": 40,
            "placementCount": 120,
            "productMapRoute": "/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/",
            "productMapRouted": True,
            "productClassCount": 34,
            "gateCount": 3,
            "directStoreUrlsInHtml": 0,
            "highRiskDirectLinks": 0,
            "personalDataCollectionAdded": False,
            "productImagesAdded": False,
        },
        ensure_ascii=False,
    )
)
