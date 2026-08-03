from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "alo186/deployment/affiliate-scope-policy-v229.json"
AFFILIATE_ROOT = ROOT / "alo186/amazon-elektrik-urunleri"


def load_policy() -> dict:
    payload = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    assert payload.get("version") == 229, "Affiliate kapsam politikası sürümü geçersiz"
    return payload


def normalized(value: str) -> str:
    return value.casefold().replace("ı", "i").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c")


def evaluate_route(slug: str, text: str, policy: dict) -> list[str]:
    slug_n = normalized(slug)
    text_n = normalized(text)
    exceptions = {normalized(item) for item in policy.get("approvedExceptions", [])}
    if slug_n in exceptions:
        return []

    failures: list[str] = []
    blocked = [normalized(item) for item in policy["blockedGenericRouteTokens"]]
    approved = [normalized(item) for item in policy["approvedRouteTokens"]]

    matched_blocked = sorted(token for token in blocked if token in slug_n)
    if matched_blocked:
        failures.append(f"genel aksesuar kapsamı yasak: {', '.join(matched_blocked)}")

    if not any(token in slug_n for token in approved):
        failures.append("rota elektrik güvenliği, enerji sürekliliği, ölçüm veya kritik cihaz görevi taşımıyor")

    disclosure_ok = "affiliate" in text_n or "satis ortakligi" in text_n
    if not disclosure_ok:
        failures.append("görünür affiliate/satış ortaklığı açıklaması eksik")

    no_buy_ok = "mevcut" in text_n and "satin alma" in text_n
    if not no_buy_ok:
        failures.append("mevcut çözüm yeterliyse satın almama sınırı eksik")

    for claim in policy["forbiddenCommercialClaims"]:
        if normalized(claim) in text_n:
            failures.append(f"yasak ticari iddia: {claim}")

    if re.search(r'Product\s*/\s*Offer|AggregateRating', text, re.I):
        failures.append("yasak ticari şema iddiası")
    return failures


def route_slugs_from_changed_files(path: Path) -> list[str]:
    slugs: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = raw.strip().replace("\\", "/")
        parts = value.split("/")
        if len(parts) >= 4 and parts[:2] == ["alo186", "amazon-elektrik-urunleri"]:
            slug = parts[2]
            if slug and slug != "index.html":
                slugs.add(slug)
    return sorted(slugs)


def read_route_text(slug: str) -> str:
    directory = AFFILIATE_ROOT / slug
    if not directory.is_dir():
        raise AssertionError(f"Affiliate rota klasörü bulunamadı: {slug}")
    chunks: list[str] = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".html", ".js", ".json", ".md"}:
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def self_test(policy: dict) -> None:
    safe = "Affiliate satış ortaklığı açıklaması. Mevcut çözüm yeterliyse satın alma yapmayın."
    assert not evaluate_route("modem-ont-mini-ups-secimi", safe, policy)
    assert evaluate_route("usb-bellek-dosya-aktarim-secimi", safe, policy)
    assert evaluate_route("webcam-secimi", safe, policy)
    assert evaluate_route("enerji-olcer-secimi", "Mevcut çözüm yeterliyse satın alma yapmayın.", policy)
    assert evaluate_route("enerji-olcer-secimi", safe + " Hemen satın al.", policy)


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 yeni affiliate rota kapsam kapısı v229")
    parser.add_argument("--changed-files", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    policy = load_policy()
    if args.self_test:
        self_test(policy)

    slugs = route_slugs_from_changed_files(args.changed_files) if args.changed_files else []
    failures: list[str] = []
    for slug in slugs:
        for failure in evaluate_route(slug, read_route_text(slug), policy):
            failures.append(f"{slug}: {failure}")

    result = {
        "ok": not failures,
        "version": policy["version"],
        "checkedRoutes": slugs,
        "checkedRouteCount": len(slugs),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
