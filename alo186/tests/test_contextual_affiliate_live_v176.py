from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186/deployment"))

import verify_contextual_affiliate_live_v176 as verifier  # noqa: E402


def valid_html() -> str:
    cards = []
    for index in range(verifier.EXPECTED_PRODUCT_CLASSES):
        cards.append(
            f'''<article data-product-card="true">
            <h2>Ürün sınıfı {index + 1}</h2>
            <a data-affiliate-action="shop"
               href="https://www.amazon.com.tr/s?k=urun+{index + 1}&tag={verifier.AFFILIATE_TAG}"
               rel="sponsored nofollow noopener">Amazon seçeneklerini incele</a>
            </article>'''
        )
    return f'''<!doctype html><html lang="tr"><head>
    <link rel="canonical" href="https://www.alo186.com{verifier.ROUTE}">
    <title>Konuya Göre Elektrik Ürünleri Haritası | ALO186</title></head><body>
    <main {verifier.DOM_MARKER}>
    <h1>Konuya göre elektrik ürünleri haritası</h1>
    <p>Satış ortaklığı açıklaması. Mevcut güvenli ürün yeterliyse yeni ürün almayın.</p>
    {''.join(cards)}
    </main>{' ' * 6000}</body></html>'''


def expect_failure(html: str, token: str) -> None:
    try:
        verifier.validate_live_html(
            html=html,
            http_code=200,
            content_type="text/html; charset=utf-8",
            effective_url=f"https://alo186.com{verifier.ROUTE}",
            origin="https://alo186.com",
        )
    except AssertionError as exc:
        assert token.casefold() in str(exc).casefold(), (token, str(exc))
    else:
        raise AssertionError(f"Beklenen hata oluşmadı: {token}")


def validate_workflow_contract() -> None:
    path = ROOT / ".github/workflows/alo186-contextual-affiliate-v176.yml"
    workflow = path.read_text(encoding="utf-8")
    assert "actions/configure-pages" not in workflow
    assert "actions/upload-pages-artifact" not in workflow
    assert "actions/deploy-pages" not in workflow
    for token in (
        "verify_live_origin.py",
        "verify_contextual_affiliate_live_v176.py",
        "verify_live_after_publish",
        "alo186-contextual-v176-live-receipt",
        "alo186-v176-live-blocker",
        "await upsert(606)",
        "await upsert(21)",
        "Fail-closed canlı kabul sonucu",
    ):
        assert token in workflow, token


def main() -> None:
    html = valid_html()
    metrics = verifier.validate_live_html(
        html=html,
        http_code=200,
        content_type="text/html; charset=utf-8",
        effective_url=f"https://alo186.com{verifier.ROUTE}",
        origin="https://alo186.com",
    )
    assert metrics["productClassCount"] == 86
    assert metrics["shopActionCount"] == 86
    assert metrics["affiliateLinkCount"] == 86
    assert metrics["personalDataCollectionAdded"] is False
    assert metrics["officialInstitutionClaimed"] is False

    expect_failure(html.replace(verifier.DOM_MARKER, ""), "DOM işareti")
    expect_failure(html.replace("sponsored nofollow noopener", "noopener", 1), "rel token")
    expect_failure(html.replace(f"tag={verifier.AFFILIATE_TAG}", "tag=yanlis", 1), "affiliate tag")
    expect_failure(html.replace(verifier.CARD_MARKER, "data-product-card=\"false\"", 1), "ürün sınıfı")
    expect_failure(html.replace(verifier.ROUTE, "/yanlis-rota/", 1), "canonical yol")

    try:
        verifier.validate_live_html(
            html=html,
            http_code=404,
            content_type="text/html",
            effective_url=f"https://alo186.com{verifier.ROUTE}",
            origin="https://alo186.com",
        )
    except AssertionError as exc:
        assert "HTTP 404" in str(exc)
    else:
        raise AssertionError("404 rota kabul edilmemeliydi")

    validate_workflow_contract()

    print(json.dumps({
        "ok": True,
        "route": verifier.ROUTE,
        "productClassCount": metrics["productClassCount"],
        "affiliateLinkCount": metrics["affiliateLinkCount"],
        "failClosedCases": 6,
        "hostingAwareWorkflow": True,
        "pagesAssumptionRemoved": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
