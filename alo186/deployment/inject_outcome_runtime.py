from __future__ import annotations

import argparse
import json
from pathlib import Path

MARKER = 'data-alo186-common-runtime="true"'
PENDING_MARKER = 'data-alo186-pending-context="true"'
OUTCOME_RELATIVE = Path("hesaplama/cozum-sonucu/index.html")


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def inject(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    common = site / "hesaplama" / "common.js"
    bridge = site / "hesaplama" / "outcome-bridge.js"
    pending_context = site / "hesaplama" / "cozum-sonucu" / "pending-context.js"
    if not common.is_file():
        raise FileNotFoundError(f"Ortak hesaplama runtime eksik: {common}")
    if not bridge.is_file():
        raise FileNotFoundError(f"Çözüm sonucu köprüsü eksik: {bridge}")
    if not pending_context.is_file():
        raise FileNotFoundError(f"Bekleyen çözüm bağlamı tüketicisi eksik: {pending_context}")

    common_url = f"{base_path}/hesaplama/common.js" if base_path else "/hesaplama/common.js"
    pending_url = f"{base_path}/hesaplama/cozum-sonucu/pending-context.js" if base_path else "/hesaplama/cozum-sonucu/pending-context.js"
    injected = 0
    already_present = 0
    pending_injected = 0
    missing_body = []

    for html_path in sorted(site.rglob("*.html")):
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        tags = []
        if MARKER not in text:
            tags.append(f'<script {MARKER} src="{common_url}"></script>')
            injected += 1
        else:
            already_present += 1

        if html_path.relative_to(site) == OUTCOME_RELATIVE and PENDING_MARKER not in text:
            tags.append(f'<script {PENDING_MARKER} src="{pending_url}"></script>')
            pending_injected += 1

        if not tags:
            continue
        if "</body>" not in text:
            missing_body.append(html_path.relative_to(site).as_posix())
            continue
        html_path.write_text(text.replace("</body>", "\n".join(tags) + "\n</body>", 1), encoding="utf-8")

    if missing_body:
        raise RuntimeError("Outcome runtime için </body> bulunamayan HTML: " + ", ".join(missing_body[:20]))

    result = {
        "ok": True,
        "basePath": base_path,
        "commonUrl": common_url,
        "pendingContextUrl": pending_url,
        "injectedPages": injected,
        "alreadyPresent": already_present,
        "pendingContextInjected": pending_injected,
        "totalPages": injected + already_present,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ortak çözüm sonucu runtime'ını bütün GitHub Pages HTML rotalarına ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
