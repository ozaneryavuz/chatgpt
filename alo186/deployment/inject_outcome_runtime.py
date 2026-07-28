from __future__ import annotations

import argparse
import json
from pathlib import Path

MARKER = 'data-alo186-common-runtime="true"'


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def inject(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    common = site / "hesaplama" / "common.js"
    bridge = site / "hesaplama" / "outcome-bridge.js"
    if not common.is_file():
        raise FileNotFoundError(f"Ortak hesaplama runtime eksik: {common}")
    if not bridge.is_file():
        raise FileNotFoundError(f"Çözüm sonucu köprüsü eksik: {bridge}")

    common_url = f"{base_path}/hesaplama/common.js" if base_path else "/hesaplama/common.js"
    injected = 0
    already_present = 0
    missing_body = []

    for html_path in sorted(site.rglob("*.html")):
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        if MARKER in text:
            already_present += 1
            continue
        if "</body>" not in text:
            missing_body.append(html_path.relative_to(site).as_posix())
            continue
        tag = f'<script {MARKER} src="{common_url}"></script>'
        html_path.write_text(text.replace("</body>", f"{tag}\n</body>", 1), encoding="utf-8")
        injected += 1

    if missing_body:
        raise RuntimeError("Outcome runtime için </body> bulunamayan HTML: " + ", ".join(missing_body[:20]))

    result = {
        "ok": True,
        "basePath": base_path,
        "commonUrl": common_url,
        "injectedPages": injected,
        "alreadyPresent": already_present,
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
