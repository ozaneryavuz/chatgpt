from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "alo186/en/index.html"
APEX = "https://alo186.com"
LEGACY = "https://www.alo186.com"


class HeadMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self.meta: list[dict[str, str]] = []
        self.json_ld: list[str] = []
        self._json_ld = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "link":
            self.links.append(values)
        elif tag == "meta":
            self.meta.append(values)
        elif tag == "script" and values.get("type") == "application/ld+json":
            self._json_ld = True
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._json_ld:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_ld:
            self.json_ld.append("".join(self._buffer))
            self._json_ld = False
            self._buffer = []


def walk(value: object):
    if isinstance(value, dict):
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)
    elif isinstance(value, str):
        yield value


def main() -> None:
    html = PAGE.read_text(encoding="utf-8")
    parser = HeadMetadataParser()
    parser.feed(html)

    canonical = [item.get("href") for item in parser.links if item.get("rel") == "canonical"]
    assert canonical == [f"{APEX}/en/"]

    alternates = {
        item.get("hreflang"): item.get("href")
        for item in parser.links
        if item.get("rel") == "alternate" and item.get("hreflang")
    }
    assert alternates == {
        "tr-TR": f"{APEX}/elektrik-portali",
        "en": f"{APEX}/en/",
        "x-default": f"{APEX}/elektrik-portali",
    }

    og_urls = [item.get("content") for item in parser.meta if item.get("property") == "og:url"]
    assert og_urls == [f"{APEX}/en/"]

    assert parser.json_ld, "English landing page must publish JSON-LD"
    structured = [json.loads(block) for block in parser.json_ld]
    urls = [text for document in structured for text in walk(document) if text.startswith("https://")]
    assert urls
    assert all(not value.startswith(LEGACY) for value in urls)
    assert f"{APEX}/#organization" in urls
    assert f"{APEX}/#website" in urls
    assert f"{APEX}/en/#webpage" in urls

    assert LEGACY not in html
    print(json.dumps({"ok": True, "canonicalHost": APEX, "hreflang": sorted(alternates)}))


if __name__ == "__main__":
    main()
