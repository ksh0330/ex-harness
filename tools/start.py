"""Small offline bootstrap: discover project, reuse installer, start interactive CLI."""

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

if __package__:
    from . import install
else:
    import install

SOURCE = install.SOURCE
SKILLS = ("discover", "agreement", "build-slice", "verify", "phase-gate",
          "handoff", "cross-review", "wrapup")
SHORT_PROMPT = "과제 README와 기존 AGENTS.md를 우선하고 .harness/templates/START.md와 .harness/AGENTS.md를 보조로 읽어 P1 분석부터 P7 전달까지 진행해."


def readmes(folder):
    return sorted(p for p in folder.iterdir()
                  if p.is_file() and (p.name.lower() == "readme" or p.name.lower().startswith("readme.")))


def candidates(cwd):
    """Only ancestors and immediate children; never scan a home tree recursively."""
    cwd = Path(os.path.abspath(cwd))
    origin = SOURCE.parent if cwd == SOURCE or SOURCE in cwd.parents else cwd
    found = set()
    for folder in (origin, *origin.parents):
        if folder == SOURCE or SOURCE in folder.parents:
            continue
        if readmes(folder):
            found.add(folder)
        if (folder / ".git").exists():
            break
    for folder in origin.iterdir():
        if (folder.is_dir() and not folder.is_symlink() and not folder.name.startswith(".")
                and folder.name not in ("node_modules", "vendor", "venv", "__pycache__")
                and folder != SOURCE and readmes(folder)):
            found.add(folder)
    return sorted(found)


def select_target(explicit=None, cwd=None):
    if explicit is not None:
        target = Path(os.path.abspath(explicit))
    else:
        options = candidates(cwd or Path.cwd())
        if len(options) == 1:
            target = options[0]
        else:
            print("Project candidates (README directories):")
            for number, folder in enumerate(options, 1):
                print(f"  {number}. {folder}")
            if not sys.stdin.isatty():
                raise ValueError("root is ambiguous or absent; use --target <README-directory>")
            answer = input("과제 루트 번호 또는 경로 (취소: 빈 입력): ").strip()
            if not answer:
                raise ValueError("root selection cancelled; no files changed")
            if answer.isdecimal():
                if not 1 <= int(answer) <= len(options):
                    raise ValueError("invalid root number; no files changed")
                target = options[int(answer) - 1]
            else:
                target = Path(os.path.abspath(Path(answer).expanduser()))
    install.plain_path(target)
    if target == SOURCE or SOURCE in target.parents:
        raise ValueError("target must be the task directory, outside the harness source")
    if not target.is_dir() or not readmes(target):
        raise ValueError(f"target needs a README: {target}")
    return target


def capture(command, cwd):
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=10)


def describe(target):
    print(f"target={target}")
    print("README=" + ", ".join(str(p) for p in readmes(target)))
    print(f"existing AGENTS.md={(target / 'AGENTS.md').exists()}")
    print("entries=" + ", ".join(p.name for p in sorted(target.iterdir()) if p.name != ".git")[:600])
    print("지정 산출물·실행 방법: Codex가 위 README와 관련 진입점을 읽어 확인합니다.")
    git = shutil.which("git")
    if git:
        try:
            result = capture([git, "status", "--short", "--untracked-files=normal"], target)
            print(f"git status exit={result.returncode}\n{result.stdout.strip()}")
            if result.returncode:
                print(result.stderr.strip())
                print("Git unavailable for this target; no git init or identity change.")
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"git status failed: {exc}; no Git changes.")
    else:
        print("git=not found; no git init.")


def cli_command():
    command = shutil.which("codex")
    if not command:
        raise ValueError("codex not found on PATH")
    if os.name == "nt" and Path(command).suffix.lower() in (".cmd", ".bat"):
        # Run the standard npm entry through Node; never interpolate a prompt
        # or project path into cmd.exe/batch syntax.
        entry = Path(command).parent / "node_modules/@openai/codex/bin/codex.js"
        node = shutil.which("node")
        if not node or not entry.is_file():
            raise ValueError("unsupported Codex batch launcher; use the provided Codex chat")
        return [node, str(entry)]
    return [command]


