from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import build  # noqa: E402

CANONICAL_ORIGIN = "https://alo186.com"
MALFORMED = re.compile(r"https://alo186\.com/amazon-elektrik-urunleri(?=[a-z0-9])", re.I)
CANONICAL_LINK = re.compile(
    r'<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']([^"\']+)["\'])[^>]*>',
    re.I,
)
JSONLD_BLOCK = re.compile(
    r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>',
    re.I | re.S,
)


def walk_urls(value) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in {"url", "item", "sameAs"} and isinstance(nested, str):
                result.append(nested)
            else:
                result.extend(walk_urls(nested))
    elif isinstance(value, list):
        for nested in value:
            result.extend(walk_urls(nested))
    return result


def route_exists(site: Path, path: str) -> bool:
    if path == "/":
        return (site / "index.html").is_file()
    target = site / path.strip("/")
    return target.is_file() or (target / "index.html").is_file()


def source_path_contracts() -> None:
    root = ROOT / "alo186/amazon-elektrik-urunleri"
    for page in sorted(root.rglob("index.html")):
        html = page.read_text(encoding="utf-8")
        match = CANONICAL_LINK.search(html)
        assert match, page
        parsed = urlsplit(match.group(1))
        route = "/" + page.parent.relative_to(ROOT / "alo186").as_posix()
        assert parsed.scheme == "https", (page, match.group(1))
        assert parsed.hostname in {"alo186.com", "www.alo186.com"}, (page, match.group(1))
        assert parsed.path.rstrip("/") == route.rstrip("/"), (page, match.group(1), route)


def artifact_contracts() -> dict[str, object]:
    with tempfile.TemporaryDirectory() as directory:
        site = Path(directory) / "site"
        release = build(ROOT, site, "commerce-canonical-v217-test")
        report = release["commercialCanonicalV217"]
        assert report["version"] == 217
        assert report["canonicalOrigin"] == CANONICAL_ORIGIN
        assert report["artifactLegacyWwwRejected"] is True
        assert report["priceStockRatingAdded"] is False
        assert report["affiliateLinksAdded"] is False

        hub_path = site / "amazon-elektrik-urunleri/index.html"
        assert hub_path.is_file()
        hub = hub_path.read_text(encoding="utf-8")
        assert not MALFORMED.search(hub)
        assert "https://www.alo186.com/amazon-elektrik-urunleri" not in hub

        graph_urls: list[str] = []
        for block in JSONLD_BLOCK.findall(hub):
            payload = json.loads(block)
            graph_urls.extend(walk_urls(payload))
            forbidden = json.dumps(payload, ensure_ascii=False).casefold()
            for token in ('"price"', '"pricecurrency"', '"availability"', '"aggregaterating"'):
                assert token not in forbidden, token

        internal = [url for url in graph_urls if (urlsplit(url).hostname or "").removeprefix("www.") == "alo186.com"]
        assert internal, "Ürün merkezi JSON-LD içinde ALO186 rotası bulunamadı."
        for url in internal:
            parsed = urlsplit(url)
            assert parsed.scheme == "https", url
            assert parsed.hostname == "alo186.com", url
            assert not MALFORMED.search(url), url
            assert route_exists(site, parsed.path), url

        commercial_pages = sorted((site / "amazon-elektrik-urunleri").rglob("index.html"))
        assert len(commercial_pages) >= 8
        for page in commercial_pages:
            html = page.read_text(encoding="utf-8")
            match = CANONICAL_LINK.search(html)
            assert match, page
            parsed = urlsplit(match.group(1))
            assert parsed.hostname == "alo186.com", (page, match.group(1))
            expected = "/" + page.parent.relative_to(site).as_posix()
            assert parsed.path.rstrip("/") == expected.rstrip("/"), (page, match.group(1), expected)

        release_file = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
        assert release_file["commercialCanonicalV217"] == report
        checksums = (site / "checksums.sha256").read_text(encoding="utf-8")
        assert "amazon-elektrik-urunleri/index.html" in checksums
        return report


def main() -> None:
    source_path_contracts()
    report = artifact_contracts()
    print(json.dumps({"ok": True, **report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
