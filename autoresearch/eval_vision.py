"""Claude-vision aesthetic judge for chart-radar.

Sends the screenshot + rubric to Claude Sonnet 4.6 (vision-capable),
gets back a strict-JSON rubric scoring. Returns scores, overall, notes,
and the cost in USD for cost-budget enforcement.

Caches by (model, sha256(screenshot_bytes), sha256(rubric_text)) — same
config rendered twice in different iterations gets the cached score.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"  # Hesham's stack default per CLAUDE.md
RUBRIC_PATH = Path(__file__).parent / "rubric.md"
CACHE_DIR = Path(__file__).parent / "runs" / "_vision_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Sonnet 4.6 pricing (per 1M tokens) — ~$3 input / $15 output per Anthropic docs.
# A 720x720 image is roughly 1300 input tokens.
SONNET_PER_1M_INPUT = 3.00
SONNET_PER_1M_OUTPUT = 15.00


@dataclass
class VisionResult:
    scores: dict[str, int]
    overall: float
    notes: str
    cost_usd: float
    cached: bool = False
    raw: dict | None = None

    def as_dict(self) -> dict:
        return {
            "scores": self.scores,
            "overall": self.overall,
            "notes": self.notes,
            "cost_usd": round(self.cost_usd, 5),
            "cached": self.cached,
        }


def _cache_key(model: str, image_bytes: bytes, rubric_text: str) -> Path:
    h = hashlib.sha256()
    h.update(model.encode())
    h.update(image_bytes)
    h.update(rubric_text.encode())
    return CACHE_DIR / f"{h.hexdigest()}.json"


def _strict_json_extract(text: str) -> dict:
    """Claude usually obeys 'strict JSON' but may wrap in ```json fences."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def judge(
    screenshot_path: Path,
    rubric_text: str | None = None,
    model: str = DEFAULT_MODEL,
    client: Optional[anthropic.Anthropic] = None,
    use_cache: bool = True,
) -> VisionResult:
    if rubric_text is None:
        rubric_text = RUBRIC_PATH.read_text()
    image_bytes = screenshot_path.read_bytes()

    cache_path = _cache_key(model, image_bytes, rubric_text)
    if use_cache and cache_path.exists():
        cached = json.loads(cache_path.read_text())
        return VisionResult(
            scores=cached["scores"],
            overall=cached["overall"],
            notes=cached["notes"],
            cost_usd=0.0,
            cached=True,
            raw=cached,
        )

    if client is None:
        client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY from env

    image_b64 = base64.standard_b64encode(image_bytes).decode()
    msg = client.messages.create(
        model=model,
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": rubric_text},
                ],
            }
        ],
    )

    response_text = "".join(b.text for b in msg.content if b.type == "text")
    parsed = _strict_json_extract(response_text)

    in_tokens = msg.usage.input_tokens
    out_tokens = msg.usage.output_tokens
    cost = (
        in_tokens * SONNET_PER_1M_INPUT / 1_000_000
        + out_tokens * SONNET_PER_1M_OUTPUT / 1_000_000
    )

    scores = parsed.get("scores", {})
    overall_raw = parsed.get("overall", 0)
    notes = parsed.get("notes", "")[:300]

    # Cultural-fit weighting: bake the 1.5x boost into combined-score callers
    # by exposing both raw and weighted overall here for transparency.
    cultural = scores.get("cultural_fit", 0)
    weighted_overall = (overall_raw * 6 + cultural * 1.5) / 7.5  # normalised
    final_overall = max(1, min(10, weighted_overall))

    result = VisionResult(
        scores=scores,
        overall=round(final_overall, 2),
        notes=notes,
        cost_usd=cost,
        cached=False,
        raw=parsed,
    )

    cache_path.write_text(json.dumps(result.as_dict()))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--on", type=str, required=True, help="screenshot PNG path")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. export it before running.", file=sys.stderr)
        sys.exit(2)

    result = judge(Path(args.on), use_cache=not args.no_cache)
    print(json.dumps(result.as_dict(), indent=2))
