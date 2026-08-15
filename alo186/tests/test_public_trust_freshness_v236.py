from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186/deployment/verify_public_trust_freshness.py"
spec = importlib.util.spec_from_file_location("verify_public_trust_freshness_v236", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

COMMIT = "0123456789abcdef0123456789abcdef01234567"
HOME = """<!doctype html><html><body>
<p>EDAŞ veya kamu kurumu değildir</p>
<p>ALO186 başvuru, ihbar veya hasar kaydı almaz</p>
<p>Tehlike varsa ticari yol kapanır</p>
</body></html>"""
HUB = """<!doctype html><html><body>
<p>Amazon satış ortaklığı</p>
<p>Mevcut sistem yeterliyse satın alma yok</p>
<p>Aktif tehlikede satış yolu kapalı</p>
<p>Affiliate açıklaması bağlantıdan önce</p>
<p>ALO186 satıcı değildir</p>
</body></html>"""


def write_checksums(site: Path) -> None:
    targets = (
        Path("index.html"),
        Path("amazon-elektrik-urunleri/index.html"),
        Path("pages-release.json"),
    )
    lines = []
    for relative in targets:
        digest = hashlib.sha256((site / relative).read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative.as_posix()}")
    (site / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_site(root: Path, *, commit: str = COMMIT, base_path: str = "", home: str = HOME, hub: str = HUB) -> Path:
    site = root / "site"
    (site / "amazon-elektrik-urunleri").mkdir(parents=True)
    (site / "index.html").write_text(home, encoding="utf-8")
    (site / "amazon-elektrik-urunleri/index.html").write_text(hub, encoding="utf-8")
    (site / "pages-release.json").write_text(
        json.dumps(
            {
                "commit": commit,
                "basePath": base_path,
                "canonicalHost": "https://alo186.com",
                "customDomain": "alo186.com",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_checksums(site)
    return site


def expect_failure(site: Path, token: str, *, expected_commit: str = COMMIT, base_path: str = "") -> None:
    try:
        module.validate_site(site, expected_commit, base_path)
    except (RuntimeError, FileNotFoundError, ValueError) as error:
        assert token.casefold() in str(error).casefold(), (token, str(error))
    else:
        raise AssertionError(f"Doğrulamanın başarısız olması bekleniyordu: {token}")


with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    site = make_site(root)
    result = module.validate_site(site, COMMIT, "")
    assert result["ok"] is True
    assert result["commit"] == COMMIT
    assert result["basePath"] == ""
    assert len(result["checksumsVerified"]) == 3

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    site = make_site(root, base_path="/chatgpt")
    result = module.validate_site(site, COMMIT, "/chatgpt")
    assert result["basePath"] == "/chatgpt"

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    site = make_site(root, hub=HUB + "<p>67 ürün seçim yolu</p>")
    expect_failure(site, "67 ürün seçim yolu")

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    site = make_site(root, commit="different")
    expect_failure(site, "commit makbuzu")

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    site = make_site(root, hub=HUB.replace("Mevcut sistem yeterliyse satın alma yok", ""))
    expect_failure(site, "satın alma yok")

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    site = make_site(root)
    (site / "index.html").write_text(HOME + "<!-- değişti -->", encoding="utf-8")
    expect_failure(site, "checksum uyuşmazlığı")

print(
    json.dumps(
        {
            "ok": True,
            "cases": 6,
            "contracts": [
                "custom-domain",
                "project-path",
                "stale-copy-rejection",
                "commit-provenance",
                "no-buy-result",
                "artifact-checksum",
            ],
        },
        ensure_ascii=False,
    )
)
