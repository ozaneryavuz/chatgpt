from __future__ import annotations

import re
from pathlib import Path

import prepare_github_pages_core as _core
from prepare_github_pages_core import *  # noqa: F401,F403


DEVICE_DAMAGE_MARKER = 'data-alo186-device-damage-deadline="true"'
DEVICE_DAMAGE_ROUTE = "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/"
_original_gateway_html = _core.gateway_html
_original_prepare = _core.prepare


def gateway_html(base_path: str, noindex: bool) -> str:
    """Pages kök gateway'inde güncel cihaz hasarı süresini görünür ve kaynaklı tutar."""

    html = _original_gateway_html(base_path, noindex)
    if DEVICE_DAMAGE_MARKER in html:
        return html

    style = (
        ".legal-deadline{margin:0 0 28px;padding:20px;border-radius:18px;"
        "background:#eef7ff;border:2px solid #4c7bd9}"
        ".legal-deadline strong{display:block;color:var(--navy);font-size:1.2rem}"
        ".legal-deadline p{margin:.55rem 0;color:#263a59}"
        ".legal-deadline a{display:inline-flex;align-items:center;min-height:44px;"
        "color:#174bb9;font-weight:900}"
    )
    if "</style>" not in html:
        raise RuntimeError("Pages gateway inline stil kapanışı bulunamadı.")
    html = html.replace("</style>", style + "</style>", 1)

    guide_url = _core.public_url(base_path, DEVICE_DAMAGE_ROUTE)
    notice = (
        f'<section class="legal-deadline" {DEVICE_DAMAGE_MARKER} '
        'aria-labelledby="device-damage-deadline">'
        '<strong id="device-damage-deadline">Cihaz hasarında başvuru süresi 10 iş günüdür</strong>'
        '<p>Dağıtım şebekesinden kaynaklandığını düşündüğünüz cihaz veya teçhizat hasarı için '
        'zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü içinde</strong> ilgili dağıtım '
        'şirketinin resmî kanalına başvurun. ALO186 başvuru, ihbar veya hasar kaydı almaz.</p>'
        f'<a href="{guide_url}">Belge ve başvuru rehberini aç →</a>'
        '</section>'
    )
    anchor = '<section class="grid" aria-label="ALO186 hızlı başlangıç">'
    if anchor not in html:
        raise RuntimeError("Pages gateway hızlı başlangıç alanı bulunamadı.")
    return html.replace(anchor, notice + "\n" + anchor, 1)


def validate_root_legal_deadline(site: Path, base_path: str) -> None:
    root = site / "index.html"
    if not root.is_file():
        raise FileNotFoundError(f"Pages kök sayfası eksik: {root}")
    html = root.read_text(encoding="utf-8")
    required = (
        DEVICE_DAMAGE_MARKER,
        "Cihaz hasarında başvuru süresi 10 iş günüdür",
        "zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü içinde</strong>",
        "ALO186 başvuru, ihbar veya hasar kaydı almaz",
        f'href="{_core.public_url(base_path, DEVICE_DAMAGE_ROUTE)}"',
    )
    missing = [item for item in required if item not in html]
    if missing:
        raise RuntimeError("Pages kök hukuki süre koruması eksik: " + ", ".join(missing))
    if re.search(r"\b30\s*(?:takvim\s*)?gün\b", html, re.IGNORECASE):
        raise RuntimeError("Pages kökünde cihaz hasarı bağlamında 30 gün ifadesi kalamaz.")


def prepare(site: Path, base_path: str, repository: str, commit: str) -> dict:
    result = _original_prepare(site, base_path, repository, commit)
    normalized = _core.normalize_base_path(base_path)
    validate_root_legal_deadline(site, normalized)
    result["rootDeviceDamageDeadline"] = "10 iş günü"
    result["rootNoApplicationDisclaimer"] = True
    release_path = site / "pages-release.json"
    if release_path.is_file():
        import json

        release = json.loads(release_path.read_text(encoding="utf-8"))
        release["rootDeviceDamageDeadline"] = "10 iş günü"
        release["rootNoApplicationDisclaimer"] = True
        release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = release
    _core.recompute_checksums(site)
    return result


_core.gateway_html = gateway_html
_core.prepare = prepare


def main() -> None:
    _core.main()


if __name__ == "__main__":
    main()
