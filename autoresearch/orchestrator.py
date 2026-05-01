"""AutoResearch loop orchestrator for chart-radar.

Main loop:
    while not stopping:
        mutation = mutate.propose(...)
        candidate = mutate.apply(best_cfg, mutation)
        if not mutate.validate(candidate):
            skip
        write candidate to radar.json
        renderer.reload_config_and_render()
        h = run_heuristics(page)
        if h.fail or h.score < best.heuristic - 0.05:
            git_ops.reset_hard(); continue
        v = eval_vision.judge(screenshot)
        combined = 0.4 * h.score + 0.6 * v.overall/10
        if combined > best.combined + 0.02:
            git_ops.commit(...); update best
        else:
            git_ops.reset_hard()
"""
from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import os
import random
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import anthropic

import eval_heuristic
import eval_vision
import git_ops
import mutate
from render import HttpServer, RadarRenderer

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CFG_PATH = PROJECT_ROOT / "electron-app" / "charts" / "configs" / "radar.json"
BASELINE_PATH = PROJECT_ROOT / "electron-app" / "charts" / "configs" / "radar.baseline.json"
RUNS_DIR = Path(__file__).parent / "runs"
STOP_FILE = Path(__file__).parent / "STOP"
DEFAULT_BRANCH = "autoresearch/radar"


@dataclass
class Best:
    config: dict
    heuristic_score: float
    vision_overall: float
    combined: float
    commit_sha: str | None = None


@dataclass
class State:
    iters: int = 0
    since_improvement: int = 0
    spent_usd: float = 0.0
    started_at: float = field(default_factory=time.time)


def stop_requested(state: State, args: argparse.Namespace) -> tuple[bool, str]:
    if state.iters >= args.max_iters:
        return True, f"max iters reached ({args.max_iters})"
    if state.since_improvement >= args.patience:
        return True, f"patience exhausted ({args.patience} since last improvement)"
    if state.spent_usd >= args.budget_usd:
        return True, f"budget cap hit (${state.spent_usd:.3f} >= ${args.budget_usd:.2f})"
    elapsed_h = (time.time() - state.started_at) / 3600
    if elapsed_h >= args.max_hours:
        return True, f"wall-clock {elapsed_h:.2f}h >= {args.max_hours}h"
    if STOP_FILE.exists():
        return True, "STOP file present"
    return False, ""


def write_config(cfg: dict) -> None:
    CFG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")


def append_log(run_dir: Path, record: dict) -> None:
    with (run_dir / "log.jsonl").open("a") as fh:
        fh.write(json.dumps(record) + "\n")


async def score_full(
    renderer: RadarRenderer,
    run_dir: Path,
    iter_idx: int,
    label: str,
    a_client: anthropic.Anthropic | None,
) -> tuple[eval_heuristic.HeuristicResult, eval_vision.VisionResult]:
    """Render + heuristic + vision (or stub vision), returning everything."""
    h = await eval_heuristic.run_heuristics(renderer.page)
    shot = run_dir / "shots" / f"iter_{iter_idx:04d}_{label}.png"
    shot.parent.mkdir(parents=True, exist_ok=True)
    await renderer.screenshot(shot)
    if a_client is None:
        # No-vision mode: stub a neutral vision score so the combined-score
        # arithmetic still works and the loop is structurally exercised.
        v = eval_vision.VisionResult(
            scores={},
            overall=6.0,
            notes="(no-vision mode)",
            cost_usd=0.0,
            cached=True,
        )
    else:
        v = eval_vision.judge(shot, client=a_client)
    return h, v


def combined_score(h_score: float, v_overall: float) -> float:
    return 0.4 * h_score + 0.6 * v_overall / 10


