from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, text: str) -> None:
    (ROOT / relative).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def migrate_builder() -> None:
    path = "alo186/deployment/build_static_site_core.py"
    text = read(path)
    text = replace_once(
        text,
        'CANONICAL_HOST = "https://www.alo186.com"\nLEGACY_HOST = "https://alo186.com"',
        'CANONICAL_HOST = "https://alo186.com"\nLEGACY_HOST = "https://www.alo186.com"',
        "builder host constants",
    )
    text = replace_once(
        text,
        '"RewriteRule ^ https://www.alo186.com%{REQUEST_URI}",',
        '"RewriteRule ^ https://alo186.com%{REQUEST_URI}",',
        "builder Apache token",
    )
    text = text.replace("Eski apex origin artifact'ta kaldı", "Eski www origin artifact'ta kaldı")
    text = text.replace(
        "robots.txt www canonical sitemap adresini taşımıyor",
        "robots.txt apex canonical sitemap adresini taşımıyor",
    )
    text = text.replace(
        "sitemap.xml www canonical origin taşımıyor",
        "sitemap.xml apex canonical origin taşımıyor",
    )
    text = text.replace(
        "sitemap.xml eski apex origin taşıyor",
        "sitemap.xml eski www origin taşıyor",
    )
    write(path, text)

    path = "alo186/deployment/build_static_site.py"
    text = read(path)
    text = replace_once(
        text,
        "https://www.alo186.com\nhttps://alo186.com\n'''",
        "https://alo186.com\nhttps://www.alo186.com\n'''",
        "builder wrapper source contract",
    )
    write(path, text)


def migrate_manifest_and_apache() -> None:
    path = "alo186/deployment/routing-manifest.json"
    text = read(path)
    text = replace_once(
        text,
        '"canonicalHost":"https://www.alo186.com"',
        '"canonicalHost":"https://alo186.com"',
        "routing manifest canonicalHost",
    )
    write(path, text)

    path = "alo186/deployment/apache-production.htaccess"
    text = read(path)
    old = """# Tek canonical host: kök alan adındaki aynı path ve query tek yönlendirmeyle www'ye gider.
RewriteCond %{HTTP_HOST} !^www\\.alo186\\.com$ [NC]
RewriteRule ^ https://www.alo186.com%{REQUEST_URI} [R=301,L,NE]

# www host üzerindeki doğrudan HTTP isteğini HTTPS'e taşı. CDN/proxy
# X-Forwarded-Proto gönderiyorsa HTTPS isteğinde yönlendirme döngüsü oluşmaz.
RewriteCond %{HTTPS} !=on
RewriteCond %{HTTP:X-Forwarded-Proto} !https [NC]
RewriteRule ^ https://www.alo186.com%{REQUEST_URI} [R=301,L,NE]

# Eski/canlı uygulama manifesti apex origin ile çağırsa da canonical www üzerinde
# aynı dosya ve doğru MIME türü sunulur. Dosya hesaplama rotasıyla artifact'a girer."""
    new = """# Tek canonical host: www veya başka bir Host aynı path ve query ile apex'e gider.
RewriteCond %{HTTP_HOST} !^alo186\\.com$ [NC]
RewriteRule ^ https://alo186.com%{REQUEST_URI} [R=301,L,NE]

# Apex host üzerindeki doğrudan HTTP isteğini HTTPS'e taşı. CDN/proxy
# X-Forwarded-Proto gönderiyorsa HTTPS isteğinde yönlendirme döngüsü oluşmaz.
RewriteCond %{HTTPS} !=on
RewriteCond %{HTTP:X-Forwarded-Proto} !https [NC]
RewriteRule ^ https://alo186.com%{REQUEST_URI} [R=301,L,NE]

# Eski/canlı uygulama manifesti www origin ile çağırsa da canonical apex üzerinde
# aynı dosya ve doğru MIME türü sunulur. Dosya hesaplama rotasıyla artifact'a girer."""
    text = replace_once(text, old, new, "Apache redirect block")
    text = replace_once(
        text,
        'Header always set Access-Control-Allow-Origin "https://www.alo186.com"',
        'Header always set Access-Control-Allow-Origin "https://alo186.com"',
        "manifest CORS origin",
    )
    write(path, text)


