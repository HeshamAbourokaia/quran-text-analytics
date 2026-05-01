"""Cheap heuristic evaluators that gate the vision-LLM judge.

5 checks, run as a single page.evaluate(...) call against the live
Plotly-rendered chart. Each returns score 0..1 and a fail flag.

Heuristics:
  1. render_error: did the chart render at all? (svg present, errors=0)
  2. label_collision: count axis-label / legend-label bbox overlaps
  3. margin_sanity: plot area not strangled by margins
  4. wcag_palette_contrast: colors distinguishable, all readable on bg
  5. legend_overflow: legend bbox stays inside the chart container

Total budget: ~600ms per iteration on the heuristic-only path.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from playwright.async_api import Page

# JS injected into the page. Returns a JSON-serialisable result object.
_HEURISTIC_JS = r"""
() => {
  const out = {scores: {}, fails: {}, details: {}};

  // 1. render_error_check
  const el = document.getElementById('chart-radar');
  const svg = el ? el.querySelector('svg.main-svg') : null;
  const renderOk = !!svg && svg.clientWidth > 0 && svg.clientHeight > 0;
  out.scores.render_error = renderOk ? 1.0 : 0.0;
  out.fails.render_error = !renderOk;
  out.details.render_error = {
    el_present: !!el,
    svg_present: !!svg,
    svg_w: svg ? svg.clientWidth : 0,
    svg_h: svg ? svg.clientHeight : 0,
  };
  if (!renderOk) {
    return out;  // can't run remaining checks
  }

  // 2. label_collision_check
  // Plotly's polar angular axis labels are hard to grab via class — use
  // a broader selector for visible <text> inside the SVG with non-zero size,
  // then exclude the radial-axis tick numbers (those are inside the polar
  // plot area and naturally don't collide with each other).
  const allTexts = Array.from(svg.querySelectorAll('text')).filter(t => {
    const r = t.getBoundingClientRect();
    return r.width > 1 && r.height > 1 && t.textContent.trim().length > 0;
  });
  const rects = allTexts.map(t => t.getBoundingClientRect());
  let overlaps = 0;
  for (let i = 0; i < rects.length; i++) {
    for (let j = i + 1; j < rects.length; j++) {
      const a = rects[i], b = rects[j];
      const xOverlap = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
      const yOverlap = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
      if (xOverlap > 1 && yOverlap > 1) overlaps++;
    }
  }
  const nLabels = Math.max(allTexts.length, 1);
  const collisionRatio = overlaps / nLabels;
  out.scores.label_collision = Math.max(0, 1 - collisionRatio * 4);  // each overlap costs 0.25
  out.fails.label_collision = collisionRatio > 0.25;
  out.details.label_collision = {n_labels: nLabels, overlaps, ratio: collisionRatio};

  // 3. margin_sanity_check
  // Layout we pulled from cfg via the mounted Vue app
  const cfg = window.__app?.chartCfg;
  let marginOk = true;
  let plotH = 0, plotW = 0;
  if (cfg && cfg.layout) {
    const m = cfg.layout.margin || {t:0,l:0,r:0,b:0};
    const h = cfg.layout.height || svg.clientHeight;
    plotH = h - (m.t||0) - (m.b||0);
    plotW = svg.clientWidth - (m.l||0) - (m.r||0);
    marginOk = plotH >= 200 && plotW >= 280;
    out.scores.margin_sanity = marginOk ? 1.0 : 0.0;
    out.fails.margin_sanity = !marginOk;
    out.details.margin_sanity = {plot_h: plotH, plot_w: plotW, ok: marginOk};
  } else {
    out.scores.margin_sanity = 0;
    out.fails.margin_sanity = true;
    out.details.margin_sanity = {note: 'no cfg available'};
  }

  // 4. wcag_palette_contrast_check
  // Compute relative-luminance contrast vs white bg, plus pairwise CIE76 ΔE distance
  function srgbToLin(c) { c = c / 255; return c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); }
  function relLuminance(hex) {
    const h = hex.replace('#','');
    const r = srgbToLin(parseInt(h.substr(0,2),16));
    const g = srgbToLin(parseInt(h.substr(2,2),16));
    const b = srgbToLin(parseInt(h.substr(4,2),16));
    return 0.2126*r + 0.7152*g + 0.0722*b;
  }
  function hexToLab(hex) {
    // Quick sRGB -> Lab via D65
    const h = hex.replace('#','');
    let r = parseInt(h.substr(0,2),16)/255;
    let g = parseInt(h.substr(2,2),16)/255;
    let b = parseInt(h.substr(4,2),16)/255;
    [r,g,b] = [r,g,b].map(c => c<=0.04045 ? c/12.92 : Math.pow((c+0.055)/1.055,2.4));
    let X = (r*0.4124 + g*0.3576 + b*0.1805) / 0.95047;
    let Y = (r*0.2126 + g*0.7152 + b*0.0722) / 1.00000;
    let Z = (r*0.0193 + g*0.1192 + b*0.9505) / 1.08883;
    [X,Y,Z] = [X,Y,Z].map(t => t>0.008856 ? Math.pow(t,1/3) : 7.787*t + 16/116);
    return {L: 116*Y - 16, a: 500*(X-Y), b: 200*(Y-Z)};
  }
  function deltaE(c1, c2) {
    const L1 = hexToLab(c1), L2 = hexToLab(c2);
    return Math.sqrt((L1.L-L2.L)**2 + (L1.a-L2.a)**2 + (L1.b-L2.b)**2);
  }
  const palette = (cfg && cfg.palette) || [];
  const bgLum = 1.0;  // assume white
  let minContrast = Infinity, minDelta = Infinity;
  palette.forEach(c => {
    const lum = relLuminance(c);
    const ratio = (Math.max(lum, bgLum) + 0.05) / (Math.min(lum, bgLum) + 0.05);
    if (ratio < minContrast) minContrast = ratio;
  });
  for (let i = 0; i < palette.length; i++) {
    for (let j = i+1; j < palette.length; j++) {
      const d = deltaE(palette[i], palette[j]);
      if (d < minDelta) minDelta = d;
    }
  }
  const contrastScore = Math.min(1, minContrast / 3.0);
  const distinctScore = Math.min(1, minDelta / 25);
  out.scores.wcag_palette_contrast = (2 * contrastScore * distinctScore) / (contrastScore + distinctScore || 1);
  out.fails.wcag_palette_contrast = minContrast < 2.5 || minDelta < 15;
  out.details.wcag_palette_contrast = {
    min_contrast: Number.isFinite(minContrast) ? minContrast.toFixed(2) : null,
    min_delta_e: Number.isFinite(minDelta) ? minDelta.toFixed(1) : null,
  };

  // 5. legend_overflow_check
  // Plotly's legend can live inside the svg (g.legend) or as a sibling
  // element in some renders. Try both.
  const legend = svg.querySelector('g.legend') || el.querySelector('.legend') || el.querySelector('g.legend');
  if (legend) {
    const lr = legend.getBoundingClientRect();
    const sr = svg.getBoundingClientRect();
    const overflow_top = Math.max(0, sr.top - lr.top);
    const overflow_bot = Math.max(0, lr.bottom - sr.bottom);
    const overflow_l = Math.max(0, sr.left - lr.left);
    const overflow_r = Math.max(0, lr.right - sr.right);
    const total = overflow_top + overflow_bot + overflow_l + overflow_r;
    out.scores.legend_overflow = total <= 2 ? 1.0 : Math.max(0, 1 - total / 50);
    out.fails.legend_overflow = total > 12;
    out.details.legend_overflow = {top: overflow_top, bot: overflow_bot, l: overflow_l, r: overflow_r};
  } else {
    // No legend rendered (showlegend=false). Treat as neutral pass.
    out.scores.legend_overflow = 1.0;
    out.fails.legend_overflow = false;
    out.details.legend_overflow = {note: 'no legend'};
  }

  return out;
}
"""


@dataclass
class HeuristicResult:
    scores: dict[str, float] = field(default_factory=dict)
    fails: dict[str, bool] = field(default_factory=dict)
    details: dict = field(default_factory=dict)
    score: float = 0.0
    fail: bool = False

    @classmethod
    def from_raw(cls, raw: dict) -> "HeuristicResult":
        scores = {k: float(v) for k, v in raw.get("scores", {}).items()}
        fails = {k: bool(v) for k, v in raw.get("fails", {}).items()}
        # Aggregate over ALL scores (not just passing) so the absolute level
        # of each check contributes — this lets the gate compare candidate
        # vs baseline on continuous signal rather than a binary trip-wire.
        all_scores = list(scores.values())
        score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        # `fail` is reserved for CATASTROPHIC issues only (chart didn't render).
        # Soft fails (low contrast, label collision) lower the score but
        # don't trip a hard gate on their own.
        catastrophic = bool(fails.get("render_error", False))
        return cls(
            scores=scores,
            fails=fails,
            details=raw.get("details", {}),
            score=score,
            fail=catastrophic,
        )


async def run_heuristics(page: Page) -> HeuristicResult:
    raw = await page.evaluate(_HEURISTIC_JS)
    return HeuristicResult.from_raw(raw)


if __name__ == "__main__":
    import argparse
    import asyncio
    from render import HttpServer, RadarRenderer  # noqa: E402

    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    async def smoke() -> None:
        with HttpServer() as srv:
            r = RadarRenderer(srv.url)
            await r.start()
            res = await run_heuristics(r.page)
            await r.stop()
        print(json.dumps(
            {
                "score": res.score,
                "fail": res.fail,
                "scores": res.scores,
                "fails": res.fails,
                "details": res.details,
            },
            indent=2,
        ))

    if args.once:
        asyncio.run(smoke())
