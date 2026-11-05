"""Bootstrap boundaries use a local fake CLI, never credentials or an AI call."""

from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import install, start


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class StartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "task with spaces"
        self.project.mkdir()
        (self.project / "README.md").write_text("# Synthetic task\nKeep output in result.json.\n", encoding="utf-8")
        self.fake = self.base / "fake_cli.py"
        self.fake.write_text('''import json, os, pathlib, sys
if sys.argv[1:] == ["--help"]:
    print("Usage: codex [OPTIONS] [PROMPT] --model MODEL")
else:
    pathlib.Path("cli-call.json").write_text(json.dumps({"cwd": os.getcwd(), "args": sys.argv[1:]}, ensure_ascii=False), encoding="utf-8")
    sys.exit(int(os.environ.get("FAKE_CODEX_EXIT", "0")))
''', encoding="utf-8")
        self.output = io.StringIO()

    def run_start(self, *args, tty=True, env=None):
        with redirect_stdout(self.output), redirect_stderr(self.output), \
                patch.dict(os.environ, {"CODEX_THREAD_ID": "", **(env or {})}), \
                patch.object(sys.stdin, "isatty", return_value=tty), \
                patch.object(self.output, "isatty", return_value=tty), \
                patch.object(start, "cli_command", return_value=[sys.executable, str(self.fake)]):
            return start.main(["--target", str(self.project), *args])

    def test_default_installs_and_waits_for_model_selection_without_prompt(self):
        self.assertEqual(self.run_start(), 0, self.output.getvalue())
        call = json.loads((self.project / "cli-call.json").read_text(encoding="utf-8"))
        self.assertEqual(Path(call["cwd"]), self.project)
        self.assertEqual(call["args"], [])
        self.assertIn("/model", self.output.getvalue())
        self.assertNotIn("exec", call["args"])
        for name in start.SKILLS:
            self.assertTrue((self.project / ".agents/skills" / name / "SKILL.md").is_file())
        self.assertFalse((self.project / ".git").exists())
        self.assertFalse((self.project / ".codex").exists())
        self.assertFalse((self.project / ".harness/hooks").exists())

    def test_explicit_model_passes_exact_id_and_one_prompt(self):
        self.assertEqual(self.run_start("--model", "provided-sol-id"), 0, self.output.getvalue())
        call = json.loads((self.project / "cli-call.json").read_text(encoding="utf-8"))
        self.assertEqual(call["args"][:2], ["--model", "provided-sol-id"])
        self.assertEqual(len(call["args"]), 3)
        self.assertIn("P1", call["args"][2])

    def test_invalid_or_prohibited_model_never_installs(self):
        before = snapshot(self.project)
        for model in ("gpt-6-astra", "Claude", "", "Sol 6.1", "-flag", "model\nID"):
            with self.subTest(model=model):
                self.assertEqual(self.run_start("--model=" + model), 2)
                self.assertEqual(before, snapshot(self.project))

    def test_model_flag_requires_cli_support(self):
        with patch.object(start, "capture", return_value=subprocess.CompletedProcess([], 0, "Usage: codex [OPTIONS] [PROMPT]", "")):
            self.assertEqual(self.run_start("--model", "provided-sol-id"), 2)
        self.assertFalse((self.project / "cli-call.json").exists())

    def test_stale_guides_preserved_but_current_source_is_used(self):
        for name in (".harness/templates/START.md", ".harness/AGENTS.md"):
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("old guidance", encoding="utf-8")
        self.assertEqual(self.run_start("--model", "provided-sol-id"), 0, self.output.getvalue())
        call = json.loads((self.project / "cli-call.json").read_text(encoding="utf-8"))
        self.assertIn(str(ROOT / "templates/START.md"), call["args"][-1])
        self.assertNotIn(".harness/templates", call["args"][-1])
        self.assertIn("GUIDE fallback", self.output.getvalue())
        self.assertEqual((self.project / ".harness/AGENTS.md").read_text(), "old guidance")

    def test_current_readme_wins_over_parent_and_child_readmes(self):
        (self.base / "README.md").write_text("parent")
        child = self.project / "service"
        child.mkdir()
        (child / "README.md").write_text("child")
        self.assertEqual(start.select_target(cwd=self.project), self.project)

    def test_submission_notice_distinguishes_nested_and_sibling_source(self):
        for source, expected in ((self.project / "ex-harness", "내부 .git 포함"),
                                 (self.base / "ex-harness", "과제 폴더 밖")):
            with patch.object(start, "SOURCE", source), redirect_stdout(self.output):
                start.describe(self.project)
            self.assertIn(expected, self.output.getvalue())
            self.output.truncate(0)
            self.output.seek(0)

    def test_preview_no_writes_no_cli(self):
        before = snapshot(self.project)
        self.assertEqual(self.run_start("--preview"), 0)
        self.assertEqual(before, snapshot(self.project))

    def test_repeat_preserves_readme_agents_dirty_files_and_identity(self):
        for name, body in (("AGENTS.md", "user rules"), ("app.py", "user unsaved work"),
                           (".git/config", "[user]\nname = user\n")):
            path = self.project / name
            path.parent.mkdir(exist_ok=True)
            path.write_text(body, encoding="utf-8")
        before = snapshot(self.project)
        self.assertEqual(self.run_start("--no-launch"), 0)
        after = snapshot(self.project)
        self.assertTrue(all(after[k] == v for k, v in before.items()))
        self.assertEqual(self.run_start("--no-launch"), 0)
        self.assertEqual(after, snapshot(self.project))

    def test_real_git_staged_user_work_and_config_are_preserved(self):
        git = shutil.which("git")
        if not git:
            self.skipTest("Git unavailable for fixture")
        subprocess.run([git, "init", str(self.project)], check=True, capture_output=True)
        subprocess.run([git, "-C", str(self.project), "add", "README.md"], check=True, capture_output=True)
        (self.project / "README.md").write_text("# Unstaged user work")
        before = snapshot(self.project / ".git")
        self.assertEqual(self.run_start("--no-launch"), 0)
        # git status may refresh stat data in the index; compare the actual
        # staged contents and config, and prove no harness file was staged.
        files = subprocess.run([git, "-C", str(self.project), "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        self.assertEqual(files.stdout.strip(), "README.md")
        self.assertEqual((self.project / "README.md").read_text(), "# Unstaged user work")
        self.assertEqual((self.project / ".git/config").read_bytes(), before["config"])
        staged = subprocess.run([git, "-C", str(self.project), "show", ":README.md"], capture_output=True, text=True, check=True)
        self.assertIn("Synthetic task", staged.stdout)

    def test_skill_conflict_uses_source_fallback_does_not_claim_activation(self):
        skill = self.project / ".agents/skills/discover"
        skill.mkdir(parents=True)
        (skill / "custom.txt").write_text("keep")
        self.assertEqual(self.run_start("--model", "provided-sol-id"), 0)
        self.assertFalse((skill / "SKILL.md").exists())
        self.assertIn("SKILL fallback (discover)", self.output.getvalue())
        self.assertIn("runtime recognition NOT verified", self.output.getvalue())
        call = json.loads((self.project / "cli-call.json").read_text(encoding="utf-8"))
        self.assertIn(str(ROOT / "skills"), call["args"][-1])

    def test_existing_session_or_no_tty_does_not_nest_cli(self):
        for args, env, tty, code in ((["--existing-session"], {}, True, 0),
                                      ([], {"CODEX_THREAD_ID": "active"}, True, 0),
                                      ([], {}, False, 2)):
            with self.subTest(args=args, tty=tty):
                self.assertEqual(self.run_start(*args, env=env, tty=tty), code)
                self.assertFalse((self.project / "cli-call.json").exists())

    def test_cli_failure_is_not_success_and_does_not_retry(self):
        self.assertEqual(self.run_start(env={"FAKE_CODEX_EXIT": "7"}), 7)
        self.assertIn("exit=7", self.output.getvalue())
        self.assertIn("No automatic retry", self.output.getvalue())

    def test_missing_or_unsupported_cli_prints_chat_fallback(self):
        with patch.object(start, "capture", return_value=subprocess.CompletedProcess([], 0, "Usage: unknown", "")):
            self.assertEqual(self.run_start(), 2)
        self.assertFalse((self.project / "cli-call.json").exists())
        with patch.object(start.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "codex not found"):
                start.cli_command()
        with patch.object(start, "launch", side_effect=ValueError("codex not found on PATH")):
            self.assertEqual(self.run_start(), 2)
        self.assertIn("codex not found", self.output.getvalue())

    def test_preflight_failure_never_launches(self):
        (self.project / ".agents").write_text("blocked")
        before = snapshot(self.project)
        self.assertEqual(self.run_start(), 2)
        self.assertEqual(snapshot(self.project), before)
        self.assertNotIn("installed created=", self.output.getvalue())

    def test_install_io_failure_rolls_back_new_files_and_never_launches(self):
        original = install.shutil.copyfileobj
        count = 0
        def fail(source, dest):
            nonlocal count
            count += 1
            if count == 3:
                dest.write(b"partial")
                raise OSError("injected disk failure")
            return original(source, dest)
        before = snapshot(self.project)
        with patch.object(install.shutil, "copyfileobj", side_effect=fail):
            self.assertEqual(self.run_start(), 2)
        self.assertEqual(snapshot(self.project), before)
        self.assertIn("injected disk failure", self.output.getvalue())

    def test_source_skill_missing_fails_before_mutation(self):
        with patch.object(start, "SKILLS", ("not-present",)):
            self.assertEqual(self.run_start(), 2)
        self.assertFalse((self.project / "AGENTS.md").exists())

    def test_target_parent_child_and_harness_locations(self):
        nested = self.project / "src/deep"
        nested.mkdir(parents=True)
        self.assertEqual(start.select_target(cwd=nested), self.project)
        self.assertEqual(start.select_target(cwd=self.base), self.project)
        harness = self.project / "ex-harness"
        harness.mkdir()
        (harness / "README.md").write_text("harness, not task")
        with patch.object(start, "SOURCE", harness):
            self.assertEqual(start.select_target(cwd=harness), self.project)
            with self.assertRaises(ValueError):
                start.select_target(harness)

    def test_ambiguous_root_requires_number_or_path_and_no_noninteractive_guess(self):
        other = self.base / "other"
        other.mkdir()
        (other / "README").write_text("other")
        with redirect_stdout(self.output), patch.object(sys.stdin, "isatty", return_value=False):
            with self.assertRaisesRegex(ValueError, "ambiguous"):
                start.select_target(cwd=self.base)
        with redirect_stdout(self.output), patch.object(sys.stdin, "isatty", return_value=True):
            with patch("builtins.input", return_value="2"):
                self.assertEqual(start.select_target(cwd=self.base), self.project)
            with patch("builtins.input", return_value=str(other)):
                self.assertEqual(start.select_target(cwd=self.base), other)
            with patch("builtins.input", return_value="999"):
                with self.assertRaises(ValueError):
                    start.select_target(cwd=self.base)

    def test_no_readme_and_harness_target_rejected(self):
        for target in (self.base, ROOT, ROOT / "tools"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                start.select_target(target)

    def test_python_entry_without_any_shell(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools/start.py"), "--target", str(self.project), "--no-launch"],
                                env={**os.environ, "PATH": "", "PYTHONUTF8": "1"}, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / ".harness/templates/START.md").exists())


@unittest.skipIf(os.name == "nt", "POSIX isolation/PTY tests run on Linux; Windows has separate wrapper test")
class PosixStartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project"
        self.project.mkdir()
        (self.project / "README.md").write_text("# Synthetic project")
        self.bin = self.base / "bin"
        self.bin.mkdir()

    def executable(self, name, body):
        path = self.bin / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o700)  # Test fixture, never changes project permissions.

    def shell(self, shell, *args):
        return subprocess.run([shell, str(ROOT / "start.sh"), *args], cwd=self.project,
                              env={**os.environ, "PATH": str(self.bin), "CODEX_THREAD_ID": ""},
                              capture_output=True, text=True, encoding="utf-8")

    def test_bash_and_posix_sh_without_execute_bit_requirement(self):
        (self.bin / "dirname").symlink_to(shutil.which("dirname"))
        (self.bin / "python3").symlink_to(sys.executable)
        for shell in ("/bin/bash", "/bin/sh"):
            with self.subTest(shell=shell):
                result = self.shell(shell, "--no-launch")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((self.project / "AGENTS.md").exists())

    def test_python_absent_low_or_broken_runtime_falls_back_without_install(self):
        (self.bin / "dirname").symlink_to(shutil.which("dirname"))
        for body in (None, "#!/bin/sh\nexit 1\n", "#!/bin/sh\nexit 126\n"):
            with self.subTest(runtime=body):
                if body:
                    self.executable("python3", body)
                result = self.shell("/bin/sh")
                self.assertEqual(result.returncode, 2)
                self.assertIn("Next:", result.stderr)
                self.assertFalse((self.project / "AGENTS.md").exists())

    def test_bash_broken_sh_and_python_fallback(self):
        (self.bin / "dirname").symlink_to(shutil.which("dirname"))
        self.executable("bash", "#!/bin/sh\nexit 126\n")
        self.executable("python3", "#!/bin/sh\nexit 1\n")
        (self.bin / "python").symlink_to(sys.executable)
        result = self.shell("/bin/sh", "--no-launch")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("version check failed", result.stderr)

    def test_real_sh_with_pty_launches_fake_cli_from_readme_directory(self):
        import pty
        # Reproduce the documented layout: README cwd, clone in ./ex-harness.
        harness = self.project / "ex-harness"
        shutil.copytree(ROOT, harness, ignore=shutil.ignore_patterns(".git", ".agents", ".codex", "__pycache__", ".run", "*.pyc"))
        (self.bin / "dirname").symlink_to(shutil.which("dirname"))
        (self.bin / "python3").symlink_to(sys.executable)
        self.executable("codex", f'#!{sys.executable}\nimport pathlib,sys,json,os\nif sys.argv[1:] == ["--help"]: print("Usage: codex [OPTIONS] [PROMPT]")\nelse: pathlib.Path("call.json").write_text(json.dumps({{"cwd":os.getcwd(),"args":sys.argv[1:]}}))\n')
        master, slave = pty.openpty()
        self.addCleanup(os.close, master)
        try:
            process = subprocess.Popen(["/bin/sh", "ex-harness/start.sh"], cwd=self.project,
                                       stdin=slave, stdout=slave, stderr=slave,
                                       env={**os.environ, "PATH": str(self.bin), "CODEX_THREAD_ID": ""})
        finally:
            os.close(slave)
        # Drain concurrently: a large install plan must not fill the PTY buffer.
        import threading
        output = []
        def drain():
            try:
                while True:
                    data = os.read(master, 4096)
                    if not data:
                        break
                    output.append(data)
            except OSError:
                pass
        reader = threading.Thread(target=drain, daemon=True)
        reader.start()
        try:
            code = process.wait(timeout=20)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
        reader.join(timeout=3)
        self.assertEqual(code, 0, b"".join(output).decode(errors="replace"))
        call = json.loads((self.project / "call.json").read_text())
        self.assertEqual(call["cwd"], str(self.project))
        self.assertEqual(call["args"], [])


class PowerShellStartTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "PowerShell wrapper is tested on Windows")
    def test_powershell_python_entry_preserves_project(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "task with spaces"
            project.mkdir()
            (project / "README.md").write_text("# Synthetic task")
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            if not powershell:
                self.skipTest("PowerShell unavailable")
            quote = lambda value: "'" + str(value).replace("'", "''") + "'"
            command = "& " + " ".join(map(quote, [sys.executable, ROOT / "tools/start.py", "--no-launch"]))
            result = subprocess.run([powershell, "-NoProfile", "-Command", command],
                                    cwd=project, capture_output=True, env={**os.environ, "PYTHONUTF8": "1"})
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            self.assertTrue((project / ".agents/skills/discover/SKILL.md").exists())

    @unittest.skipUnless(os.name == "nt", "Optional PS1 wrapper is tested on Windows")
    def test_optional_ps1_wrapper_or_report_execution_policy(self):
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            self.skipTest("PowerShell unavailable")
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / "README.md").write_text("# Synthetic task")
            result = subprocess.run([powershell, "-NoProfile", "-File", str(ROOT / "start.ps1"), "--no-launch"],
                                    cwd=project, capture_output=True, env={**os.environ, "PYTHONUTF8": "1"})
            if b"UnauthorizedAccess" in result.stderr or b"PSSecurityException" in result.stderr:
                self.assertFalse((project / "AGENTS.md").exists())
                self.skipTest("PS1 blocked by existing execution policy; use tested Python entry, no bypass")
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            self.assertTrue((project / ".agents/skills/discover/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
