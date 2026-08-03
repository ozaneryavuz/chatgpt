from __future__ import annotations

import json
import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(os.environ.get("ALO186_SITE_ROOT", "alo186"))
PAGE_REL = Path("amazon-elektrik-urunleri/akim-korumali-priz-yuk-uygunluk-secimi/index.html")
CANONICAL = "https://alo186.com/amazon-elektrik-urunleri/akim-korumali-priz-yuk-uygunluk-secimi/"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.fragment_hrefs: list[str] = []
        self.amazon_links: list[dict[str, str]] = []
        self.json_blocks: list[str] = []
        self._json_depth = 0
        self._json_parts: list[str] = []
        self.visible_parts: list[str] = []
        self.table_count = 0
        self.article_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: (value or "") for key, value in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        href = data.get("href", "")
        if href.startswith("#"):
            self.fragment_hrefs.append(href[1:])
        if "amazon.com.tr" in href:
            self.amazon_links.append(data)
        if tag == "table":
            self.table_count += 1
        if tag == "article":
            self.article_count += 1
        if tag == "script" and data.get("type") == "application/ld+json":
            self._json_depth = 1
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_depth:
            self.json_blocks.append("".join(self._json_parts))
            self._json_depth = 0
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._json_depth:
            self._json_parts.append(data)
        else:
            self.visible_parts.append(data)


def _load_page() -> tuple[str, PageParser]:
    html = (ROOT / PAGE_REL).read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(html)
    return html, parser


def _graph_nodes(parser: PageParser) -> list[dict]:
    assert parser.json_blocks, "JSON-LD block missing"
    nodes: list[dict] = []
    for block in parser.json_blocks:
        payload = json.loads(block)
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            nodes.extend(payload["@graph"])
        elif isinstance(payload, dict):
            nodes.append(payload)
    return nodes


def _type_values(node: dict) -> set[str]:
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def _repo_target_for_url(url: str) -> Path:
    parsed = urlparse(url)
    assert parsed.scheme == "https" and parsed.netloc == "alo186.com", url
    path = parsed.path.strip("/")
    return ROOT / path / "index.html" if path else ROOT / "index.html"


def test_structured_data_contract_and_no_unverified_offer() -> None:
    html, parser = _load_page()
    nodes = _graph_nodes(parser)
    types = {value for node in nodes for value in _type_values(node)}
    required = {"CollectionPage", "Product", "Brand", "ItemList", "BreadcrumbList", "FAQPage"}
    assert required <= types
    assert "Recommendation" not in types
    assert "Offer" not in types
    assert '"offers"' not in html and '"price"' not in html and '"priceCurrency"' not in html
    products = [node for node in nodes if "Product" in _type_values(node)]
    assert len(products) == 3
    for product in products:
        assert product.get("brand")
        assert product.get("identifier")
        assert product.get("additionalProperty")
        assert product.get("about")
        assert product.get("isRelatedTo")
    item_list = next(node for node in nodes if "ItemList" in _type_values(node))
    assert item_list.get("numberOfItems") == 3
    assert len(item_list.get("itemListElement", [])) == 3


def test_deep_links_are_unique_and_resolve() -> None:
    _, parser = _load_page()
    assert len(parser.ids) == len(set(parser.ids)), "duplicate HTML id detected"
    required_ids = {
        "senaryo-ev-ofis-elektronigi-koruma",
        "karar-toplam-yuk-ve-topraklama",
        "karsilastirma-akim-korumali-prizler",
        "urun-akim-korumali-priz-tuncmatik-tsk6136",
        "urun-akim-korumali-priz-tuncmatik-tsk5015",
        "urun-akim-korumali-priz-cata-ct9186",
        "sss-koruma-ekipmani",
    }
    assert required_ids <= set(parser.ids)
    assert parser.fragment_hrefs
    assert set(parser.fragment_hrefs) <= set(parser.ids)


def test_static_html_progressive_enhancement_and_faq_links() -> None:
    html, parser = _load_page()
    visible = " ".join(" ".join(parser.visible_parts).split())
    assert parser.table_count >= 1
    assert parser.article_count == 3
    assert "JavaScript olmadan okunabilen ürün karşılaştırması" in visible
    assert "İlgili koruma ekipmanını inceleyin." in visible
    assert "/hesaplama/akim-korumali-priz-spd-koruma-zinciri/" in html
    assert "catalog-v249.js" in html and "app-v249.js" in html
    assert html.index("<table") < html.index("catalog-v249.js")
    assert html.index("<article") < html.index("catalog-v249.js")


def test_affiliate_rel_and_visible_disclosure() -> None:
    html, parser = _load_page()
    visible = " ".join(" ".join(parser.visible_parts).split())
    assert visible.count("Görünür satış ortaklığı açıklaması:") >= 3
    for link in parser.amazon_links:
        rel = set(link.get("rel", "").split())
        assert {"sponsored", "nofollow", "noopener"} <= rel
    for match in re.finditer(r"<a\b[^>]*data-affiliate-asin=", html):
        tag = html[match.start(): html.find(">", match.start()) + 1]
        rel_match = re.search(r'rel="([^"]+)"', tag)
        assert rel_match, tag
        assert {"sponsored", "nofollow", "noopener"} <= set(rel_match.group(1).split())


def test_llms_taxonomy_only_lists_live_canonical_routes() -> None:
    text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for heading in (
        "## Resmî Kanallar",
        "## Teknik Çözüm ve Ekipman Rehberleri",
        "### Ev/Ofis Kesinti Hazırlığı",
        "### Cihaz ve Pano Koruması",
        "### GES ve Yedek Enerji Sistemleri",
        "## Ticari Şeffaflık",
    ):
        assert heading in text
    urls = re.findall(r"\((https://alo186\.com[^)]+)\)", text)
    assert len(urls) >= 9
    assert len(urls) == len(set(urls))
    sitemap_files = sorted(ROOT.glob("sitemap*.xml"))
    sitemap_text = "\n".join(path.read_text(encoding="utf-8") for path in sitemap_files)
    for url in urls:
        assert "#" not in url and "?" not in url
        target = _repo_target_for_url(url)
        assert target.is_file() or url.rstrip("/") in sitemap_text, f"llms route missing: {url}"
    official = text.split("## Resmî Kanallar", 1)[1].split("## Teknik Çözüm", 1)[0]
    assert "amazon" not in official.lower() and "satış ortaklığı" not in official.lower()


def test_robots_ai_groups_and_private_path_denials() -> None:
    text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    assert "User-agent: *" in text and "Allow: /" in text
    for agent in ("GPTBot", "PerplexityBot", "ClaudeBot", "Bytespider", "Google-Extended"):
        assert f"User-agent: {agent}" in text
    for path in ("/.github/", "/admin/", "/artifacts/", "/deployment/", "/node_modules/", "/preview/", "/tests/", "/tmp/", "/_production_site/"):
        if f"Disallow: {path}" not in text:
            assert not (ROOT / path.strip("/")).exists(), f"public path is neither denied nor excluded: {path}"
    assert "Sitemap: https://alo186.com/sitemap.xml" in text


def test_canonical_and_sitemap_contract() -> None:
    html, _ = _load_page()
    assert f'<link rel="canonical" href="{CANONICAL}">' in html
    sitemap_files = sorted(ROOT.glob("sitemap*.xml"))
    assert sitemap_files, "no sitemap files found"
    sitemap = "\n".join(path.read_text(encoding="utf-8") for path in sitemap_files)
    assert CANONICAL.rstrip("/") in sitemap or CANONICAL in sitemap
