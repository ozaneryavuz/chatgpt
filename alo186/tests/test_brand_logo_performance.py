from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186/deployment/verify_brand_logo.py"
spec = importlib.util.spec_from_file_location("verify_brand_logo", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

current_markup = """
<img src="/_vinext/image?url=%2Fbrand%2Falo186-logo.png&amp;w=1200&amp;q=75"
 alt="ALO186.com" width="749" height="130" loading="eager"
 fetchpriority="high" decoding="async"
 srcset="/_vinext/image?url=%2Fbrand%2Falo186-logo.png&amp;w=640&amp;q=75 640w,
 /_vinext/image?url=%2Fbrand%2Falo186-logo.png&amp;w=1200&amp;q=75 1200w"
 class="brand-logo">
"""
report = module.audit_html(current_markup)
assert not report["ok"]
assert "fetchpriority_must_be_high" not in report["hardIssues"]
assert "intrinsic_width_exceeds_2x_rendered_width" in report["hardIssues"]
assert "intrinsic_height_exceeds_2x_rendered_height" in report["hardIssues"]
assert "intrinsic_aspect_ratio_must_match_162x28" in report["hardIssues"]
assert "sizes_must_bound_logo_slot_to_150_162px" in report["hardIssues"]
assert "unbounded_srcset_can_download_oversized_candidate" in report["hardIssues"]

vinext_fixed = """
<img src="/_vinext/image?url=%2Fbrand%2Falo186-logo.png&amp;w=384&amp;q=70"
 alt="ALO186.com" width="162" height="28" sizes="(max-width: 480px) 150px, 162px"
 loading="eager" fetchpriority="high" decoding="async"
 srcset="/_vinext/image?url=%2Fbrand%2Falo186-logo.png&amp;w=256&amp;q=70 256w,
 /_vinext/image?url=%2Fbrand%2Falo186-logo.png&amp;w=384&amp;q=70 384w"
 class="brand-logo">
"""
report = module.audit_html(vinext_fixed)
assert report["ok"], report
assert report["logo"]["slotWidthsPx"] == [150, 162]
assert report["logo"]["candidateWidths"] == [256, 384]
assert report["logo"]["aspectRatioValid"] is True
assert report["recommendations"] == ["verify_vinext_response_content_type_is_avif_or_webp"]

picture_fixed = """
<picture>
  <source type="image/avif" srcset="/brand/alo186-logo-162.avif 162w, /brand/alo186-logo-324.avif 324w">
  <source type="image/webp" srcset="/brand/alo186-logo-162.webp 162w, /brand/alo186-logo-324.webp 324w">
  <img src="/brand/alo186-logo-162.webp"
       srcset="/brand/alo186-logo-162.webp 162w, /brand/alo186-logo-324.webp 324w"
       sizes="(max-width: 480px) 150px, 162px" alt="ALO186.com" width="162" height="28"
       loading="eager" fetchpriority="high" decoding="async" class="brand-logo">
</picture>
"""
report = module.audit_html(picture_fixed)
assert report["ok"], report
assert report["logo"]["usesExplicitModernFormat"] is True
assert report["recommendations"] == []

mixed_unbounded_sizes = vinext_fixed.replace(
    'sizes="(max-width: 480px) 150px, 162px"',
    'sizes="(max-width: 480px) 100vw, 162px"',
).replace("w=384&amp;q=70 384w", "w=1200&amp;q=70 1200w")
report = module.audit_html(mixed_unbounded_sizes)
assert not report["ok"]
assert "sizes_must_bound_logo_slot_to_150_162px" in report["hardIssues"]
assert "unbounded_srcset_can_download_oversized_candidate" in report["hardIssues"]
assert report["logo"]["slotWidthsPx"] == []

wrong_aspect_ratio = vinext_fixed.replace('width="162" height="28"', 'width="162" height="56"')
report = module.audit_html(wrong_aspect_ratio)
assert not report["ok"]
assert "intrinsic_aspect_ratio_must_match_162x28" in report["hardIssues"]

tiny_wrong_aspect_ratio = vinext_fixed.replace('width="162" height="28"', 'width="1" height="1"')
report = module.audit_html(tiny_wrong_aspect_ratio)
assert not report["ok"]
assert "intrinsic_aspect_ratio_must_match_162x28" in report["hardIssues"]

missing_priority = vinext_fixed.replace('fetchpriority="high"', "")
report = module.audit_html(missing_priority)
assert "fetchpriority_must_be_high" in report["hardIssues"]

print(json.dumps({
    "ok": True,
    "currentMarkupRejected": True,
    "vinextContractAccepted": True,
    "pictureContractAccepted": True,
    "unboundedSizesRejected": True,
    "aspectRatioGuard": True,
    "fetchPriorityGuard": True,
}, ensure_ascii=False))
