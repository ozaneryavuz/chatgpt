from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

VERSION = 177
ROUTE = "/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/"
MARKER = "data-alo186-contextual-affiliate-v177"
TAG = "alo186rehber-21"
DISCLOSURE = "Bir Amazon Gelir Ortağı olarak nitelikli satın alımlardan kazanç elde ediyorum."
JS_FILE = "alo186-contextual-affiliate-v177.js"
CSS_FILE = "alo186-contextual-affiliate-v177.css"
EXPECTED_PLACEMENTS = 3
REQUIRED_REL = "sponsored nofollow noopener"

CANONICAL_RE = re.compile(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', re.I)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
SCRIPT_RE = re.compile(r'<script\b[^>]*src=["\']([^"\']+)', re.I)
STYLE_RE = re.compile(r'<link\b[^>]*href=["\']([^"\']+)', re.I)
STATIC_AMAZON_RE = re.compile(r'<a\b[^>]*href=["\']https?://(?:www\.)?(?:amazon\.com\.tr|amzn\.to)', re.I)
FORBIDDEN_SCHEMA_RE = re.compile(r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"', re.I)


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def normalized_path(value: str) -> str:
    return (urlparse(value).path.rstrip("/") or "/")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str, accept: str) -> dict[str, object]:
    request = Request(
        url,
        headers={
            "Accept": accept,
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
            "User-Agent": "ALO186-live-v177-verifier/1.0",
        },
    )
    try:
        with urlopen(request, timeout=25) as response:
            body = response.read()
            return {
                "status": int(response.status),
                "contentType": response.headers.get("Content-Type", ""),
                "effectiveUrl": response.geturl(),
                "body": body,
            }
    except HTTPError as error:
        return {
            "status": int(error.code),
            "contentType": error.headers.get("Content-Type", "") if error.headers else "",
            "effectiveUrl": error.geturl(),
            "body": error.read(),
        }
    except URLError as error:
        raise RuntimeError(f"Canlı istek başarısız: {error}") from error


def asset_url(html: str, filename: str, pattern: re.Pattern[str], origin: str) -> str:
    for match in pattern.finditer(html):
        candidate = match.group(1)
        if candidate.split("?", 1)[0].endswith(filename):
            return urljoin(origin.rstrip("/") + "/", candidate)
    raise AssertionError(f"Canlı v177 asset bağlantısı eksik: {filename}")


def validate_page(html: str, response: dict[str, object], origin: str, route: str = ROUTE) -> dict[str, object]:
    status = int(response["status"])
    content_type = str(response["contentType"])
    effective_url = str(response["effectiveUrl"])
    if status != 200:
        raise AssertionError(f"Canlı v177 rota HTTP {status} döndü")
    if content_type.split(";", 1)[0].strip().casefold() != "text/html":
        raise AssertionError(f"Canlı v177 rota HTML değil: {content_type}")
    expected_host = (urlparse(origin).hostname or "").removeprefix("www.")
    effective_host = (urlparse(effective_url).hostname or "").removeprefix("www.")
    if effective_host != expected_host or normalized_path(effective_url) != normalized_path(route):
        raise AssertionError(f"Canlı v177 rota başka hedefe gitti: {effective_url}")
    if len(html.encode("utf-8")) < 4000:
        raise AssertionError("Canlı v177 HTML gövdesi beklenenden küçük")
    if MARKER not in html or TAG not in html:
        raise AssertionError("Canlı v177 markerı veya affiliate etiketi eksik")

    visible = text_only(html).casefold()
    for token in ("konuya göre elektrik ürünleri haritası", "amazon gelir ortağı", "yeni ürün almayın"):
        if token not in visible:
            raise AssertionError(f"Canlı v177 kullanıcı sözleşmesi eksik: {token}")

    h1 = H1_RE.search(html)
    if not h1 or "konuya göre elektrik ürünleri haritası" not in text_only(h1.group(1)).casefold():
        raise AssertionError("Canlı v177 H1 yanlış veya eksik")
    canonical_match = CANONICAL_RE.search(html)
    if not canonical_match:
        raise AssertionError("Canlı v177 canonical bağlantısı eksik")
    canonical = canonical_match.group(1)
    if normalized_path(canonical) != normalized_path(route):
        raise AssertionError(f"Canlı v177 canonical yol yanlış: {canonical}")

    placements = html.count('class="alo186-contextual-product"')
    gates = html.count("data-affiliate-gate=")
    if placements != EXPECTED_PLACEMENTS or gates != EXPECTED_PLACEMENTS:
        raise AssertionError(f"Canlı v177 yerleşim/kapı sayısı yanlış: {placements}/{gates}")
    static_links = len(STATIC_AMAZON_RE.findall(html))
    if static_links:
        raise AssertionError(f"Canlı v177 HTML içinde kapısız mağaza bağlantısı var: {static_links}")
    if FORBIDDEN_SCHEMA_RE.search(html):
        raise AssertionError("Canlı v177 sayfasında yasaklı ticari schema bulundu")

    return {
        "canonical": canonical,
        "placementCount": placements,
        "gateCount": gates,
        "staticStoreLinkCount": static_links,
        "jsUrl": asset_url(html, JS_FILE, SCRIPT_RE, origin),
        "cssUrl": asset_url(html, CSS_FILE, STYLE_RE, origin),
    }


def validate_javascript(javascript: str, response: dict[str, object]) -> dict[str, object]:
    status = int(response["status"])
    content_type = str(response["contentType"])
    if status != 200:
        raise AssertionError(f"Canlı v177 JavaScript HTTP {status} döndü")
    media_type = content_type.split(";", 1)[0].strip().casefold()
    if media_type not in {"application/javascript", "text/javascript", "application/x-javascript", "text/plain"}:
        raise AssertionError(f"Canlı v177 asset JavaScript değil: {content_type}")
    if len(javascript.encode("utf-8")) < 1000:
        raise AssertionError("Canlı v177 JavaScript gövdesi beklenenden küçük")
    for token in (TAG, REQUIRED_REL, "affiliate_context_view", "affiliate_gate_open", "affiliate_product_select", "window.alo186Analytics.track"):
        if token not in javascript:
            raise AssertionError(f"Canlı v177 JavaScript sözleşmesi eksik: {token}")
    for forbidden in ("localStorage", "document.cookie"):
        if forbidden in javascript:
            raise AssertionError(f"Canlı v177 JavaScript kişisel izleme alanı taşıyor: {forbidden}")
    return {
        "affiliateTag": TAG,
        "requiredRel": REQUIRED_REL,
        "localStorageUsed": False,
        "cookieUsed": False,
    }


def verify(origin: str, route: str, diagnostics: Path, attempts: int, sleep_seconds: int) -> dict[str, object]:
    origin = origin.rstrip("/")
    diagnostics.mkdir(parents=True, exist_ok=True)
    errors: list[dict[str, object]] = []
    for attempt in range(1, attempts + 1):
        nonce = f"{int(time.time())}-{attempt}"
        page_response = fetch(f"{origin}{route}?v177_live={nonce}", "text/html")
        page_body = bytes(page_response["body"])
        (diagnostics / f"page-{attempt}.html").write_bytes(page_body)
        try:
            html = page_body.decode("utf-8", errors="ignore")
            page = validate_page(html, page_response, origin, route)
            js_response = fetch(f"{page['jsUrl']}?v177_live={nonce}", "application/javascript,text/javascript,*/*")
            js_body = bytes(js_response["body"])
            (diagnostics / f"asset-{attempt}.js").write_bytes(js_body)
            javascript = js_body.decode("utf-8", errors="ignore")
            asset = validate_javascript(javascript, js_response)
            return {
                "ok": True,
                "checkedAt": datetime.now(timezone.utc).isoformat(),
                "version": VERSION,
                "origin": origin,
                "route": route,
                "verifiedAttempt": attempt,
                "pageStatus": page_response["status"],
                "pageEffectiveUrl": page_response["effectiveUrl"],
                "pageSha256": sha256(page_body),
                "pageBytes": len(page_body),
                "jsSha256": sha256(js_body),
                "jsBytes": len(js_body),
                **page,
                **asset,
                "personalDataCollectionAdded": False,
                "officialInstitutionClaimed": False,
            }
        except (AssertionError, RuntimeError) as error:
            errors.append({
                "attempt": attempt,
                "error": str(error),
                "pageStatus": page_response.get("status"),
                "pageEffectiveUrl": page_response.get("effectiveUrl"),
                "pageSha256": sha256(page_body),
                "pageBytes": len(page_body),
            })
        if attempt < attempts:
            time.sleep(sleep_seconds)
    return {
        "ok": False,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "version": VERSION,
        "origin": origin,
        "route": route,
        "attempts": attempts,
        "errors": errors[-5:],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 v177 ürün haritasını gerçek canlı origin üzerinde doğrular.")
    parser.add_argument("--origin", default="https://alo186.com")
    parser.add_argument("--route", default=ROUTE)
    parser.add_argument("--diagnostics", type=Path, default=Path("/tmp/alo186-v177-live-diagnostics"))
    parser.add_argument("--receipt", type=Path, default=Path("/tmp/alo186-v177-live-receipt.json"))
    parser.add_argument("--attempts", type=int, default=24)
    parser.add_argument("--sleep-seconds", type=int, default=10)
    args = parser.parse_args()
    receipt = verify(args.origin, args.route, args.diagnostics, max(1, args.attempts), max(0, args.sleep_seconds))
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    if not receipt.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
