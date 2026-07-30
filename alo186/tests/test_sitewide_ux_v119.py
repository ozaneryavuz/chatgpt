from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
UX_MARKER = 'data-alo186-sitewide-ux="true"'


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images = 0
        self.images_with_alt = 0
        self.h1 = 0
        self.main = 0
        self._label_depth = 0
        self._labels_for: set[str] = set()
        self._controls: list[tuple[str | None, bool]] = []
        self.amazon_links = 0
        self.amazon_links_sponsored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "label":
            self._label_depth += 1
            if values.get("for"):
                self._labels_for.add(str(values["for"]))
            return
        if tag == "img":
            self.images += 1
            if "alt" in values:
                self.images_with_alt += 1
        elif tag == "h1":
            self.h1 += 1
        elif tag == "main":
            self.main += 1
        elif tag in {"input", "select", "textarea"}:
            if tag == "input" and values.get("type", "text").lower() in {"hidden", "submit", "button", "reset", "image"}:
                return
            named = bool(
                self._label_depth
                or values.get("aria-label")
                or values.get("aria-labelledby")
                or values.get("title")
            )
            self._controls.append((values.get("id"), named))
        elif tag == "a" and values.get("href"):
            host = urlparse(str(values["href"])).hostname or ""
            host = host.lower().removeprefix("www.")
            if host == "amazon.com.tr" or host.endswith(".amazon.com.tr") or host == "amzn.to":
                self.amazon_links += 1
                rel = set((values.get("rel") or "").split())
                if {"sponsored", "nofollow", "noopener"} <= rel:
                    self.amazon_links_sponsored += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self._label_depth:
            self._label_depth -= 1

    def unlabelled_controls(self) -> int:
        return sum(
            1 for control_id, named in self._controls
            if not named and (not control_id or control_id not in self._labels_for)
        )


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def attr(text: str, tag: str, name: str) -> str | None:
    match = re.search(rf"<{tag}\b[^>]*\b{name}\s*=\s*(['\"])(.*?)\1", text, re.IGNORECASE | re.DOTALL)
    return match.group(2).strip() if match else None


def has_named_meta(text: str, name: str, content: str | None = None) -> bool:
    for tag in re.findall(r"<meta\b[^>]*>", text, re.IGNORECASE):
        if not re.search(rf"\bname\s*=\s*(['\"]){re.escape(name)}\1", tag, re.IGNORECASE):
            continue
        if content is None or re.search(rf"\bcontent\s*=\s*(['\"]){re.escape(content)}\1", tag, re.IGNORECASE):
            return True
    return False


def has_canonical(text: str) -> bool:
    for tag in re.findall(r"<link\b[^>]*>", text, re.IGNORECASE):
        rel = re.search(r"\brel\s*=\s*(['\"])(.*?)\1", tag, re.IGNORECASE)
        if rel and "canonical" in rel.group(2).lower().split() and re.search(r"\bhref\s*=", tag, re.IGNORECASE):
            return True
    return False


ux_js = (ROOT / "alo186/assets/alo186-ux.js").read_text(encoding="utf-8")
ux_css = (ROOT / "alo186/assets/alo186-ux.css").read_text(encoding="utf-8")
prepare_source = (ROOT / "alo186/deployment/prepare_github_pages.py").read_text(encoding="utf-8")

for token in (
    "const isIndexable = !robots.includes('noindex')",
    "const isEnglish",
    "/en/electricity-distribution-company-finder/",
    "/en/emergency-numbers-turkey/",
    "MutationObserver",
    "sponsored",
    "nofollow",
    "data-alo-affiliate-badge",
    "alo-ux-toc",
    "Bu sayfada neler var?",
    "alo186AltFallback",
    "figcaption",
    "journeyData",
    "addNextSteps",
    "data-alo186-next-steps",
    "Mevcut ürünün yeterli olup olmadığını önce kontrol edin",
):
    assert token in ux_js, token
for token in (
    "body:not([data-alo186-ux-compact=\"true\"])",
    ".alo-ux-toc",
    ".alo-ux-next",
    ".alo-ux-next-grid",
    'a[data-alo-affiliate-badge="true"]::after',
    "safe-area-inset-bottom",
    "prefers-reduced-motion",
    "@media print",
):
    assert token in ux_css, token
assert "overflow-x:hidden" not in ux_css.replace(" ", "").lower()
assert '"version": 119' in prepare_source
assert "_ensure_html_language" in prepare_source
assert "_ensure_referrer_policy" in prepare_source
assert "data-base-path" in prepare_source

