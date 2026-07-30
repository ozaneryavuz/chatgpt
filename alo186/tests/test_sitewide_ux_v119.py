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


class PageAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images = 0
        self.images_with_alt = 0
        self.h1 = 0
        self.main = 0
        self.label_depth = 0
        self.labels_for: set[str] = set()
        self.controls: list[tuple[str | None, bool]] = []
        self.amazon = 0
        self.amazon_sponsored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "label":
            self.label_depth += 1
            if values.get("for"):
                self.labels_for.add(str(values["for"]))
            return
        if tag == "img":
            self.images += 1
            self.images_with_alt += int("alt" in values)
        elif tag == "h1":
            self.h1 += 1
        elif tag == "main":
            self.main += 1
        elif tag in {"input", "select", "textarea"}:
            if tag == "input" and values.get("type", "text").lower() in {"hidden", "submit", "button", "reset", "image"}:
                return
            named = bool(self.label_depth or values.get("aria-label") or values.get("aria-labelledby") or values.get("title"))
            self.controls.append((values.get("id"), named))
        elif tag == "a" and values.get("href"):
            host = (urlparse(str(values["href"])).hostname or "").lower().removeprefix("www.")
            if host == "amazon.com.tr" or host.endswith(".amazon.com.tr") or host == "amzn.to":
                self.amazon += 1
                rel = set((values.get("rel") or "").split())
                self.amazon_sponsored += int({"sponsored", "nofollow", "noopener"} <= rel)

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self.label_depth:
            self.label_depth -= 1

    @property
    def unlabelled(self) -> int:
        return sum(1 for control_id, named in self.controls if not named and (not control_id or control_id not in self.labels_for))


def run(*command: str) -> None:
    subprocess.run(list(command), cwd=ROOT, check=True)


def attribute(text: str, tag: str, name: str) -> str | None:
    match = re.search(rf"<{tag}\b[^>]*\b{name}\s*=\s*(['\"])(.*?)\1", text, re.I | re.S)
    return match.group(2).strip() if match else None


def named_meta(text: str, name: str, content: str | None = None) -> bool:
    for tag in re.findall(r"<meta\b[^>]*>", text, re.I):
        if not re.search(rf"\bname\s*=\s*(['\"]){re.escape(name)}\1", tag, re.I):
            continue
        if content is None or re.search(rf"\bcontent\s*=\s*(['\"]){re.escape(content)}\1", tag, re.I):
            return True
    return False


def canonical_present(text: str) -> bool:
    return any(
        re.search(r"\brel\s*=\s*(['\"])(.*?)\1", tag, re.I)
        and "canonical" in re.search(r"\brel\s*=\s*(['\"])(.*?)\1", tag, re.I).group(2).lower().split()
        and re.search(r"\bhref\s*=", tag, re.I)
        for tag in re.findall(r"<link\b[^>]*>", text, re.I)
    )


ux_js = (ROOT / "alo186/assets/alo186-ux.js").read_text(encoding="utf-8")
ux_css = (ROOT / "alo186/assets/alo186-ux.css").read_text(encoding="utf-8")
prepare_source = (ROOT / "alo186/deployment/prepare_github_pages.py").read_text(encoding="utf-8")

for token in (
    "const isEnglish",
    "/en/electricity-distribution-company-finder/",
    "/en/emergency-numbers-turkey/",
    "MutationObserver",
    "sponsored",
    "nofollow",
    "aloAffiliateBadge",
    "alo-ux-toc",
    "alo186AltFallback",
    "journeyData",
    "addNextSteps",
    "alo186NextSteps",
    "Mevcut ürünün yeterli olup olmadığını önce kontrol edin",
):
    assert token in ux_js, token
