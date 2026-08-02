from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

VERSION = 214
FORBIDDEN = (
    "sorun sayfası aramayın",
    "30 gün içinde edaş kaydı açın",
    "89 rehber",
    "25 rehber",
    "12 kaynaklı makale",
)
HOME_POSITIVE = (
    "60 saniyede doğru elektrik rotası",
    "elektrik sorununu güvenli biçimde sınıflandırın",
    "elektrik sorununda önce doğru ve güvenli adımı bulun",
)
PORTAL_REQUIRED = "30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun"


class VisibleText(HTMLParser):
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in self.SKIP:
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in self.SKIP and self.depth:
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.depth and data.strip():
            self.parts.append(data)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


def normalize_origin(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"Canlı origin yalnız geçerli HTTPS olabilir: {value!r}")
    return f"https://{parsed.hostname}"


def fetch(url: str, *, accept: str = "*/*") -> tuple[bytes, str, str, int]:
    request = Request(
        url,
        headers={
            "User-Agent": "ALO186-live-quality-v214/1.0",
            "Accept": accept,
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    context = ssl.create_default_context()
    with urlopen(request, timeout=30, context=context) as response:
        body = response.read()
        return body, response.headers.get_content_type(), response.geturl(), response.status


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def visible_text(html: str) -> str:
    parser = VisibleText(); parser.feed(html)
    return parser.text


def canonical_values(html: str) -> list[str]:
    return re.findall(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', html, re.I)


def validate_html(label: str, body: bytes, effective_url: str, expected_path: str) -> dict:
    html = body.decode("utf-8", errors="replace")
    folded = visible_text(html).casefold()
    failures = [term for term in FORBIDDEN if term in folded]
    if failures:
        raise AssertionError(("forbidden_live_copy", label, failures))
    canonicals = canonical_values(html)
    if len(canonicals) != 1:
        raise AssertionError(("canonical_count", label, len(canonicals)))
    canonical = urlparse(canonicals[0])
    if canonical.scheme != "https" or canonical.hostname != "alo186.com":
        raise AssertionError(("canonical_host", label, canonicals[0]))
    canonical_path = (canonical.path or "/").rstrip("/") or "/"
    normalized_expected = expected_path.rstrip("/") or "/"
    if canonical_path != normalized_expected:
        raise AssertionError(("canonical_path", label, canonical_path, normalized_expected))
    effective = urlparse(effective_url)
    if effective.hostname != "alo186.com":
        raise AssertionError(("effective_host", label, effective_url))
    if label == "home" and not any(token in folded for token in HOME_POSITIVE):
        raise AssertionError(("home_positive_copy_missing", HOME_POSITIVE))
    if label == "portal" and PORTAL_REQUIRED not in folded:
        raise AssertionError(("portal_official_channel_copy_missing", PORTAL_REQUIRED))
    if "alo186" not in folded or "bağımsız" not in folded:
        raise AssertionError(("independence_copy_missing", label))
    return {
        "label": label,
        "bytes": len(body),
        "sha256": sha256(body),
        "canonical": canonicals[0],
        "effectiveUrl": effective_url,
        "forbiddenCopyCount": 0,
    }


def verify_once(origin: str, expected_commit: str | None, attempt: int) -> dict:
    nonce = f"v214-{attempt}-{int(time.time())}"
    home_body, home_type, home_url, home_status = fetch(f"{origin}/?quality={nonce}", accept="text/html")
    portal_body, portal_type, portal_url, portal_status = fetch(f"{origin}/elektrik-portali?quality={nonce}", accept="text/html")
    if home_status != 200 or home_type != "text/html":
        raise AssertionError(("home_response", home_status, home_type, home_url))
    if portal_status != 200 or portal_type != "text/html":
        raise AssertionError(("portal_response", portal_status, portal_type, portal_url))
    pages_body, pages_type, pages_url, pages_status = fetch(f"{origin}/pages-release.json?quality={nonce}", accept="application/json")
    quality_body, quality_type, quality_url, quality_status = fetch(f"{origin}/live-quality-v214.json?quality={nonce}", accept="application/json")
    if pages_status != 200 or pages_type not in {"application/json", "application/manifest+json"}:
        raise AssertionError(("pages_release_response", pages_status, pages_type, pages_url))
    if quality_status != 200 or quality_type not in {"application/json", "application/manifest+json"}:
        raise AssertionError(("quality_receipt_response", quality_status, quality_type, quality_url))
    pages = json.loads(pages_body.decode("utf-8"))
    quality = json.loads(quality_body.decode("utf-8"))
    metadata = pages.get("liveQualityCompletionV214") or {}
    if metadata.get("version") != VERSION:
        raise AssertionError(("release_v214_missing", metadata))
    if quality.get("version") != VERSION or quality.get("ok") is not True:
        raise AssertionError(("quality_receipt_invalid", quality.get("version"), quality.get("ok")))
    if quality.get("internalLinks", {}).get("brokenInternalLinks") != 0:
        raise AssertionError(("broken_internal_links", quality.get("internalLinks")))
    if quality.get("searchDiscovery", {}).get("sitemapCanonicalMismatches") != 0:
        raise AssertionError(("sitemap_canonical_mismatch", quality.get("searchDiscovery")))
    if metadata.get("personalDataCollectionAdded") is not False or metadata.get("officialInstitutionClaimed") is not False:
        raise AssertionError(("trust_contract", metadata))
    served_commit = str(pages.get("commit") or "")
    if expected_commit and served_commit != expected_commit:
        raise AssertionError(("served_commit", served_commit, expected_commit))

    robots_body, robots_type, robots_url, robots_status = fetch(f"{origin}/robots.txt?quality={nonce}", accept="text/plain")
    sitemap_body, sitemap_type, sitemap_url, sitemap_status = fetch(f"{origin}/sitemap.xml?quality={nonce}", accept="application/xml,text/xml")
    if robots_status != 200 or robots_type != "text/plain":
        raise AssertionError(("robots_response", robots_status, robots_type, robots_url))
    if sitemap_status != 200 or sitemap_type not in {"application/xml", "text/xml"}:
        raise AssertionError(("sitemap_response", sitemap_status, sitemap_type, sitemap_url))
    robots = robots_body.decode("utf-8", errors="replace")
    if "Sitemap: https://alo186.com/sitemap.xml" not in robots:
        raise AssertionError("robots.txt apex sitemap bildirimi taşımıyor")
    if re.search(r"^\s*Disallow:\s*/\s*$", robots, re.I | re.M):
        raise AssertionError("robots.txt tüm siteyi engelliyor")
    sitemap_root = ElementTree.fromstring(sitemap_body.decode("utf-8"))
    locs = [element.text.strip() for element in sitemap_root.iter() if element.tag.casefold().endswith("loc") and element.text]
    if not locs or len(locs) != len(set(locs)):
        raise AssertionError(("sitemap_empty_or_duplicate", len(locs), len(set(locs))))
    if any(not loc.startswith("https://alo186.com/") for loc in locs):
        raise AssertionError("sitemap.xml apex dışı URL taşıyor")

    return {
        "ok": True,
        "version": VERSION,
        "origin": origin,
        "servedCommit": served_commit,
        "home": validate_html("home", home_body, home_url, "/"),
        "portal": validate_html("portal", portal_body, portal_url, "/elektrik-portali"),
        "releaseSha256": sha256(pages_body),
        "qualityReceiptSha256": sha256(quality_body),
        "robotsSha256": sha256(robots_body),
        "sitemapSha256": sha256(sitemap_body),
        "sitemapUrlCount": len(locs),
        "forbiddenLiveCopy": [],
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }


def verify(origin: str, expected_commit: str | None, attempts: int, sleep_seconds: int) -> dict:
    normalized = normalize_origin(origin)
    errors: list[str] = []
    for attempt in range(1, attempts + 1):
        try:
            result = verify_once(normalized, expected_commit, attempt)
            result["attempt"] = attempt
            return result
        except (AssertionError, HTTPError, URLError, TimeoutError, ElementTree.ParseError, json.JSONDecodeError) as exc:
            errors.append(f"attempt {attempt}: {exc}")
            if attempt < attempts:
                time.sleep(sleep_seconds)
    raise RuntimeError("ALO186 canlı kopya v214 kabulü başarısız:\n- " + "\n- ".join(errors[-10:]))


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı ana sayfa, portal, release, robots ve sitemap kopyasını fail-closed doğrular.")
    parser.add_argument("--origin", default="https://alo186.com")
    parser.add_argument("--expected-commit", default="")
    parser.add_argument("--attempts", type=int, default=36)
    parser.add_argument("--sleep-seconds", type=int, default=10)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.origin, args.expected_commit or None, max(1, args.attempts), max(0, args.sleep_seconds))
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
