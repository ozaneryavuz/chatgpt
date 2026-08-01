from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

from verify_live_origin import normalize_origin, run_curl, sha256

ROUTE = "/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/"
VERSION = 177
DOM_MARKER = "data-alo186-contextual-affiliate-v177"
PRODUCT_CARD_MARKER = 'class="alo186-contextual-product"'
GATE_MARKER = "data-affiliate-gate="
AFFILIATE_TAG = "alo186rehber-21"
DISCLOSURE = "Bir Amazon Gelir Ortağı olarak nitelikli satın alımlardan kazanç elde ediyorum."
EXPECTED_PAGE_PLACEMENTS = 3
REQUIRED_REL = "sponsored nofollow noopener"
JS_FILE = "alo186-contextual-affiliate-v177.js"
CSS_FILE = "alo186-contextual-affiliate-v177.css"

H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
CANONICAL_RE = re.compile(
    r"<link\b[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)[\"']",
    re.I,
)
SCRIPT_RE = re.compile(r"<script\b[^>]*src=[\"']([^\"']+)[\"'][^>]*>", re.I)
STYLE_RE = re.compile(r"<link\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>", re.I)
STATIC_AMAZON_RE = re.compile(
    r'<a\b[^>]*href=["\']https?://(?:www\.)?(?:amazon\.com\.tr|amzn\.to)',
    re.I,
)
FORBIDDEN_SCHEMA_RE = re.compile(
    r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"',
    re.I,
)


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def normalized_path(value: str) -> str:
    path = urlparse(value).path or "/"
    return path.rstrip("/") or "/"


def find_asset(html: str, filename: str, pattern: re.Pattern[str]) -> str:
    for match in pattern.finditer(html):
        value = match.group(1)
        if value.split("?", 1)[0].endswith(filename):
            return value
    raise AssertionError(f"Canlı v177 asset bağlantısı eksik: {filename}")


def validate_live_html(
    *,
    html: str,
    http_code: int,
    content_type: str,
    effective_url: str,
    origin: str,
    route: str = ROUTE,
) -> dict[str, object]:
    media_type = content_type.split(";", 1)[0].strip().casefold()
    expected_host = (urlparse(origin).hostname or "").casefold().removeprefix("www.")
    effective = urlparse(effective_url)
    effective_host = (effective.hostname or "").casefold().removeprefix("www.")

    if http_code != 200:
        raise AssertionError(f"Canlı v177 rota HTTP {http_code} döndü")
    if media_type != "text/html":
        raise AssertionError(f"Canlı v177 rota HTML değil: {content_type}")
    if effective_host != expected_host:
        raise AssertionError(f"Canlı v177 rota farklı hosta gitti: {effective_url}")
    if normalized_path(effective_url) != normalized_path(route):
        raise AssertionError(f"Canlı v177 rota başka yola yönlendi: {effective_url}")
    if len(html.encode("utf-8")) < 4000:
        raise AssertionError("Canlı v177 HTML gövdesi beklenenden küçük")
    if DOM_MARKER not in html:
        raise AssertionError("Canlı v177 DOM işareti bulunamadı")
    if AFFILIATE_TAG not in html:
        raise AssertionError("Canlı v177 affiliate etiketi bulunamadı")

    visible = text_only(html)
    folded = visible.casefold()
    for token in (
        "konuya göre elektrik ürünleri haritası",
        "amazon gelir ortağı",
        "yeni ürün almayın",
    ):
        if token not in folded:
            raise AssertionError(f"Canlı v177 kullanıcı sözleşmesi eksik: {token}")

    h1 = H1_RE.search(html)
    if not h1 or "konuya göre elektrik ürünleri haritası" not in text_only(h1.group(1)).casefold():
        raise AssertionError("Canlı v177 H1 yanlış veya eksik")

    canonical_match = CANONICAL_RE.search(html)
    if not canonical_match:
        raise AssertionError("Canlı v177 canonical bağlantısı eksik")
    canonical = canonical_match.group(1)
    canonical_host = (urlparse(canonical).hostname or "").casefold().removeprefix("www.")
    if canonical_host != expected_host:
        raise AssertionError(f"Canlı v177 canonical host yanlış: {canonical}")
    if normalized_path(canonical) != normalized_path(route):
        raise AssertionError(f"Canlı v177 canonical yol yanlış: {canonical}")

    placements = html.count(PRODUCT_CARD_MARKER)
    gates = html.count(GATE_MARKER)
    if placements != EXPECTED_PAGE_PLACEMENTS:
        raise AssertionError(
            f"Canlı v177 ürün yerleşimi {placements}; beklenen {EXPECTED_PAGE_PLACEMENTS}"
        )
    if gates != EXPECTED_PAGE_PLACEMENTS:
        raise AssertionError(
            f"Canlı v177 ticari kapı sayısı {gates}; beklenen {EXPECTED_PAGE_PLACEMENTS}"
        )
    static_store_links = len(STATIC_AMAZON_RE.findall(html))
    if static_store_links:
        raise AssertionError(
            f"Canlı v177 HTML içinde kapısız mağaza bağlantısı bulundu: {static_store_links}"
        )
    if FORBIDDEN_SCHEMA_RE.search(html):
        raise AssertionError("Canlı v177 sayfasında yasaklı ticari schema türü bulundu")

    js_src = find_asset(html, JS_FILE, SCRIPT_RE)
    css_href = find_asset(html, CSS_FILE, STYLE_RE)
    return {
        "canonical": canonical,
        "placementCount": placements,
        "gateCount": gates,
        "staticStoreLinkCount": static_store_links,
        "jsUrl": urljoin(origin.rstrip("/") + "/", js_src),
        "cssUrl": urljoin(origin.rstrip("/") + "/", css_href),
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
        "unverifiedCommercialFieldsPublished": False,
    }


