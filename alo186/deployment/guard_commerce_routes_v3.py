from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import guard_commerce_routes_v2 as v2
import aeo_control_plane_v216 as aeo_authority
import inject_affiliate_decision_funnel_v215 as affiliate_decision
import inject_portal_purchase_checkpoint_v213 as portal_checkpoint

# V2, bağlantının çevresindeki sabit 900 karakteri tarıyordu. Uzun hesaplayıcı
# sayfalarında başka bir bölümde geçen "topraklama" gibi güvenlik metinleri,
# düşük riskli tak-çalıştır ürün kartını yanlışlıkla yüksek riskli sayabiliyordu.
# V3 yalnız bağlantının gerçek DOM bağlamını (ürün/sonuç/öneri kartını) tarar.
CONTEXT_TAGS = {"article", "li", "td", "aside", "section", "div"}
CONTEXT_MARKER = re.compile(
    r"(?:product|urun|ürün|card|kart|result|sonuc|sonuç|recommend|öner|oner|"
    r"option|secenek|seçenek|choice|shop|magaza|mağaza|affiliate|commercial|"
    r"equipment|ekipman|kit|shortlist|cta)",
    re.I,
)
MAX_CONTEXT_CHARS = 5000


@dataclass
class Node:
    tag: str
    attrs: dict[str, str]
    parent: "Node | None" = None
    text_parts: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return v2.text_only(" ".join(self.text_parts))

    @property
    def marker(self) -> str:
        names = (
            "class",
            "id",
            "role",
            "data-product",
            "data-product-card",
            "data-result",
            "data-recommendation",
            "data-affiliate",
            "data-commercial-scope",
        )
        return " ".join(self.attrs.get(name, "") for name in names)


class ContextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {})
        self.stack: list[Node] = [self.root]
        self.anchors: list[Node] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(
            tag.casefold(),
            {name.casefold(): unescape(value or "") for name, value in attrs},
            self.stack[-1],
        )
        self.stack.append(node)
        if node.tag == "a":
            self.anchors.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(
            tag.casefold(),
            {name.casefold(): unescape(value or "") for name, value in attrs},
            self.stack[-1],
        )
        if node.tag == "a":
            self.anchors.append(node)

    def handle_endtag(self, tag: str) -> None:
        folded = tag.casefold()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == folded:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        for node in self.stack:
            node.text_parts.append(data)


def product_context(anchor: Node) -> str:
    """Return the nearest meaningful commercial DOM context for an anchor."""
    candidate = anchor.parent
    fallback = anchor.text
    while candidate and candidate.tag != "document":
        text = candidate.text
        if text and len(text) <= MAX_CONTEXT_CHARS:
            fallback = text
            semantic_tag = candidate.tag in {"article", "li", "td", "aside"}
            marked = bool(CONTEXT_MARKER.search(candidate.marker))
            compact_section = candidate.tag in {"section", "div"} and len(text) <= 1800
            if semantic_tag or marked or compact_section:
                return text
        candidate = candidate.parent
    return fallback


def scan_affiliate_anchors(path: Path, site: Path) -> list[str]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    relative = path.relative_to(site).as_posix()
    errors: list[str] = []
    visible = v2.text_only(html)
    has_disclosure = bool(v2.DISCLOSURE_PATTERN.search(visible))

    parser = ContextParser()
    parser.feed(html)
    parser.close()

    for anchor in parser.anchors:
        href = anchor.attrs.get("href", "")
        if not v2.is_affiliate_url(href):
            continue
        rel = {token.casefold() for token in anchor.attrs.get("rel", "").split() if token}
        missing = v2.REQUIRED_REL - rel
        if missing:
            errors.append(
                f"{relative}: affiliate bağlantısında eksik rel tokenları: {', '.join(sorted(missing))}"
            )
        if not has_disclosure:
            errors.append(f"{relative}: affiliate bağlantısı var fakat görünür satış ortaklığı açıklaması yok")
        context = product_context(anchor)
        risky = v2.HIGH_RISK_PATTERN.search(context)
        if risky:
            errors.append(
                f"{relative}: yüksek riskli/sabit tesisat ürün bağlamında doğrudan mağaza bağlantısı yasak: {risky.group(0)}"
            )
    return errors


