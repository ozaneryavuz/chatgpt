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


def normalize_route(value: str) -> str:
    """Karşılaştırmalarda /rota ve /rota/ biçimlerini tek kimlikte birleştir."""
    cleaned = "/" + str(value or "").strip().strip("/")
    return cleaned if cleaned != "" else "/"


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


def commerce_pair_matches(left: dict, right: dict) -> tuple[bool, str]:
    headline_score, headline_common, field = pair_score(left, right)
    summary_score, summary_common = similarity(left["summaryTokens"], right["summaryTokens"])
    # Güvenlik kapılı güncel seçiciler eski katalog sayfalarından daha kapsamlıdır;
    # Jaccard oranı bu nedenle düşebilir. Aynı ürün görevi için başlıkta en az üç
    # veya özet sinyalinde en az sekiz ortak teknik token kanıt kabul edilir.
    matches = headline_common >= 3 or summary_common >= 8
    return matches, (
        f"{field}={headline_score:.2f}, ortak={headline_common}; "
        f"özet={summary_score:.2f}, ortak={summary_common}"
    )


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    config = load_config()
    route_by_path: dict[str, dict] = {}
    for route in manifest["routes"]:
        canonical = route["canonicalPath"]
        route_by_path[canonical] = route
        route_by_path[canonical.rstrip("/") or "/"] = route
    declared_pairs = {
        (normalize_route(item["aliasPath"]), normalize_route(item["canonicalPath"]))
        for item in config["consolidations"]
    }
    alias_paths = {normalize_route(item["aliasPath"]) for item in config["consolidations"]}

    for item in config["consolidations"]:
        alias_route = route_by_path.get(item["aliasPath"])
        target_route = route_by_path.get(item["canonicalPath"])
        assert alias_route, f"Birleştirilecek alias routing envanterinde yok: {item['aliasPath']}"
        assert target_route, f"Canonical hedef routing envanterinde yok: {item['canonicalPath']}"
        assert alias_route["type"] == target_route["type"], (
            f"Birleştirilen rotaların içerik türü aynı olmalı: {item['aliasPath']} "
            f"({alias_route['type']}) → {item['canonicalPath']} ({target_route['type']})"
        )
        assert alias_route["type"] in {"article", "commerce-guide"}, (
            f"Desteklenmeyen canonical birleştirme türü: {alias_route['type']}"
        )
        alias_signature = article_signature(alias_route["source"])
        target_signature = article_signature(target_route["source"])
        if alias_route["type"] == "commerce-guide":
            matches, evidence = commerce_pair_matches(alias_signature, target_signature)
        else:
            matches, evidence = declared_pair_matches(alias_signature, target_signature)
        assert matches, (
            f"İlan edilen içerik birleştirmesi aynı arama niyetini doğrulamıyor: "
            f"{item['aliasPath']} → {item['canonicalPath']} ({evidence})"
        )

    active_articles = [
        route for route in manifest["routes"]
        if route["type"] == "article" and normalize_route(route["canonicalPath"]) not in alias_paths
    ]
    signatures = [(route, article_signature(route["source"])) for route in active_articles]
    collisions: list[str] = []
    for index, (left_route, left) in enumerate(signatures):
        for right_route, right in signatures[index + 1 :]:
            score, common, field = pair_score(left, right)
            if score >= 0.74 and common >= 4:
                pair = (
                    normalize_route(left_route["canonicalPath"]),
                    normalize_route(right_route["canonicalPath"]),
                )
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
                "supportedConsolidationTypes": ["article", "commerce-guide"],
                "trailingSlashNormalization": True,
                "undeclaredHighSimilarityCollisions": 0,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
