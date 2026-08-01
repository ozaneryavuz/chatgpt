from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186/deployment"))

import verify_contextual_affiliate_live_v177 as verifier  # noqa: E402


def valid_html() -> str:
    cards = []
    for index in range(verifier.EXPECTED_PAGE_PLACEMENTS):
        cards.append(
            f'''<article class="alo186-contextual-product" data-product-class="product-{index + 1}">
            <h2>Ürün sınıfı {index + 1}</h2>
            <button type="button" data-affiliate-gate="gate-{index + 1}">Teknik uygunluğu doğrula</button>
            </article>'''
        )
    return f'''<!doctype html><html lang="tr"><head>
    <link rel="canonical" href="https://www.alo186.com{verifier.ROUTE}">
    <link rel="stylesheet" href="/assets/{verifier.CSS_FILE}">
    <title>Konuya Göre Elektrik Ürünleri Haritası | ALO186</title></head><body>
    <main {verifier.DOM_MARKER}>
    <h1>Konuya göre elektrik ürünleri haritası</h1>
    <p>{verifier.DISCLOSURE} Mevcut ürün yeterliyse yeni ürün almayın.</p>
    <script type="application/json">{{"affiliateTag":"{verifier.AFFILIATE_TAG}"}}</script>
    {''.join(cards)}
    </main>
    <script src="/assets/{verifier.JS_FILE}"></script>
    {' ' * 5000}</body></html>'''


def valid_javascript() -> str:
    return f'''(() => {{
    const affiliateTag = "{verifier.AFFILIATE_TAG}";
    const rel = "{verifier.REQUIRED_REL}";
    function track(name) {{ if (window.alo186Analytics) window.alo186Analytics.track(name, {{}}); }}
    track("affiliate_context_view");
    track("affiliate_gate_open");
    track("affiliate_product_select");
    window.Alo186V177 = {{ affiliateTag, rel }};
    }})();{' ' * 2000}'''


def expect_html_failure(html: str, token: str) -> None:
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
        raise AssertionError(f"Beklenen HTML hatası oluşmadı: {token}")


def expect_js_failure(javascript: str, token: str) -> None:
    try:
        verifier.validate_live_javascript(
            javascript=javascript,
            http_code=200,
            content_type="application/javascript; charset=utf-8",
            effective_url=f"https://alo186.com/assets/{verifier.JS_FILE}",
        )
    except AssertionError as exc:
        assert token.casefold() in str(exc).casefold(), (token, str(exc))
    else:
        raise AssertionError(f"Beklenen JavaScript hatası oluşmadı: {token}")


def validate_workflow_contract() -> None:
    workflow = (ROOT / ".github/workflows/alo186-pages-autobootstrap-live.yml").read_text(encoding="utf-8")
    for token in (
        "ALO186_PAGES_ADMIN_TOKEN",
        "ADMIN_TOKEN_PRESENT",
        "verify_live_origin.py",
        "verify_contextual_affiliate_live_v177.py",
        "alo186-v177-live-blocker",
        "alo186-v177-live-receipt",
        "Fail-closed canlı kabul sonucu",
    ):
        assert token in workflow, token
    assert "if (error.status !== 404) throw error" not in workflow
    assert "await github.request('POST /repos/{owner}/{repo}/pages'" in workflow
    assert "if (!adminTokenPresent)" in workflow


def main() -> None:
    html = valid_html()
    page = verifier.validate_live_html(
        html=html,
        http_code=200,
        content_type="text/html; charset=utf-8",
        effective_url=f"https://alo186.com{verifier.ROUTE}",
        origin="https://alo186.com",
    )
    assert page["placementCount"] == 3
    assert page["gateCount"] == 3
    assert page["staticStoreLinkCount"] == 0
    assert page["jsUrl"].endswith(verifier.JS_FILE)
    assert page["cssUrl"].endswith(verifier.CSS_FILE)

    javascript = valid_javascript()
    asset = verifier.validate_live_javascript(
        javascript=javascript,
        http_code=200,
        content_type="application/javascript; charset=utf-8",
        effective_url=f"https://alo186.com/assets/{verifier.JS_FILE}",
    )
    assert asset["affiliateTag"] == verifier.AFFILIATE_TAG
    assert asset["localStorageUsed"] is False
    assert asset["cookieUsed"] is False

    expect_html_failure(html.replace(verifier.DOM_MARKER, ""), "DOM işareti")
    expect_html_failure(html.replace(verifier.AFFILIATE_TAG, "yanlis-etiket", 1), "affiliate etiketi")
    expect_html_failure(html.replace(verifier.PRODUCT_CARD_MARKER, 'class="other"', 1), "ürün yerleşimi")
    expect_html_failure(html.replace(verifier.GATE_MARKER, "data-other=", 1), "ticari kapı")
    expect_html_failure(
        html.replace("</main>", '<a href="https://www.amazon.com.tr/s?k=test">Kapısız mağaza</a></main>'),
        "kapısız mağaza",
    )
    expect_html_failure(html.replace(verifier.ROUTE, "/yanlis-rota/", 1), "canonical yol")
    expect_js_failure(javascript.replace(verifier.REQUIRED_REL, "noopener"), "rel")
    expect_js_failure(javascript + "\nlocalStorage.setItem('x','y');", "localStorage")

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
        "version": verifier.VERSION,
        "route": verifier.ROUTE,
        "placementCount": page["placementCount"],
        "gateCount": page["gateCount"],
        "failClosedCases": 9,
        "dualHostingWorkflow": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
