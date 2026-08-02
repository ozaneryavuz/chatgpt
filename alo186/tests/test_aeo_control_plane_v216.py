from __future__ import annotations

import inspect
import json
import sys
import tempfile
from pathlib import Path

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

import aeo_control_plane_v216 as aeo


def page(canonical: str, body: str) -> str:
    return f'''<!doctype html><html lang="tr"><head><title>ALO186 test sayfası ve güvenli doğrudan cevap</title><meta name="description" content="Bu test açıklaması AEO kontrol düzleminin meta description ve canonical sözleşmesini güvenli biçimde doğrular."><link rel="canonical" href="{canonical}"><script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","@id":"{canonical}#webpage"}}</script></head><body><main><h1>Elektrik kesintisinde ne yapılır?</h1><p>{body}</p></main></body></html>'''


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
        assert first["injectedPageCount"] == 2 and first["volatileCopyReplacements"] == 2, first
        assert second["injectedPageCount"] == 2 and second["newlyInjectedPageCount"] == 0, second

        html = home.read_text(encoding="utf-8")
        assert html.count(aeo.MARKER) == 1 and html.count(aeo.SCHEMA_MARKER) == 1
        assert "/preview/uzman/ozan-eryavuz" in html
        assert "/preview/assets/aeo-authority-v216.css" in html
        assert "50+ elektrik ürünü" not in html
        assert "25 rehberin tamamını gör" not in html

        proof = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))["aeoAuthority"]
        assert proof["version"] == 216
        assert proof["injectedPageCount"] == 2
        assert proof["volatileCopyReplacements"] == 2
        assert proof["personalContactPublished"] is False
        assert aeo.ASSET in (site / "checksums.sha256").read_text(encoding="utf-8")

    root = Path(__file__).resolve().parents[2]
    intent_payload = json.loads((root / "alo186/aeo/intent-registry-v216.json").read_text(encoding="utf-8"))
    benchmark_payload = json.loads((root / "alo186/aeo/ai-citation-benchmark-v216.json").read_text(encoding="utf-8"))
    intents = intent_payload["intents"]
    queries = benchmark_payload["queries"]
    assert len(intents) >= 15
    assert len(queries) >= 15

    intent_paths = {item["canonicalPath"] for item in intents}
    benchmark_paths = {item["expectedPath"] for item in queries}
    assert "/haberler/planli-elektrik-kesintisi-ne-kadar-once-bildirilir" in intent_paths
    assert "/hesaplama/yedek-guc-cozum-secici/" in benchmark_paths
    assert "/sektor-rehberi/planli-elektrik-kesintisi-sorgulama" not in intent_paths | benchmark_paths
    assert "/haberler/ups-mi-tasinabilir-guc-istasyonu-mu" not in benchmark_paths
    assert "require_release_proof" in inspect.signature(aeo.validate).parameters

    print(json.dumps({"ok": True, "version": 216}))


if __name__ == "__main__":
    main()
