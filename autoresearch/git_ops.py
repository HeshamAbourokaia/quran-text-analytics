"""Project-local git wrappers for the AutoResearch loop.

Hard-checks that we're operating on the quran-analytics project repo,
NEVER on the parent /Users/Hesham home-directory repo. The orchestrator
calls verify_repo() at startup; mismatch raises and the loop refuses to
start.
"""
from __future__ import annotations

from pathlib import Path

import git

EXPECTED_TOPLEVEL = Path("/Users/Hesham/Documents/quran-analytics").resolve()


class WrongRepoError(RuntimeError):
    pass


class DirtyTreeError(RuntimeError):
    pass


def open_repo(path: Path | None = None) -> git.Repo:
    repo = git.Repo(path or EXPECTED_TOPLEVEL, search_parent_directories=False)
    return repo


def verify_repo(repo: git.Repo) -> None:
    """Raise if repo's working tree isn't the expected project-local one.

    Defends against: orchestrator accidentally pointed at /Users/Hesham,
    where reset/commit operations would touch the entire home directory.
    """
    actual = Path(repo.working_tree_dir).resolve()
    if actual != EXPECTED_TOPLEVEL:
        raise WrongRepoError(
            f"Refusing to operate. Expected toplevel {EXPECTED_TOPLEVEL}, got {actual}."
        )


def refuse_if_dirty(repo: git.Repo) -> None:
    if repo.is_dirty(untracked_files=True):
        dirty = [item.a_path for item in repo.index.diff(None)]
        untracked = repo.untracked_files
        raise DirtyTreeError(
            f"Working tree not clean. Modified: {dirty[:10]}  Untracked: {untracked[:10]}"
        )


def ensure_branch(repo: git.Repo, branch_name: str) -> None:
    """Switch to branch; create from current HEAD if it doesn't exist."""
    if branch_name in [h.name for h in repo.heads]:
        repo.git.checkout(branch_name)
    else:
        repo.git.checkout("-b", branch_name)


def commit_all(repo: git.Repo, message: str) -> str:
    """Stage all changes (respecting .gitignore) and commit. Returns sha."""
    repo.git.add("-A")
    repo.index.commit(message)
    return repo.head.commit.hexsha[:8]


def reset_hard(repo: git.Repo) -> None:
    """Discard all uncommitted changes. Working tree returns to HEAD."""
    repo.git.reset("--hard", "HEAD")
    repo.git.clean("-fd")  # remove any untracked files written this iteration


def commit_count_on_branch(repo: git.Repo, branch_name: str, since_ref: str = "main") -> int:
    """How many commits has the branch accumulated past its base?"""
    return sum(1 for _ in repo.iter_commits(f"{since_ref}..{branch_name}"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="verify repo is project-local + clean"
    )
    args = parser.parse_args()

    if args.check:
        repo = open_repo()
        verify_repo(repo)
        print(f"toplevel ok: {repo.working_tree_dir}")
        try:
            refuse_if_dirty(repo)
            print("tree clean")
        except DirtyTreeError as e:
            print(f"DIRTY: {e}")
        print(f"current branch: {repo.active_branch.name}")
