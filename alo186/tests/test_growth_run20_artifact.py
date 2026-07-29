from __future__ import annotations

import argparse
import json
from pathlib import Path

ROUTE = "/hesaplama/usb-c-guc-ve-goruntu-karar-merkezi/"
TARGETS = [
    "hesaplama/index.html",
    "elektrik-portali/index.html",
    "akilli-urun-secimi/index.html",
    "amazon-elektrik-urunleri/index.html",
    "katalog-guven-durumu/index.html",
]


def public_url(base_path: str, route: str) -> str:
    base = "" if not base_path or base_path == "/" else "/" + base_path.strip("/")
    return f"{base}{route}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    root = args.site.resolve()
    expected = public_url(args.base_path, ROUTE)
    page = root / ROUTE.strip("/") / "index.html"
    assert page.is_file(), page
    html = page.read_text(encoding="utf-8")
    for token in [
        'data-action="power-chain"',
        'data-action="display-diagnosis"',
        'data-action="desktop-passport"',
        "TTL=365*86400000",
        "180*86400000",
    ]:
        assert token in html, token
    assert "amazon.com.tr" not in html.lower()
    assert 'type="email"' not in html.lower() and 'type="tel"' not in html.lower()

    for relative in TARGETS:
        text = (root / relative).read_text(encoding="utf-8")
        assert 'data-alo186-growth-run20-entry="true"' in text, relative
        assert expected in text, (relative, expected)

    search = json.loads((root / "arama/search-index.json").read_text(encoding="utf-8"))
    entry = next(item for item in search["entries"] if item["canonicalPath"] == ROUTE)
    assert entry["url"] == expected

    release = json.loads((root / "alo186-release.json").read_text(encoding="utf-8"))
    pages = json.loads((root / "pages-release.json").read_text(encoding="utf-8"))
    metadata = release["growthRun20"]
    assert metadata["route"] == expected
    assert metadata["directAffiliateLinksAdded"] == 0
    assert metadata["hazardCommerceClosed"] is True
    assert metadata["unknownCapabilityCommerceClosed"] is True
    assert metadata["noBuyOutcomePreserved"] is True
    assert metadata["passportRecordLimit"] == 6
    assert metadata["passportTtlDays"] == 365
    assert metadata["passportReviewDays"] == 180
    assert metadata["unverifiedCommercialFieldsUsed"] == []
    assert pages["growthRun20"]["route"] == expected

    assert expected in (root / "sw.js").read_text(encoding="utf-8")
    manifest = json.loads((root / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert any(item.get("url") == expected for item in manifest.get("shortcuts", []))
    assert f"https://www.alo186.com{ROUTE}" in (root / "sitemap.xml").read_text(encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "site": str(root),
        "basePath": args.base_path,
        "route": expected,
        "entryPoints": len(TARGETS),
        "directAffiliateLinks": 0,
        "passportTtlDays": 365,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
