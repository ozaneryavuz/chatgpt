from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

VERSION = 1
CSS_FILE = "alo186-live-quality.css"
CSS_MARKER = "/* ALO186 final user entry points v1 */"
ROOT_ROUTE = "index.html"
PORTAL_ROUTE = "elektrik-portali/index.html"

COPY_REPLACEMENTS = (
    (
        "GitHub Pages tabanlı bu sürüm, kritik rehberleri ilk ziyaretten sonra çevrimdışı erişim için önbelleğe alır.",
        "Kritik rehberler, ilk ziyaretten sonra internet bağlantısı zayıfken de açılabilir.",
    ),
    ("Güven ve sürdürülebilir gelir", "Güven, şeffaflık ve teknik kanıt"),
    (
        "Nasıl gelir elde edildiğini, hangi teslimi alacağınızı ve ne zaman geri dönmeniz gerektiğini görün.",
        "ALO186'ın nasıl çalıştığını, hangi teknik çıktıları sunduğunu ve sonuçların nasıl takip edildiğini görün.",
    ),
    ("Gelir ve Bağımsızlık", "Şeffaflık ve Bağımsızlık"),
    (
        "Affiliate, ücretli hizmet ve sponsorluk kurallarını inceleyin.",
        "Satış ortaklığı, ücretli hizmet ve sponsorlu içerik kurallarını açık biçimde inceleyin.",
    ),
    ("Affiliate Product Knowledge Graph", "Ürün Bilgi Grafiği"),
    ("Affiliate ürün Knowledge Graph", "Ürün, ihtiyaç ve teknik kanıt grafiği"),
    ("Affiliate ürün ilişkilerini görün.", "Ürün, ihtiyaç ve teknik kanıt ilişkilerini görün."),
    (
        "Affiliate ilişkisi yalnız nitelikli kategori rehberinin yanında açıklanır.",
        "Satış ortaklığı ilişkisi yalnız nitelikli kategori rehberinin yanında açıklanır.",
    ),
    ("Envanter önce · satın almama · şeffaf affiliate", "Envanter önce · satın almama · şeffaf satış ortaklığı"),
    ("yeni canonical eşleşmeleri", "yeni içerik eşleşmelerini"),
    ("aktif canonical teknik rehber", "güncel teknik rehber"),
    ("tek canonical içerikte birleştirilen tekrar niyeti", "yinelenen arama niyeti tek içerikte birleştirildi"),
)

FORBIDDEN_VISIBLE_TERMS = (
    "affiliate",
    "canonical",
    "knowledge graph",
    "gelir elde edildiğini",
    "github pages tabanlı",
)

GATEWAY_RE = re.compile(
    r'(?P<open><section\b[^>]*class=["\'][^"\']*\bgrid\b[^"\']*["\'][^>]*aria-label=["\']ALO186 hızlı başlangıç["\'][^>]*>)'
    r'(?P<body>.*?)'
    r'(?P<close></section>)',
    re.IGNORECASE | re.DOTALL,
)
ANCHOR_RE = re.compile(r"<a\b[^>]*>.*?</a>", re.IGNORECASE | re.DOTALL)

PRIMARY_CARD_TOKENS = (
    'data-alo186-primary-start="true"',
    "/karar-motoru/",
    "/edas-bul/",
    "/kesintiye-hazirlik-atolyesi/",
    "/elektrik-portali/",
)

ENTRYPOINT_CSS = f"""
{CSS_MARKER}
.button,.btn,a[role="button"]{{display:inline-flex;align-items:center;justify-content:center}}
.alo186-more-tools{{max-width:1120px;margin:18px auto 28px;border:1px solid #d7e2ed;border-radius:18px;background:#fff;box-shadow:0 10px 30px rgba(7,22,49,.08)}}
.alo186-more-tools>summary{{display:flex;min-height:52px;align-items:center;justify-content:space-between;padding:14px 18px;cursor:pointer;color:#071631;font-weight:850;list-style:none}}
.alo186-more-tools>summary::-webkit-details-marker{{display:none}}
.alo186-more-tools>summary::after{{content:"+";font-size:1.25rem}}
.alo186-more-tools[open]>summary::after{{content:"−"}}
.alo186-more-tools>p{{margin:0;padding:0 18px 14px;color:#596b82}}
.alo186-more-tools:not([open])>.grid{{display:none!important}}
.alo186-more-tools[open]>.grid{{margin:0;padding:0 18px 18px}}
@media(max-width:760px){{.button,.btn,a[role="button"]{{min-height:44px}}.alo186-more-tools{{border-radius:14px}}}}
@media(forced-colors:active){{.alo186-more-tools{{border:2px solid CanvasText;background:Canvas;color:CanvasText;box-shadow:none}}}}
@media print{{.alo186-more-tools:not([open]){{display:none!important}}}}
""".strip() + "\n"