for token in (
    'body:not([data-alo186-ux-compact="true"])',
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
for token in ('"version": 119', "_ensure_html_language", "_ensure_referrer_policy", "data-base-path"):
    assert token in prepare_source, token

with tempfile.TemporaryDirectory(prefix="alo186-ux-v119-") as folder:
    canonical = Path(folder) / "canonical"
    run(sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "ux-v119-test")
    results = []

    for target_name, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = Path(folder) / target_name
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run(
            sys.executable, "alo186/deployment/prepare_github_pages.py",
            "--site", str(target), "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt", "--commit", "ux-v119-test",
        )
        run(sys.executable, "alo186/deployment/smoke_github_pages.py", "--site", str(target), "--base-path", base_path)

        pages = sorted(target.rglob("*.html"))
        assert len(pages) >= 450
        missing_ux: list[str] = []
        missing_metadata: list[str] = []
        wrong_language: list[str] = []
        missing_h1: list[str] = []
        multiple_h1: list[str] = []
        missing_main: list[str] = []
        images = alt_images = controls = unlabelled = amazon = amazon_sponsored = english = noindex = 0
        css_url = f"{base_path}/assets/alo186-ux.css" if base_path else "/assets/alo186-ux.css"
        js_url = f"{base_path}/assets/alo186-ux.js" if base_path else "/assets/alo186-ux.js"
        base_marker = f'data-base-path="{base_path}"'

        for page in pages:
            text = page.read_text(encoding="utf-8")
            relative = page.relative_to(target).as_posix()
            noindex += int(bool(re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', text, re.I)))
            if text.count(UX_MARKER) != 2 or css_url not in text or js_url not in text or base_marker not in text:
                missing_ux.append(relative)
            title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
            if not (
                named_meta(text, "viewport")
                and title and re.sub(r"\s+", " ", title.group(1)).strip()
                and canonical_present(text)
                and named_meta(text, "referrer", "strict-origin-when-cross-origin")
            ):
                missing_metadata.append(relative)
            lang = attribute(text, "html", "lang")
            expected = "en" if relative.lower().startswith("en/") else "tr"
            english += int(bool(lang and lang.lower().startswith("en")))
            if not lang or not lang.lower().startswith(expected):
                wrong_language.append(relative)

            audit = PageAudit()
            audit.feed(text)
            images += audit.images
            alt_images += audit.images_with_alt
            controls += len(audit.controls)
            unlabelled += audit.unlabelled
            amazon += audit.amazon
            amazon_sponsored += audit.amazon_sponsored
            if audit.h1 == 0:
                missing_h1.append(relative)
            elif audit.h1 > 1:
                multiple_h1.append(relative)
            if audit.main == 0:
                missing_main.append(relative)

        assert not missing_ux, missing_ux[:20]
        assert not missing_metadata, missing_metadata[:20]
        assert not wrong_language, wrong_language[:20]
        assert not multiple_h1, multiple_h1[:20]
        h1_coverage = (len(pages) - len(missing_h1)) / len(pages)
        main_coverage = (len(pages) - len(missing_main)) / len(pages)
        form_coverage = 1.0 if not controls else (controls - unlabelled) / controls
        assert h1_coverage >= .99, {"coverage": h1_coverage, "missing": missing_h1[:20]}
        assert main_coverage >= .88, {"coverage": main_coverage, "missing": missing_main[:20]}
        assert form_coverage >= .85, {"coverage": form_coverage, "controls": controls, "unlabelled": unlabelled}
        assert english >= 10

        for route in (
            "index.html", "edas-bul/index.html", "arama/index.html", "acil-numaralar/index.html",
            "elektrik-durum-merkezi/index.html", "en/index.html",
            "en/electricity-outage-turkey/index.html",
            "en/electricity-distribution-company-finder/index.html",
            "en/emergency-numbers-turkey/index.html",
        ):
            assert (target / route).is_file(), route

        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        ux = release["sitewideUx"]
        assert ux["version"] == 119
        assert ux["injectedPages"] + ux["alreadyInjectedPages"] == len(pages)
        for key in (
            "basePathAware", "languageAware", "englishMobileNavigation",
            "contextualNextSteps", "longPageToc", "dynamicAffiliateLinkHardening",
        ):
            assert ux[key] is True, key
        assert ux["languagePages"]["en"] >= 10

        results.append({
            "target": target_name,
            "basePath": base_path,
            "pages": len(pages),
            "englishPages": english,
            "noindexPages": noindex,
            "h1Coverage": round(h1_coverage, 4),
            "mainCoverage": round(main_coverage, 4),
            "staticImageAltCoverage": round(1.0 if not images else alt_images / images, 4),
            "formControlLabelCoverage": round(form_coverage, 4),
            "staticAffiliateRelCoverage": round(1.0 if not amazon else amazon_sponsored / amazon, 4),
            "runtimeAffiliateHardening": True,
        })

run("node", "--check", "alo186/assets/alo186-ux.js")
run(sys.executable, "-m", "py_compile", "alo186/deployment/prepare_github_pages.py")
print(json.dumps({
    "ok": True,
    "version": 119,
    "targets": results,
    "mobileUtilityBar": "indexable-tr-and-en",
    "projectPathAware": True,
    "contextualNextSteps": True,
    "dynamicAffiliateHardening": True,
    "personalStorage": False,
    "officialAffiliationClaimed": False,
}, ensure_ascii=False))