def validate_live_javascript(
    *,
    javascript: str,
    http_code: int,
    content_type: str,
    effective_url: str,
) -> dict[str, object]:
    media_type = content_type.split(";", 1)[0].strip().casefold()
    if http_code != 200:
        raise AssertionError(f"Canlı v177 JavaScript HTTP {http_code} döndü")
    if media_type not in {"application/javascript", "text/javascript", "application/x-javascript", "text/plain"}:
        raise AssertionError(f"Canlı v177 asset JavaScript değil: {content_type}")
    if len(javascript.encode("utf-8")) < 1000:
        raise AssertionError("Canlı v177 JavaScript gövdesi beklenenden küçük")
    for token in (
        AFFILIATE_TAG,
        REQUIRED_REL,
        "affiliate_context_view",
        "affiliate_gate_open",
        "affiliate_product_select",
        "window.alo186Analytics.track",
    ):
        if token not in javascript:
            raise AssertionError(f"Canlı v177 JavaScript sözleşmesi eksik: {token}")
    for forbidden in ("localStorage", "document.cookie"):
        if forbidden in javascript:
            raise AssertionError(f"Canlı v177 JavaScript kişisel izleme alanı taşıyor: {forbidden}")
    return {
        "jsEffectiveUrl": effective_url,
        "affiliateTag": AFFILIATE_TAG,
        "requiredRel": REQUIRED_REL,
        "analyticsEvents": [
            "affiliate_context_view",
            "affiliate_gate_open",
            "affiliate_product_select",
        ],
        "localStorageUsed": False,
        "cookieUsed": False,
    }


def verify(
    *,
    origin: str,
    route: str,
    diagnostics: Path,
    attempts: int,
    sleep_seconds: int,
) -> dict[str, object]:
    live_origin = normalize_origin(origin)
    diagnostics.mkdir(parents=True, exist_ok=True)
    errors: list[dict[str, object]] = []

    for attempt in range(1, attempts + 1):
        page = run_curl(
            url=f"{live_origin}{route}?v177_live={int(time.time())}-{attempt}",
            name=f"contextual-v177-page-{attempt}",
            diagnostics=diagnostics,
            follow=True,
            accept="text/html",
            fail_http=False,
        )
        html = page.body_path.read_text(encoding="utf-8", errors="ignore") if page.body_path.exists() else ""
        try:
            page_metrics = validate_live_html(
                html=html,
                http_code=page.http_code,
                content_type=page.content_type,
                effective_url=page.effective_url,
                origin=live_origin,
                route=route,
            )
            js_url = str(page_metrics["jsUrl"])
            asset = run_curl(
                url=f"{js_url}{'&' if '?' in js_url else '?'}v177_live={int(time.time())}-{attempt}",
                name=f"contextual-v177-js-{attempt}",
                diagnostics=diagnostics,
                follow=True,
                accept="application/javascript,text/javascript,*/*",
                fail_http=False,
            )
            javascript = asset.body_path.read_text(encoding="utf-8", errors="ignore") if asset.body_path.exists() else ""
            js_metrics = validate_live_javascript(
                javascript=javascript,
                http_code=asset.http_code,
                content_type=asset.content_type,
                effective_url=asset.effective_url,
            )
            return {
                "ok": True,
                "checkedAt": datetime.now(timezone.utc).isoformat(),
                "origin": live_origin,
                "route": route,
                "version": VERSION,
                "verifiedAttempt": attempt,
                "pageHttpCode": page.http_code,
                "pageContentType": page.content_type,
                "pageEffectiveUrl": page.effective_url,
                "pageSha256": sha256(page.body_path),
                "pageBytes": page.body_path.stat().st_size,
                "jsSha256": sha256(asset.body_path),
                "jsBytes": asset.body_path.stat().st_size,
                **page_metrics,
                **js_metrics,
            }
        except AssertionError as exc:
            errors.append(
                {
                    "attempt": attempt,
                    "error": str(exc),
                    "pageHttpCode": page.http_code,
                    "pageContentType": page.content_type,
                    "pageEffectiveUrl": page.effective_url,
                    "pageBytes": page.body_path.stat().st_size if page.body_path.exists() else 0,
                    "pageSha256": sha256(page.body_path) if page.body_path.exists() else None,
                }
            )
        if attempt < attempts:
            time.sleep(sleep_seconds)

    return {
        "ok": False,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "origin": live_origin,
        "route": route,
        "version": VERSION,
        "attempts": attempts,
        "errors": errors[-5:],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 v177 bağlamsal ürün haritasını gerçek canlı origin üzerinde fail-closed doğrular.")
    parser.add_argument("--origin", default="https://alo186.com")
    parser.add_argument("--route", default=ROUTE)
    parser.add_argument("--diagnostics", type=Path, default=Path("/tmp/alo186-v177-live-diagnostics"))
    parser.add_argument("--receipt", type=Path, default=Path("/tmp/alo186-v177-live-receipt.json"))
    parser.add_argument("--attempts", type=int, default=24)
    parser.add_argument("--sleep-seconds", type=int, default=10)
    args = parser.parse_args()
    receipt = verify(
        origin=args.origin,
        route=args.route,
        diagnostics=args.diagnostics,
        attempts=max(1, args.attempts),
        sleep_seconds=max(0, args.sleep_seconds),
    )
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    if not receipt.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
