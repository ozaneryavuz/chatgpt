from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROUTE = "/hesaplama/kombi-kesinti-yedek-guc-uygunluk/"
CANONICAL = "https://alo186.com" + ROUTE


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def run(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    page = site / ROUTE.strip("/") / "index.html"
    script = page.with_name("app.js")
    styles = page.with_name("styles.css")
    common_path = site / "hesaplama/common.js"
    assert page.is_file() and script.is_file() and styles.is_file() and common_path.is_file()
    html = page.read_text(encoding="utf-8")
    js = script.read_text(encoding="utf-8")
    common = common_path.read_text(encoding="utf-8")
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
    assert "boilerContinuityCard" in common
    assert ROUTE in common
    assert "data-alo186-boiler-continuity-card" in common
    assert "37 çekirdek araç" in common
    search_path = site / "arama/search-index.json"
    if search_path.is_file():
        payload = json.loads(search_path.read_text(encoding="utf-8"))
        entries = payload.get("entries", [])
        entry = next(item for item in entries if item.get("canonicalPath") == ROUTE)
        assert entry.get("url") == expected
        assert "kombi" in (entry.get("title", "") + " " + entry.get("description", "")).lower()
    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        assert release.get("canonicalHost") == "https://alo186.com"
        assert release.get("customDomain") == "alo186.com"
    return {"ok": True, "route": expected, "basePath": base_path, "canonical": CANONICAL, "runtimeToolCount": 37}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