class VisibleTextParser(HTMLParser):
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in self.SKIP:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in self.SKIP and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth and data.strip():
            self.parts.append(data)


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def visible_text(html: str) -> str:
    parser = VisibleTextParser()
    parser.feed(html)
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def normalize_copy(html: str) -> tuple[str, int]:
    changed = 0
    for old, new in COPY_REPLACEMENTS:
        occurrences = html.count(old)
        if occurrences:
            html = html.replace(old, new)
            changed += occurrences
    html, count = re.subn(
        r"(\d+)\s+aktif canonical teknik rehber",
        r"\1 güncel teknik rehber",
        html,
        flags=re.IGNORECASE,
    )
    changed += count
    html, count = re.subn(
        r"(\d+)\s+tek canonical içerikte birleştirilen tekrar niyeti",
        r"\1 yinelenen arama niyeti tek içerikte birleştirildi",
        html,
        flags=re.IGNORECASE,
    )
    changed += count
    return html, changed


def prioritize_gateway(html: str) -> tuple[str, bool, int, int]:
    if 'data-alo186-secondary-tools="true"' in html:
        match = GATEWAY_RE.search(html)
        primary_count = len(ANCHOR_RE.findall(match.group("body"))) if match else 0
        secondary_match = re.search(
            r'<details\b[^>]*data-alo186-secondary-tools=["\']true["\'][^>]*>(.*?)</details>',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        secondary_count = len(ANCHOR_RE.findall(secondary_match.group(1))) if secondary_match else 0
        return html, False, primary_count, secondary_count

    match = GATEWAY_RE.search(html)
    if not match:
        return html, False, 0, 0

    cards = ANCHOR_RE.findall(match.group("body"))
    if not cards:
        return html, False, 0, 0

    primary: list[str] = []
    selected: set[int] = set()
    for token in PRIMARY_CARD_TOKENS:
        for index, card in enumerate(cards):
            if index not in selected and token in card:
                primary.append(card)
                selected.add(index)
                break

    if len(primary) != len(PRIMARY_CARD_TOKENS):
        return html, False, len(primary), len(cards) - len(primary)

    secondary = [card for index, card in enumerate(cards) if index not in selected]
    if not secondary:
        return html, False, len(primary), 0

    primary_section = match.group("open") + "\n" + "\n".join(primary) + "\n" + match.group("close")
    secondary_section = (
        '\n<details class="alo186-more-tools" data-alo186-secondary-tools="true">'
        "<summary>Daha fazla ücretsiz araç ve takip seçeneği</summary>"
        "<p>Sonuç takibi, teknik karşılaştırma ve bakım planlama araçlarını ihtiyacınız olduğunda açın.</p>"
        '<div class="grid" aria-label="Diğer ALO186 araçları">\n'
        + "\n".join(secondary)
        + "\n</div></details>"
    )
    updated = html[: match.start()] + primary_section + secondary_section + html[match.end() :]
    return updated, True, len(primary), len(secondary)


def append_css(site: Path) -> bool:
    path = site / CSS_FILE
    if not path.is_file():
        raise FileNotFoundError(f"Canlı kalite CSS dosyası eksik: {CSS_FILE}")
    css = path.read_text(encoding="utf-8")
    if CSS_MARKER in css:
        return False
    path.write_text(css.rstrip() + "\n\n" + ENTRYPOINT_CSS, encoding="utf-8")
    return True


def update_release(path: Path, base_path: str, result: dict) -> None:
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["finalUserEntryPointAudit"] = {
        "version": VERSION,
        "scope": [public_url(base_path, "/"), public_url(base_path, "/elektrik-portali/")],
        "primaryCardsFirst": True,
        "primaryCardCount": result["primaryCardCount"],
        "secondaryToolsProgressive": True,
        "secondaryCardCount": result["secondaryCardCount"],
        "userFacingInternalJargon": 0,
        "minimumTouchTargetCssPx": 44,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute_checksums(site: Path) -> None:
    checksum = site / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in sorted(item for item in site.rglob("*") if item.is_file())
    ]
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def audit(site: Path) -> dict:
    failures: list[str] = []
    root_path = site / ROOT_ROUTE
    portal_path = site / PORTAL_ROUTE
    css_path = site / CSS_FILE

    for path in (root_path, portal_path, css_path):
        if not path.is_file():
            failures.append(f"Kritik final dosyası eksik: {path.relative_to(site)}")

    if failures:
        raise RuntimeError("ALO186 final kullanıcı giriş denetimi başarısız:\n- " + "\n- ".join(failures))

    root = root_path.read_text(encoding="utf-8")
    portal = portal_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")

    for label, html in (("ana sayfa", root), ("elektrik portalı", portal)):
        copy = visible_text(html).casefold()
        for term in FORBIDDEN_VISIBLE_TERMS:
            if term.casefold() in copy:
                failures.append(f"{label} kullanıcı dilinde iç jargon kaldı: {term}")

    match = GATEWAY_RE.search(root)
    primary_count = len(ANCHOR_RE.findall(match.group("body"))) if match else 0
    secondary_match = re.search(
        r'<details\b[^>]*data-alo186-secondary-tools=["\']true["\'][^>]*>(.*?)</details>',
        root,
        re.IGNORECASE | re.DOTALL,
    )
    secondary_count = len(ANCHOR_RE.findall(secondary_match.group(1))) if secondary_match else 0
    if primary_count != len(PRIMARY_CARD_TOKENS):
        failures.append(f"Ana sayfa temel görev sayısı {primary_count}; beklenen {len(PRIMARY_CARD_TOKENS)}")
    if secondary_count < 1:
        failures.append("Ana sayfa ikincil araçları progresif alana taşınmadı")
    if 'data-alo186-secondary-tools="true"' not in root:
        failures.append("Ana sayfa ikincil araç ayrımı eksik")
    positions = [root.find(token) for token in PRIMARY_CARD_TOKENS]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        failures.append("Ana sayfa temel görev sırası bozuk")
    if root.find('data-alo186-primary-start="true"') > root.find('data-alo186-secondary-tools="true"'):
        failures.append("Ana sayfada ikincil araçlar temel görevden önce geliyor")

    for token in (CSS_MARKER, '.button,.btn,a[role="button"]{display:inline-flex', ".alo186-more-tools"):
        if token not in css:
            failures.append(f"Final kullanıcı CSS sözleşmesi eksik: {token}")

    if failures:
        raise RuntimeError("ALO186 final kullanıcı giriş denetimi başarısız:\n- " + "\n- ".join(failures[:100]))

    return {
        "ok": True,
        "criticalPages": 2,
        "primaryCardCount": primary_count,
        "secondaryCardCount": secondary_count,
        "userFacingInternalJargon": 0,
        "minimumTouchTargetCssPx": 44,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    if not site.is_dir():
        raise FileNotFoundError(f"Yayın artifactı bulunamadı: {site}")

    root_path = site / ROOT_ROUTE
    portal_path = site / PORTAL_ROUTE
    changed_files = 0
    copy_replacements = 0
    gateway_reordered = False
    primary_count = 0
    secondary_count = 0

    for path in (root_path, portal_path):
        if not path.is_file():
            raise FileNotFoundError(f"Kritik giriş sayfası eksik: {path.relative_to(site)}")
        original = path.read_text(encoding="utf-8")
        updated, count = normalize_copy(original)
        copy_replacements += count
        if path == root_path:
            updated, reordered, primary_count, secondary_count = prioritize_gateway(updated)
            gateway_reordered = gateway_reordered or reordered
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1

    css_appended = append_css(site)
    preliminary = {
        "primaryCardCount": primary_count,
        "secondaryCardCount": secondary_count,
    }
    update_release(site / "alo186-release.json", base_path, preliminary)
    update_release(site / "pages-release.json", base_path, preliminary)
    recompute_checksums(site)
    result = audit(site)
    result.update(
        {
            "version": VERSION,
            "basePath": base_path,
            "changedHtmlFiles": changed_files,
            "copyReplacements": copy_replacements,
            "gatewayReordered": gateway_reordered,
            "cssAppended": css_appended,
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final artifactında kullanıcı öncelikli girişleri fail-closed doğrular.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
