# Quran Analytics — AutoResearch chart-tuning loop

Adapts Karpathy's [autoresearch](https://github.com/karpathy/autoresearch)
pattern (release Mar 2026) to Plotly chart tuning. Iteratively mutates
`electron-app/charts/configs/radar.json`, scores each mutation against a
hybrid (heuristic + Claude-vision) evaluator, commits the wins on the
`autoresearch/radar` branch.

The plan that produced this code lives at
`/Users/Hesham/.claude/plans/g-day-partitioned-pony.md`.

## Quickstart (full overnight run)

```bash
cd /Users/Hesham/Documents/quran-analytics
source .venv/bin/activate

# Set your Anthropic key — required for the vision judge
export ANTHROPIC_API_KEY='sk-ant-...'

# 8h overnight run on chart-radar, default budget $25
python3 autoresearch/orchestrator.py
```

What you'll get next morning:
- `git log autoresearch/radar` — linear history of validated improvements (one commit per win)
- `autoresearch/runs/<date>_radar/log.jsonl` — every iteration's mutation, scores, decision
- `autoresearch/runs/<date>_radar/shots/` — PNGs of each iteration's render

To review wins visually:
```bash
git checkout autoresearch/radar
git log --oneline                              # see all wins
git diff main..autoresearch/radar -- '*radar.json'   # cumulative config delta
npm start --prefix electron-app                # eyeball the result
```

If you want the wins back on `main`:
```bash
git checkout main
git merge autoresearch/radar
```

## Killing a running loop

Two ways to stop cleanly:

```bash
touch /Users/Hesham/Documents/quran-analytics/autoresearch/STOP
```
The orchestrator checks for this file each iteration and exits gracefully
after the current iteration finishes. The working tree is left clean.

Or just `Ctrl+C` — the SIGINT handler does `git reset --hard HEAD` before
exit, so the working tree always returns to the last committed state.

## Smoke testing (before a long run)

Each component has a `--once` or `--check` self-test:

```bash
# 1. Render a single chart, save PNG
python3 autoresearch/render.py --once

# 2. Run the 5 heuristic checks against the rendered chart
python3 autoresearch/eval_heuristic.py --once

# 3. Vision judge a saved PNG (costs ~$0.008)
python3 autoresearch/eval_vision.py --on autoresearch/runs/smoke/render_once.png

# 4. Repo + branch sanity
python3 autoresearch/git_ops.py --check

# 5. Propose 5 mutations to inspect the search space
python3 autoresearch/mutate.py --config electron-app/charts/configs/radar.json --n 5

# 6. Tiny full-loop smoke (no API costs, won't actually win — vision is stubbed)
python3 autoresearch/orchestrator.py --max-iters 5 --no-vision
```

## CLI flags

```
--max-iters N         hard iteration cap (default 200)
--patience N          stop after N iterations with no improvement (default 40)
--budget-usd USD      spend cap for vision API calls (default $25)
--max-hours H         wall-clock cap (default 8.0)
--branch NAME         target branch (default autoresearch/radar)
--seed N              RNG seed (default 42)
--improvement-margin  combined-score margin to commit (default 0.02)
--heuristic-drop      max heuristic drop vs best before gate-reject (default 0.05)
--structural-every N  force a structural mutation every N iters (default 20)
--allow-dirty         bypass the clean-tree preflight check
--no-vision           skip Claude vision; use stub (structural test only)
```

## What gets mutated

The loop only ever modifies `electron-app/charts/configs/radar.json`. The
Vue app reads this file at runtime via `fetch()` (see the `created()` hook
in `app.html`). Mutation surface — bounded knobs in `search_space.json`:

| Category | Knobs |
|---|---|
| Palette | swap to one of 8 curated 5-color sets, or HSL-shift the current set |
| Typography | angular/radial tickfont family + size, legend font size |
| Layout | margins (t/l/r/b), height, legend orientation/position |
| Polar | radial range max, angular rotation, tick values, gridcolor |
| Trace style | surah line width, marker size, fill alpha |
| Toggles | showlegend, radialaxis visibility |

Pre-flight schema validation rejects degenerate configs (margins eating
>50% of width, palette <5 colors, etc.) before they reach the renderer.

