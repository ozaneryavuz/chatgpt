from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

try:
    from .export_chatgpt_sites_bundle import REPO_ROOT, write_json
    from .export_chatgpt_sites_bundle_v2 import export_bundle as export_v2_bundle
except ImportError:
    from export_chatgpt_sites_bundle import REPO_ROOT, write_json
    from export_chatgpt_sites_bundle_v2 import export_bundle as export_v2_bundle

VERSION = 3
SOURCE_MANIFEST = REPO_ROOT / "alo186/sites-sync/sites-source-manifest.json"


def _rebuild_checksums(output: Path) -> None:
    checksum = output / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines: list[str] = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(output).as_posix()}")
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_bundle(output: Path, source_commit: str) -> dict[str, Any]:
    manifest = export_v2_bundle(output, source_commit)
    if not SOURCE_MANIFEST.is_file():
        raise FileNotFoundError(f"ChatGPT Sites kaynak aktarım manifesti bulunamadı: {SOURCE_MANIFEST}")

    authority = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if authority.get("target") != "chatgpt-sites" or authority.get("siteSlug") != "alo186":
        raise ValueError("Sites kaynak aktarım manifestinin hedefi geçersiz")
    if authority.get("canonicalHost") != "https://alo186.com":
        raise ValueError("Sites kaynak aktarım manifesti canonical host sözleşmesini bozmamalı")
    transfer = authority.get("transferStrategy") or {}
    if transfer.get("automaticPublishAllowed") is not False:
        raise ValueError("Bağlı Sites yazma erişimi olmadan otomatik yayın açılamaz")
    if transfer.get("humanOrConnectedSitesWriteRequired") is not True:
        raise ValueError("Sites yazma erişimi gereksinimi açıkça belirtilmeli")

    target = output / "data/sites-source-manifest.json"
    write_json(target, authority)
    manifest["exporterVersion"] = VERSION
    manifest["authority"] = authority["authority"]
    manifest["transferStrategy"] = authority["transferStrategy"]
    manifest["sitesSourceManifest"] = "data/sites-source-manifest.json"
    manifest["livePublishStatus"] = "prepared-not-published"
    write_json(output / "sites-import.json", manifest)

    receipt = {
        "schemaVersion": 1,
        "siteSlug": "alo186",
        "targetPlatform": "ChatGPT Sites",
        "sourceCommit": source_commit,
        "exporterVersion": VERSION,
        "status": "prepared-not-published",
        "reason": "Bu paket içerik ve veri aktarımını hazırlar. Canlı yayın için bağlı ChatGPT Sites yazma erişimi ve Sites yayın makbuzu gerekir.",
        "automaticPublishAllowed": False,
        "connectedSitesWriteRequired": True,
        "githubPagesCustomDomainAllowed": False,
    }
    write_json(output / "SITES_TRANSFER_RECEIPT.json", receipt)
    _rebuild_checksums(output)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ChatGPT Sites aktarım paketi v3")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "unknown"))
    args = parser.parse_args()
    manifest = export_bundle(args.output.resolve(), args.commit)
    print(
        json.dumps(
            {
                "ok": True,
                "exporterVersion": VERSION,
                "status": manifest["livePublishStatus"],
                "stats": manifest["stats"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
