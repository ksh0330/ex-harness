import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.install import plan


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / "project with spaces"
        self.target.mkdir()
        (self.target / "README.md").write_text("# Synthetic task", encoding="utf-8")

    def run_install(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "tools/install.py"), "--target", str(self.target), *args], capture_output=True, text=True)

    def test_preview_creates_nothing(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("mode=preview", result.stdout)
        self.assertEqual(list(self.target.iterdir()), [self.target / "README.md"])

    def test_apply_preserves_existing_and_repeat_is_identical(self):
        files = {"AGENTS.md": "project rules\n", "docs/STATUS.md": "user progress\n",
                 ".harness/GUIDE.md": "user guide\n", ".git/config": "[user]\n name = unchanged\n",
                 ".agents/skills/discover/custom.txt": "existing skill\n"}
        for name, value in files.items():
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
        before = snapshot(self.target)
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = snapshot(self.target)
        self.assertTrue(all(after[k] == v for k, v in before.items()))
        self.assertFalse((self.target / ".agents/skills/discover/SKILL.md").exists())
        self.assertTrue((self.target / ".agents/skills/verify/SKILL.md").exists())
        self.assertFalse((self.target / ".codex").exists())
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("created=0", result.stdout)
        self.assertEqual(snapshot(self.target), after)

    def test_fresh_project_gets_agents_but_no_app_code_by_default(self):
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.target / "AGENTS.md").is_file())
        self.assertFalse((self.target / ".harness/kit").exists())
        self.assertFalse((self.target / "docs").exists())

    def test_installed_guides_have_resolvable_local_links(self):
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        morning = self.target / ".harness/docs/MORNING.md"
        self.assertEqual(morning.read_bytes(), (ROOT / "docs/MORNING.md").read_bytes())
        basics = self.target / ".harness/docs/BASICS.md"
        self.assertEqual(basics.read_bytes(), (ROOT / "docs/BASICS.md").read_bytes())
        for name in ("REVIEW.md", "FINAL_REVIEW.md"):
            self.assertEqual((self.target / ".harness/templates" / name).read_bytes(),
                             (ROOT / "templates" / name).read_bytes())
        for path in (self.target / ".harness").rglob("*.md"):
            for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8-sig")):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link.split("#", 1)[0]).exists(), f"{path.name}: {link}")

    def test_preflight_rejects_blocked_parent_without_partial_install(self):
        (self.target / ".agents").write_text("blocked", encoding="utf-8")
        before = snapshot(self.target)
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(snapshot(self.target), before)

    def test_rejects_source_and_non_directory_target(self):
        with self.assertRaises(ValueError):
            plan(ROOT)
        with self.assertRaises(ValueError):
            plan(self.target / "README.md")

    def test_missing_readme_or_absent_target_never_installs(self):
        (self.target / "README.md").unlink()
        self.assertEqual(self.run_install("--apply").returncode, 2)
        self.assertEqual(list(self.target.iterdir()), [])
        self.target.rmdir()
        self.assertEqual(self.run_install("--apply").returncode, 2)
        self.assertFalse(self.target.exists())

    def test_link_escape_is_rejected(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        link = self.target / ".harness"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            if sys.platform != "win32":
                raise
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        try:
            result = self.run_install("--apply")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertFalse((self.target / "AGENTS.md").exists())
        finally:
            if link.is_symlink():
                link.unlink()
            else:
                link.rmdir()

    def test_bash_wrapper(self):
        git_bash = Path("C:/Program Files/Git/bin/bash.exe")
        bash = str(git_bash) if git_bash.is_file() else shutil.which("bash")
        if not bash:
            self.skipTest("Bash unavailable")
        before = snapshot(self.target)
        result = subprocess.run([bash, str(ROOT / "install.sh")], cwd=self.target, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.target), before, "wrapper must preview by default")
        result = subprocess.run([bash, str(ROOT / "install.sh"), "--apply"], cwd=self.target, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.target / "AGENTS.md").is_file())


if __name__ == "__main__":
    unittest.main()