## How the evaluator works

Per iteration:

1. **Heuristic gate** (~600ms, free): 5 JS-injected checks
   - render error (catastrophic — chart didn't render at all)
   - label collision (axis + legend bbox overlaps)
   - margin sanity (plot area not strangled)
   - WCAG palette contrast + pairwise CIE76 ΔE distance
   - legend overflow

   Aggregate = mean of all 5 scores. If the candidate's aggregate drops
   more than `--heuristic-drop` below current best, gate-reject (skip
   vision). About 50% of mutations are gate-rejected on real data.

2. **Vision judge** (~3s, ~$0.008): if gate passed, screenshot the
   chart and send to Claude Sonnet 4.6 with `rubric.md`. Returns 7
   sub-scores + an `overall`. Cultural-fit weighted 1.5×.

3. **Combined score** = `0.4 * heuristic + 0.6 * vision_overall/10`.

4. If combined > best.combined + `--improvement-margin` (default 0.02):
   `git commit` on the branch. Else: `git reset --hard`.

## Cost expectations

- Heuristic-only iters (gate-rejected): **$0**
- Full path with vision: **~$0.008** per call
- Realistic overnight run: 500-700 iters, ~50% gate-rejected → **~$3-5/night**

Hard cap: `--budget-usd 25` (overridable). Loop stops as soon as it's hit.

## Project-local repo isolation (important)

The autoresearch loop runs ONLY against the project-local git repo at
`/Users/Hesham/Documents/quran-analytics/.git`. The parent
`/Users/Hesham/.git` is a separate (defensive `.gitignore=*`) repo. The
orchestrator's `git_ops.verify_repo()` refuses to start if pointed at
anything other than the project-local repo — this prevents `git reset
--hard` from ever touching the home directory.

Branch isolation: every run operates on `autoresearch/radar` (or
`--branch`). Wins land on that branch. `main` is never touched until you
explicitly merge.

## Expanding to other Page 17 charts

Once the chart-radar PoC produces 5+ committed wins you've reviewed:

1. Pick another chart (sunburst, treemap, heatmap, etc.).
2. Extract its inline Plotly config from `app.html` to
   `electron-app/charts/configs/<chart-name>.json` (the radar extraction
   is a model — see `git log d8c725f`).
3. Mirror the surgical patch in the relevant `render<Chart>` method
   (await chartCfgReady, route layout/style through the cfg).
4. Add a chart-type-specific knob block to `search_space.json`.
5. Spawn a per-chart orchestrator: `--branch autoresearch/<chart-name>`.

Each chart's loop is independent — you can run several in parallel by
giving each its own branch and run-dir. The HTTP server only needs to be
running once; just spawn multiple orchestrator processes.

## Files

```
electron-app/
├── app.html                                # Vue app (modified for JSON config)
└── charts/configs/
    ├── radar.json                          # mutated by the loop
    └── radar.baseline.json                 # immutable reference

autoresearch/
├── orchestrator.py                         # main loop
├── render.py                               # HTTP server + Playwright wrapper
├── mutate.py                               # propose + apply mutations
├── eval_heuristic.py                       # 5 JS-injected checks
├── eval_vision.py                          # Claude-vision judge
├── git_ops.py                              # project-local git wrappers
├── search_space.json                       # bounded mutation knobs
├── rubric.md                               # vision-judge rubric
├── smoke_test_app.py                       # one-shot patch verifier
├── pyproject.toml                          # deps
└── runs/                                   # per-run logs + screenshots (gitignored)
```

## Known limitations

- **Vision-judge calibration drift**: same screenshot can score ±0.5
  day-to-day. The `+0.02` improvement margin is calibrated against this
  noise floor. Every 25 iterations the orchestrator could re-judge the
  current best to track drift — not yet implemented.
- **Playwright Chromium ≠ Electron Chromium pixel-exact**: especially
  for Amiri (Arabic). The judge sees Playwright; you see Electron.
  Always eyeball-review winners in real Electron before merging.
- **Local-minimum risk**: random search will tend to converge on slight
  tweaks of the current config. The `--structural-every 20` flag forces
  a structural mutation (legend orientation, height ±60, polar rotation)
  every 20 iters as a defense.
