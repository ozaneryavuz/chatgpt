from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186" / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

isolated = importlib.import_module("inject_affiliate_aeo_v250_isolated")
base = importlib.import_module("inject_affiliate_aeo_v250")
validator = importlib.import_module("validate_affiliate_aeo_v250")


def seed(site: Path) -> None:
    generic = """<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>ALO186 teknik rehber</title></head><body><main><h1>Teknik rehber</h1><p>Güvenlik kontrolü tamamlanmadan ürün seçilmez.</p></main></body></html>"""
    for target in base.TARGETS:
        path = site / target.file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(generic, encoding="utf-8")
    (site / "pages-release.json").write_text(
        json.dumps({"version": 1}), encoding="utf-8"
    )
    (site / "checksums.sha256").write_text("placeholder\n", encoding="utf-8")


def declared_ids(target) -> set[str]:
    values = {target.scenario_id}
    values.update(item.deep_id for item in target.recommendations)
    values.update(item[0] for item in target.faq_items)
    return values


def test_hardlink_and_symlink_targets_are_isolated() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)

        hard_source = site / base.TARGETS[0].file
        hard_alias = site / base.TARGETS[1].file
        hard_alias.unlink()
        os.link(hard_source, hard_alias)
        assert hard_source.stat().st_ino == hard_alias.stat().st_ino

        symlink_source = site / base.TARGETS[2].file
        symlink_alias = site / base.TARGETS[3].file
        symlink_alias.unlink()
        symlink_alias.symlink_to(symlink_source.resolve())
        assert symlink_alias.is_symlink()
        assert symlink_source.stat().st_ino == symlink_alias.stat().st_ino

        result = isolated.inject(site, "/chatgpt")
        isolation = result["targetFileIsolation"]
        assert isolation["validation"]["ok"] is True
        assert isolation["validation"]["targetCount"] == len(base.TARGETS)
        assert isolation["detach"]["sharedInodeGroupCountBefore"] == 2

        assert hard_source.stat().st_ino != hard_alias.stat().st_ino
        assert symlink_source.stat().st_ino != symlink_alias.stat().st_ino
        assert not symlink_alias.is_symlink()

        all_owned = set().union(*(declared_ids(target) for target in base.TARGETS))
        for target in base.TARGETS:
            html = (site / target.file).read_text(encoding="utf-8")
            ids = {
                base.unescape(match.group(2)).strip()
                for match in base.ID_RE.finditer(html)
            }
            own = declared_ids(target)
            assert own <= ids
            assert not ((ids & all_owned) - own), target.key
            assert html.count(base.MARKER) == 1
            assert html.count(base.SCHEMA_MARKER) == 1
            assert html.count(base.STYLE_MARKER) == 1

        validation = validator.validate(site, "/chatgpt")
        assert validation["ok"] is True, validation["errors"]

        release = json.loads(
            (site / "pages-release.json").read_text(encoding="utf-8")
        )
        receipt = release["affiliateAeoV250"]["targetFileIsolation"]
        assert receipt["validation"]["ok"] is True
        assert receipt["detach"]["sharedInodeGroupCountBefore"] == 2

        second = isolated.inject(site, "/chatgpt")
        assert second["injectedTargets"] == []
        assert second["targetFileIsolation"]["validation"]["ok"] is True
        second_validation = validator.validate(site, "/chatgpt")
        assert second_validation["ok"] is True, second_validation["errors"]


def test_foreign_identifier_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        base.inject(site, "")

        first = site / base.TARGETS[0].file
        foreign = base.TARGETS[1].scenario_id
        html = first.read_text(encoding="utf-8")
        html = html.replace("</main>", f'<div id="{foreign}"></div></main>', 1)
        first.write_text(html, encoding="utf-8")

        try:
            isolated._validate_target_isolation(site)
        except RuntimeError as exc:
            assert "başka hedefe ait deep-link" in str(exc)
            return
        raise AssertionError("Yabancı v250 deep-link kimliği fail-closed durmadı")


if __name__ == "__main__":
    test_hardlink_and_symlink_targets_are_isolated()
    test_foreign_identifier_is_rejected()
    print("ALO186 affiliate AEO v250 target isolation: PASS")
