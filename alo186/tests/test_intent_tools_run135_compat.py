from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186" / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

import inject_intent_tools_run135_compat as compat  # noqa: E402


def test_equivalent_positive_validation_is_normalized_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        target = site / compat.ROUTES[0].strip("/") / "index.html"
        target.parent.mkdir(parents=True)
        target.write_text(
            """<!doctype html><input id=\"hours\" type=\"number\" min=\"0\" max=\"8760\">\n"
            "<script>\n"
            "const input=document.getElementById('hours');\n"
            "const rawHours=input.value.trim();\n"
            "const hours=rawHours===''?Number.NaN:Number(rawHours);\n"
            "const valid=rawHours!==''&&Number.isFinite(hours)&&hours>=0&&hours<=8760;\n"
            "if(!valid){ throw new Error('invalid'); }\n"
            "</script>""",
            encoding="utf-8",
        )

        assert compat.harden_outage_input(site) is True
        updated = target.read_text(encoding="utf-8")
        assert "rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760" in updated
        assert "if(invalid){" in updated
        assert "const valid=" not in updated

        # Idempotent: the strict base injector accepts the normalised form.
        assert compat.harden_outage_input(site) is False


if __name__ == "__main__":
    test_equivalent_positive_validation_is_normalized_fail_closed()
    print("ALO186 run135 compatibility: PASS")
