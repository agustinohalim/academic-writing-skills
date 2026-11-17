"""Tests for install.py (install, update, rollback, uninstall). Standard library only, no network.

    python -m unittest discover tests
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "academic-writing"

spec = importlib.util.spec_from_file_location("aws_install", ROOT / "install.py")
inst = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inst)


def run(argv, stdin_tty=False):
    out, err = io.StringIO(), io.StringIO()
    stdin = io.StringIO("")
    stdin.isatty = lambda: stdin_tty
    old_stdin = inst.sys.stdin
    inst.sys.stdin = stdin
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = inst.main(argv)
    finally:
        inst.sys.stdin = old_stdin
    return code, out.getvalue() + err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aws-test-"))
        self.dest = self.tmp / "skills"
        self.backups = self.tmp / "backups"
        os.environ["ACADEMIC_WRITING_BACKUP_DIR"] = str(self.backups)
        fake_home = self.tmp / "home"
        self._targets = inst.user_targets
        inst.user_targets = lambda: {k: fake_home / k for k in ("agents", "claude", "gemini", "opencode")}
        self._fetch = inst.fetch
        with contextlib.redirect_stdout(io.StringIO()):
            self.skills = inst.discover_skills(PLUGIN)
        self.version = inst.plugin_version(PLUGIN)

    def tearDown(self):
        inst.fetch = self._fetch
        inst.user_targets = self._targets
        os.environ.pop("ACADEMIC_WRITING_BACKUP_DIR", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def install(self):
        code, out = run(["install", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        return out

    def manifest(self):
        return json.loads((self.dest / ".academic-writing" / "manifest.json").read_text(encoding="utf-8"))

    def build_zip(self, version="99.0.0", drop=(), extra=None, name="release.zip"):
        """A GitHub-style archive of the repo's plugin with a chosen version."""
        stage = self.tmp / ("stage-" + name)
        top = stage / "academic-writing-skills-main"
        plugin = top / "plugins" / "academic-writing"
        shutil.copytree(PLUGIN, plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for d in (plugin / "skills").iterdir():
            if d.name not in self.skills or d.name in drop:
                shutil.rmtree(d)
        pj = plugin / ".claude-plugin" / "plugin.json"
        data = json.loads(pj.read_text(encoding="utf-8"))
        data["version"] = version
        pj.write_text(json.dumps(data), encoding="utf-8")
        shutil.copy2(ROOT / "install.py", top / "install.py")
        zpath = self.tmp / name
        with zipfile.ZipFile(zpath, "w") as zf:
            for f in sorted(stage.rglob("*")):
                if f.is_file():
                    zf.write(f, f.relative_to(stage).as_posix())
            for arcname, content in (extra or {}).items():
                zf.writestr(arcname, content)
        shutil.rmtree(stage)
        return zpath.read_bytes()


class InstallTests(Base):
    def test_copies_skills_rewrites_paths_and_adds_agents(self):
        self.install()
        for name in self.skills:
            self.assertTrue((self.dest / name / "SKILL.md").is_file(), name)
        for md in self.dest.rglob("*.md"):
            self.assertNotIn("${CLAUDE_SKILL_DIR}", md.read_text(encoding="utf-8"), md)
        audit = (self.dest / "thesis-audit" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn((self.dest / "thesis-audit").resolve().as_posix() + "/scripts/prepare_audit.py", audit)
        agents = sorted(p.name for p in (self.dest / "manuscript-review" / "agents").glob("*.md"))
        self.assertEqual(agents, sorted(p.name for p in (PLUGIN / "agents").glob("*.md")))
        review = (self.dest / "manuscript-review" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Running outside Claude Code", review)
        m = self.manifest()
        self.assertEqual(m["version"], self.version)
        self.assertEqual(m["skills"], self.skills)
        self.assertTrue((self.dest / ".academic-writing" / "install.py").is_file())

    def test_unrelated_skill_untouched_and_reinstall_drops_stale_files(self):
        other = self.dest / "other-skill"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_text("---\nname: other-skill\n---\n", encoding="utf-8")
        self.install()
        stale = self.dest / "research-integrity" / "stale.txt"
        stale.write_text("old", encoding="utf-8")
        self.install()
        self.assertFalse(stale.exists())
        self.assertTrue((other / "SKILL.md").is_file())
        review = (self.dest / "manuscript-review" / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(review.count("Running outside Claude Code"), 1)

    def test_project_target_path(self):
        args = inst.build_parser().parse_args(["install", "--project", str(self.tmp / "repo"), "--target", "gemini"])
        self.assertEqual(inst.resolve_dest(args), (self.tmp / "repo" / ".gemini" / "skills").resolve())

    def test_uninstall_leaves_unrelated_and_needs_confirmation(self):
        other = self.dest / "other-skill"
        other.mkdir(parents=True)
        self.install()
        code, out = run(["uninstall", "--dest", str(self.dest)])  # no --yes, no terminal
        self.assertEqual(code, 1)
        self.assertIn("--yes", out)
        self.assertTrue((self.dest / "thesis-audit").is_dir())
        code, out = run(["uninstall", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        for name in self.skills:
            self.assertFalse((self.dest / name).exists(), name)
        self.assertFalse((self.dest / ".academic-writing").exists())
        self.assertTrue(other.is_dir())


class UpdateTests(Base):
    def test_update_then_rollback(self):
        self.install()
        data = self.build_zip("99.0.0")
        inst.fetch = lambda url, timeout=60: data
        code, out = run(["update", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.manifest()["version"], "99.0.0")
        self.assertEqual(self.manifest()["source"]["ref"], "main")
        self.assertEqual(len(list(self.backups.iterdir())), 1)
        code, out = run(["rollback", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.manifest()["version"], self.version)
        self.assertTrue((self.dest / "thesis-audit" / "SKILL.md").is_file())

    def test_update_from_installed_copy_finds_its_dest(self):
        self.install()
        installed = self.dest / ".academic-writing" / "install.py"
        spec2 = importlib.util.spec_from_file_location("aws_installed", installed)
        mod = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(mod)
        args = mod.build_parser().parse_args(["update"])
        self.assertEqual(mod.resolve_dest(args), self.dest.resolve())

    def test_rejects_parent_paths(self):
        self.install()
        data = self.build_zip("99.0.0", extra={"../evil.txt": "x"})
        inst.fetch = lambda url, timeout=60: data
        code, out = run(["update", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 1)
        self.assertIn("unsafe path", out)
        self.assertEqual(self.manifest()["version"], self.version)
        self.assertFalse((self.tmp / "evil.txt").exists())

    def test_rejects_symlink(self):
        zpath = self.tmp / "link.zip"
        with zipfile.ZipFile(zpath, "w") as zf:
            info = zipfile.ZipInfo("top/link")
            info.external_attr = (0o120777 << 16)
            zf.writestr(info, "/etc/passwd")
        (self.tmp / "out").mkdir()
        with self.assertRaises(inst.InstallError):
            inst.safe_extract(zpath, self.tmp / "out")

    def test_rejects_release_missing_a_skill(self):
        self.install()
        data = self.build_zip("99.0.0", drop=("research-integrity",))
        inst.fetch = lambda url, timeout=60: data
        code, out = run(["update", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 1)
        self.assertIn("research-integrity", out)
        self.assertTrue((self.dest / "research-integrity").is_dir())
        code, out = run(["update", "--dest", str(self.dest), "--yes", "--allow-removal"])
        self.assertEqual(code, 0, out)
        self.assertFalse((self.dest / "research-integrity").exists())

    def test_rejects_skill_folder_without_skill_md(self):
        self.install()
        data = self.build_zip("99.0.0", extra={
            "academic-writing-skills-main/plugins/academic-writing/skills/broken/notes.md": "x"})
        inst.fetch = lambda url, timeout=60: data
        code, out = run(["update", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 1)
        self.assertIn("without SKILL.md", out)

    def test_refuses_downgrade(self):
        self.install()
        data = self.build_zip("0.0.1")
        inst.fetch = lambda url, timeout=60: data
        code, out = run(["update", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 1)
        self.assertIn("older", out)

    def test_archive_url(self):
        self.assertTrue(inst.archive_url("main").endswith("/archive/refs/heads/main.zip"))
        self.assertTrue(inst.archive_url("v1.13.0").endswith("/archive/refs/tags/v1.13.0.zip"))

    def test_check_update(self):
        self.install()
        inst.fetch = lambda url, timeout=60: json.dumps({"version": "99.0.0"}).encode()
        code, out = run(["check-update", "--dest", str(self.dest)])
        self.assertEqual(code, 0, out)
        self.assertIn("Update available", out)
        inst.fetch = lambda url, timeout=60: json.dumps({"version": self.version}).encode()
        code, out = run(["check-update", "--dest", str(self.dest)])
        self.assertIn("Up to date", out)

    def test_version_parsing(self):
        self.assertEqual(inst.parse_version("v1.12.0"), (1, 12, 0))
        self.assertLess(inst.parse_version("1.9.2"), inst.parse_version("1.10.0"))


NEW_SKILL = {"academic-writing-skills-main/plugins/academic-writing/skills/zz-new/SKILL.md":
             "---\nname: zz-new\ndescription: test\n---\n"}


class SafetyTests(Base):
    """Fixes for data-loss findings: tampered names, foreign folders, overlap, links, restore."""

    def write_manifest(self, **changes):
        m = self.manifest()
        m.update(changes)
        (self.dest / ".academic-writing" / "manifest.json").write_text(json.dumps(m), encoding="utf-8")

    def make_source(self):
        src = self.tmp / "src"
        shutil.copytree(PLUGIN, src / "plugins" / "academic-writing",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for d in (src / "plugins" / "academic-writing" / "skills").iterdir():
            if d.name not in self.skills:
                shutil.rmtree(d)
        shutil.copy2(ROOT / "install.py", src / "install.py")
        return src

    # 1 -----------------------------------------------------------------
    def test_check_name_rejects_unsafe(self):
        for bad in ("", ".", "..", "../x", "/abs", "C:/x", "a/b", "A", ".hidden", None, 3):
            with self.assertRaises(inst.InstallError, msg=repr(bad)):
                inst.check_name(bad)
        self.assertEqual(inst.check_name("thesis-audit"), "thesis-audit")
        for bad in ("1.0", "1.0.0/../x", "v1.0.0", "", None):
            with self.assertRaises(inst.InstallError, msg=repr(bad)):
                inst.check_version(bad)

    def test_tampered_manifest_never_deletes_dest_or_parent(self):
        self.install()
        sentinel = self.tmp / "sentinel.txt"
        sentinel.write_text("keep", encoding="utf-8")
        for bad in ([""], ["."], [".."], [str(self.tmp)], ["../skills"]):
            self.write_manifest(skills=bad)
            code, out = run(["uninstall", "--dest", str(self.dest), "--yes"])
            self.assertEqual(code, 1, (bad, out))
            self.assertIn("invalid skill name", out)
            code, out = run(["install", "--dest", str(self.dest), "--yes"])
            self.assertEqual(code, 1, (bad, out))
            self.assertTrue(sentinel.is_file())
            self.assertTrue((self.dest / "thesis-audit" / "SKILL.md").is_file())

    def test_tampered_version_refused_before_backup(self):
        self.install()
        self.write_manifest(version="1.0.0/../../evil")
        data = self.build_zip("99.0.0")
        inst.fetch = lambda url, timeout=60: data
        code, out = run(["update", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 1)
        self.assertIn("invalid version", out)
        self.assertFalse(self.backups.exists() and any(self.backups.iterdir()))

    def test_child_guard(self):
        self.dest.mkdir(parents=True)
        with self.assertRaises(inst.InstallError):
            inst.child(self.dest, "..")
        with self.assertRaises(inst.InstallError):
            inst.remove_child(self.dest, "")
        self.assertEqual(inst.child(self.dest, "x"), self.dest / "x")

    # 2 -----------------------------------------------------------------
    def test_refuses_same_named_folder_it_does_not_own(self):
        mine = self.dest / "thesis-audit"
        mine.mkdir(parents=True)
        (mine / "mine.txt").write_text("user data", encoding="utf-8")
        code, out = run(["install", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 1)
        self.assertIn("--force-overwrite", out)
        self.assertTrue((mine / "mine.txt").is_file())
        self.assertFalse((self.dest / "research-integrity").exists())
        code, out = run(["install", "--dest", str(self.dest), "--yes", "--force-overwrite"])
        self.assertEqual(code, 0, out)
        self.assertFalse((mine / "mine.txt").exists())

    # 3 -----------------------------------------------------------------
    def test_refuses_dest_overlapping_source(self):
        src = self.make_source()
        skills = src / "plugins" / "academic-writing" / "skills"
        for dest in (skills, skills / "thesis-audit", src):
            code, out = run(["install", "--source", str(src), "--dest", str(dest), "--yes"])
            self.assertEqual(code, 1, (dest, out))
            self.assertIn("overlaps the source", out)
        self.assertTrue((skills / "thesis-audit" / "SKILL.md").is_file())

    def _link(self, link: Path, target: Path):
        try:
            os.symlink(target, link, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                self.skipTest("cannot create symlinks here")
            import _winapi
            try:
                _winapi.CreateJunction(str(target), str(link))
            except OSError:
                self.skipTest("cannot create symlinks or junctions here")

    def test_refuses_target_linked_into_source(self):
        src = self.make_source()
        skill = src / "plugins" / "academic-writing" / "skills" / "research-integrity"
        self.dest.mkdir(parents=True)
        self._link(self.dest / "research-integrity", skill)
        code, out = run(["install", "--source", str(src), "--dest", str(self.dest), "--yes",
                         "--force-overwrite"])
        self.assertEqual(code, 1, out)
        self.assertIn("source tree", out)
        self.assertTrue((skill / "SKILL.md").is_file())

    # 4 -----------------------------------------------------------------
    def test_link_removal_removes_link_only(self):
        self.install()
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "precious.txt").write_text("keep", encoding="utf-8")
        shutil.rmtree(self.dest / "research-integrity")
        self._link(self.dest / "research-integrity", outside)
        self.assertTrue(inst.is_link(self.dest / "research-integrity"))
        code, out = run(["uninstall", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        self.assertFalse(inst.exists(self.dest / "research-integrity"))
        self.assertTrue((outside / "precious.txt").is_file())

    def test_permission_error_retried_then_reported(self):
        self.dest.mkdir(parents=True)
        (self.dest / "x").mkdir()
        calls = []
        orig_remove, orig_sleep = inst._remove_once, inst.time.sleep
        inst.time.sleep = lambda s: None

        def flaky(p):
            calls.append(p)
            if len(calls) < 3:
                raise PermissionError("locked")
            orig_remove(p)
        try:
            inst._remove_once = flaky
            inst.remove_child(self.dest, "x")
            self.assertEqual(len(calls), 3)
            self.assertFalse((self.dest / "x").exists())
            (self.dest / "y").mkdir()
            inst._remove_once = lambda p: (_ for _ in ()).throw(PermissionError("locked"))
            with self.assertRaises(inst.InstallError) as cm:
                inst.remove_child(self.dest, "y")
            self.assertIn(str(self.dest / "y"), str(cm.exception))
        finally:
            inst._remove_once, inst.time.sleep = orig_remove, orig_sleep

    # 5 -----------------------------------------------------------------
    def test_rollback_removes_skills_the_update_created(self):
        self.install()
        data = self.build_zip("99.0.0", extra=NEW_SKILL)
        inst.fetch = lambda url, timeout=60: data
        code, out = run(["update", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        self.assertTrue((self.dest / "zz-new" / "SKILL.md").is_file())
        code, out = run(["rollback", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        self.assertFalse((self.dest / "zz-new").exists())
        self.assertEqual(self.manifest()["version"], self.version)

    def test_incomplete_backup_refused_before_deleting(self):
        self.install()
        data = self.build_zip("99.0.0")
        inst.fetch = lambda url, timeout=60: data
        self.assertEqual(run(["update", "--dest", str(self.dest), "--yes"])[0], 0)
        (bdir,) = list(self.backups.iterdir())
        shutil.rmtree(bdir / "thesis-audit")
        code, out = run(["rollback", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 1)
        self.assertIn("incomplete", out)
        self.assertEqual(self.manifest()["version"], "99.0.0")
        self.assertTrue((self.dest / "thesis-audit" / "SKILL.md").is_file())

    # 6 -----------------------------------------------------------------
    def test_interrupt_during_update_restores(self):
        self.install()
        data = self.build_zip("99.0.0")
        inst.fetch = lambda url, timeout=60: data
        orig = inst.apply_install

        def interrupted(plan, installer_src, source):
            inst.remove_child(self.dest, "thesis-audit")
            raise KeyboardInterrupt
        inst.apply_install = interrupted
        try:
            with self.assertRaises(KeyboardInterrupt):
                run(["update", "--dest", str(self.dest), "--yes"])
        finally:
            inst.apply_install = orig
        self.assertEqual(self.manifest()["version"], self.version)
        self.assertTrue((self.dest / "thesis-audit" / "SKILL.md").is_file())

    # 7 -----------------------------------------------------------------
    def test_rollback_steps_back_and_can_be_undone(self):
        self.install()
        for v in ("99.0.0", "99.1.0"):
            data = self.build_zip(v, name=f"r{v}.zip")
            inst.fetch = lambda url, timeout=60, data=data: data
            self.assertEqual(run(["update", "--dest", str(self.dest), "--yes"])[0], 0)
        self.assertEqual(run(["rollback", "--dest", str(self.dest), "--yes"])[0], 0)
        self.assertEqual(self.manifest()["version"], "99.0.0")
        self.assertEqual(run(["rollback", "--dest", str(self.dest), "--yes"])[0], 0)
        self.assertEqual(self.manifest()["version"], self.version)
        code, out = run(["rollback", "--dest", str(self.dest), "--list"])
        self.assertEqual(code, 0)
        snaps = [line.split()[0] for line in out.splitlines() if " rollback " in line]
        self.assertEqual(len(snaps), 2)
        self.assertIn("(restored)", out)
        # undo the last rollback: the newest snapshot holds 99.0.0
        code, out = run(["rollback", "--dest", str(self.dest), "--yes", "--to", sorted(snaps)[-1]])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.manifest()["version"], "99.0.0")
        code, out = run(["rollback", "--dest", str(self.dest), "--yes", "--to", "../../etc"])
        self.assertEqual(code, 1)

    # 8 -----------------------------------------------------------------
    def test_reinstall_backs_up_and_confirms_removals(self):
        self.install()
        old = self.dest / "old-skill"
        old.mkdir()
        (old / "SKILL.md").write_text("---\nname: old-skill\n---\n", encoding="utf-8")
        self.write_manifest(skills=self.manifest()["skills"] + ["old-skill"])
        code, out = run(["install", "--dest", str(self.dest)])  # no --yes, no terminal
        self.assertEqual(code, 1)
        self.assertTrue(old.is_dir())
        code, out = run(["install", "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        self.assertFalse(old.exists())
        backups = list(self.backups.iterdir())
        self.assertEqual(len(backups), 1)
        self.assertTrue((backups[0] / "old-skill" / "SKILL.md").is_file())

    # 9 -----------------------------------------------------------------
    def test_bom_and_non_utf8(self):
        src = self.make_source()
        skill_md = src / "plugins" / "academic-writing" / "skills" / "thesis-audit" / "SKILL.md"
        skill_md.write_bytes(b"\xef\xbb\xbf" + skill_md.read_bytes())
        code, out = run(["install", "--source", str(src), "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 0, out)
        installed = (self.dest / "thesis-audit" / "SKILL.md").read_bytes()
        self.assertTrue(installed.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"${CLAUDE_SKILL_DIR}", installed)
        bad = src / "plugins" / "academic-writing" / "skills" / "research-integrity" / "references" / "bad.md"
        bad.write_bytes(b"\xff\xfe not utf-8 \x80")
        stale = self.dest / "research-integrity" / "SKILL.md"
        before = stale.read_bytes()
        code, out = run(["install", "--source", str(src), "--dest", str(self.dest), "--yes"])
        self.assertEqual(code, 1)
        self.assertIn("not UTF-8", out)
        self.assertEqual(stale.read_bytes(), before)
        self.assertFalse((self.dest / "research-integrity" / "references" / "bad.md").exists())


if __name__ == "__main__":
    unittest.main()
