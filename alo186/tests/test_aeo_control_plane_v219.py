from __future__ import annotations

import inspect
import json
import re
import sys
import tempfile
from pathlib import Path

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

import aeo_control_plane_v219 as aeo


def page(canonical: str, body: str) -> str:
    return f'''<!doctype html><html lang="tr"><head><title>ALO186 test sayfası ve güvenli doğrudan cevap</title><meta name="description" content="Bu test açıklaması kurumsal AEO kontrol düzleminin meta description ve canonical sözleşmesini doğrular."><link rel="canonical" href="{canonical}"><script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","@id":"{canonical}#webpage"}}</script></head><body><main><h1>Elektrik kesintisinde ne yapılır?</h1><p>{body}</p></main></body></html>'''


def main() -> None:
    with tempfile.TemporaryDirectory() as raw:
        site = Path(raw)
        (site / "pages-release.json").write_text("{}\n", encoding="utf-8")
        (site / "checksums.sha256").write_text("x\n", encoding="utf-8")

        home = site / "index.html"
        home.write_text(
            page(
                "https://alo186.com/",
                "Önce can güvenliği kontrol edilir; ardından 112, 186 veya yetkili elektrikçi arasında doğru kanal seçilir. 50+ elektrik ürünü için Amazon seçim kartları ve 25 rehberin tamamını gör.",
            ),
            encoding="utf-8",
        )
        article = site / "haberler/ornek/index.html"
        article.parent.mkdir(parents=True)
        article.write_text(
            page(
                "https://alo186.com/haberler/ornek",
                "Elektrik riski uzaktan kesin teşhis edilmez. Görünür tehlike varsa yaklaşmadan güvenli alana geçilir ve resmî yardım kanalı kullanılır.",
            ),
            encoding="utf-8",
        )

        first = aeo.inject(site, "/preview")
        second = aeo.inject(site, "/preview")
        assert first["injectedPageCount"] == 2, first
        assert first["volatileCopyReplacements"] == 2, first
        assert first["personalProfilePublished"] is False, first
        assert second["injectedPageCount"] == 2, second
        assert second["newlyInjectedPageCount"] == 0, second

        html = home.read_text(encoding="utf-8")
        assert html.count(aeo.MARKER) == 1
        assert html.count(aeo.SCHEMA_MARKER) == 1
        assert "/preview/yayin-politikasi" in html
        assert "/preview/assets/aeo-institutional-v219.css" in html
        assert "50+ elektrik ürünü" not in html
        assert "25 rehberin tamamını gör" not in html
        assert '"@type":"Organization"' in html
        assert '"publishingPrinciples":"https://alo186.com/yayin-politikasi"' in html
        assert not aeo.PERSONAL_SCHEMA_RE.search(html)

        proof = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))[
            "aeoInstitutional"
        ]
        assert proof["version"] == 219
        assert proof["editorType"] == "Organization"
        assert proof["personalProfilePublished"] is False
        assert proof["personalContactPublished"] is False
        assert proof["injectedPageCount"] == 2
        assert proof["volatileCopyReplacements"] == 2
        assert aeo.ASSET in (site / "checksums.sha256").read_text(encoding="utf-8")

    root = Path(__file__).resolve().parents[2]
    intent_path = root / "alo186/aeo/intent-registry-v219.json"
    benchmark_path = root / "alo186/aeo/ai-citation-benchmark-v219.json"
    policy_path = root / "alo186/yayin-politikasi/index.html"
    control_path = root / "alo186/deployment/aeo_control_plane_v219.py"
    workflow_path = root / ".github/workflows/alo186-aeo-control-plane-v219.yml"

    intents = json.loads(intent_path.read_text(encoding="utf-8"))["intents"]
    queries = json.loads(benchmark_path.read_text(encoding="utf-8"))["queries"]
    assert len(intents) >= 15
    assert len(queries) >= 15
    assert any(item["canonicalPath"] == "/yayin-politikasi" for item in intents)
    assert any(item["expectedPath"] == "/yayin-politikasi" for item in queries)
    assert "require_release_proof" in inspect.signature(aeo.validate).parameters

    forbidden = re.compile(r'(?:ProfilePage|/uzman/|["\']@type["\']\s*:\s*["\']Person["\'])', re.I)
    for path in (intent_path, benchmark_path, policy_path, control_path, workflow_path):
        content = path.read_text(encoding="utf-8")
        assert not forbidden.search(content), path

    policy_html = policy_path.read_text(encoding="utf-8")
    assert "kişisel isim" in policy_html
    assert "Kurumsal yayın denetimi" in policy_html
    assert '"@type":"Organization"' in policy_html

    print(json.dumps({"ok": True, "version": 219, "personalProfilePublished": False}))


if __name__ == "__main__":
    main()