async def run(args: argparse.Namespace) -> int:
    # === Phase 0: safety preflight ===
    repo = git_ops.open_repo()
    git_ops.verify_repo(repo)
    if not args.allow_dirty:
        try:
            git_ops.refuse_if_dirty(repo)
        except git_ops.DirtyTreeError as e:
            print(f"FATAL: {e}", file=sys.stderr)
            return 2

    if not args.no_vision and not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "FATAL: ANTHROPIC_API_KEY not set. "
            "Either export it or run with --no-vision (heuristic-only loop).",
            file=sys.stderr,
        )
        return 2

    git_ops.ensure_branch(repo, args.branch)
    print(f"[preflight] repo={repo.working_tree_dir} branch={args.branch}")

    # === Phase 1: setup ===
    rng = random.Random(args.seed)
    space = mutate.load_space()
    a_client = None if args.no_vision else anthropic.Anthropic()

    run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S") + "_radar"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[setup] run dir: {run_dir}")

    # Reset config to baseline so we always start from a known state
    baseline_cfg = json.loads(BASELINE_PATH.read_text())
    write_config(baseline_cfg)

    state = State()

    with HttpServer() as srv:
        renderer = RadarRenderer(srv.url)
        await renderer.start()

        # === Phase 2: baseline scoring ===
        print("[baseline] scoring iter 0...")
        h0, v0 = await score_full(renderer, run_dir, 0, "baseline", a_client)
        state.spent_usd += v0.cost_usd if not v0.cached else 0
        best_combined = combined_score(h0.score, v0.overall)
        best = Best(
            config=baseline_cfg,
            heuristic_score=h0.score,
            vision_overall=v0.overall,
            combined=best_combined,
            commit_sha=None,
        )
        append_log(
            run_dir,
            {
                "iter": 0,
                "label": "baseline",
                "heuristic": dataclasses.asdict(h0),
                "vision": v0.as_dict(),
                "combined": best_combined,
                "accepted": True,
                "spent_usd": state.spent_usd,
            },
        )
        print(
            f"[baseline] heuristic={h0.score:.3f} vision={v0.overall:.2f}/10 "
            f"combined={best_combined:.3f} spent=${state.spent_usd:.4f}"
        )

        # === Phase 3: main loop ===
        while True:
            should_stop, why = stop_requested(state, args)
            if should_stop:
                print(f"[stop] {why}")
                break

            state.iters += 1
            force_structural = state.iters % args.structural_every == 0
            mut = mutate.propose(
                space, best.config, force_structural=force_structural, rng=rng
            )
            candidate = mutate.apply(best.config, mut)
            ok, reason = mutate.validate(candidate, space)
            if not ok:
                state.since_improvement += 1
                append_log(
                    run_dir,
                    {
                        "iter": state.iters,
                        "mutation": mut.as_dict(),
                        "skipped_validation": reason,
                    },
                )
                continue

            write_config(candidate)
            try:
                await renderer.reload_config_and_render()
            except Exception as e:
                print(f"[iter {state.iters}] render error: {e}; resetting")
                git_ops.reset_hard(repo)
                state.since_improvement += 1
                continue

            h = await eval_heuristic.run_heuristics(renderer.page)

            # Heuristic gate: catastrophic render failure OR meaningful score drop
            if h.fail or h.score < best.heuristic_score - args.heuristic_drop:
                # `h.fail` here means render_error only (eval_heuristic now
                # restricts `fail` to catastrophic cases). Soft fails like
                # WCAG-below-2.5 just lower the score and are gated by the
                # relative drop.
                git_ops.reset_hard(repo)
                state.since_improvement += 1
                append_log(
                    run_dir,
                    {
                        "iter": state.iters,
                        "mutation": mut.as_dict(),
                        "heuristic": dataclasses.asdict(h),
                        "vision": None,
                        "decision": "gate_rejected",
                        "spent_usd": state.spent_usd,
                    },
                )
                if state.iters % 10 == 0:
                    print(
                        f"[iter {state.iters}] gate-reject ({mut.summary})  "
                        f"h={h.score:.3f} since_imp={state.since_improvement}"
                    )
                continue

            # Vision judge (or stub in --no-vision mode)
            shot = run_dir / "shots" / f"iter_{state.iters:04d}.png"
            shot.parent.mkdir(parents=True, exist_ok=True)
            await renderer.screenshot(shot)
            if a_client is None:
                # --no-vision: stub a deterministic-ish score so structural
                # tests still produce wins and rejects.
                v = eval_vision.VisionResult(
                    scores={},
                    overall=6.0 + (h.score - best.heuristic_score) * 5,
                    notes="(no-vision mode)",
                    cost_usd=0.0,
                    cached=True,
                )
            else:
                v = eval_vision.judge(shot, client=a_client)
            if not v.cached:
                state.spent_usd += v.cost_usd

            combined = combined_score(h.score, v.overall)
            improvement = combined - best.combined
            accepted = improvement > args.improvement_margin

            if accepted:
                msg = (
                    f"radar: {mut.summary} | h={h.score:.2f} v={v.overall:.1f}/10 "
                    f"combined={combined:.3f} (+{improvement:.3f})"
                )
                sha = git_ops.commit_all(repo, msg)
                best = Best(
                    config=candidate,
                    heuristic_score=h.score,
                    vision_overall=v.overall,
                    combined=combined,
                    commit_sha=sha,
                )
                state.since_improvement = 0
                print(
                    f"[iter {state.iters}] [WIN] {msg} sha={sha} "
                    f"spent=${state.spent_usd:.4f}"
                )
            else:
                git_ops.reset_hard(repo)
                # screenshot was orphaned by reset — but we keep it on disk
                # by virtue of being inside autoresearch/runs (gitignored)
                state.since_improvement += 1
                if state.iters % 10 == 0:
                    print(
                        f"[iter {state.iters}] reject ({mut.summary})  "
                        f"h={h.score:.2f} v={v.overall:.1f} combined={combined:.3f} "
                        f"(best {best.combined:.3f}, since_imp={state.since_improvement})"
                    )

            append_log(
                run_dir,
                {
                    "iter": state.iters,
                    "mutation": mut.as_dict(),
                    "heuristic": dataclasses.asdict(h),
                    "vision": v.as_dict(),
                    "combined": combined,
                    "decision": "accept" if accepted else "reject",
                    "best_so_far": best.combined,
                    "spent_usd": state.spent_usd,
                },
            )

        # === Phase 4: shutdown ===
        await renderer.stop()

    print(
        f"\n=== run summary ===\n"
        f"iters: {state.iters}\n"
        f"final best: heuristic={best.heuristic_score:.3f} "
        f"vision={best.vision_overall:.2f}/10 combined={best.combined:.3f}\n"
        f"final commit: {best.commit_sha}\n"
        f"spent: ${state.spent_usd:.4f}\n"
        f"branch: {args.branch}\n"
        f"log: {run_dir}/log.jsonl"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AutoResearch loop for chart-radar")
    parser.add_argument("--max-iters", type=int, default=200)
    parser.add_argument("--patience", type=int, default=40, help="iters since improvement before stop")
    parser.add_argument("--budget-usd", type=float, default=25.0, help="total API spend cap")
    parser.add_argument("--max-hours", type=float, default=8.0)
    parser.add_argument("--branch", type=str, default=DEFAULT_BRANCH)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--improvement-margin",
        type=float,
        default=0.02,
        help="strict combined-score margin required to commit",
    )
    parser.add_argument(
        "--heuristic-drop",
        type=float,
        default=0.05,
        help="how far heuristic can fall vs best before gate-reject",
    )
    parser.add_argument(
        "--structural-every",
        type=int,
        default=20,
        help="force a structural mutation every N iterations",
    )
    parser.add_argument("--allow-dirty", action="store_true", help="bypass clean-tree check")
    parser.add_argument(
        "--no-vision",
        action="store_true",
        help="skip Claude vision judge; use stub scores. For structural smoke testing only — "
        "the loop won't actually find aesthetic improvements without real vision feedback.",
    )
    args = parser.parse_args()

    # Graceful Ctrl-C: ensure git tree returns to clean before exit
    def handle_sigint(signum, frame):
        try:
            repo = git_ops.open_repo()
            git_ops.reset_hard(repo)
        except Exception:
            pass
        print("\n[interrupt] reset working tree to HEAD; exiting.")
        sys.exit(130)

    signal.signal(signal.SIGINT, handle_sigint)

    return asyncio.run(run(args))


if __name__ == "__main__":
    sys.exit(main())
