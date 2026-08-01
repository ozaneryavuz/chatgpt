from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from verify_live_origin import normalize_origin, run_curl, sha256

ROUTE = "/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/"
DOM_MARKER = 'data-alo186-product-map-v176="true"'
CARD_MARKER = 'data-product-card="true"'
SHOP_MARKER = 'data-affiliate-action="shop"'
AFFILIATE_TAG = "alo186rehber-21"
EXPECTED_PRODUCT_CLASSES = 86
EXPECTED_GROUPS = 13
REQUIRED_REL = {"sponsored", "nofollow", "noopener"}

ANCHOR_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>", re.I | re.S)
ATTR_RE = re.compile(
    r"(?P<name>[a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
    re.S,
)
CANONICAL_RE = re.compile(r"<link\b[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)[\"']", re.I)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)


def attributes(raw: str) -> dict[str, str]:
    return {
        match.group("name").casefold(): match.group("value")
        for match in ATTR_RE.finditer(raw)
    }


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def normalized_path(value: str) -> str:
    path = urlparse(value).path or "/"
    return path.rstrip("/") or "/"


def validate_affiliate_anchors(html: str) -> int:
    count = 0
    for match in ANCHOR_RE.finditer(html):
        attrs = attributes(match.group("attrs"))
        href = attrs.get("href", "")
        parsed = urlparse(href)
        host = (parsed.hostname or "").casefold().removeprefix("www.")
        if host not in {"amazon.com.tr", "amzn.to"}:
            continue
        count += 1
        rel = {token.casefold() for token in attrs.get("rel", "").split() if token}
        missing = REQUIRED_REL - rel
        if missing:
            raise AssertionError(
                f"Affiliate bağlantısında eksik rel tokenları: {sorted(missing)} → {href}"
            )
        query = parse_qs(parsed.query)
        if host == "amazon.com.tr" and AFFILIATE_TAG not in query.get("tag", []):
            raise AssertionError(f"Amazon bağlantısında affiliate tag eksik: {href}")
    return count


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
    expected_host = urlparse(origin).hostname or ""
    effective = urlparse(effective_url)
    if http_code != 200:
        raise AssertionError(f"Canlı v176 rota HTTP {http_code} döndü")
    if media_type != "text/html":
        raise AssertionError(f"Canlı v176 rota HTML değil: {content_type}")
    if effective.hostname != expected_host:
        raise AssertionError(f"Canlı v176 rota farklı hosta gitti: {effective_url}")
    if normalized_path(effective_url) != normalized_path(route):
        raise AssertionError(f"Canlı v176 rota başka yola yönlendi: {effective_url}")
    if len(html.encode("utf-8")) < 5000:
        raise AssertionError("Canlı v176 HTML gövdesi beklenenden küçük")
    if DOM_MARKER not in html:
        raise AssertionError("Canlı v176 DOM işareti bulunamadı")
    if AFFILIATE_TAG not in html:
        raise AssertionError("Canlı v176 affiliate etiketi bulunamadı")

    folded = text_only(html).casefold()
    for token in (
        "konuya göre elektrik ürünleri haritası",
        "satış ortaklığı",
        "mevcut güvenli ürün yeterliyse yeni ürün almayın",
    ):
        if token not in folded:
            raise AssertionError(f"Canlı v176 kullanıcı sözleşmesi eksik: {token}")

    h1_match = H1_RE.search(html)
    if not h1_match or "konuya göre elektrik ürünleri haritası" not in text_only(h1_match.group(1)).casefold():
        raise AssertionError("Canlı v176 H1 yanlış veya eksik")

    canonical_match = CANONICAL_RE.search(html)
    if not canonical_match:
        raise AssertionError("Canlı v176 canonical bağlantısı eksik")
    canonical = canonical_match.group(1)
    canonical_host = (urlparse(canonical).hostname or "").casefold().removeprefix("www.")
    if canonical_host != expected_host.casefold().removeprefix("www."):
        raise AssertionError(f"Canlı v176 canonical host yanlış: {canonical}")
    if normalized_path(canonical) != normalized_path(route):
        raise AssertionError(f"Canlı v176 canonical yol yanlış: {canonical}")

    product_cards = html.count(CARD_MARKER)
    shop_actions = html.count(SHOP_MARKER)
    if product_cards != EXPECTED_PRODUCT_CLASSES:
        raise AssertionError(
            f"Canlı v176 ürün sınıfı sayısı {product_cards}; beklenen {EXPECTED_PRODUCT_CLASSES}"
        )
    if shop_actions != EXPECTED_PRODUCT_CLASSES:
        raise AssertionError(
            f"Canlı v176 mağaza eylemi sayısı {shop_actions}; beklenen {EXPECTED_PRODUCT_CLASSES}"
        )
    affiliate_links = validate_affiliate_anchors(html)
    if affiliate_links < EXPECTED_PRODUCT_CLASSES:
        raise AssertionError(
            f"Canlı v176 affiliate bağlantısı {affiliate_links}; en az {EXPECTED_PRODUCT_CLASSES} bekleniyor"
        )

    forbidden_schema = re.compile(
        r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"',
        re.I,
    )
    if forbidden_schema.search(html):
        raise AssertionError("Canlı v176 sayfasında yasaklı ticari schema türü bulundu")

    return {
        "productClassCount": product_cards,
        "shopActionCount": shop_actions,
        "affiliateLinkCount": affiliate_links,
        "affiliateTag": AFFILIATE_TAG,
        "requiredRel": sorted(REQUIRED_REL),
        "canonical": canonical,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
        "unverifiedCommercialFieldsPublished": False,
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
    last_result = None

    for attempt in range(1, attempts + 1):
        result = run_curl(
            url=f"{live_origin}{route}?v176_live={int(time.time())}-{attempt}",
            name=f"contextual-v176-{attempt}",
            diagnostics=diagnostics,
            follow=True,
            accept="text/html",
            fail_http=False,
        )
        last_result = result
        html = result.body_path.read_text(encoding="utf-8", errors="ignore") if result.body_path.exists() else ""
        try:
            metrics = validate_live_html(
                html=html,
                http_code=result.http_code,
                content_type=result.content_type,
                effective_url=result.effective_url,
                origin=live_origin,
                route=route,
            )
            return {
                "ok": True,
                "checkedAt": datetime.now(timezone.utc).isoformat(),
                "origin": live_origin,
                "route": route,
                "verifiedAttempt": attempt,
                "httpCode": result.http_code,
                "contentType": result.content_type,
                "effectiveUrl": result.effective_url,
                "htmlSha256": sha256(result.body_path),
                "htmlBytes": result.body_path.stat().st_size,
                **metrics,
            }
        except AssertionError as exc:
            errors.append(
                {
                    "attempt": attempt,
                    "error": str(exc),
                    "httpCode": result.http_code,
                    "contentType": result.content_type,
                    "effectiveUrl": result.effective_url,
                    "htmlBytes": result.body_path.stat().st_size if result.body_path.exists() else 0,
                    "htmlSha256": sha256(result.body_path) if result.body_path.exists() else None,
                }
            )
        if attempt < attempts:
            time.sleep(sleep_seconds)

    return {
        "ok": False,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "origin": live_origin,
        "route": route,
        "attempts": attempts,
        "lastHttpCode": getattr(last_result, "http_code", None),
        "lastContentType": getattr(last_result, "content_type", None),
        "lastEffectiveUrl": getattr(last_result, "effective_url", None),
        "errors": errors[-5:],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 v176 ürün haritasını gerçek canlı origin üzerinde fail-closed doğrular.")
    parser.add_argument("--origin", default="https://alo186.com")
    parser.add_argument("--route", default=ROUTE)
    parser.add_argument("--diagnostics", type=Path, default=Path("/tmp/alo186-v176-live-diagnostics"))
    parser.add_argument("--receipt", type=Path, default=Path("/tmp/alo186-v176-live-receipt.json"))
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
