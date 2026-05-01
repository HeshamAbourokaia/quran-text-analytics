"""Playwright-based renderer for chart-radar.

Exposes:
  - HttpServer: context manager wrapping a tiny http.server thread
  - RadarRenderer: long-lived browser/page, can re-render after mutations
    without full page reload
  - render_once: convenience for smoke tests

The orchestrator uses RadarRenderer directly; HTTP server stays up for the
whole run, the page stays mounted, and only the JSON content changes
between iterations. That keeps per-iteration latency to ~1-2s.
"""
from __future__ import annotations

import argparse
import asyncio
import http.server
import json
import socketserver
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

ELECTRON_APP_DIR = Path(__file__).parent.parent / "electron-app"
DEFAULT_SURAHS = [36, 55, 67]  # Yasin, Ar-Rahman, Al-Mulk
DEFAULT_VIEWPORT = {"width": 1100, "height": 900}


class HttpServer:
    """Serves electron-app/ on 127.0.0.1:PORT in a daemon thread."""

    def __init__(self, root: Path = ELECTRON_APP_DIR, port: int = 0):
        self.root = root
        self._requested_port = port
        self._httpd: Optional[socketserver.TCPServer] = None
        self._thread: Optional[threading.Thread] = None

    @property
    def port(self) -> int:
        if self._httpd is None:
            return self._requested_port
        return self._httpd.server_address[1]

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self) -> "HttpServer":
        root = self.root

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(root), **kwargs)

            def log_message(self, *args, **kwargs):
                pass

        self._httpd = socketserver.TCPServer(("127.0.0.1", self._requested_port), Handler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
        self._httpd = None


class RadarRenderer:
    """Long-lived browser/page for rendering chart-radar repeatedly.

    Workflow:
        await r.start()                          # boot browser, open page
        ...mutate radar.json on disk...
        await r.reload_config_and_render()       # re-fetch, re-render
        await r.screenshot(path)                 # save PNG of #chart-radar
        ...
        await r.stop()
    """

    def __init__(
        self,
        http_url: str,
        surahs: list[int] | None = None,
        viewport: dict | None = None,
        headless: bool = True,
    ):
        self.url = f"{http_url}/app.html"
        self.surahs = surahs or DEFAULT_SURAHS
        self.viewport = viewport or DEFAULT_VIEWPORT
        self.headless = headless
        self._pw = None
        self._browser: Optional[Browser] = None
        self._ctx: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    @property
    def page(self) -> Page:
        if not self._page:
            raise RuntimeError("RadarRenderer not started")
        return self._page

    async def start(self) -> None:
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self.headless)
        self._ctx = await self._browser.new_context(viewport=self.viewport)
        self._page = await self._ctx.new_page()

        # Capture page errors for the heuristic eval to look at
        self._page_errors: list[str] = []
        self._page.on("pageerror", lambda e: self._page_errors.append(str(e)))

        await self._page.goto(self.url, wait_until="networkidle", timeout=25000)
        await self._page.wait_for_timeout(1500)
        await self._set_initial_state()

    async def _set_initial_state(self) -> None:
        surahs_json = json.dumps(self.surahs)
        await self._page.evaluate(
            f"""
            async () => {{
              const app = window.__app;
              if (!app) throw new Error('window.__app missing — app.html patch incomplete');
              app.currentPage = 17;
              app.radarSurahs = {surahs_json};
              await new Promise(r => setTimeout(r, 100));
              if (typeof Plotly !== 'undefined') Plotly.purge('chart-radar');
              if (typeof app.renderRadarChart === 'function') {{
                await app.renderRadarChart();
              }}
              await new Promise(r => setTimeout(r, 350));
            }}
            """
        )

    async def reload_config_and_render(self) -> None:
        """Re-fetch radar.json (cache-busted) and re-render."""
        await self._page.evaluate(
            """
            async () => {
              const app = window.__app;
              const url = 'charts/configs/radar.json?_=' + Date.now();
              const cfg = await fetch(url).then(r => r.json());
              app.chartCfg = cfg;
              if (typeof Plotly !== 'undefined') Plotly.purge('chart-radar');
              await app.renderRadarChart();
              await new Promise(r => setTimeout(r, 300));
            }
            """
        )

    async def screenshot(self, path: Path) -> Path:
        chart = await self._page.query_selector("#chart-radar")
        if not chart:
            raise RuntimeError("#chart-radar element not found")
        path.parent.mkdir(parents=True, exist_ok=True)
        await chart.screenshot(path=str(path))
        return path

    @property
    def page_errors(self) -> list[str]:
        return list(self._page_errors)

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()


async def render_once(output_path: Path, surahs: list[int] | None = None) -> dict:
    """One-shot render. Used by the smoke test."""
    with HttpServer() as srv:
        r = RadarRenderer(srv.url, surahs)
        await r.start()
        await r.screenshot(output_path)
        errors = r.page_errors
        await r.stop()
    return {"screenshot": str(output_path), "page_errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="one-shot render to --out")
    parser.add_argument(
        "--out", type=str, default=None, help="output PNG path"
    )
    args = parser.parse_args()

    if args.once:
        out = (
            Path(args.out)
            if args.out
            else Path(__file__).parent / "runs" / "smoke" / "render_once.png"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        res = asyncio.run(render_once(out))
        print(json.dumps(res, indent=2))
