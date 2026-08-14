from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186/deployment"))

from inject_live_quality_hardening import (  # noqa: E402
    CANONICAL_ORIGIN,
    CSS_FILE,
    CSS_MARKER,
)
from inject_live_quality_hardening_v2 import (  # noqa: E402
    normalize_text,
    run,
    wrong_damage_deadline_contexts,
)


def seed(site: Path, base_path: str) -> None:
    route = site / "elektrik-portali"
    route.mkdir(parents=True)
    css_href = f"{base_path}/{CSS_FILE}" if base_path else f"/{CSS_FILE}"
    portal_html = f'''<!doctype html><html lang="tr"><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="canonical" href="https://www.alo186.com/elektrik-portali">
<title>Test portalı</title></head><body><main>
<h1>Elektrik portalı</h1>
<p>Elektrik kesintisi cihazımı bozduysa zararın ortaya çıktığı tarihten itibaren 30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun.</p>
<p>Başvuru haklı bulunmazsa dağıtım şirketi teknik raporu 10 iş günü içinde bildirir.</p>
<a href="{base_path}/elektrik-portali" aria-label="Portal">Portal</a>
</main></body></html>'''
    root_html = f'''<!doctype html><html lang="tr"><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="canonical" href="https://www.alo186.com/">
<title>Test ana sayfa</title></head><body><main>
<h1>ALO186</h1>
<section class="grid" aria-label="ALO186 hızlı başlangıç">
<a data-alo186-primary-start="true" href="{base_path}/elektrik-durum-merkezi/">Elektrik Durum Merkezi</a>
<a href="{base_path}/karar-motoru/">112, 186 veya elektrikçi</a>
<a href="{base_path}/edas-bul/">EDAŞ bul</a>
<a href="{base_path}/kesintiye-hazirlik-atolyesi/">Kesintiye hazırlan</a>
<a href="{base_path}/elektrik-portali/">Elektrik Portalı</a>
<a href="{base_path}/arama/">Teknik arama</a>
</section>
</main></body></html>'''
    (route / "index.html").write_text(portal_html, encoding="utf-8")
    (site / "index.html").write_text(root_html, encoding="utf-8")
    (site / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://alo186.com/sitemap.xml\n", encoding="utf-8")
    (site / "sitemap.xml").write_text('<?xml version="1.0"?><urlset><url><loc>https://alo186.com/elektrik-portali</loc></url></urlset>', encoding="utf-8")
    (site / ".htaccess").write_text("RewriteCond %{HTTP_HOST} !^www\\.alo186\\.com$ [NC]\nRewriteRule ^ https://www.alo186.com%{REQUEST_URI} [R=301,L]\n", encoding="utf-8")
    release = {
        "canonicalHost": "https://www.alo186.com",
        "routes": [{"canonicalPath": "/elektrik-portali", "source": "alo186/index.html", "type": "collection"}],
    }
    (site / "alo186-release.json").write_text(json.dumps(release), encoding="utf-8")
    (site / "pages-release.json").write_text(json.dumps({"canonicalHost": "https://www.alo186.com", "basePath": base_path}), encoding="utf-8")
    assert css_href not in portal_html


def test_deadline_normalization_is_one_way() -> None:
    current = "Cihaz hasarı için zararın ortaya çıktığı tarihten itibaren 30 gün içinde dağıtım şirketine başvurun."
    stale = "Cihaz hasarı için zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde EDAŞ kaydı açın."
    response = "Cihaz hasarı başvurusu reddedilirse dağıtım şirketi teknik raporu 10 iş günü içinde bildirir."
    post_injector_variants = (
        "Cihaz Hasarı Takibi: 10 iş günlük süreç, kanıt ve resmî başvuru durumunu izleyin.",
        "ALO186 başvuru almaz. Ücretsiz paket, 10 iş günlük başvuru süresini ve dağıtım şirketine götürülecek kanıt kontrolünü düzenler.",
        "Cihaz hasarı belgesini gecikmeden hazırlayın. 10 iş günlük resmî başvuru süresini kontrol edin.",
        "Cihaz hasarı başvuru takibi — 10 iş günü · kanıt · resmî kanal",
        "Cihaz hasarı EDAŞ başvuru paketi: 10 iş günlük süreyi, kanıtı ve resmî takip adımlarını düzenleyin.",
    )

    assert normalize_text(current) == current
    normalized_stale = normalize_text(stale)
    assert "zararın ortaya çıktığı tarihten itibaren 30 gün içinde" in normalized_stale
    assert "10 iş günü içinde EDAŞ kaydı açın" not in normalized_stale
    assert normalize_text(response) == response
    assert wrong_damage_deadline_contexts(stale)
    assert not wrong_damage_deadline_contexts(response)

    for variant in post_injector_variants:
        normalized = normalize_text(variant)
        assert "10 iş gün" not in normalized, variant
        assert "30 gün" in normalized, variant
        assert not wrong_damage_deadline_contexts(normalized), normalized

    masked_by_next_paragraph = (
        "<p>Cihaz hasarı için 10 iş günü içinde dağıtım şirketine başvurun.</p>"
        "<p>Başvuru reddedilirse şirket teknik raporu bildirir.</p>"
    )
    assert wrong_damage_deadline_contexts(masked_by_next_paragraph)

    masked_by_next_sentence = (
        "Cihaz hasarı için 10 iş günü içinde dağıtım şirketine başvurun. "
        "Başvuru reddedilirse şirket teknik raporu bildirir."
    )
    assert wrong_damage_deadline_contexts(masked_by_next_sentence)


def test_custom_domain() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site, "")
        result = run(site, "")
        assert result["canonicalOrigin"] == CANONICAL_ORIGIN
        assert result["deviceDamageDeadline"] == "30 gün"
        assert result["deviceDamageDeadlineContexts"] > 0
        assert result["minimumTouchTargetCssPx"] == 44
        assert result["officialInstitutionClaimed"] is False
        assert result["personalDataCollectionAdded"] is False
        assert result["finalUserEntryPoints"]["ok"] is True
        assert result["finalUserEntryPoints"]["primaryCardCount"] == 5
        assert result["finalUserEntryPoints"]["secondaryCardCount"] == 1
        portal = (site / "elektrik-portali/index.html").read_text(encoding="utf-8")
        root = (site / "index.html").read_text(encoding="utf-8")
        assert "https://www.alo186.com" not in portal
        assert '<link rel="canonical" href="https://alo186.com/elektrik-portali">' in portal
        assert "zararın ortaya çıktığı tarihten itibaren 30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun" in portal
        assert "teknik raporu 10 iş günü içinde bildirir" in portal
        assert "zararın ortaya çıktığı tarihten itibaren 10 iş günü" not in portal
        assert CSS_MARKER in portal and f'href="/{CSS_FILE}"' in portal
        assert 'data-alo186-secondary-tools="true"' in root
        assert "Sitemap: https://alo186.com/sitemap.xml" in (site / "robots.txt").read_text(encoding="utf-8")
        assert "!^alo186\\.com$" in (site / ".htaccess").read_text(encoding="utf-8")
        for name in ("alo186-release.json", "pages-release.json"):
            release = json.loads((site / name).read_text(encoding="utf-8"))
            assert release["canonicalHost"] == CANONICAL_ORIGIN
            assert release["liveTechnicalQuality"]["minimumTouchTargetCssPx"] == 44
            assert release["liveTechnicalQuality"]["deviceDamageDeadline"] == "30 gün"
            assert release["finalUserEntryPointAudit"]["primaryCardCount"] == 5
        css = (site / CSS_FILE).read_text(encoding="utf-8")
        for token in [
            "min-height:44px",
            ".amazon-intent-card small",
            ".amazon-intent-card a[href]",
            "[class*=\"answerList\"]>article>span",
            "button[data-analytics-choice]",
            "font-size:max(.875rem,14px)",
            "input,select,textarea,button{font-size:16px}",
            "focus-visible",
            "overflow-wrap:anywhere",
        ]:
            assert token in css
        assert "body{overflow-x:clip}" not in css


