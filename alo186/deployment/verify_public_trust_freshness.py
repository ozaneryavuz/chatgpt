from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HOME = Path("index.html")
PRODUCT_HUB = Path("amazon-elektrik-urunleri/index.html")
RELEASE = Path("pages-release.json")
CHECKSUMS = Path("checksums.sha256")

FORBIDDEN_STALE_OR_OUT_OF_SCOPE = (
    "25 rehber",
    "152 karşılaştırılmış model",
    "152 model",
    "67 ürün seçim yolu",
    "usb-c hub ve çoklayıcı",
)
HOME_REQUIRED = (
    "edaş veya kamu kurumu değildir",
    "alo186 başvuru, ihbar veya hasar kaydı almaz",
    "tehlike varsa ticari yol kapanır",
)
PRODUCT_HUB_REQUIRED = (
    "amazon satış ortaklığı",
    "mevcut sistem yeterliyse satın alma yok",
    "aktif tehlikede satış yolu kapalı",
    "affiliate açıklaması bağlantıdan önce",
    "alo186 satıcı değildir",
)
CHECKSUM_TARGETS = (HOME, PRODUCT_HUB, RELEASE)


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def read_required(site: Path, relative: Path) -> str:
    path = site / relative
    if not path.is_file():
        raise FileNotFoundError(f"Yayın güven doğrulaması için dosya eksik: {relative.as_posix()}")
    return path.read_text(encoding="utf-8", errors="strict")


def parse_checksums(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            raise RuntimeError(f"Geçersiz checksum satırı: {raw}")
        relative = parts[1].strip().lstrip("*")
        if relative in entries:
            raise RuntimeError(f"Checksum listesinde yinelenen yol: {relative}")
        entries[relative] = parts[0]
    return entries


def validate_checksums(site: Path) -> dict[str, str]:
    entries = parse_checksums(read_required(site, CHECKSUMS))
    verified: dict[str, str] = {}
    for relative in CHECKSUM_TARGETS:
        key = relative.as_posix()
        expected = entries.get(key)
        if not expected:
            raise RuntimeError(f"Checksum makbuzunda kritik dosya eksik: {key}")
        actual = hashlib.sha256((site / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Yayımlanan artifact checksum uyuşmazlığı: {key}")
        verified[key] = actual
    return verified


def validate_site(site: Path, expected_commit: str, expected_base_path: str = "") -> dict:
    site = site.resolve()
    expected_commit = str(expected_commit or "").strip()
    if not expected_commit:
        raise ValueError("Beklenen commit boş olamaz")
    expected_base_path = normalize_base_path(expected_base_path)

    home = normalized_text(read_required(site, HOME))
    hub = normalized_text(read_required(site, PRODUCT_HUB))
    combined = home + " " + hub

    stale = [token for token in FORBIDDEN_STALE_OR_OUT_OF_SCOPE if token.casefold() in combined]
    if stale:
        raise RuntimeError("Eski veya kapsam dışı canlı ifade bulundu: " + ", ".join(stale))

    missing_home = [token for token in HOME_REQUIRED if token.casefold() not in home]
    if missing_home:
        raise RuntimeError("Ana sayfa güven sözleşmesi eksik: " + ", ".join(missing_home))

    missing_hub = [token for token in PRODUCT_HUB_REQUIRED if token.casefold() not in hub]
    if missing_hub:
        raise RuntimeError("Affiliate merkezi güven sözleşmesi eksik: " + ", ".join(missing_hub))

    release = json.loads(read_required(site, RELEASE))
    actual_commit = str(release.get("commit") or "").strip()
    if actual_commit != expected_commit:
        raise RuntimeError(
            f"Yayın commit makbuzu eski veya farklı: beklenen={expected_commit}, artifact={actual_commit or 'boş'}"
        )
    actual_base_path = normalize_base_path(str(release.get("basePath") or ""))
    if actual_base_path != expected_base_path:
        raise RuntimeError(
            f"Yayın base-path makbuzu farklı: beklenen={expected_base_path or '/'}, artifact={actual_base_path or '/'}"
        )
    if release.get("canonicalHost") != "https://alo186.com":
        raise RuntimeError("Canonical host yalnız https://alo186.com olmalıdır")
    if release.get("customDomain") != "alo186.com":
        raise RuntimeError("Custom-domain makbuzu alo186.com olmalıdır")

    checksums = validate_checksums(site)
    return {
        "ok": True,
        "commit": actual_commit,
        "basePath": actual_base_path,
        "canonicalHost": release["canonicalHost"],
        "customDomain": release["customDomain"],
        "staleClaimsRejected": list(FORBIDDEN_STALE_OR_OUT_OF_SCOPE),
        "homeTrustSignals": len(HOME_REQUIRED),
        "affiliateTrustSignals": len(PRODUCT_HUB_REQUIRED),
        "checksumsVerified": sorted(checksums),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 yayımlanan artifact commit, tazelik, bağımsızlık ve affiliate güven sözleşmesini doğrular."
    )
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    result = validate_site(args.site, args.expected_commit, args.base_path)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