def migrate_static_smoke() -> None:
    path = "alo186/deployment/smoke_static_site.py"
    text = read(path)
    text = replace_once(
        text,
        'CANONICAL_HOST = "https://www.alo186.com"\nLEGACY_HOST = "https://alo186.com"',
        'CANONICAL_HOST = "https://alo186.com"\nLEGACY_HOST = "https://www.alo186.com"',
        "static smoke host constants",
    )
    text = replace_once(
        text,
        '"RewriteRule ^ https://www.alo186.com%{REQUEST_URI}",',
        '"RewriteRule ^ https://alo186.com%{REQUEST_URI}",',
        "static smoke Apache token",
    )
    text = text.replace(
        "Eski apex origin route HTML içinde kaldı",
        "Eski www origin route HTML içinde kaldı",
    )
    write(path, text)


def migrate_live_smoke() -> None:
    path = "alo186/deployment/smoke_live_routes.py"
    text = read(path)
    text = replace_once(
        text,
        'CANONICAL_HOST = "https://www.alo186.com"',
        'CANONICAL_HOST = "https://alo186.com"\nLEGACY_HOST = "https://www.alo186.com"',
        "live smoke host constants",
    )
    text = text.replace('"https://www.alo186.com/', '"https://alo186.com/')

    old = '''    # Apex URL'nin aynı path ile tek canonical www hostuna ulaşmasını doğrula.
    apex_url = base_url.replace("://www.", "://", 1) + "/"
    try:
        status, final_url, _body, _headers, duration = fetch(apex_url)
        results.append(
            {
                "path": "apex-redirect",
                "status": status,
                "requestedUrl": apex_url,
                "finalUrl": final_url,
                "durationMs": round(duration * 1000, 1),
            }
        )
        if status != 200 or normalize_url(final_url) != normalize_url(f"{CANONICAL_HOST}/"):
            failures.append(f"Apex canonical yönlendirme yanlış: {apex_url} → {final_url} (HTTP {status})")
    except (HTTPError, URLError, TimeoutError, ssl.SSLError) as exc:
        failures.append(f"Apex canonical yönlendirme erişim hatası: {exc}")'''
    new = '''    # www URL'nin aynı path ile tek canonical apex hostuna ulaşmasını doğrula.
    www_url = LEGACY_HOST + "/"
    try:
        status, final_url, _body, _headers, duration = fetch(www_url)
        results.append(
            {
                "path": "www-redirect",
                "status": status,
                "requestedUrl": www_url,
                "finalUrl": final_url,
                "durationMs": round(duration * 1000, 1),
            }
        )
        if status != 200 or normalize_url(final_url) != normalize_url(f"{CANONICAL_HOST}/"):
            failures.append(f"www canonical yönlendirme yanlış: {www_url} → {final_url} (HTTP {status})")
    except (HTTPError, URLError, TimeoutError, ssl.SSLError) as exc:
        failures.append(f"www canonical yönlendirme erişim hatası: {exc}")'''
    text = replace_once(text, old, new, "live redirect probe")
    text = replace_once(
        text,
        '            if normalize_url(final_url).startswith("https://alo186.com"):\n'
        '                failures.append(f"{path}: www olmayan final URL: {final_url}")',
        '            if normalize_url(final_url).startswith(LEGACY_HOST):\n'
        '                failures.append(f"{path}: canonical olmayan www final URL: {final_url}")',
        "live final URL guard",
    )
    text = replace_once(
        text,
        '            if root_path == "/sitemap.xml" and "https://alo186.com" in body.decode("utf-8", errors="replace"):\n'
        '                failures.append("/sitemap.xml: eski apex origin içeriyor")',
        '            if root_path == "/sitemap.xml" and LEGACY_HOST in body.decode("utf-8", errors="replace"):\n'
        '                failures.append("/sitemap.xml: eski www origin içeriyor")',
        "live sitemap legacy guard",
    )
    write(path, text)


def migrate_existing_contract() -> None:
    path = "alo186/tests/test_active_production_contract.py"
    text = read(path)
    old = '''    # Canonical host policy is www everywhere and live smoke verifies apex redirect.
    assert "https://www.alo186.com" in apache
    assert "https://www.alo186.com" in builder
    assert "apex-redirect" in live_smoke
    assert "https://alo186.com" in builder'''
    new = '''    # Canonical host policy is apex everywhere and live smoke verifies www redirect.
    assert "https://alo186.com" in apache
    assert "https://alo186.com" in builder
    assert "www-redirect" in live_smoke
    assert "https://www.alo186.com" in builder'''
    text = replace_once(text, old, new, "active production canonical contract")
    write(path, text)


