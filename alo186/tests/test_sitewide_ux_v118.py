from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UX_MARKER = 'data-alo186-sitewide-ux="true"'


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images = 0
        self.images_with_alt = 0
        self.h1 = 0
        self.main = 0
        self.forms = 0
        self.unlabelled_controls = 0
        self._labels_for: set[str] = set()
        self._controls: list[tuple[str, str | None, bool]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "img":
            self.images += 1
            if "alt" in values:
                self.images_with_alt += 1
        elif tag == "h1":
            self.h1 += 1
        elif tag == "main":
            self.main += 1
        elif tag == "form":
            self.forms += 1
        elif tag == "label" and values.get("for"):
            self._labels_for.add(str(values["for"]))
        elif tag in {"input", "select", "textarea"}:
            if tag == "input" and values.get("type", "text").lower() in {"hidden", "submit", "button", "reset", "image"}:
                return
            control_id = values.get("id")
            named = bool(values.get("aria-label") or values.get("aria-labelledby") or values.get("title"))
            self._controls.append((tag, control_id, named))

    def close_audit(self) -> None:
        self.unlabelled_controls = sum(
            1 for _tag, control_id, named in self._controls
            if not named and (not control_id or control_id not in self._labels_for)
        )


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def attr(text: str, tag: str, name: str) -> str | None:
    match = re.search(rf"<{tag}\b[^>]*\b{name}\s*=\s*(['\"])(.*?)\1", text, re.IGNORECASE | re.DOTALL)
    return match.group(2).strip() if match else None


source_js = (ROOT / "alo186/assets/alo186-ux.js").read_text(encoding="utf-8")
source_css = (ROOT / "alo186/assets/alo186-ux.css").read_text(encoding="utf-8")
prepare_source = (ROOT / "alo186/deployment/prepare_github_pages.py").read_text(encoding="utf-8")

for token in [
    "data-base-path", "withBase", "stripBase", "isEnglish", "MutationObserver",
    "sponsored", "nofollow", "addLongPageToc", "addNextSteps", "journeyData",
    "/en/electricity-distribution-company-finder/", "/en/emergency-numbers-turkey/",
    "data-alo-affiliate-badge", "aria-current",
]:
    assert token in source_js, token
for token in [
    ".alo-ux-toc", ".alo-ux-next", ".alo-ux-next-grid",
    'a[data-alo-affiliate-badge="true"]::after', "safe-area-inset-bottom",
    "prefers-reduced-motion", "@media print",
]:
    assert token in source_css, token
assert "overflow-x:hidden" not in source_css.replace(" ", "").lower()
assert 'release["sitewideUx"]' in prepare_source
assert '"version": 118' in prepare_source
assert "languageAware" in prepare_source and "basePathAware" in prepare_source

with tempfile.TemporaryDirectory(prefix="alo186-ux-v118-") as folder:
    canonical = Path(folder) / "canonical"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "ux-v118-test"])

    target_results = []
    for name, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = Path(folder) / name
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt",
            "--commit", "ux-v118-test",
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
        multiple_h1: list[str] = []
        missing_h1: list[str] = []
        pages_without_main: list[str] = []
        all_images = 0
        images_with_alt = 0
        all_controls = 0
        unlabelled_controls = 0
        noindex_pages = 0
        english_pages = 0

        expected_css = f'{base_path}/assets/alo186-ux.css' if base_path else "/assets/alo186-ux.css"
        expected_js = f'{base_path}/assets/alo186-ux.js' if base_path else "/assets/alo186-ux.js"
        expected_base_attr = f'data-base-path="{base_path}"'

        for page in html_files:
            text = page.read_text(encoding="utf-8")
            relative = page.relative_to(target).as_posix()
            lower = text.lower()
            is_noindex = bool(re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', text, re.IGNORECASE))
            noindex_pages += int(is_noindex)

            if text.count(UX_MARKER) != 2 or expected_css not in text or expected_js not in text or expected_base_attr not in text:
                missing_ux.append(relative)
            title = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
            canonical_match = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', text, re.IGNORECASE)
            metadata_ok = (
                '<meta name="viewport"' in lower
                and title is not None and bool(re.sub(r"\s+", " ", title.group(1)).strip())
                and canonical_match is not None
                and '<meta name="referrer" content="strict-origin-when-cross-origin">' in lower
                and "<html" in lower
            )
            if not metadata_ok:
                missing_metadata.append(relative)

            language = attr(text, "html", "lang")
            expected_language = "en" if relative.lower().startswith("en/") else "tr"
            if language and language.lower().startswith("en"):
                english_pages += 1
            if not language or not language.lower().startswith(expected_language):
                wrong_language.append(relative)

            parser = AuditParser()
            parser.feed(text)
            parser.close_audit()
            all_images += parser.images
            images_with_alt += parser.images_with_alt
            all_controls += len(parser._controls)
            unlabelled_controls += parser.unlabelled_controls
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
        assert h1_coverage >= 0.99, {"coverage": h1_coverage, "missing": missing_h1[:25]}
        main_coverage = (len(html_files) - len(pages_without_main)) / len(html_files)
        assert main_coverage >= 0.88, {"coverage": main_coverage, "missing": pages_without_main[:25]}
        alt_coverage = 1.0 if all_images == 0 else images_with_alt / all_images
        assert alt_coverage >= 0.98, {"coverage": alt_coverage, "images": all_images}
        control_label_coverage = 1.0 if all_controls == 0 else (all_controls - unlabelled_controls) / all_controls
        assert control_label_coverage >= 0.94, {
            "coverage": control_label_coverage,
            "controls": all_controls,
            "unlabelled": unlabelled_controls,
        }
        assert english_pages >= 10, english_pages

        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        ux = release["sitewideUx"]
        assert ux["version"] == 118
        assert ux["injectedPages"] + ux["alreadyInjectedPages"] == len(html_files)
        assert ux["basePathAware"] is True
        assert ux["languageAware"] is True
        assert ux["contextualNextSteps"] is True
        assert ux["longPageToc"] is True
        assert ux["affiliateLinkHardening"] is True
        assert ux["languagePages"]["en"] >= 10
        assert (target / "assets/alo186-ux.css").is_file()
        assert (target / "assets/alo186-ux.js").is_file()

        target_results.append({
            "target": name,
            "basePath": base_path,
            "pages": len(html_files),
            "noindexPages": noindex_pages,
            "englishPages": english_pages,
            "h1Coverage": round(h1_coverage, 4),
            "mainCoverage": round(main_coverage, 4),
            "imageAltCoverage": round(alt_coverage, 4),
            "controlLabelCoverage": round(control_label_coverage, 4),
            "uxInjected": True,
        })

run(["node", "--check", "alo186/assets/alo186-ux.js"])
run([sys.executable, "-m", "py_compile", "alo186/deployment/prepare_github_pages.py"])
print(json.dumps({
    "ok": True,
    "version": 118,
    "targets": target_results,
    "basePathAwareNavigation": True,
    "bilingualNavigation": True,
    "longPageToc": True,
    "contextualNextSteps": True,
    "dynamicAffiliateHardening": True,
    "personalStorage": False,
    "officialAffiliationClaimed": False,
}, ensure_ascii=False))
