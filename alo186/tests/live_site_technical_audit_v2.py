from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from live_site_technical_audit import Audit as BaseAudit
from live_site_technical_audit import DEFAULT_OUTPUT, DEVICES, KEY_ROUTES

PERSONAL_TYPES = {"email", "tel"}
PERSONAL_AUTOCOMPLETE = {"name", "given-name", "family-name", "email", "tel", "street-address", "address-line1", "address-line2", "postal-code"}
PUBLIC_TRUST_ROUTES = ("/", "/elektrik-portali", "/elektrik-kesintisi", "/dagitim-sirketleri")
DEADLINE_ROUTES = ("/elektrik-portali", "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu")


class Audit(BaseAudit):
    def audit_public_trust_and_deadline(self, preferred: str) -> None:
        for route in PUBLIC_TRUST_ROUTES:
            url = urljoin(preferred + "/", route.lstrip("/"))
            response = self.request(url)
            if response is None or response.status_code != 200:
                continue
            soup = BeautifulSoup(response.text, "lxml")
            text = soup.get_text(" ", strip=True)
            normalized = text.casefold()
            has_independent = "bağımsız" in normalized
            has_not_official = ("edaş veya kamu kurumu değildir" in normalized or "kamu kurumu değildir" in normalized)
            if not (has_independent and has_not_official):
                self.add("P1", "trust-disclosure", "Bağımsızlık ve resmî kurum olmadığı açıklaması birlikte görünmüyor.", url=url)
            risky_fields = []
            for field in soup.select("input,textarea,select"):
                field_type = str(field.get("type", "")).casefold()
                autocomplete = str(field.get("autocomplete", "")).casefold()
                name = str(field.get("name", "")).casefold()
                if field_type in PERSONAL_TYPES or autocomplete in PERSONAL_AUTOCOMPLETE or name in {"email", "telefon", "phone", "adres", "address", "tc", "kimlik", "abone_no", "subscriber"}:
                    risky_fields.append({"tag": field.name, "type": field_type, "name": name, "autocomplete": autocomplete})
            if risky_fields:
                self.add("P0", "privacy", "Kamu yararı/karar sayfasında kişisel veri girişi bulundu.", url=url, fields=risky_fields)

        for route in DEADLINE_ROUTES:
            url = urljoin(preferred + "/", route.lstrip("/"))
            response = self.request(url)
            if response is None or response.status_code != 200:
                continue
            text = BeautifulSoup(response.text, "lxml").get_text(" ", strip=True)
            if re.search(r"cihaz\s+hasar", text, re.IGNORECASE) and re.search(r"\b30\s*(?:takvim\s*)?gün\b", text, re.IGNORECASE):
                self.add("P0", "device-damage-deadline", "Canlı sayfa cihaz hasarı başvurusu için eski 30 gün ifadesini yayımlıyor; güncel 10 iş günü korumasıyla çelişiyor.", url=url)
            if "10 iş günü" not in text.casefold():
                self.add("P1", "device-damage-deadline", "Cihaz hasarı sayfasında görünür 10 iş günü uyarısı bulunmuyor.", url=url)

    def audit_accessibility_details(self, preferred: str) -> None:
        axe_path = Path("node_modules/axe-core/axe.min.js")
        if not axe_path.is_file():
            return
        axe_source = axe_path.read_text(encoding="utf-8")
        targets = ("/elektrik-portali", "/amazon-elektrik-urunleri")
        details: list[dict[str, Any]] = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
            for route in targets:
                for device_name, settings in DEVICES.items():
                    context = browser.new_context(**settings, locale="tr-TR", reduced_motion="reduce")
                    page = context.new_page()
                    url = urljoin(preferred + "/", route.lstrip("/"))
                    response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    if response and response.status == 200:
                        page.add_script_tag(content=axe_source)
                        result = page.evaluate("""async () => await axe.run(document,{runOnly:{type:'rule',values:['color-contrast']},resultTypes:['violations']})""")
                        for violation in result.get("violations", []):
                            details.append({
                                "url": url,
                                "device": device_name,
                                "id": violation.get("id"),
                                "impact": violation.get("impact"),
                                "nodes": [
                                    {
                                        "target": node.get("target"),
                                        "html": node.get("html", "")[:500],
                                        "failureSummary": node.get("failureSummary", "")[:800],
                                    }
                                    for node in violation.get("nodes", [])[:25]
                                ],
                            })
                    context.close()
            browser.close()
        self.results["accessibilityDetails"] = details
        for finding in self.findings:
            if finding.check != "accessibility":
                continue
            matches = [item for item in details if item["url"] == finding.url and item["device"] == finding.device]
            if matches:
                finding.evidence["nodeDetails"] = matches

    def normalize_findings(self) -> None:
        bad_browser_pairs = {
            (item.url, item.device)
            for item in self.findings
            if item.check == "browser-navigation" and "HTTP 404" in item.message
        }
        cleaned = []
        for item in self.findings:
            if item.check == "trust":
                continue
            if item.check == "privacy":
                fields = item.evidence.get("fields", [])
                if fields and all(str(field).casefold().startswith("search ") for field in fields):
                    continue
            if item.check in {"mobile-overflow", "layout-overflow"}:
                viewport = item.evidence.get("viewport", {})
                if int(item.evidence.get("scrollWidth", 0)) <= int(viewport.get("w", 0)) + 2:
                    continue
            if (item.url, item.device) in bad_browser_pairs and item.check != "browser-navigation":
                continue
            if item.check == "text-clipping":
                samples = item.evidence.get("sample", [])
                visible = [sample for sample in samples if "sr-only" not in str(sample.get("class", "")).split() and sample.get("tag") not in {"THEAD", "TR"}]
                if not visible:
                    continue
                item.evidence["sample"] = visible
                item.message = f"{len(visible)} görünür metin alanında kırpılma sinyali bulundu."
            cleaned.append(item)
        self.findings = cleaned

    def run(self) -> int:
        preferred = self.audit_origins()
        self.audit_robots(preferred)
        self.audit_sitemap(preferred)
        self.audit_internal_links(preferred)
        self.audit_browser(preferred)
        self.audit_public_trust_and_deadline(preferred)
        self.audit_accessibility_details(preferred)
        self.audit_pagespeed(preferred)
        self.normalize_findings()
        return self.write_reports(preferred)


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı teknik kalite denetimi v2")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    sys.exit(Audit(args.output).run())


if __name__ == "__main__":
    main()
