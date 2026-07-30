from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROUTE = "/hesaplama/buzdolabi-dondurucu-kesinti-guvenligi/"
CANONICAL = "https://alo186.com" + ROUTE


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
    assert "Buzdolabı ve Dondurucu Kesinti Güvenliği" in html
    assert "Amazon satış ortaklığı bağlantılarıdır" in html
    assert "ALO186 sağlık veya gıda denetim kurumu" in html
    assert "RRULE:FREQ=WEEKLY;COUNT=12" in js
    assert "rel=\"sponsored nofollow noopener\"" in js
    assert not re.search(r'"@type"\s*:\s*"Offer"|priceCurrency|aggregateRating|availability', html, re.I)
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
    hub = (site / "hesaplama/index.html").read_text(encoding="utf-8")
    expected = f"{base_path}{ROUTE}" if base_path else ROUTE
    assert expected in hub or './buzdolabi-dondurucu-kesinti-guvenligi/' in hub
    assert "36 çekirdek araç" in hub
    search_path = site / "arama/search-index.json"
    if search_path.is_file():
        payload = json.loads(search_path.read_text(encoding="utf-8"))
        entries = payload.get("entries", [])
        entry = next(item for item in entries if item.get("canonicalPath") == ROUTE)
        assert entry.get("url") == expected
    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        assert release.get("canonicalHost") == "https://alo186.com"
        assert release.get("customDomain") == "alo186.com"
    return {"ok": True, "route": expected, "basePath": base_path, "canonical": CANONICAL}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
