"""Offline, additive installer. Preview by default; never changes Git/config."""

import argparse
import os
from pathlib import Path
import shutil
import stat
import sys

SOURCE = Path(__file__).resolve().parents[1]


def plain_path(path):
    """Reject symlinks and Windows junction/reparse points, including parents."""
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError(f"linked path is not allowed: {part}")


def plan(target, with_examples=False):
    target = Path(os.path.abspath(target))
    plain_path(target)
    if target == SOURCE or SOURCE in target.parents:
        raise ValueError("target must be outside the harness source")
    if target.exists() and not target.is_dir():
        raise ValueError("target must be a directory")
    pairs = [(SOURCE / "AGENTS.md", target / "AGENTS.md"),
             (SOURCE / "AGENTS.md", target / ".harness/AGENTS.md"),
             (SOURCE / "templates/GUIDE.md", target / ".harness/GUIDE.md")]
    for src in sorted((SOURCE / "templates").rglob("*")):
        if src.is_file() and src.name != "GUIDE.md":
            pairs.append((src, target / ".harness/templates" / src.relative_to(SOURCE / "templates")))
    # Only operational guides belong in a target project, not this repo's status.
    for name in ("BASICS.md", "MORNING.md", "QUICKSTART.md", "MANUAL.md", "ARCHITECTURE.md", "SIMULATION.md", "SOURCES.md", "VERIFICATION.md"):
        src = SOURCE / "docs" / name
        if src.is_file():
            pairs.append((src, target / ".harness/docs" / name))
    for folder, destination in ((SOURCE / "docs/assets", target / ".harness/docs/assets"),
                                (SOURCE / "examples/tasks", target / ".harness/examples/tasks")):
        for src in sorted(folder.rglob("*")):
            if src.is_file():
                pairs.append((src, destination / src.relative_to(folder)))
    for skill in sorted((SOURCE / "skills").iterdir()):
        dest = target / ".agents/skills" / skill.name
        plain_path(dest)
        if dest.exists():  # An existing skill is one unit: do not merge versions.
            continue
        for src in sorted(skill.rglob("*")):
            if src.is_file():
                pairs.append((src, dest / src.relative_to(skill)))
    if with_examples:
        for name in ("fde", "examples"):
            for src in sorted((SOURCE / name).rglob("*")):
                if src.is_file() and "__pycache__" not in src.parts and src.suffix != ".pyc":
                    pairs.append((src, target / ".harness/kit" / src.relative_to(SOURCE)))
    # Validate the entire plan before any directory/file creation.
    for src, dest in pairs:
        plain_path(src)
        plain_path(dest)
        if not src.is_file():
            raise ValueError(f"missing source: {src}")
        if dest.exists() and not dest.is_file():
            raise ValueError(f"file destination is a directory: {dest}")
        for parent in dest.parents:
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"parent is not a directory: {parent}")
    return pairs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true", help="create missing files")
    parser.add_argument("--with-examples", action="store_true", help="copy optional Python kit")
    args = parser.parse_args(argv)
    try:
        pairs = plan(args.target, args.with_examples)
        created = 0
        for src, dest in pairs:
            if dest.exists():
                print(f"KEEP {dest}")
                continue
            print(f"{'CREATE' if args.apply else 'PLAN'} {dest}")
            if args.apply:
                plain_path(dest)
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open("xb") as output, src.open("rb") as source:
                    shutil.copyfileobj(source, output)
                created += 1
        print(f"created={created}; mode={'apply' if args.apply else 'preview'}")
        print("Existing files/skills are kept; no automatic upgrades. Read .harness/AGENTS.md explicitly when AGENTS.md already exists.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"install: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
