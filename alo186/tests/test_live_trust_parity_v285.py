#!/usr/bin/env python3
"""ALO186 source/live trust contract.

The pull-request mode validates repository source without network access.
The live mode verifies that production has not drifted back to volatile
catalog counts or ungated merchant links.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE_HUB = ROOT / "amazon-elektrik-urunleri" / "index.html"
SOURCE_ENTRY = ROOT / "amazon-elektrik-urunleri" / "guvenli-baslangic" / "index.html"


@dataclass
class PageFacts:
    canonicals: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    text: list[str] = field(default_factory=list)


class FactsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.facts = PageFacts()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag.lower() == "link" and values.get("rel", "").lower() == "canonical":
            self.facts.canonicals.append(values.get("href", ""))
        if tag.lower() == "a" and values.get("href"):
            self.facts.links.append(values["href"])

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.facts.text.append(value)


def parse_html(html: str) -> PageFacts:
    parser = FactsParser()
    parser.feed(html)
    return parser.facts


def fetch(url: str, timeout: int = 20) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "ALO186-Trust-Parity/285 (+https://alo186.com/yayin-ilkeleri)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed trusted URLs
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def merchant_links(facts: PageFacts) -> list[str]:
    return [
        href
        for href in facts.links
        if re.search(r"(?:amazon\.com\.tr|amzn\.to)", href, flags=re.IGNORECASE)
    ]


def assert_contains(text: str, needles: tuple[str, ...], label: str, errors: list[str]) -> None:
    lowered = text.casefold()
    for needle in needles:
        if needle.casefold() not in lowered:
            errors.append(f"{label}: required trust marker missing: {needle!r}")


def check_source(errors: list[str]) -> None:
    for path in (SOURCE_HUB, SOURCE_ENTRY):
        if not path.exists():
            errors.append(f"source missing: {path.relative_to(ROOT)}")
            continue
        html = path.read_text(encoding="utf-8")
        facts = parse_html(html)
        if merchant_links(facts):
            errors.append(f"{path.relative_to(ROOT)}: static merchant href is not allowed")
        if re.search(r'"@type"\s*:\s*"(?:Offer|AggregateRating|Review)"', html):
            errors.append(f"{path.relative_to(ROOT)}: unsupported commercial schema found")

    entry = SOURCE_ENTRY.read_text(encoding="utf-8") if SOURCE_ENTRY.exists() else ""
    assert_contains(
        entry,
        (
            "Bağımsızlık açıklaması",
            "satış ortaklığı bağlantısıdır",
            "Mevcut çözüm yeterli — yeni ürün almayın",
            "professional-only",
            "yanıtları sunucuya göndermez",
        ),
        "trust-first entry",
        errors,
    )
    if "localStorage" in entry or "sessionStorage" in entry:
        errors.append("trust-first entry: persistent browser storage is forbidden")


def check_live(base_url: str, errors: list[str]) -> None:
    urls = {
        "home": f"{base_url.rstrip('/')}/",
        "hub": f"{base_url.rstrip('/')}/amazon-elektrik-urunleri/",
        "entry": f"{base_url.rstrip('/')}/amazon-elektrik-urunleri/guvenli-baslangic/",
    }
    pages: dict[str, str] = {}
    for name, url in urls.items():
        try:
            pages[name] = fetch(url)
        except (HTTPError, URLError, TimeoutError) as exc:
            errors.append(f"live {name}: fetch failed for {url}: {exc}")

    if "home" in pages:
        facts = parse_html(pages["home"])
        if facts.canonicals != [f"{base_url.rstrip('/')}/"]:
            errors.append(f"live home: canonical drift: {facts.canonicals!r}")
        assert_contains(
            " ".join(facts.text),
            ("Bağımsız bilgilendirme platformudur", "EDAŞ veya kamu kurumu değildir"),
            "live home",
            errors,
        )

    if "hub" in pages:
        facts = parse_html(pages["hub"])
        direct = merchant_links(facts)
        if direct:
            errors.append(f"live hub: {len(direct)} ungated merchant link(s) found")
        visible = " ".join(facts.text)
        volatile_patterns = (
            r"\b\d+\s+rehberin tamamını gör\b",
            r"\b\d+\s+modeli doğrulanmış\b",
            r"\b\d+\s+ürün karşılaştırma seçeneği\b",
            r"\b\d+\+\s+elektrik ürünü\b",
        )
        for pattern in volatile_patterns:
            if re.search(pattern, visible, flags=re.IGNORECASE):
                errors.append(f"live hub: volatile catalog claim found: {pattern}")
        assert_contains(
            visible,
            (
                "satış ortaklığı",
                "mevcut sistem yeterliyse satın alma",
                "fiyat, stok",
            ),
            "live hub",
            errors,
        )

    if "entry" in pages:
        visible = " ".join(parse_html(pages["entry"]).text)
        assert_contains(
            visible,
            (
                "Elektrik ürünü aramadan önce doğru çıkışı bulun",
                "Mevcut çözüm yeterli — yeni ürün almayın",
                "EDAŞ veya kamu kurumu değildir",
            ),
            "live trust-first entry",
            errors,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-base", help="Also verify deployed HTML, e.g. https://alo186.com")
    args = parser.parse_args()

    errors: list[str] = []
    check_source(errors)
    if args.live_base:
        check_live(args.live_base, errors)

    if errors:
        print("ALO186 trust parity v285: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("ALO186 trust parity v285: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
