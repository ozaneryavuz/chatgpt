from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

MARKER = 'data-alo186-common-runtime="true"'
PENDING_MARKER = 'data-alo186-pending-context="true"'
CARD_MARKER = 'data-alo186-outcome-card="true"'
OUTCOME_RELATIVE = Path("hesaplama/cozum-sonucu/index.html")
PORTAL_RELATIVE = Path("elektrik-portali/index.html")
GATEWAY_RELATIVE = Path("index.html")


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def insert_after_grid_open(text: str, card: str) -> tuple[str, bool]:
    if CARD_MARKER in text:
        return text, False
    match = re.search(r'<section\b[^>]*class=["\'][^"\']*\bgrid\b[^"\']*["\'][^>]*>', text, re.I)
    if not match:
        return text, False
    return text[: match.end()] + "\n" + card + text[match.end() :], True


def outcome_card(base_path: str, gateway: bool = False) -> str:
    href = public_url(base_path, "/hesaplama/cozum-sonucu/")
    if gateway:
        return f'<a class="card" {CARD_MARKER} href="{href}"><strong>Çözüm gerçekten işe yaradı mı?</strong><p>Öneri, ürün, bakım veya resmî kanal sonucunu kişisel veri vermeden kaydedin; tekrar eden problemi doğru rotaya taşıyın.</p><span>Sonucu kaydet ve izle →</span></a>'
    return f'<a class="card" {CARD_MARKER} href="{href}"><span class="tag">Kapalı döngü · satın almama · tekrar önleme</span><h2>Çözüm Sonucu Merkezi</h2><p>Karar, hesap, ürün, bakım veya resmî kanalın gerçekten işe yarayıp yaramadığını izleyin; çözüldüyse yeni ürün önerilmez.</p><b>Sonucu kaydet ve tekrar riskini izle →</b></a>'


def add_offline_route(site: Path, base_path: str) -> bool:
    sw_path = site / "sw.js"
    if not sw_path.is_file():
        raise FileNotFoundError(f"GitHub Pages service worker eksik: {sw_path}")
    outcome_url = public_url(base_path, "/hesaplama/cozum-sonucu/")
    text = sw_path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    critical = json.loads(match.group(1))
    if outcome_url in critical:
        return False
    critical.append(outcome_url)
    updated = text[: match.start(1)] + json.dumps(critical, ensure_ascii=False) + text[match.end(1) :]
    sw_path.write_text(updated, encoding="utf-8")
    return True


def update_pages_release(site: Path, base_path: str, injected: int, pending_injected: int, cards_injected: int, offline_added: bool) -> None:
    release_path = site / "pages-release.json"
    if not release_path.is_file():
        return
    release = json.loads(release_path.read_text(encoding="utf-8"))
    release["outcomeRuntime"] = {
        "version": 1,
        "basePath": base_path,
        "injectedPages": injected,
        "pendingContextInjected": pending_injected,
        "entryCardsInjected": cards_injected,
        "pendingRecordLimit": 6,
        "pendingTtlDays": 45,
        "offlineOutcomeRoute": public_url(base_path, "/hesaplama/cozum-sonucu/"),
    }
    if offline_added:
        release["offlineCriticalRouteCount"] = int(release.get("offlineCriticalRouteCount") or 0) + 1
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute_checksums(site: Path) -> None:
    checksum_path = site / "checksums.sha256"
    if checksum_path.exists():
        checksum_path.unlink()
    lines = []
    for path in sorted(item for item in site.rglob("*") if item.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(site).as_posix()}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    common_url = public_url(base_path, "/hesaplama/common.js")
    pending_url = public_url(base_path, "/hesaplama/cozum-sonucu/pending-context.js")
    injected = 0
    already_present = 0
    pending_injected = 0
    cards_injected = 0
    missing_body = []

    for html_path in sorted(site.rglob("*.html")):
        relative = html_path.relative_to(site)
        text = html_path.read_text(encoding="utf-8", errors="ignore")

        if relative == PORTAL_RELATIVE:
            text, added = insert_after_grid_open(text, outcome_card(base_path))
            cards_injected += int(added)
        elif relative == GATEWAY_RELATIVE:
            text, added = insert_after_grid_open(text, outcome_card(base_path, gateway=True))
            cards_injected += int(added)

        tags = []
        if MARKER not in text:
            tags.append(f'<script {MARKER} src="{common_url}"></script>')
            injected += 1
        else:
            already_present += 1

        if relative == OUTCOME_RELATIVE and PENDING_MARKER not in text:
            tags.append(f'<script {PENDING_MARKER} src="{pending_url}"></script>')
            pending_injected += 1

        if tags:
            if "</body>" not in text:
                missing_body.append(relative.as_posix())
                continue
            text = text.replace("</body>", "\n".join(tags) + "\n</body>", 1)

        html_path.write_text(text, encoding="utf-8")

    if missing_body:
        raise RuntimeError("Outcome runtime için </body> bulunamayan HTML: " + ", ".join(missing_body[:20]))

    offline_added = add_offline_route(site, base_path)
    update_pages_release(site, base_path, injected, pending_injected, cards_injected, offline_added)
    recompute_checksums(site)

    result = {
        "ok": True,
        "basePath": base_path,
        "commonUrl": common_url,
        "pendingContextUrl": pending_url,
        "injectedPages": injected,
        "alreadyPresent": already_present,
        "pendingContextInjected": pending_injected,
        "entryCardsInjected": cards_injected,
        "offlineOutcomeRouteAdded": offline_added,
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