# Ürün merkezindeki v210 yönlendiricisi kişisel veri istemeyen üç kapalı
# seçimden oluşur. V2'nin bütün <form> etiketlerini kişisel veri formu sayan
# eski kontrolü yalnız bu kesin sözleşme için daraltılır; serbest veya kişisel
# veri alanı eklenirse kapı yeniden kapanır.
_original_validate_commercial_pages = v2.validate_commercial_pages


def _trusted_closed_choice_router(site: Path) -> bool:
    path = v2.route_file(site, "/amazon-elektrik-urunleri")
    if not path.is_file():
        return False
    html = path.read_text(encoding="utf-8", errors="ignore")
    if 'data-alo186-affiliate-intent-v210="true"' not in html:
        return False
    forms = re.findall(r"<form\b(?P<attrs>[^>]*)>(?P<body>.*?)</form>", html, re.I | re.S)
    if len(forms) != 1:
        return False
    attrs, body = forms[0]
    if "data-affiliate-intent-form" not in attrs:
        return False
    if re.search(r"<(?:input|textarea)\b", body, re.I):
        return False
    if re.search(r"\b(?:email|tel|phone|address|surname|file|location|message)\b", body, re.I):
        return False
    names = re.findall(r"<select\b[^>]*\bname=[\"']([^\"']+)[\"']", body, re.I)
    return names == ["need", "duration", "status"]


def validate_commercial_pages(site: Path) -> tuple[list[str], dict]:
    errors, stats = _original_validate_commercial_pages(site)
    if _trusted_closed_choice_router(site):
        blocked = "/amazon-elektrik-urunleri: ticari içerik sayfası kişisel veri formu içermemeli"
        errors = [error for error in errors if error != blocked]
    return errors, stats


v2.validate_commercial_pages = validate_commercial_pages

# V2'nin ticari sayfa, hizmet, katalog, canonical ve rapor sözleşmeleri aynen
# korunur; yalnız yanlış pozitif üreten anchor bağlam çözümlemesi değiştirilir.
v2.scan_affiliate_anchors = scan_affiliate_anchors

_original_validate_site = v2.validate_site


def _checkpoint_base_path(site: Path) -> str:
    """Mevcut CLI sözleşmesini değiştirmeden Pages base path değerini bulur."""
    release_path = site / "pages-release.json"
    if not release_path.is_file():
        return ""
    try:
        payload = json.loads(release_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    for key in ("affiliateDecisionFunnel", "affiliateIntentRouter", "homeAffiliateShowcase", "affiliateMeasurement"):
        value = payload.get(key)
        if isinstance(value, dict) and isinstance(value.get("basePath"), str):
            return value["basePath"]
    value = payload.get("basePath")
    return value if isinstance(value, str) else ""


def validate_site(site: Path) -> dict:
    """Son artifacta karar hunisi, portal kontrolü ve AEO otoritesini ekler; ardından fail-closed tarar."""
    resolved = site.resolve()
    base_path = _checkpoint_base_path(resolved)
    decision_result = affiliate_decision.inject(resolved, base_path)
    checkpoint_result = portal_checkpoint.inject(resolved, base_path)
    authority_result = aeo_authority.inject(resolved, base_path)
    result = _original_validate_site(resolved)
    result["affiliateDecisionFunnel"] = decision_result
    result["portalPurchaseCheckpoint"] = checkpoint_result
    result["aeoAuthority"] = authority_result
    return result


v2.validate_site = validate_site
main = v2.main


if __name__ == "__main__":
    main()