def write_regression() -> None:
    path = ROOT / "alo186/tests/test_apex_canonical_contract_v203.py"
    path.write_text(
        '''from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186" / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

import build_static_site  # noqa: E402
import smoke_live_routes  # noqa: E402
import smoke_static_site  # noqa: E402


CANONICAL = "https://alo186.com"
LEGACY = "https://www.alo186.com"


def test_source_contract_uses_apex_and_redirects_www() -> None:
    manifest = json.loads((DEPLOYMENT / "routing-manifest.json").read_text(encoding="utf-8"))
    apache = (DEPLOYMENT / "apache-production.htaccess").read_text(encoding="utf-8")

    assert manifest["canonicalHost"] == CANONICAL
    assert build_static_site.CANONICAL_HOST == CANONICAL
    assert build_static_site.LEGACY_HOST == LEGACY
    assert smoke_static_site.CANONICAL_HOST == CANONICAL
    assert smoke_static_site.LEGACY_HOST == LEGACY
    assert smoke_live_routes.CANONICAL_HOST == CANONICAL
    assert smoke_live_routes.LEGACY_HOST == LEGACY
    assert "RewriteCond %{HTTP_HOST} !^alo186\\\\.com$ [NC]" in apache
    assert "RewriteRule ^ https://alo186.com%{REQUEST_URI} [R=301,L,NE]" in apache
    assert "RewriteRule ^ https://www.alo186.com%{REQUEST_URI}" not in apache
    assert 'Access-Control-Allow-Origin "https://alo186.com"' in apache


def test_full_production_bundle_contains_only_apex_canonicals(tmp_path: Path) -> None:
    output = tmp_path / "site"
    release = build_static_site.build(ROOT, output, "apex-contract-test")
    smoke = smoke_static_site.smoke(output, ROOT)

    assert release["canonicalHost"] == CANONICAL
    assert smoke["ok"] is True
    assert f"Sitemap: {CANONICAL}/sitemap.xml" in (output / "robots.txt").read_text(encoding="utf-8")
    assert LEGACY not in (output / "sitemap.xml").read_text(encoding="utf-8")

    leaked: list[str] = []
    for candidate in output.rglob("*"):
        if not candidate.is_file() or candidate.name == "checksums.sha256":
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY in text:
            leaked.append(candidate.relative_to(output).as_posix())
    assert leaked == []


def test_live_smoke_probes_www_then_accepts_apex(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_fetch(url: str, timeout: int = 20):
        calls.append(url)
        if url == LEGACY + "/":
            return 200, CANONICAL + "/", b"", {}, 0.01
        if url.endswith("/robots.txt"):
            body = f"Sitemap: {CANONICAL}/sitemap.xml".encode()
            return 200, url.replace(LEGACY, CANONICAL), body, {"content-type": "text/plain"}, 0.01
        if url.endswith("/sitemap.xml"):
            body = f"<loc>{CANONICAL}/</loc>".encode()
            return 200, url.replace(LEGACY, CANONICAL), body, {"content-type": "application/xml"}, 0.01
        if url.endswith("/tailwindcss"):
            return 200, url.replace(LEGACY, CANONICAL), b"", {"content-type": "text/css"}, 0.01
        if url.endswith("/404.html"):
            return 200, url.replace(LEGACY, CANONICAL), b"", {"content-type": "text/html"}, 0.01

        canonical = url.replace(LEGACY, CANONICAL)
        route_path = canonical.removeprefix(CANONICAL) or "/"
        route = next(item for item in smoke_live_routes.ROUTES if item[0] == route_path)
        html = (
            f"<html><head><title>{route[1]}</title>"
            f"<link rel=\\"canonical\\" href=\\"{route[2]}\\"></head>"
            "<body>Bağımsız bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir. "
            "Cihaz hasarı başvurusu 30 gün içinde yapılır.</body></html>"
        ).encode()
        headers = {name: "present" for name in smoke_live_routes.REQUIRED_SECURITY_HEADERS}
        headers["content-type"] = "text/html"
        return 200, canonical, html, headers, 0.01

    monkeypatch.setattr(smoke_live_routes, "fetch", fake_fetch)
    result = smoke_live_routes.run(CANONICAL, check_assets=False)
    assert result["ok"] is True
    assert calls[0] == LEGACY + "/"
    assert result["results"][0]["path"] == "www-redirect"
''',
        encoding="utf-8",
    )


def remove_one_shot_files() -> None:
    (ROOT / ".github/workflows/alo186-one-shot-apex-canonical-v203.yml").unlink(missing_ok=True)
    Path(__file__).unlink(missing_ok=True)


def main() -> None:
    migrate_builder()
    migrate_manifest_and_apache()
    migrate_static_smoke()
    migrate_live_smoke()
    migrate_existing_contract()
    write_regression()
    remove_one_shot_files()


if __name__ == "__main__":
    main()
