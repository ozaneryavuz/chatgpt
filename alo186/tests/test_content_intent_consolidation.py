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


def html_text(html: str, tag: str) -> str:
    match = re.search(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
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
    return {
        "source": source,
        "title": title,
        "h1": h1,
        "titleTokens": normalized_tokens(title),
        "h1Tokens": normalized_tokens(h1),
    }


def pair_score(left: dict, right: dict) -> tuple[float, int, str]:
    title_score, title_common = similarity(left["titleTokens"], right["titleTokens"])
    h1_score, h1_common = similarity(left["h1Tokens"], right["h1Tokens"])
    if h1_score >= title_score:
        return h1_score, h1_common, "h1"
    return title_score, title_common, "title"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    config = load_config()
    raw_config = json.loads((DEPLOYMENT / "content-consolidations.json").read_text(encoding="utf-8"))
    kind_by_intent = {
        str(item.get("intentKey")): str(item.get("kind") or "same-intent-article")
        for item in raw_config.get("consolidations", [])
    }
    route_by_path = {route["canonicalPath"]: route for route in manifest["routes"]}
    declared_pairs = {(item["aliasPath"], item["canonicalPath"]) for item in config["consolidations"]}
    alias_paths = {item["aliasPath"] for item in config["consolidations"]}

    for item in config["consolidations"]:
        kind = kind_by_intent.get(item["intentKey"], "same-intent-article")
        alias_route = route_by_path.get(item["aliasPath"])
        target_route = route_by_path.get(item["canonicalPath"])
        assert target_route, f"Canonical hedef routing envanterinde yok: {item['canonicalPath']}"

        if kind == "same-intent-article":
            assert alias_route, f"Birleştirilecek alias routing envanterinde yok: {item['aliasPath']}"
            assert alias_route["type"] == "article" and target_route["type"] == "article"
            alias_signature = article_signature(alias_route["source"])
            target_signature = article_signature(target_route["source"])
            score, common, field = pair_score(alias_signature, target_signature)
            assert score >= 0.50 and common >= 3, (
                f"İlan edilen içerik birleştirmesi aynı arama niyetini doğrulamıyor: "
                f"{item['aliasPath']} → {item['canonicalPath']} ({field}={score:.2f}, ortak={common})"
            )
        elif kind == "legacy-commerce":
            assert item["aliasPath"] == "/amazon-elektrik-urunleri"
            assert item["canonicalPath"] == "/akilli-urun-secimi"
            assert target_route["type"] == "tool"
            if alias_route:
                assert alias_route["canonicalPath"] in alias_paths
        else:
            raise AssertionError(f"Desteklenmeyen consolidation kind: {kind}")

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
                "legacyCommerceAliasCount": sum(1 for value in kind_by_intent.values() if value == "legacy-commerce"),
                "undeclaredHighSimilarityCollisions": 0,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
