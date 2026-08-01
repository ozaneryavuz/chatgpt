from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186/deployment"))

import verify_contextual_affiliate_live_v177 as verifier  # noqa: E402


def valid_html() -> str:
    cards = []
    for index in range(verifier.EXPECTED_PLACEMENTS):
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
    <main {verifier.MARKER}>
    <h1>Konuya göre elektrik ürünleri haritası</h1>
    <p>{verifier.DISCLOSURE} Mevcut ürün yeterliyse yeni ürün almayın.</p>
    <script type="application/json">{{"affiliateTag":"{verifier.TAG}"}}</script>
    {''.join(cards)}
    </main>
    <script src="/assets/{verifier.JS_FILE}"></script>
    {' ' * 5000}</body></html>'''


def valid_javascript() -> str:
    return f'''(() => {{
    const affiliateTag = "{verifier.TAG}";
    const rel = "{verifier.REQUIRED_REL}";
    function track(name) {{ if (window.alo186Analytics) window.alo186Analytics.track(name, {{}}); }}
    track("affiliate_context_view");
    track("affiliate_gate_open");
    track("affiliate_product_select");
    window.Alo186V177 = {{ affiliateTag, rel }};
    }})();{' ' * 2000}'''


def expect_page_failure(html: str, token: str) -> None:
    response = {
        "status": 200,
        "contentType": "text/html; charset=utf-8",
        "effectiveUrl": f"https://alo186.com{verifier.ROUTE}",
    }
    try:
        verifier.validate_page(html, response, "https://alo186.com")
    except AssertionError as exc:
        assert token.casefold() in str(exc).casefold(), (token, str(exc))
    else:
        raise AssertionError(f"Beklenen sayfa hatası oluşmadı: {token}")


def expect_js_failure(javascript: str, token: str) -> None:
    response = {
        "status": 200,
        "contentType": "application/javascript; charset=utf-8",
        "effectiveUrl": f"https://alo186.com/assets/{verifier.JS_FILE}",
    }
    try:
        verifier.validate_javascript(javascript, response)
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
        "sites_current",
        "already_live_on_sites",
        "alo186-v177-live-blocker",
        "alo186-v177-live-receipt",
        "dispatch_pages:",
        "workflow_id: 'alo186-github-pages.yml'",
        "actions: write",
        "group: alo186-pages-production",
    ):
        assert token in workflow, token
    assert "actions/deploy-pages@" not in workflow
    assert "if (!adminTokenPresent)" in workflow
    assert "if (error.status !== 404) throw error" not in workflow
    assert "schedule:" in workflow and "*/30 * * * *" in workflow


def main() -> None:
    html = valid_html()
    page = verifier.validate_page(
        html,
        {
            "status": 200,
            "contentType": "text/html; charset=utf-8",
            "effectiveUrl": f"https://alo186.com{verifier.ROUTE}",
        },
        "https://alo186.com",
    )
    assert page["placementCount"] == 3
    assert page["gateCount"] == 3
    assert page["staticStoreLinkCount"] == 0
    assert page["jsUrl"].endswith(verifier.JS_FILE)
    assert page["cssUrl"].endswith(verifier.CSS_FILE)

    javascript = valid_javascript()
    asset = verifier.validate_javascript(
        javascript,
        {
            "status": 200,
            "contentType": "application/javascript; charset=utf-8",
            "effectiveUrl": f"https://alo186.com/assets/{verifier.JS_FILE}",
        },
    )
    assert asset["affiliateTag"] == verifier.TAG
    assert asset["localStorageUsed"] is False
    assert asset["cookieUsed"] is False

    expect_page_failure(html.replace(verifier.MARKER, ""), "marker")
    expect_page_failure(html.replace(verifier.TAG, "yanlis-etiket", 1), "affiliate etiketi")
    expect_page_failure(html.replace('class="alo186-contextual-product"', 'class="other"', 1), "yerleşim")
    expect_page_failure(html.replace("data-affiliate-gate=", "data-other=", 1), "yerleşim/kapı")
    expect_page_failure(
        html.replace("</main>", '<a href="https://www.amazon.com.tr/s?k=test">Kapısız mağaza</a></main>'),
        "kapısız mağaza",
    )
    expect_page_failure(html.replace(verifier.ROUTE, "/yanlis-rota/", 1), "canonical yol")
    expect_js_failure(javascript.replace(verifier.REQUIRED_REL, "noopener"), "javascript sözleşmesi")
    expect_js_failure(javascript + "\nlocalStorage.setItem('x','y');", "localStorage")

    try:
        verifier.validate_page(
            html,
            {
                "status": 404,
                "contentType": "text/html",
                "effectiveUrl": f"https://alo186.com{verifier.ROUTE}",
            },
            "https://alo186.com",
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
        "hostingAwareScheduledWorkflow": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