def test_project_base_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site, "/chatgpt")
        result = run(site, "/chatgpt")
        assert result["basePath"] == "/chatgpt"
        assert result["deviceDamageDeadline"] == "30 gün"
        assert result["finalUserEntryPoints"]["primaryCardCount"] == 5
        portal = (site / "elektrik-portali/index.html").read_text(encoding="utf-8")
        assert f'href="/chatgpt/{CSS_FILE}"' in portal
        release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
        assert release["liveTechnicalQuality"]["stylesheet"] == f"/chatgpt/{CSS_FILE}"
        assert release["liveTechnicalQuality"]["deviceDamageDeadline"] == "30 gün"
        assert release["finalUserEntryPointAudit"]["scope"] == ["/chatgpt/", "/chatgpt/elektrik-portali/"]


if __name__ == "__main__":
    test_deadline_normalization_is_one_way()
    test_custom_domain()
    test_project_base_path()
    print(json.dumps({
        "ok": True,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "deviceDamageDeadline": "30 gün",
        "obsoleteApplicationDeadlineRejected": True,
        "postInjectorDeadlineVariantsNormalized": 5,
        "crossStatementMaskingBlocked": True,
        "validResponseDeadlinePreserved": True,
        "minimumTouchTargetCssPx": 44,
        "knownContrastSelectors": 4,
        "finalPrimaryCardCount": 5,
        "secondaryToolsProgressive": True,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }, ensure_ascii=False, indent=2))
