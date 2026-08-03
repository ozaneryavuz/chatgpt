from __future__ import annotations

import json
import re
import sys
import unicodedata
from html import unescape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from apply_content_consolidation import load_config  # noqa: E402
from build_static_site import load_effective_manifest  # noqa: E402

STOPWORDS = {
    "alo186", "nedir", "neden", "nasil", "nasıl", "olur", "olmali", "olmalı", "mi", "mı", "mu", "mü",
    "icin", "için", "ve", "ile", "bir", "ne", "edilir", "edilmeli", "farki", "farkı", "kontrol", "rehberi",
    "elektrik", "teknik", "cihazi", "cihazı", "sistemi", "sistem", "kullanilir", "kullanılır",
}
AFCI_ALIAS_INTENT = "pv-inverter-afci-dc-arc-alarm"


def html_text(html: str, tag: str) -> str:
    match = re.search(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    if not match:
        return ""
    return unescape(re.sub(r"<[^>]+>", " ", match.group(1)))


def meta_description(html: str) -> str:
    match = re.search(
        r'<meta\b(?=[^>]*\bname=["\']description["\'])(?=[^>]*\bcontent=["\']([^"\']*)["\'])[^>]*>',
        html,
        re.I,
    )
    return unescape(match.group(1)) if match else ""


def class_text(html: str, class_name: str) -> str:
    match = re.search(
        fr'<[^>]+\bclass=["\'][^"\']*\b{re.escape(class_name)}\b[^"\']*["\'][^>]*>(.*?)</[^>]+>',
        html,
        re.I | re.S,
    )
    if not match:
        return ""
    return unescape(re.sub(r"<[^>]+>", " ", match.group(1)))


def normalized_tokens(value: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    tokens = re.findall(r"[a-z0-9]+", normalized)
    return {token for token in tokens if len(token) > 1 and token not in STOPWORDS}


def similarity(left: set[str], right: set[str]) -> tuple[float, int]:
    if not left or not right:
        return 0.0, 0
    common = left & right
    return len(common) / len(left | right), len(common)


def article_signature(source: str) -> dict:
    path = REPO_ROOT / source
    html = path.read_text(encoding="utf-8")
    title = html_text(html, "title")
    h1 = html_text(html, "h1")
    summary = " ".join(
        value for value in (
            title,
            h1,
            meta_description(html),
            class_text(html, "lead"),
            class_text(html, "answer"),
        )
        if value
    )
    return {
        "source": source,
        "title": title,
        "h1": h1,
        "titleTokens": normalized_tokens(title),
        "h1Tokens": normalized_tokens(h1),
        "summaryTokens": normalized_tokens(summary),
    }


def pair_score(left: dict, right: dict) -> tuple[float, int, str]:
    title_score, title_common = similarity(left["titleTokens"], right["titleTokens"])
    h1_score, h1_common = similarity(left["h1Tokens"], right["h1Tokens"])
    if h1_score >= title_score:
        return h1_score, h1_common, "h1"
    return title_score, title_common, "title"


def declared_pair_matches(left: dict, right: dict) -> tuple[bool, str]:
    headline_score, headline_common, field = pair_score(left, right)
    if headline_score >= 0.50 and headline_common >= 3:
        return True, f"{field}={headline_score:.2f}, ortak={headline_common}"

    summary_score, summary_common = similarity(left["summaryTokens"], right["summaryTokens"])
    matches = summary_score >= 0.22 and summary_common >= 8
    return matches, (
        f"{field}={headline_score:.2f}, ortak={headline_common}; "
        f"özet={summary_score:.2f}, ortak={summary_common}"
    )


def assert_afci_alias_bridge(item: dict, alias_source: str, target_source: str) -> None:
    alias_html = (REPO_ROOT / alias_source).read_text(encoding="utf-8")
    target_html = (REPO_ROOT / target_source).read_text(encoding="utf-8")
    expected = f"https://alo186.com{item['canonicalPath']}"

    assert 'data-alo186-content-alias="true"' in alias_html
    assert re.search(r'<meta\s+name="robots"\s+content="noindex,follow"', alias_html, re.I)
    assert f'<link rel="canonical" href="{expected}">' in alias_html
    assert f'"mainEntityOfPage":"{expected}"' in alias_html
    assert f'href="{item["canonicalPath"]}"' in alias_html
    assert "https://www.alo186.com" not in alias_html
    assert f'<link rel="canonical" href="{expected}">' in target_html


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    config = load_config()
    route_by_path = {route["canonicalPath"]: route for route in manifest["routes"]}
    declared_pairs = {(item["aliasPath"], item["canonicalPath"]) for item in config["consolidations"]}
    alias_paths = {item["aliasPath"] for item in config["consolidations"]}
    afci_alias_checked = False

    for item in config["consolidations"]:
        alias_route = route_by_path.get(item["aliasPath"])
        target_route = route_by_path.get(item["canonicalPath"])
        assert alias_route, f"Birleştirilecek alias routing envanterinde yok: {item['aliasPath']}"
        assert target_route, f"Canonical hedef routing envanterinde yok: {item['canonicalPath']}"
        assert alias_route["type"] == "article" and target_route["type"] == "article"
        alias_signature = article_signature(alias_route["source"])
        target_signature = article_signature(target_route["source"])
        matches, evidence = declared_pair_matches(alias_signature, target_signature)
        assert matches, (
            f"İlan edilen içerik birleştirmesi aynı arama niyetini doğrulamıyor: "
            f"{item['aliasPath']} → {item['canonicalPath']} ({evidence})"
        )
        if item.get("intentKey") == AFCI_ALIAS_INTENT:
            assert_afci_alias_bridge(item, alias_route["source"], target_route["source"])
            afci_alias_checked = True

    assert afci_alias_checked, "AFCI/DC ark alias canonical regresyon kaydı bulunamadı"

    active_articles = [
        route for route in manifest["routes"]
        if route["type"] == "article" and route["canonicalPath"] not in alias_paths
    ]
    signatures = [(route, article_signature(route["source"])) for route in active_articles]
    collisions: list[str] = []
    for index, (left_route, left) in enumerate(signatures):
        for right_route, right in signatures[index + 1 :]:
            score, common, field = pair_score(left, right)
            if score >= 0.74 and common >= 4:
                pair = (left_route["canonicalPath"], right_route["canonicalPath"])
                reverse = (pair[1], pair[0])
                if pair not in declared_pairs and reverse not in declared_pairs:
                    collisions.append(
                        f"{pair[0]} ↔ {pair[1]} ({field} benzerliği={score:.2f}, ortak token={common})"
                    )

    assert not collisions, (
        "Yeni aynı-niyet içerik çakışmaları bulundu. Yeni makale eklemek yerine mevcut canonical içeriği güncelleyin "
        "veya content-consolidations.json içinde gerekçeli birleştirme tanımlayın:\n" + "\n".join(collisions[:30])
    )

    print(
        json.dumps(
            {
                "ok": True,
                "effectiveArticleCount": len([route for route in manifest["routes"] if route["type"] == "article"]),
                "activeCanonicalArticleCountAfterConsolidation": len(active_articles),
                "consolidationCount": len(config["consolidations"]),
                "undeclaredHighSimilarityCollisions": 0,
                "afciAliasCanonicalGuard": afci_alias_checked,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
