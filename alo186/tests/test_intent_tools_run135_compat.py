from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186" / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

import inject_intent_tools_run135_compat as compat  # noqa: E402

RAW_PREFIX = """<!doctype html><input id=\"hours\" type=\"number\" min=\"0\" max=\"8760\">
<script>
const input=document.getElementById('hours');
const rawHours=input.value.trim();
const hours=rawHours===''?Number.NaN:Number(rawHours);
"""
RAW_SUFFIX = "\n</script>"


def target_path(site: Path) -> Path:
    return site / compat.ROUTES[0].strip("/") / "index.html"


def write_case(site: Path, javascript: str) -> Path:
    target = target_path(site)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(RAW_PREFIX + javascript + RAW_SUFFIX, encoding="utf-8")
    return target


def test_equivalent_positive_validation_is_normalized_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        target = write_case(
            site,
            compat._POSITIVE_CONDITION + "\nif(!valid){ throw new Error('invalid'); }",
        )

        assert compat.harden_outage_input(site) is True
        updated = target.read_text(encoding="utf-8")
        assert compat._NEGATIVE_CONDITION in updated
        assert "if(invalid){" in updated
        assert "const valid=" not in updated

        # Idempotent: the strict base injector accepts the normalised form.
        assert compat.harden_outage_input(site) is False


def test_current_dual_validation_is_accepted_without_rewrite() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        target = write_case(
            site,
            "\n".join(
                (
                    compat._CURRENT_NEGATIVE_CONDITION,
                    compat._POSITIVE_CONDITION,
                    "if(invalidHours){ throw new Error('invalid'); }",
                )
            ),
        )
        before = target.read_text(encoding="utf-8")

        assert compat.harden_outage_input(site) is False
        after = target.read_text(encoding="utf-8")
        assert after == before
        assert compat._CURRENT_NEGATIVE_CONDITION in after
        assert compat._CURRENT_NEGATIVE_USE in after
        assert compat._POSITIVE_CONDITION in after


def test_legacy_negative_validation_remains_idempotent() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        target = write_case(
            site,
            compat._NEGATIVE_CONDITION + "\nif(invalid){ throw new Error('invalid'); }",
        )
        before = target.read_text(encoding="utf-8")
        assert compat.harden_outage_input(site) is False
        assert target.read_text(encoding="utf-8") == before


def test_unknown_positive_usage_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        write_case(
            site,
            compat._POSITIVE_CONDITION + "\nif(valid===false){ throw new Error('invalid'); }",
        )
        try:
            compat.harden_outage_input(site)
        except RuntimeError as exc:
            assert "güvenli kullanım kalıbı tanınmadı" in str(exc)
            return
        raise AssertionError("Tanınmayan pozitif doğrulama fail-closed durmadı")


def test_missing_page_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        try:
            compat.harden_outage_input(Path(tmp))
        except FileNotFoundError:
            return
        raise AssertionError("Eksik tazminat aracı fail-closed durmadı")


if __name__ == "__main__":
    test_equivalent_positive_validation_is_normalized_fail_closed()
    test_current_dual_validation_is_accepted_without_rewrite()
    test_legacy_negative_validation_remains_idempotent()
    test_unknown_positive_usage_fails_closed()
    test_missing_page_fails_closed()
    print("ALO186 run135 compatibility: PASS")
