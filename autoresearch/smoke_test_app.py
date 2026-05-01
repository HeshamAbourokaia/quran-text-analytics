"""Smoke test that the patched app.html loads cleanly + the radar JSON
config is fetched without errors.

Loads the app via http://127.0.0.1:8765 (must be running), waits for the
network to go idle, then queries the page state.

This is a one-shot patch verifier, NOT part of the loop. The loop uses
render.py against render_host.html. The richer "did the radar actually
render" verification happens once render_host.html is built.
"""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8765/app.html"
OUT_DIR = Path(__file__).parent / "runs" / "smoke"
OUT_DIR.mkdir(parents=True, exist_ok=True)


async def main() -> int:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await ctx.new_page()

        page_errors: list[str] = []
        console_errors: list[str] = []
        radar_request_seen = {"hit": False, "status": None}

        page.on("pageerror", lambda e: page_errors.append(str(e)))

        def on_console(msg):
            if msg.type in ("error", "warning"):
                console_errors.append(f"[{msg.type}] {msg.text}")

        page.on("console", on_console)

        def on_response(resp):
            if "charts/configs/radar.json" in resp.url:
                radar_request_seen["hit"] = True
                radar_request_seen["status"] = resp.status

        page.on("response", on_response)

        await page.goto(URL, wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(2000)  # let Vue mount + async fetch resolve

        # Probe key globals/state without depending on Vue 3 internals
        state = await page.evaluate(
            """
            () => {
              return {
                title: document.title,
                vue_root_present: !!document.getElementById('app'),
                vue_root_children: document.getElementById('app')?.children?.length || 0,
                data_loaded: typeof DATA !== 'undefined' && !!DATA?.surahStats,
                verses_data_loaded: typeof VERSES_DATA !== 'undefined',
                plotly_loaded: typeof Plotly !== 'undefined',
              };
            }
            """
        )

        await page.screenshot(path=str(OUT_DIR / "fullpage.png"), full_page=False)
        await browser.close()

    print("=== smoke test result ===")
    print(f"page state: {state}")
    print(f"radar.json fetch: hit={radar_request_seen['hit']} status={radar_request_seen['status']}")
    print(f"page errors ({len(page_errors)}): {page_errors[:5]}")
    print(f"console errors ({len(console_errors)}): {console_errors[:5]}")
    print(f"screenshot: {OUT_DIR}/fullpage.png")

    ok = (
        state.get("vue_root_present")
        and state.get("vue_root_children", 0) > 0
        and state.get("data_loaded")
        and state.get("plotly_loaded")
        and radar_request_seen["hit"]
        and radar_request_seen["status"] == 200
        and not page_errors
    )
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
