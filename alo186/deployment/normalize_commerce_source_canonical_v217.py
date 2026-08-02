from __future__ import annotations

import argparse
import json
from pathlib import Path

LEGACY = "https://www.alo186.com"
CANONICAL = "https://alo186.com"

TARGETS = (
    "alo186/amazon-elektrik-urunleri/index.html",
    "alo186/amazon-elektrik-urunleri/powerbank-usb-c-secimi/index.html",
    "alo186/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi/index.html",
    "alo186/amazon-elektrik-urunleri/modem-mini-ups-secimi/index.html",
    "alo186/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi/index.html",
    "alo186/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi/index.html",
    "alo186/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/index.html",
    "alo186/amazon-elektrik-urunleri/ges-malzemeleri-secimi/index.html",
    "alo186/hizmetler/otel-elektrik-surekliligi-denetimi/index.html",
    "alo186/hizmetler/elektrik-teklif-teknik-inceleme/index.html",
    "alo186/hizmetler/ges-batarya-ev-sarj-fizibilitesi/index.html",
)


def normalize(repo_root: Path, *, check: bool = False) -> dict[str, object]:
    changed: list[str] = []
    replacements = 0
    missing: list[str] = []

    for relative in TARGETS:
        path = repo_root / relative
        if not path.is_file():
            missing.append(relative)
            continue
        source = path.read_text(encoding="utf-8")
        count = source.count(LEGACY)
        if not count:
            continue
        changed.append(relative)
        replacements += count
        if not check:
            path.write_text(source.replace(LEGACY, CANONICAL), encoding="utf-8")

    if missing:
        raise FileNotFoundError("Canonical hedef dosyaları eksik: " + ", ".join(missing))
    if check and changed:
        raise RuntimeError(
            "Legacy www canonical/source referansları kaldı: " + ", ".join(changed)
        )

    return {
        "ok": True,
        "check": check,
        "canonicalOrigin": CANONICAL,
        "targetCount": len(TARGETS),
        "changedFileCount": len(changed),
        "replacementCount": replacements,
        "changedFiles": changed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 ticari ve hizmet kaynaklarında www canonical driftini apex'e taşır."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(normalize(args.repo_root.resolve(), check=args.check), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
