from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from normalize_legacy_project_links_v214 import normalize_html, rewrite_legacy_url, run  # noqa: E402


def fixture() -> str:
    return '''<!doctype html><html lang="tr"><body>
<a href="/chatgpt">Ana sayfa</a>
<a href='/chatgpt/elektrik-portali/?from=test#route'>Portal</a>
<img src="/chatgpt/assets/hero.webp" alt="Elektrik portalı" width="640" height="360">
<form action="/chatgpt/arama/"><button>Ara</button></form>
<video poster="/chatgpt/assets/poster.webp"></video>
<div data-src="/chatgpt/data.json" data-href="/chatgpt/karar-motoru/"></div>
<img srcset="/chatgpt/img/a.webp 1x, /chatgpt/img/a@2x.webp 2x" alt="Örnek" width="100" height="100">
<a href="https://github.com/ozaneryavuz/chatgpt">GitHub deposu</a>
<script>const literal='/chatgpt/js-literal-preserved';</script>
</body></html>'''


def create_targets(site: Path) -> None:
    for relative in [
        "elektrik-portali/index.html",
        "assets/hero.webp",
        "arama/index.html",
        "assets/poster.webp",
        "data.json",
        "karar-motoru/index.html",
        "img/a.webp",
        "img/a@2x.webp",
    ]:
        path = site / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok", encoding="utf-8")


def test_url_rewrite_contract() -> None:
    assert rewrite_legacy_url("/chatgpt") == "/"
    assert rewrite_legacy_url("/chatgpt/") == "/"
    assert rewrite_legacy_url("/chatgpt/foo") == "/foo"
    assert rewrite_legacy_url("/chatgpt?x=1") == "/?x=1"
    assert rewrite_legacy_url("/chatgpt#x") == "/#x"
    assert rewrite_legacy_url("https://example.com/chatgpt") == "https://example.com/chatgpt"
    assert rewrite_legacy_url("/chatgpt-old") == "/chatgpt-old"


def test_normalize_html_only_url_attributes() -> None:
    updated, count = normalize_html(fixture())
    assert count == 9
    assert 'href="/"' in updated
    assert "href='/elektrik-portali/?from=test#route'" in updated
    assert 'src="/assets/hero.webp"' in updated
    assert 'action="/arama/"' in updated
    assert 'poster="/assets/poster.webp"' in updated
    assert 'data-src="/data.json"' in updated
    assert 'data-href="/karar-motoru/"' in updated
    assert 'srcset="/img/a.webp 1x, /img/a@2x.webp 2x"' in updated
    assert "const literal='/chatgpt/js-literal-preserved'" in updated
    assert 'href="https://github.com/ozaneryavuz/chatgpt"' in updated


def test_custom_domain_run() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        (site / "index.html").write_text(fixture(), encoding="utf-8")
        create_targets(site)
        result = run(site, "")
        assert result["ok"] is True
        assert result["mode"] == "custom-domain-normalized"
        assert result["changedFiles"] == 1
        assert result["rewrittenReferences"] == 9
        assert result["residualLegacyReferences"] == 0
        updated = (site / "index.html").read_text(encoding="utf-8")
        assert "/chatgpt/elektrik-portali" not in updated
        assert "js-literal-preserved" in updated
        second = run(site, "")
        assert second["changedFiles"] == 0
        assert second["rewrittenReferences"] == 0


def test_project_path_is_preserved() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        path = site / "index.html"
        path.write_text(fixture(), encoding="utf-8")
        result = run(site, "/chatgpt")
        assert result["ok"] is True
        assert result["mode"] == "project-path-preserved"
        assert result["changedFiles"] == 0
        assert result["rewrittenReferences"] == 0
        assert path.read_text(encoding="utf-8") == fixture()


if __name__ == "__main__":
    test_url_rewrite_contract()
    test_normalize_html_only_url_attributes()
    test_custom_domain_run()
    test_project_path_is_preserved()
    print(json.dumps({
        "ok": True,
        "version": 214,
        "customDomainLegacyLinksNormalized": True,
        "projectPathPreserved": True,
        "scriptLiteralsUntouched": True,
        "externalLinksUntouched": True,
    }, ensure_ascii=False, indent=2))
