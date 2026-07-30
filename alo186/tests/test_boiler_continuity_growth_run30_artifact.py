from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROUTE = "/hesaplama/kombi-kesinti-yedek-guc-uygunluk/"
CANONICAL = "https://alo186.com" + ROUTE
HUB_MARKER = 'data-alo186-boiler-hub-card="true"'
PANEL_MARKER = 'data-alo186-boiler-continuity-run30="true"'


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def run(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    page = site / ROUTE.strip("/") / "index.html"
    script = page.with_name("app.js")
    styles = page.with_name("styles.css")
    assert page.is_file() and script.is_file() and styles.is_file()
    html = page.read_text(encoding="utf-8")
    js = script.read_text(encoding="utf-8")
    assert html.count("<h1") == 1
    assert "Kombi Kesinti Yedek Güç ve UPS Uygunluğu" in html
    assert "Amazon satış ortaklığı ilişkisi" in html
    assert "doğrudan mağaza bağlantısı vermez" in html
    assert "Mevcut çözüm yeterliyse satın alma önerilmez" in html
    assert "RRULE:FREQ=MONTHLY;COUNT=12" in js
    assert not re.search(r"amazon\.(?:com|com\.tr)|amzn\.", html + js, re.I)
    assert not re.search(r'"@type"\s*:\s*"(?:Product|Offer)"|priceCurrency|aggregateRating|availability', html, re.I)
    canonical = re.findall(r'<link\b[^>]*rel=["\'][^"\']*canonical[^"\']*["\'][^>]*href=["\']([^"\']+)', html, re.I)
    assert canonical == [CANONICAL]
    robots = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)', html, re.I)
    assert robots
    if base_path:
        assert "noindex" in robots.group(1).lower()
    else:
        assert "index" in robots.group(1).lower() and "noindex" not in robots.group(1).lower()
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    assert f"<loc>{CANONICAL}</loc>" in sitemap
    expected = f"{base_path}{ROUTE}" if base_path else ROUTE
    hub = (site / "hesaplama/index.html").read_text(encoding="utf-8")
    assert HUB_MARKER in hub
    assert f'href="{expected}"' in hub
    count_match = re.search(r"(\d+) çekirdek araç", hub)
    assert count_match and int(count_match.group(1)) >= 37
    for relative in ["elektrik-portali/index.html", "akilli-urun-secimi/index.html", "amazon-elektrik-urunleri/index.html"]:
        target = site / relative
        assert target.is_file() and PANEL_MARKER in target.read_text(encoding="utf-8")
    search_path = site / "arama/search-index.json"
    if search_path.is_file():
        payload = json.loads(search_path.read_text(encoding="utf-8"))
        entries = payload.get("entries", [])
        entry = next(item for item in entries if item.get("canonicalPath") == ROUTE)
        assert entry.get("url") == expected
        assert "kombi" in (entry.get("title", "") + " " + entry.get("description", "")).lower()
    release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    metadata = release.get("boilerContinuitySuitability") or {}
    assert metadata.get("directAffiliateLinksAdded") == 0
    assert metadata.get("noBuyOutcomePreserved") is True
    assert metadata.get("hazardCommerceClosed") is True
    assert metadata.get("electricBoilerConsumerCommerceClosed") is True
    assert metadata.get("recordLimit") == 10 and metadata.get("reviewMonths") == 12
    return {"ok": True, "route": expected, "basePath": base_path, "canonical": CANONICAL, "toolCount": int(count_match.group(1)), "entries": metadata.get("entryCardsInjected")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
