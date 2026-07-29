from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2] / "alo186"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.local_refs: list[tuple[str, str]] = []
        self.has_title = False
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs}
        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)

        if tag == "meta" and values.get("name") == "viewport":
            self.has_viewport = True
        if tag == "title":
            self.has_title = True

        for attr in ("href", "src"):
            value = values.get(attr)
            if value:
                self.local_refs.append((attr, value))


def is_local_ref(value: str) -> bool:
    # Root-relative references point to canonical production routes. Source folders do
    # not necessarily mirror those routes, so their existence is enforced by the
    # routing-manifest/sitemap tests rather than resolved relative to the HTML file.
    if value.startswith(("http://", "https://", "tel:", "mailto:", "#", "data:", "/")):
        return False
    return not bool(urlparse(value).scheme)


def resolve_local(page: Path, value: str) -> Path:
    clean = value.split("?", 1)[0].split("#", 1)[0]
    target = (page.parent / clean).resolve()
    if clean.endswith("/"):
        target = target / "index.html"
    return target


def referenced_ids(js_text: str) -> set[str]:
    patterns = [
        r"getElementById\(\s*['\"]([^'\"]+)['\"]\s*\)",
        r"\$\(\s*['\"]([^'\"]+)['\"]\s*\)",
    ]
    result: set[str] = set()
    for pattern in patterns:
        result.update(re.findall(pattern, js_text))
    return result


def dynamically_declared_ids(js_text: str) -> set[str]:
    """Return literal IDs created by page JavaScript before they are referenced.

    Static pages may insert accessibility/status panels at runtime. Treat only literal
    assignments and literal id attributes as declarations; computed values remain
    fail-closed and must still exist in source HTML or be made explicit.
    """
    patterns = [
        r"\.id\s*=\s*['\"]([^'\"]+)['\"]",
        r"\bid\s*=\s*['\"]([^'\"]+)['\"]",
    ]
    result: set[str] = set()
    for pattern in patterns:
        result.update(re.findall(pattern, js_text))
    return result


def main() -> int:
    errors: list[str] = []
    pages = sorted(ROOT.rglob("index.html"))
    if not pages:
        errors.append("ALO186 içinde index.html bulunamadı")

    for page in pages:
        parser = PageParser()
        html = page.read_text(encoding="utf-8")
        parser.feed(html)
        relative = page.relative_to(ROOT)

        if not parser.has_title:
            errors.append(f"{relative}: title etiketi yok")
        if not parser.has_viewport:
            errors.append(f"{relative}: viewport meta etiketi yok")
        if parser.duplicate_ids:
            errors.append(f"{relative}: yinelenen id: {sorted(parser.duplicate_ids)}")

        for attr, ref in parser.local_refs:
            if not is_local_ref(ref):
                continue
            target = resolve_local(page, ref)
            if not target.exists():
                errors.append(f"{relative}: {attr} hedefi bulunamadı: {ref}")

        app = page.parent / "app.js"
        if app.exists():
            js_text = app.read_text(encoding="utf-8")
            available_ids = parser.ids | dynamically_declared_ids(js_text)
            missing = sorted(referenced_ids(js_text) - available_ids)
            if missing:
                errors.append(f"{relative}: app.js tarafından kullanılan id'ler HTML'de yok: {missing}")

    if errors:
        print("ALO186 doğrulaması başarısız:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"ALO186 doğrulaması başarılı: {len(pages)} sayfa kontrol edildi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
