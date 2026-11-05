"""Small offline bootstrap: discover project, reuse installer, start interactive CLI."""

import argparse
import os
from pathlib import Path
import platform
import re
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


readmes = install.readmes


def candidates(cwd):
    """Only ancestors and immediate children; never scan a home tree recursively."""
    cwd = Path(os.path.abspath(cwd))
    origin = SOURCE.parent if cwd == SOURCE or SOURCE in cwd.parents else cwd
    # The documented entry is the task README cwd, even in a monorepo.
    if readmes(origin):
        return [origin]
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
    if target == SOURCE or SOURCE in target.parents:
        raise ValueError("target must be the task directory, outside the harness source")
    return install.task_root(target)


def capture(command, cwd):
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=10)


def describe(target):
    print(f"target={target}")
    print("README=" + ", ".join(str(p) for p in readmes(target)))
    print(f"existing AGENTS.md={(target / 'AGENTS.md').exists()}")
    print("entries=" + ", ".join(p.name for p in sorted(target.iterdir()) if p.name != ".git")[:600])
    print("지정 산출물·실행 방법: Codex가 위 README와 관련 진입점을 읽어 확인합니다.")
    if target in SOURCE.parents:
        print(f"SUBMISSION: 하네스 원본 {SOURCE.relative_to(target)} (내부 .git 포함)이 과제 폴더 안에 있습니다.")
        print("폴더 전체 제출에는 이 원본도 포함됩니다. .gitignore만으로 제출 용량에서 제외되지 않습니다.")
    else:
        print("SUBMISSION: 하네스 원본은 과제 폴더 밖입니다. 설치 지침은 과제 폴더 안에 추가됩니다.")
    print("P7에서 과제의 제출 범위·파일 수·실제 용량을 확인합니다. 원본/기존 파일 자동 삭제는 하지 않습니다.")
    git = shutil.which("git")
    if git:
        try:
            result = capture([git, "--no-optional-locks", "status", "--short", "--untracked-files=normal"], target)
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


def task_prompt(target=None):
    """Preserve old guides, but never silently launch using their stale contents."""
    guides = (("AGENTS.md", ".harness/AGENTS.md"),
              ("templates/START.md", ".harness/templates/START.md"))
    try:
        current = target and all((target / dest).is_file()
                                 and (target / dest).read_bytes() == (SOURCE / src).read_bytes()
                                 for src, dest in guides)
    except OSError:
        current = False
    if current:
        prompt = SHORT_PROMPT
    else:
        prompt = f'과제 README와 기존 AGENTS.md를 우선하고 "{SOURCE / "templates/START.md"}"와 "{SOURCE / "AGENTS.md"}"를 보조로 읽어 P1부터 P7까지 진행해.'
    return prompt + f' Skill 충돌/미인식 시 원본 "{SOURCE / "skills"}"의 해당 SKILL.md를 읽어.'


def model_guidance():
    print("Codex에서 /model 또는 제공 선택 화면으로 허용 모델을 먼저 선택합니다.")
    print("사용자 제공 시험 안내: Sol 6.1 권장; Sol 6.0 / Terra 5.6 / Luna 6.0. Astra·Claude 금지.")
    print("표시 이름을 CLI ID로 추측하지 않습니다. 현장 목록·규정이 우선이며 버전/설정은 변경하지 않습니다.")


def fallback(target=None, installed=False):
    print("Automatic recovery: no runtime/config/security changes. No automatic retry.")
    model_guidance()
    print("Next: 제공된 Codex 채팅에 한 문장 입력:")
    # Source-only recovery must work even when the destination cannot be read.
    print(task_prompt(target if installed else None))
    if target:
        print(f"작업 폴더: {target}")
    print("CLI/채팅 모두 없으면 감독자에게 제공 진입점을 문의합니다. 설치·업데이트·권한 우회는 하지 않습니다.")


def launch(target, model=None):
    command = cli_command()
    result = capture([*command, "--help"], target)
    if result.returncode or "[PROMPT]" not in result.stdout:
        raise ValueError(f"{command[0]} --help failed or interactive PROMPT unsupported (exit={result.returncode}): {result.stderr.strip()[:400]}")
    if model:
        if "--model" not in result.stdout:
            raise ValueError("provided codex --help does not advertise --model; use model selection in the provided chat")
        command += ["--model", model, task_prompt(target)]
        print(f"Starting interactive Codex with explicitly supplied model ID: {model}", flush=True)
    else:
        model_guidance()
        print("모델 선택 후 최초 프롬프트:\n" + task_prompt(target))
        print("Starting interactive Codex without a task prompt; select the allowed model first.", flush=True)
    # Inherit the terminal. Piping a prompt into `codex exec` would be one-shot.
    result = subprocess.run(command, cwd=target)
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
    parser.add_argument("--model", help="exact allowed model ID confirmed in the provided CLI; sends initial prompt automatically")
    args = parser.parse_args(argv)
    target = None
    installed = False
    try:
        if args.model is not None and (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]*", args.model)
                                       or any(name in args.model.lower() for name in ("astra", "claude"))):
            raise ValueError("invalid or prohibited model ID; select an allowed model in the provided Codex")
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
        for src, dest in ((SOURCE / "AGENTS.md", target / ".harness/AGENTS.md"),
                          (SOURCE / "templates/START.md", target / ".harness/templates/START.md")):
            if dest.read_bytes() != src.read_bytes():
                print(f"GUIDE fallback: preserved {dest}; read current source {src}")
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
        return launch(target, args.model)
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
