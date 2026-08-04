from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186/deployment"))

from bootstrap_github_pages import (  # noqa: E402
    DEFAULT_CUSTOM_DOMAIN,
    LEGACY_CUSTOM_DOMAIN,
    PagesBootstrapError,
    ensure_pages,
    main,
)
from smoke_github_pages import executable_html_text  # noqa: E402


class FakePagesHandler(BaseHTTPRequestHandler):
    site_exists = False
    cname = None
    requests: list[tuple[str, dict | None]] = []

    @classmethod
    def reset(cls, *, exists: bool = False, cname: str | None = None) -> None:
        cls.site_exists = exists
        cls.cname = cname
        cls.requests = []

    def log_message(self, _format: str, *_args) -> None:
        return

    def _payload(self) -> dict | None:
        length = int(self.headers.get("Content-Length", "0"))
        if not length:
            return None
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _json(self, status: int, payload: dict | None = None) -> None:
        body = json.dumps(payload).encode("utf-8") if payload is not None else b""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        type(self).requests.append(("GET", None))
        if not type(self).site_exists:
            self._json(404, {"message": "Not Found"})
            return
        self._json(
            200,
            {
                "build_type": "workflow",
                "cname": type(self).cname,
                "status": "built",
                "html_url": "https://alo186.com",
                "https_enforced": False,
                "protected_domain_state": "pending",
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        payload = self._payload()
        type(self).requests.append(("POST", payload))
        if type(self).site_exists:
            self._json(409, {"message": "Conflict"})
            return
        self.assert_payload(payload, {"build_type": "workflow"})
        type(self).site_exists = True
        self._json(201, {"build_type": "workflow"})

    def do_PUT(self) -> None:  # noqa: N802
        payload = self._payload()
        type(self).requests.append(("PUT", payload))
        self.assert_payload(payload, {"build_type": "workflow", "cname": "alo186.com"})
        type(self).site_exists = True
        type(self).cname = payload["cname"]
        self._json(204)

    def assert_payload(self, actual: dict | None, expected: dict) -> None:
        if actual != expected:
            self._json(422, {"message": f"unexpected payload: {actual!r}"})
            raise AssertionError((actual, expected))


@contextlib.contextmanager
def fake_api(*, exists: bool = False, cname: str | None = None):
    FakePagesHandler.reset(exists=exists, cname=cname)
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakePagesHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


class PagesBootstrapTests(unittest.TestCase):
    def test_creates_workflow_site_and_sets_apex_custom_domain(self) -> None:
        with fake_api() as api_base:
            result = ensure_pages(
                repository="ozaneryavuz/chatgpt",
                custom_domain="alo186.com.",
                token="test-admin-token-never-log",
                api_base=api_base,
            )

        self.assertTrue(result.created)
        self.assertTrue(result.updated)
        self.assertEqual(result.build_type, "workflow")
        self.assertEqual(result.custom_domain, "alo186.com")
        self.assertEqual(
            [method for method, _payload in FakePagesHandler.requests],
            ["GET", "POST", "PUT", "GET"],
        )
        self.assertEqual(FakePagesHandler.requests[1][1], {"build_type": "workflow"})
        self.assertEqual(
            FakePagesHandler.requests[2][1],
            {"build_type": "workflow", "cname": "alo186.com"},
        )

    def test_legacy_www_input_is_normalized_to_apex(self) -> None:
        with fake_api(exists=True, cname="old.example.com") as api_base:
            result = ensure_pages(
                repository="ozaneryavuz/chatgpt",
                custom_domain="www.alo186.com",
                token="test-admin-token-never-log",
                api_base=api_base,
            )

        self.assertFalse(result.created)
        self.assertEqual(
            [method for method, _payload in FakePagesHandler.requests],
            ["GET", "PUT", "GET"],
        )
        self.assertEqual(result.custom_domain, "alo186.com")
        self.assertEqual(FakePagesHandler.requests[1][1], {"build_type": "workflow", "cname": "alo186.com"})

    def test_rejects_missing_token_and_invalid_targets(self) -> None:
        with self.assertRaises(PagesBootstrapError):
            ensure_pages(
                repository="ozaneryavuz/chatgpt",
                custom_domain="alo186.com",
                token="",
            )
        with self.assertRaises(PagesBootstrapError):
            ensure_pages(
                repository="invalid",
                custom_domain="alo186.com",
                token="token",
            )
        with self.assertRaises(PagesBootstrapError):
            ensure_pages(
                repository="ozaneryavuz/chatgpt",
                custom_domain="https://alo186.com/path",
                token="token",
            )

    def test_cli_output_never_contains_admin_token(self) -> None:
        secret = "pages-admin-secret-must-not-leak"
        with fake_api() as api_base, patch.dict(
            os.environ,
            {
                "ALO186_PAGES_ADMIN_TOKEN": secret,
                "GITHUB_REPOSITORY": "ozaneryavuz/chatgpt",
            },
            clear=False,
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main(["--api-base", api_base])

        self.assertEqual(exit_code, 0)
        self.assertNotIn(secret, stdout.getvalue())
        self.assertNotIn(secret, stderr.getvalue())
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["custom_domain"], "alo186.com")

    def test_workflow_uses_optional_admin_bootstrap_without_printing_secret(self) -> None:
        workflow = (ROOT / ".github/workflows/alo186-github-pages.yml").read_text(encoding="utf-8")
        self.assertIn("ALO186_PAGES_ADMIN_TOKEN", workflow)
        self.assertIn("bootstrap_github_pages.py", workflow)
        self.assertIn("custom-domain alo186.com", workflow)
        self.assertNotIn('echo "$PAGES_ADMIN_TOKEN"', workflow)
        self.assertNotIn("set -x", workflow)

    def test_domain_constants_are_apex_first(self) -> None:
        self.assertEqual(DEFAULT_CUSTOM_DOMAIN, "alo186.com")
        self.assertEqual(LEGACY_CUSTOM_DOMAIN, "www.alo186.com")

    def test_marked_base_path_aware_ga4_runtime_is_excluded_from_root_scan(self) -> None:
        html = """
        <script data-alo186-ga4-consent="true">
        const BASE="/chatgpt";
        const logicalPath=location.pathname.slice(BASE.length)||"/";
        </script>
        <script>const target="/unsafe-root";</script>
        """
        executable = executable_html_text(html)
        self.assertNotIn("logicalPath", executable)
        self.assertIn('const target="/unsafe-root"', executable)

    def test_unmarked_or_non_base_aware_scripts_remain_fail_closed(self) -> None:
        unmarked = '<script>const target="/";</script>'
        falsely_marked = '<script data-alo186-ga4-consent="true">const target="/";</script>'
        self.assertIn('const target="/"', executable_html_text(unmarked))
        self.assertIn('const target="/"', executable_html_text(falsely_marked))


if __name__ == "__main__":
    unittest.main()
