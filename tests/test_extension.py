"""End-to-end checks for the gh-relnote wrapper script."""

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "gh-relnote"


def git(cwd, *args):
    env = dict(os.environ,
               GIT_AUTHOR_NAME="Ada Lovelace", GIT_AUTHOR_EMAIL="ada@example.com",
               GIT_COMMITTER_NAME="Ada Lovelace", GIT_COMMITTER_EMAIL="ada@example.com")
    subprocess.run(["git", *args], cwd=cwd, check=True, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class ExtensionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "commit", "--allow-empty", "-m", "chore: initial")
        git(self.repo, "tag", "v1.0.0")
        git(self.repo, "commit", "--allow-empty", "-m", "feat(cli): add sync")
        git(self.repo, "commit", "--allow-empty", "-m", "fix: handle commas")

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args, env=None):
        return subprocess.run([str(SCRIPT), *args], cwd=self.repo, text=True,
                              capture_output=True, env=env or os.environ.copy())

    def test_script_is_executable(self):
        self.assertTrue(SCRIPT.stat().st_mode & stat.S_IXUSR)

    def test_prints_notes(self):
        out = self.run_script()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("### Features", out.stdout)
        self.assertIn("add sync", out.stdout)
        self.assertIn("### Fixes", out.stdout)
        self.assertNotIn("initial", out.stdout)

    def test_passes_relnote_flags(self):
        out = self.run_script("--version")
        self.assertEqual(out.returncode, 0)
        self.assertIn("relnote", out.stdout)

    def test_usage(self):
        out = self.run_script("help")
        self.assertEqual(out.returncode, 0)
        self.assertIn("gh relnote create TAG", out.stdout)

    def test_create_requires_tag(self):
        out = self.run_script("create")
        self.assertEqual(out.returncode, 2)

    def test_create_calls_gh_release_with_notes(self):
        bindir = Path(self.tmp.name) / "bin"
        bindir.mkdir()
        log = Path(self.tmp.name) / "gh.log"
        fake = bindir / "gh"
        fake.write_text(
            "#!/usr/bin/env bash\n"
            f'echo "$@" > "{log}"\n'
            'while [ $# -gt 0 ]; do\n'
            '  if [ "$1" = "--notes-file" ]; then cat "$2" >> "' + str(log) + '"; fi\n'
            '  shift\n'
            'done\n'
        )
        fake.chmod(0o755)
        env = dict(os.environ, PATH=f"{bindir}{os.pathsep}{os.environ['PATH']}")
        out = self.run_script("create", "v1.1.0", "--draft", "--", "--max", "1", env=env)
        self.assertEqual(out.returncode, 0, out.stderr)
        text = log.read_text()
        self.assertTrue(text.startswith("release create v1.1.0 --draft --notes-file "))
        self.assertIn("handle commas", text)
        self.assertNotIn("add sync", text)


if __name__ == "__main__":
    unittest.main()