def fallback(target=None, installed=False):
    print("Automatic recovery: no runtime/config/security changes. No automatic retry.")
    if installed:
        print("Next: 제공된 Codex 채팅에 한 문장 입력:\n" + SHORT_PROMPT)
    else:
        print("Next: 제공된 Codex 채팅에 한 문장 입력:")
        print(f'과제 README와 기존 AGENTS.md를 먼저 읽고 "{SOURCE / "AGENTS.md"}"와 "{SOURCE / "templates/START.md"}"를 보조로 읽어 P1부터 P7까지 진행해.')
    if target:
        print(f"작업 폴더: {target}")
    print("CLI/채팅 모두 없으면 감독자에게 제공 진입점을 문의합니다. 설치·업데이트·권한 우회는 하지 않습니다.")


def launch(target):
    command = cli_command()
    result = capture([*command, "--help"], target)
    if result.returncode or "[PROMPT]" not in result.stdout:
        raise ValueError(f"{command[0]} --help failed or interactive PROMPT unsupported (exit={result.returncode}): {result.stderr.strip()[:400]}")
    prompt = SHORT_PROMPT + f' Skill 충돌/미인식 시 원본 "{SOURCE / "skills"}"의 해당 SKILL.md를 읽어.'
    print("Starting interactive Codex [PROMPT] in the target; no exec or policy overrides.", flush=True)
    # Inherit the terminal. Piping a prompt into `codex exec` would be one-shot.
    result = subprocess.run([*command, prompt], cwd=target)
    if result.returncode:
        print(f"FAILED interactive Codex exit={result.returncode}; installation is present, session start not confirmed.", file=sys.stderr)
        fallback(target, installed=True)
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, help="explicit task README directory")
    parser.add_argument("--preview", action="store_true", help="show plan; no writes or CLI launch")
    parser.add_argument("--no-launch", action="store_true", help="install only, print one-sentence chat prompt")
    parser.add_argument("--existing-session", action="store_true", help="install but do not nest another Codex session")
    args = parser.parse_args(argv)
    target = None
    installed = False
    try:
        print(f"cwd={Path.cwd()}\nharness={SOURCE}\nos={platform.system()}\npython={sys.executable} {platform.python_version()}")
        for name in ("bash", "sh", "python3", "python", "codex"):
            print(f"{name}={shutil.which(name) or 'not found'}")
        target = select_target(args.target)
        describe(target)
        for name in SKILLS:
            source = SOURCE / "skills" / name / "SKILL.md"
            install.plain_path(source)
            if not source.is_file():
                raise ValueError(f"missing source skill: {source}")
        pairs = install.plan(target)
        print(f"PLAN create={sum(not dest.exists() for _, dest in pairs)} keep={sum(dest.exists() for _, dest in pairs)}; existing files preserved; no config/Git writes.")
        if args.preview:
            print("mode=preview; no writes or Codex launch")
            return 0
        created = install.apply_plan(pairs)
        installed = True
        present = 0
        for name in SKILLS:
            path = target / ".agents/skills" / name / "SKILL.md"
            install.plain_path(path)
            if path.is_file():
                present += 1
            if not path.is_file() or path.read_bytes() != (SOURCE / "skills" / name / "SKILL.md").read_bytes():
                print(f"SKILL fallback ({name}): read {SOURCE / 'skills' / name / 'SKILL.md'}")
        print(f"installed created={created}; skill files={present}/8; runtime recognition NOT verified.")
        if args.no_launch or args.existing_session or os.environ.get("CODEX_THREAD_ID"):
            if args.existing_session or os.environ.get("CODEX_THREAD_ID"):
                print("현재 세션을 보존합니다. 목록 미갱신 시 HANDOFF·Git 상태 저장 후 제공 터미널에서 codex resume으로 선택 재개합니다.")
            else:
                print("--no-launch: 설치만 수행했습니다. 제공 채팅에 아래 문장을 입력합니다.")
            fallback(target, installed=True)
            return 0
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print("Interactive terminal unavailable; CLI not launched.", file=sys.stderr)
            fallback(target, installed=True)
            return 2
        return launch(target)
    except (OSError, ValueError, subprocess.TimeoutExpired, EOFError) as exc:
        print(f"FAILED bootstrap: {exc}", file=sys.stderr)
        fallback(target, installed)
        return 2
    except KeyboardInterrupt:
        print("Interrupted; no automatic retry. Inspect Git status and existing files before resuming.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("Python 3.10+ required; no install. Read templates/START.md in the provided Codex chat.", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main())
