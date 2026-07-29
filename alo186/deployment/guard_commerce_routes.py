from __future__ import annotations

import argparse
import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit

AFFILIATE_HOSTS = {
    "amazon.com.tr",
    "www.amazon.com.tr",
    "amzn.to",
    "www.amzn.to",
}
REQUIRED_REL = {"sponsored", "nofollow", "noopener"}
DISCLOSURE_PATTERN = re.compile(r"satış\s+ortaklığı|affiliate|nitelikli\s+satın\s+alımlardan\s+komisyon", re.I)
QUALIFIED_GATE_MARKER = 'data-alo186-affiliate-gate="qualified"'
HIGH_RISK_PATTERN = re.compile(
    r"\b(?:rccb|rcbo|mcb|kaçak\s+akım\s+rölesi|parafudr|\bspd\b|gerilim\s+koruma\s+rölesi|"
    r"kontaktör|sigorta|dağıtım\s+panosu|wallbox|jeneratör|transfer\s+şalteri|inverter\s+batarya|"
    r"topraklama|harmonik\s+filtre|ges\s+inverter)\b",
    re.I,
)
ANCHOR_PATTERN = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>", re.I | re.S)
ATTR_PATTERN = re.compile(r"(?P<name>[a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)", re.S)


def attributes(raw: str) -> dict[str, str]:
    return {match.group("name").casefold(): unescape(match.group("value")) for match in ATTR_PATTERN.finditer(raw)}


def is_affiliate_url(value: str) -> bool:
    parsed = urlsplit(value.strip())
    return parsed.scheme in {"http", "https"} and parsed.hostname in AFFILIATE_HOSTS


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def scan_html(path: Path, site: Path) -> list[str]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    relative = path.relative_to(site).as_posix()
    errors: list[str] = []
    has_disclosure = bool(DISCLOSURE_PATTERN.search(text_only(html)))
    has_qualified_gate = QUALIFIED_GATE_MARKER in html

    for match in ANCHOR_PATTERN.finditer(html):
        attrs = attributes(match.group("attrs"))
        href = attrs.get("href", "")
        if not is_affiliate_url(href):
            continue

        rel = {token.casefold() for token in attrs.get("rel", "").split() if token}
        missing_rel = REQUIRED_REL - rel
        if missing_rel:
            errors.append(f"{relative}: affiliate bağlantısında eksik rel tokenları: {', '.join(sorted(missing_rel))}")
        if not has_disclosure:
            errors.append(f"{relative}: affiliate bağlantısı var fakat görünür satış ortaklığı açıklaması yok")
        if not has_qualified_gate:
            errors.append(f"{relative}: statik mağaza bağlantısı nitelikli affiliate kapısı işareti olmadan yayımlanamaz")

        start = max(0, match.start() - 900)
        end = min(len(html), match.end() + 900)
        context = text_only(html[start:end])
        risky = HIGH_RISK_PATTERN.search(context)
        if risky:
            errors.append(
                f"{relative}: yüksek riskli/sabit tesisat bağlamında doğrudan mağaza bağlantısı yasak: {risky.group(0)}"
            )

    return errors


def validate_legacy_alias(site: Path) -> list[str]:
    alias = site / "amazon-elektrik-urunleri" / "index.html"
    canonical = site / "akilli-urun-secimi" / "index.html"
    errors: list[str] = []
    if not canonical.is_file():
        errors.append("akilli-urun-secimi/index.html: güvenli canonical ürün merkezi artifactta eksik")
    if not alias.is_file():
        errors.append("amazon-elektrik-urunleri/index.html: legacy rota için fail-closed alias sayfası eksik")
        return errors

    text = alias.read_text(encoding="utf-8", errors="ignore")
    if 'data-alo186-content-alias="true"' not in text:
        errors.append("amazon-elektrik-urunleri/index.html: legacy sayfa canonical alias olarak işaretlenmemiş")
    if 'rel="canonical" href="https://www.alo186.com/akilli-urun-secimi"' not in text:
        errors.append("amazon-elektrik-urunleri/index.html: canonical hedef güvenli ürün merkezi değil")
    if re.search(r"https?://(?:www\.)?(?:amazon\.com\.tr|amzn\.to)", text, re.I):
        errors.append("amazon-elektrik-urunleri/index.html: legacy alias doğrudan mağaza bağlantısı içeriyor")
    return errors


def validate_site(site: Path) -> dict:
    site = site.resolve()
    if not site.is_dir():
        raise FileNotFoundError(f"Site artifactı bulunamadı: {site}")

    errors: list[str] = []
    for path in sorted(site.rglob("*.html")):
        errors.extend(scan_html(path, site))
    errors.extend(validate_legacy_alias(site))

    result = {
        "ok": not errors,
        "htmlFileCount": len(list(site.rglob("*.html"))),
        "legacyAlias": "/amazon-elektrik-urunleri -> /akilli-urun-secimi",
        "staticAffiliatePolicy": "qualified-gate + visible-disclosure + sponsored-nofollow-noopener; high-risk direct links forbidden",
        "errorCount": len(errors),
        "errors": errors,
    }
    if errors:
        raise AssertionError(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 statik yayında ticari güven kapılarını fail-closed doğrular.")
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate_site(args.site), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
