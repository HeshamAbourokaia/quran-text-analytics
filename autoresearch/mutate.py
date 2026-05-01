"""Mutation logic for the chart-radar AutoResearch loop.

Reads search_space.json and proposes/applies bounded mutations to the
chart config. Knob types: set_swap, int_range, float_range, hsl_shift.

Public API:
    space = load_space()
    mutation = propose(space, current_config, history, force_structural=False)
    new_config = apply(current_config, mutation)
    ok = validate(new_config, space)
"""
from __future__ import annotations

import colorsys
import copy
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SPACE_PATH = Path(__file__).parent / "search_space.json"


@dataclass
class Mutation:
    knob: str
    path: str
    new_value: Any
    summary: str
    structural: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


def load_space(path: Path = SPACE_PATH) -> dict:
    return json.loads(path.read_text())


def _get_path(obj: Any, dotted: str) -> Any:
    """Read obj at dotted path. Supports list indexing via path[N]."""
    parts = _split_path(dotted)
    cur = obj
    for p in parts:
        cur = cur[p]
    return cur


def _set_path(obj: Any, dotted: str, value: Any) -> None:
    parts = _split_path(dotted)
    cur = obj
    for p in parts[:-1]:
        cur = cur[p]
    cur[parts[-1]] = value


def _split_path(dotted: str) -> list:
    """'layout.polar.radialaxis.range[1]' -> ['layout', 'polar', 'radialaxis', 'range', 1]."""
    parts: list = []
    for seg in dotted.split("."):
        # Handle list-index brackets
        if "[" in seg:
            name, rest = seg.split("[", 1)
            if name:
                parts.append(name)
            idx = int(rest.rstrip("]"))
            parts.append(idx)
        else:
            parts.append(seg)
    return parts


def _hex_to_hsl(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, ss, ll


def _hsl_to_hex(h: float, s: float, ll: float) -> str:
    h = (h % 360) / 360.0
    s = max(0.0, min(1.0, s))
    ll = max(0.0, min(1.0, ll))
    r, g, b = colorsys.hls_to_rgb(h, ll, s)
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def propose(
    space: dict,
    current_config: dict,
    history: list[dict] | None = None,
    force_structural: bool = False,
    rng: random.Random | None = None,
) -> Mutation:
    rng = rng or random.Random()
    knobs = space["knobs"]
    if force_structural:
        candidates = [k for k in knobs if k.get("structural")]
    else:
        candidates = knobs
    weights = [k.get("weight", 1) for k in candidates]
    knob = rng.choices(candidates, weights=weights, k=1)[0]
    return _mutation_from_knob(knob, current_config, rng)


def _mutation_from_knob(knob: dict, cfg: dict, rng: random.Random) -> Mutation:
    t = knob["type"]
    name = knob["name"]
    path = knob["path"]
    structural = bool(knob.get("structural", False))
    summary_tpl = knob.get("summary_template", f"{name} -> {{0}}")

    if t == "set_swap":
        options = list(knob["options"])
        try:
            current = _get_path(cfg, path)
        except Exception:
            current = None
        # Avoid no-op: pick a different option than current
        choices = [o for o in options if o != current]
        if not choices:
            choices = options
        new_val = rng.choice(choices)
        if isinstance(new_val, list):
            summary = summary_tpl.format(*new_val)
        else:
            summary = summary_tpl.format(new_val)
        return Mutation(name, path, new_val, summary, structural)

    if t == "int_range":
        lo, hi, step = knob["min"], knob["max"], knob.get("step", 1)
        steps = list(range(lo, hi + 1, step))
        try:
            current = _get_path(cfg, path)
        except Exception:
            current = None
        choices = [s for s in steps if s != current]
        if not choices:
            choices = steps
        new_val = rng.choice(choices)
        return Mutation(name, path, new_val, summary_tpl.format(new_val), structural)

    if t == "float_range":
        lo, hi, step = knob["min"], knob["max"], knob.get("step", 0.1)
        n = int(round((hi - lo) / step)) + 1
        steps = [round(lo + i * step, 4) for i in range(n)]
        try:
            current = _get_path(cfg, path)
        except Exception:
            current = None
        choices = [s for s in steps if s != current]
        if not choices:
            choices = steps
        new_val = rng.choice(choices)
        return Mutation(name, path, new_val, summary_tpl.format(new_val), structural)

    if t == "hsl_shift":
        # Shifts every color in the palette by the same HSL delta
        dh = rng.uniform(*knob["hue_delta_range"])
        ds = rng.uniform(*knob["saturation_delta_range"])
        dl = rng.uniform(*knob["lightness_delta_range"])
        try:
            palette = _get_path(cfg, path)
        except Exception:
            palette = []
        new_palette = []
        for c in palette:
            h, s, ll = _hex_to_hsl(c)
            new_palette.append(_hsl_to_hex(h + dh, s + ds, ll + dl))
        return Mutation(
            name,
            path,
            new_palette,
            summary_tpl.format(dh=int(dh), ds=ds, dl=dl),
            structural,
        )

    raise ValueError(f"unknown knob type: {t}")


def apply(cfg: dict, mutation: Mutation) -> dict:
    new_cfg = copy.deepcopy(cfg)
    _set_path(new_cfg, mutation.path, mutation.new_value)
    return new_cfg


def validate(cfg: dict, space: dict) -> tuple[bool, str]:
    """Pre-render schema/sanity guards. Returns (ok, reason)."""
    g = space.get("guards", {})
    palette = cfg.get("palette", [])
    if len(palette) < g.get("palette_min_size", 5):
        return False, f"palette too small ({len(palette)})"
    layout = cfg.get("layout", {})
    h = layout.get("height", 0)
    margin = layout.get("margin", {})
    plot_h = h - margin.get("t", 0) - margin.get("b", 0)
    width = 1100  # viewport-bounded
    plot_w = width - margin.get("l", 0) - margin.get("r", 0)
    if plot_h < g.get("min_plot_height", 240):
        return False, f"plot height too small ({plot_h})"
    if plot_w < g.get("min_plot_width", 320):
        return False, f"plot width too small ({plot_w})"
    radial_max = layout.get("polar", {}).get("radialaxis", {}).get("range", [0, 0])[1]
    if radial_max < g.get("radial_range_min", 100):
        return False, f"radial range max too small ({radial_max})"
    return True, "ok"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--n", type=int, default=5, help="propose N mutations and print them")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    space = load_space()
    cfg = json.loads(Path(args.config).read_text())
    rng = random.Random(args.seed)
    for i in range(args.n):
        m = propose(space, cfg, rng=rng)
        new_cfg = apply(cfg, m)
        ok, reason = validate(new_cfg, space)
        print(f"[{i}] {m.summary}  -> valid={ok} ({reason})")