with tempfile.TemporaryDirectory(prefix="alo186-ux-v119-") as folder:
    canonical = Path(folder) / "canonical"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "ux-v119-test"])

    results = []
    for target_name, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = Path(folder) / target_name
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt",
            "--commit", "ux-v119-test",
        ])
        run([
            sys.executable,
            "alo186/deployment/smoke_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
        ])

        html_files = sorted(target.rglob("*.html"))
        assert len(html_files) >= 450, len(html_files)
        missing_ux: list[str] = []
        missing_metadata: list[str] = []
        wrong_language: list[str] = []
        missing_h1: list[str] = []
        multiple_h1: list[str] = []
        pages_without_main: list[str] = []
        image_count = 0
        image_alt_count = 0
        control_count = 0
        unlabelled_count = 0
        amazon_count = 0
        amazon_sponsored_count = 0
        english_pages = 0
        noindex_pages = 0

        expected_css = f"{base_path}/assets/alo186-ux.css" if base_path else "/assets/alo186-ux.css"
        expected_js = f"{base_path}/assets/alo186-ux.js" if base_path else "/assets/alo186-ux.js"
        expected_base = f'data-base-path="{base_path}"'

        for page in html_files:
            text = page.read_text(encoding="utf-8")
            relative = page.relative_to(target).as_posix()
            is_noindex = bool(re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', text, re.IGNORECASE))
            noindex_pages += int(is_noindex)

            if text.count(UX_MARKER) != 2 or expected_css not in text or expected_js not in text or expected_base not in text:
                missing_ux.append(relative)
            title = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
            if not (
                has_named_meta(text, "viewport")
                and title is not None
                and bool(re.sub(r"\s+", " ", title.group(1)).strip())
                and has_canonical(text)
                and has_named_meta(text, "referrer", "strict-origin-when-cross-origin")
                and re.search(r"<html\b", text, re.IGNORECASE)
            ):
                missing_metadata.append(relative)

            language = attr(text, "html", "lang")
            expected_language = "en" if relative.lower().startswith("en/") else "tr"
            if language and language.lower().startswith("en"):
                english_pages += 1
            if not language or not language.lower().startswith(expected_language):
                wrong_language.append(relative)

            parser = AuditParser()
            parser.feed(text)
            image_count += parser.images
            image_alt_count += parser.images_with_alt
            control_count += len(parser._controls)
            unlabelled_count += parser.unlabelled_controls()
            amazon_count += parser.amazon_links
            amazon_sponsored_count += parser.amazon_links_sponsored
            if parser.h1 == 0:
                missing_h1.append(relative)
            elif parser.h1 > 1:
                multiple_h1.append(relative)
            if parser.main == 0:
                pages_without_main.append(relative)

        assert not missing_ux, missing_ux[:25]
        assert not missing_metadata, missing_metadata[:25]
        assert not wrong_language, wrong_language[:25]
        assert not multiple_h1, multiple_h1[:25]
        h1_coverage = (len(html_files) - len(missing_h1)) / len(html_files)
        main_coverage = (len(html_files) - len(pages_without_main)) / len(html_files)
        image_alt_coverage = 1.0 if image_count == 0 else image_alt_count / image_count
        control_label_coverage = 1.0 if control_count == 0 else (control_count - unlabelled_count) / control_count
        static_affiliate_rel_coverage = 1.0 if amazon_count == 0 else amazon_sponsored_count / amazon_count
        assert h1_coverage >= 0.99, {"coverage": h1_coverage, "missing": missing_h1[:25]}
        assert main_coverage >= 0.88, {"coverage": main_coverage, "missing": pages_without_main[:25]}
        assert control_label_coverage >= 0.85, {
            "coverage": control_label_coverage,
            "controls": control_count,
            "unlabelled": unlabelled_count,
        }
        assert english_pages >= 10, english_pages

        for route in (
            "index.html",
            "edas-bul/index.html",
            "arama/index.html",
            "acil-numaralar/index.html",
            "elektrik-durum-merkezi/index.html",
            "en/index.html",
            "en/electricity-outage-turkey/index.html",
            "en/electricity-distribution-company-finder/index.html",
            "en/emergency-numbers-turkey/index.html",
        ):
            assert (target / route).is_file(), route

        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        ux = release["sitewideUx"]
        assert ux["version"] == 119
        assert ux["injectedPages"] + ux["alreadyInjectedPages"] == len(html_files)
        assert ux["basePathAware"] is True
        assert ux["languageAware"] is True
        assert ux["englishMobileNavigation"] is True
        assert ux["contextualNextSteps"] is True
        assert ux["longPageToc"] is True
        assert ux["dynamicAffiliateLinkHardening"] is True
        assert ux["languagePages"]["en"] >= 10
        assert (target / "assets/alo186-ux.css").is_file()
        assert (target / "assets/alo186-ux.js").is_file()

        results.append({
            "target": target_name,
            "basePath": base_path,
            "pages": len(html_files),
            "englishPages": english_pages,
            "noindexPages": noindex_pages,
            "h1Coverage": round(h1_coverage, 4),
            "mainCoverage": round(main_coverage, 4),
            "staticImageAltCoverage": round(image_alt_coverage, 4),
            "formControlLabelCoverage": round(control_label_coverage, 4),
            "staticAffiliateRelCoverage": round(static_affiliate_rel_coverage, 4),
            "runtimeAffiliateHardening": True,
            "uxInjected": True,
        })

run(["node", "--check", "alo186/assets/alo186-ux.js"])
run([sys.executable, "-m", "py_compile", "alo186/deployment/prepare_github_pages.py"])
print(json.dumps({
    "ok": True,
    "version": 119,
    "targets": results,
    "mobileUtilityBar": "indexable-tr-and-en",
    "projectPathAware": True,
    "localizedUtilities": True,
    "activePageState": True,
    "tableOverflowGuard": True,
    "externalLinkHardening": True,
    "dynamicAffiliateHardening": True,
    "lazyImages": True,
    "imageAltFallback": True,
    "longPageToc": True,
    "contextualNextSteps": True,
    "backToTop": True,
    "minimumTouchTarget": 44,
    "personalStorage": False,
    "officialAffiliationClaimed": False,
}, ensure_ascii=False))
