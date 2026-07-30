from __future__ import annotations

import json
import shutil
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import build  # noqa: E402
from prepare_github_pages import prepare  # noqa: E402


class JsonLdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.active = False
        self.current: list[str] = []
        self.payloads: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): value for key, value in attrs}
        if tag.casefold() == "script" and (values.get("type") or "").casefold() == "application/ld+json":
            self.active = True
            self.current = []

    def handle_data(self, data: str) -> None:
        if self.active:
            self.current.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "script" and self.active:
            self.payloads.append(json.loads("".join(self.current)))
            self.current = []
            self.active = False


def public_url(base_path: str, route: str) -> str:
    prefix = "/" + base_path.strip("/") if base_path.strip("/") else ""
    return (prefix + "/" + route.lstrip("/")).replace("//", "/")


def prepare_variant(canonical: Path, target: Path, base_path: str) -> dict:
    shutil.copytree(canonical, target)
    return prepare(target, base_path, "ozaneryavuz/chatgpt", "article-discovery-test")


def test_source_contract() -> None:
    overlay = json.loads(
        (ROOT / "alo186/deployment/routing-overlays/130-user-centered-article-hub.json").read_text(
            encoding="utf-8"
        )
    )
    assert overlay["version"] >= 130
    assert overlay["routes"] == [
        {
            "source": "alo186/article-hub/index.html",
            "canonicalPath": "/haberler/",
            "type": "collection",
        }
    ]
    hub = (ROOT / "alo186/article-hub/index.html").read_text(encoding="utf-8")
    assert "ALO186_ARTICLE_CARDS" in hub
    assert 'id="article-search"' in hub
    assert 'data-category="outage-rights"' in hub
    assert 'data-category="maintenance"' in hub
    assert "amazon.com.tr" not in hub.casefold()
    script = (ROOT / "alo186/article-hub/app.js").read_text(encoding="utf-8")
    assert "localStorage" not in script
    assert "fetch(" not in script
    assert "data-result-count" in script


def test_every_article_is_discoverable_in_custom_and_project_modes() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        canonical = root / "canonical"
        core_release = build(ROOT, canonical, "article-discovery-test")
        articles = [route["canonicalPath"] for route in core_release["routes"] if route["type"] == "article"]
        assert len(articles) >= 50
        assert "/haberler/" in {route["canonicalPath"] for route in core_release["routes"]}

        for name, base_path in (("custom", ""), ("project", "/chatgpt")):
            site = root / name
            pages = prepare_variant(canonical, site, base_path)
            discovery = pages["articleDiscoveryV1"]
            assert discovery["articleCount"] == len(articles)
            assert discovery["articleBacklinksInjected"] == len(articles)
            assert discovery["portalCardInjected"] is True
            assert discovery["rawQueryStored"] is False
            assert discovery["commercialRankingUsed"] is False
            assert sum(discovery["categoryCounts"].values()) == len(articles)
            assert all(value > 0 for value in discovery["categoryCounts"].values())

            hub = (site / "haberler/index.html").read_text(encoding="utf-8")
            assert hub.count("data-article-card") == len(articles)
            assert f"<strong data-article-count>{len(articles)}</strong>" in hub
            assert "ticari sıralama yok" in hub.casefold()
            assert "amazon.com.tr" not in hub.casefold()
            for route in articles:
                assert f'href="{public_url(base_path, route)}"' in hub
                article = (site / route.strip("/") / "index.html").read_text(encoding="utf-8")
                assert 'data-alo186-article-hub-link="true"' in article
                assert 'data-alo186-article-discovery-style="true"' in article
                assert f'href="{public_url(base_path, "/haberler/")}"' in article
                assert f'href="{public_url(base_path, "/arama/")}"' in article
                assert public_url(base_path, "/assets/alo186-article-discovery.css") in article

            collector = JsonLdCollector()
            collector.feed(hub)
            graph = next(payload["@graph"] for payload in collector.payloads if "@graph" in payload)
            collection = next(item for item in graph if item.get("@type") == "CollectionPage")
            assert collection["mainEntity"]["numberOfItems"] == len(articles)
            assert len(collection["mainEntity"]["itemListElement"]) == len(articles)

            portal = (site / "elektrik-portali/index.html").read_text(encoding="utf-8")
            assert portal.count('data-alo186-article-hub-card="true"') == 1
            assert f'href="{public_url(base_path, "/haberler/")}"' in portal
            assert portal.index('data-alo186-article-hub-card="true"') > portal.index('data-alo186-resource-library="true"')
            assert portal.count('data-alo186-primary-task=') == 4

            manifest = json.loads((site / "manifest.webmanifest").read_text(encoding="utf-8"))
            shortcut_urls = {item.get("url") for item in manifest.get("shortcuts", [])}
            assert public_url(base_path, "/haberler/") in shortcut_urls
            assert (site / "assets/alo186-article-discovery.css").is_file()

            audit = pages["sitewideUserExperienceAudit"]
            assert audit["pageCount"] >= int(pages["routeCount"])
            assert audit["brokenInternalLinks"] == 0


def main() -> None:
    test_source_contract()
    test_every_article_is_discoverable_in_custom_and_project_modes()
    print(json.dumps({"ok": True, "articleHub": True, "basePathModes": 2}, ensure_ascii=False))


if __name__ == "__main__":
    main()
