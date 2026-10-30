"""Dependency-free checks for this repository's deliberately small skill format."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def check():
    errors = []
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for path in skills:
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0] != "":
            errors.append(f"{path}: missing frontmatter")
            continue
        fields = dict(line.split(": ", 1) for line in parts[1].strip().splitlines() if ": " in line)
        if fields.get("name") != path.parent.name or not re.fullmatch(r"[a-z0-9-]{1,64}", fields.get("name", "")):
            errors.append(f"{path}: invalid name")
        if not fields.get("description") or not parts[2].strip():
            errors.append(f"{path}: missing description/body")
    # Local Markdown references in authoring docs must resolve, including images.
    for path in [ROOT / "README.md", *(ROOT / "docs").rglob("*.md")]:
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            if not (path.parent / target.split("#", 1)[0]).exists():
                errors.append(f"{path.relative_to(ROOT)}: missing link {target}")
    for error in errors:
        print(error)
    print(f"skills={len(skills)}; errors={len(errors)} (restricted frontmatter/link check; not the official YAML validator)")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(check())
