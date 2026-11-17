#!/usr/bin/env python3
"""Install, update, roll back, or remove the academic-writing skills for agents other than
Claude Code's plugin system: Codex, Gemini CLI, OpenCode, and any agent that reads the Agent
Skills format (a folder per skill with SKILL.md at its root). Python 3.10+, standard library only.

Claude Code users should install the plugin from the marketplace instead (see README). A copy in
~/.claude/skills is allowed, but if the plugin is also installed every skill appears twice.

    python install.py install                         # ~/.agents/skills (Codex, Gemini CLI, OpenCode)
    python install.py install --target gemini         # ~/.gemini/skills
    python install.py install --target opencode       # ~/.config/opencode/skills
    python install.py install --project path/to/repo  # <repo>/.agents/skills
    python install.py install --dest ~/.hermes/skills # any other agent's skills folder
    python install.py version
    python install.py check-update
    python install.py update [--ref main|v1.13.0]
    python install.py rollback [--list | --to <backup-id>]
    python install.py uninstall

The installer copies itself to <dest>/.academic-writing/install.py next to a manifest, so an
installed family can update itself without a clone:

    python ~/.agents/skills/.academic-writing/install.py update

What install does to the copied files, and why:
  - ${CLAUDE_SKILL_DIR} in every .md is replaced by the installed skill's absolute path, because
    only Claude Code expands that variable.
  - The five reviewer roles (Claude Code plugin agents) are copied into manuscript-review/agents/
    and the installed manuscript-review/SKILL.md gains a note to run them one at a time when the
    agent cannot start subagents.
  - Only folders this family owns (listed in its manifest) are replaced or removed. A same-named
    folder it does not own is refused unless --force-overwrite; other skills are untouched.
  - Reinstalling over an existing install, updating, and rolling back each take a backup first.

Integrity of an update rests on HTTPS, safe extraction (no absolute paths, no "..", no symlinks),
and structural validation of the release (plugin.json present, every skill folder has a SKILL.md
whose name matches the folder, no downgrade, no silently dropped skill). No checksum is claimed.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO = "agustinohalim/academic-writing-skills"
FAMILY = "academic-writing-skills"
STATE_DIR = ".academic-writing"
PLUGIN_PARTS = ("plugins", "academic-writing")
RAW_PLUGIN_JSON = f"https://raw.githubusercontent.com/{REPO}/main/plugins/academic-writing/.claude-plugin/plugin.json"
USER_AGENT = "academic-writing-skills-installer (+https://github.com/" + REPO + ")"
SKILL_DIR_VARS = ("${CLAUDE_SKILL_DIR}", "$CLAUDE_SKILL_DIR")
REVIEW_SKILL = "manuscript-review"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
BACKUP_ID_RE = re.compile(r"^[0-9]{8}-[0-9]{6}-[0-9]{6}-[a-z-]+-\d+\.\d+\.\d+$")
NOTE_MARK = "<!-- installed-by: install.py -->"
NOTE = f"""

{NOTE_MARK}
## Running outside Claude Code

This copy was installed by `install.py` for an agent without Claude Code plugin agents. The five
reviewer roles are in `agents/` next to this file: `review-editor.md`, `review-methods.md`,
`review-domain.md`, `review-presentation.md`, `review-devils-advocate.md`. If this agent can
start subagents, give each one its role file. Otherwise use the fallback in step 3: read one role
file, write that role's `findings/<role>.json`, then move to the next role, and never re-open an
earlier role's output.
"""


class InstallError(Exception):
    pass


# ---------------------------------------------------------------- validation

def say(msg: str = "") -> None:
    print(msg, flush=True)


def check_name(name) -> str:
    """A skill name from a manifest, backup, or release, before it touches a path."""
    if not isinstance(name, str) or name in (".", "..") or not NAME_RE.match(name):
        raise InstallError(f"invalid skill name: {name!r}")
    return name


def check_version(v) -> str:
    if not isinstance(v, str) or not VERSION_RE.match(v):
        raise InstallError(f"invalid version: {v!r} (expected X.Y.Z)")
    return v


def parse_version(v: str) -> tuple[int, ...]:
    m = re.match(r"^\s*v?(\d+(?:\.\d+)*)", v or "")
    if not m:
        raise InstallError(f"not a version: {v!r}")
    parts = [int(x) for x in m.group(1).split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def read_json(p: Path) -> dict:
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        raise InstallError(f"cannot read {p}: {e}") from e
    if not isinstance(data, dict):
        raise InstallError(f"{p} is not a JSON object")
    return data


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        raise InstallError(f"{p} is not UTF-8: {e}") from e


def frontmatter_name(skill_md: Path) -> str | None:
    lines = read_text(skill_md).splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^name:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip("'\"")
    return None


def plugin_version(plugin_root: Path) -> str:
    pj = plugin_root / ".claude-plugin" / "plugin.json"
    if not pj.is_file():
        raise InstallError(f"plugin.json not found: {pj}")
    return check_version(str(read_json(pj).get("version", "")))


def discover_skills(plugin_root: Path, strict: bool = False) -> list[str]:
    """Skill folders under plugins/academic-writing/skills that hold a SKILL.md.

    strict (downloaded releases): a folder without SKILL.md, with an invalid name, or whose
    frontmatter name differs from the folder is an error. Otherwise it is skipped with a note.
    """
    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        raise InstallError(f"no skills folder: {skills_dir}")
    found = []
    for d in sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith(".")):
        problem = None
        if not NAME_RE.match(d.name):
            problem = f"invalid skill folder name: {d.name!r}"
        elif not (d / "SKILL.md").is_file():
            problem = f"skill folder without SKILL.md: {d.name}"
        else:
            name = frontmatter_name(d / "SKILL.md")
            if name != d.name:
                problem = f"skill {d.name}: frontmatter name is {name!r}, expected {d.name!r}"
        if problem:
            if strict:
                raise InstallError(problem)
            say(f"  skip {problem}")
            continue
        found.append(d.name)
    if not found:
        raise InstallError("no skills found")
    return found


def check_manifest(m: dict, where: Path) -> dict:
    skills = m.get("skills")
    if not isinstance(skills, list):
        raise InstallError(f"{where}: 'skills' must be a list")
    for name in skills:
        check_name(name)
    check_version(m.get("version"))
    return m


# ---------------------------------------------------------------- guarded filesystem

def is_link(p: Path) -> bool:
    """Symlink or Windows junction (any reparse point), without following it."""
    try:
        st = os.lstat(p)
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(st.st_mode):
        return True
    attrs = getattr(st, "st_file_attributes", 0)
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def exists(p: Path) -> bool:
    return is_link(p) or p.exists()


def child(dest: Path, name: str, internal: bool = False) -> Path:
    """dest/name after checking that it is a direct child of dest."""
    if not (internal and name == STATE_DIR):
        check_name(name)
    p = dest / name
    if Path(os.path.abspath(p)).parent != Path(os.path.abspath(dest)):
        raise InstallError(f"refusing path outside {dest}: {name!r}")
    if not is_link(p) and p.resolve(strict=False).parent != dest.resolve():
        raise InstallError(f"refusing path outside {dest}: {name!r}")
    return p


def _remove_once(p: Path) -> None:
    if is_link(p):
        try:
            os.unlink(p)
        except (IsADirectoryError, PermissionError, OSError):
            os.rmdir(p)  # Windows directory symlink or junction: removes the link only
        return
    if p.is_file():
        p.unlink()
        return

    def retry(func, path, _exc):  # read-only files on Windows; never chmod through a link
        if not os.path.islink(path):
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        func(path)
    if sys.version_info >= (3, 12):
        shutil.rmtree(p, onexc=retry)
    else:
        shutil.rmtree(p, onerror=retry)


def remove_child(dest: Path, name: str, internal: bool = False) -> None:
    p = child(dest, name, internal)
    if not exists(p):
        return
    delays = (0.1, 0.3, 0.9)
    for attempt in range(len(delays) + 1):
        try:
            _remove_once(p)
            return
        except PermissionError as e:
            if attempt == len(delays):
                raise InstallError(f"could not remove {p}: {e} (is a file open in another program?)") from e
            time.sleep(delays[attempt])


def copy_dir(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))


def cache_dir() -> Path:
    override = os.environ.get("ACADEMIC_WRITING_BACKUP_DIR")
    if override:
        return Path(override)
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return base / FAMILY / "backups"
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / FAMILY / "backups"


def confirm(question: str, yes: bool) -> bool:
    if yes:
        return True
    if not sys.stdin or not sys.stdin.isatty():
        say(f"{question} — refused: no terminal to confirm. Re-run with --yes.")
        return False
    try:
        answer = input(f"{question} [y/N] ").strip().lower()
    except EOFError:
        return False
    return answer in ("y", "yes", "ya")


def fetch(url: str, timeout: int = 60) -> bytes:
    """The only network access. Tests replace this function."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (https URLs only)
        return r.read()


# ---------------------------------------------------------------- locations

def this_file() -> Path:
    return Path(__file__).resolve()


def running_from_install() -> Path | None:
    """If this copy lives in <dest>/.academic-writing/, return <dest>."""
    here = this_file().parent
    if here.name == STATE_DIR and (here / "manifest.json").is_file():
        return here.parent
    return None


def source_root(arg: str | None) -> Path | None:
    root = Path(arg).resolve() if arg else this_file().parent
    return root if (root.joinpath(*PLUGIN_PARTS) / "skills").is_dir() else None


def config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")


def user_targets() -> dict[str, Path]:
    home = Path.home()
    return {
        "agents": home / ".agents" / "skills",
        "claude": home / ".claude" / "skills",
        "gemini": home / ".gemini" / "skills",
        "opencode": config_home() / "opencode" / "skills",
    }


PROJECT_TARGETS = {"agents": ".agents/skills", "claude": ".claude/skills",
                   "gemini": ".gemini/skills", "opencode": ".opencode/skills"}


def resolve_dest(args) -> Path:
    if args.dest:
        return Path(args.dest).expanduser().resolve()
    target = args.target or "agents"
    if args.project:
        return (Path(args.project).expanduser() / PROJECT_TARGETS[target]).resolve()
    if not args.target:
        installed = running_from_install()
        if installed:
            return installed
    return user_targets()[target]


def manifest_path(dest: Path) -> Path:
    return dest / STATE_DIR / "manifest.json"


def load_manifest(dest: Path) -> dict | None:
    p = manifest_path(dest)
    return check_manifest(read_json(p), p) if p.is_file() else None


# ---------------------------------------------------------------- install: plan, then apply

def _inside(a: Path, b: Path) -> bool:
    """a equals b or lies inside b."""
    return a == b or b in a.parents


def plan_install(plugin_root: Path, dest: Path, strict: bool = False,
                 force_overwrite: bool = False) -> dict:
    """Every check that can fail runs here, before anything in dest changes."""
    skills = discover_skills(plugin_root, strict=strict)
    version = plugin_version(plugin_root)
    for name in skills:
        for md in (plugin_root / "skills" / name).rglob("*.md"):
            read_text(md)
    for a in (plugin_root / "agents").glob("*.md") if (plugin_root / "agents").is_dir() else []:
        read_text(a)

    src_skills = (plugin_root / "skills").resolve()
    rdest = dest.resolve()
    if _inside(rdest, src_skills) or _inside(src_skills, rdest):
        raise InstallError(f"destination {dest} overlaps the source skills folder {src_skills}")

    old = load_manifest(dest) or {"skills": [], "version": None}
    owned = set(old["skills"])
    foreign = []
    for name in skills:
        p = child(dest, name)
        if not exists(p):
            continue
        if _inside(p.resolve(), src_skills):
            raise InstallError(f"{p} resolves into the source tree ({src_skills}); remove the link first")
        if name not in owned:
            foreign.append(name)
    if foreign and not force_overwrite:
        raise InstallError(
            f"{dest} already has folder(s) this installer does not own: {', '.join(foreign)}. "
            "Remove them by hand, or pass --force-overwrite to replace them (they are backed up "
            "only if this family is already installed there).")
    return {
        "plugin_root": plugin_root, "dest": dest, "skills": skills, "version": version,
        "old": old if old["version"] else None,
        "removed": sorted(owned - set(skills)),
        "created": sorted(set(skills) - owned),
        "foreign": foreign,
    }


def rewrite_skill_dir(skill_dir: Path) -> int:
    posix = skill_dir.resolve().as_posix()
    changed = 0
    for md in skill_dir.rglob("*.md"):
        raw = md.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as e:
            raise InstallError(f"{md} is not UTF-8: {e}") from e
        new = text
        for var in SKILL_DIR_VARS:
            new = new.replace(var, posix)
        if new != text:
            md.write_bytes((b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8"))
            changed += 1
    return changed


def apply_install(plan: dict, installer_src: Path, source: dict) -> dict:
    plugin_root, dest, skills = plan["plugin_root"], plan["dest"], plan["skills"]
    dest.mkdir(parents=True, exist_ok=True)

    for gone in plan["removed"]:
        say(f"  remove {gone} (no longer shipped)")
        remove_child(dest, gone)

    for name in skills:
        target = child(dest, name)
        remove_child(dest, name)
        copy_dir(plugin_root / "skills" / name, target)
        n = rewrite_skill_dir(target)
        say(f"  {name}" + (f"  (${{CLAUDE_SKILL_DIR}} rewritten in {n} file(s))" if n else ""))

    agents = []
    agents_src = plugin_root / "agents"
    if REVIEW_SKILL in skills and agents_src.is_dir():
        agents_dst = dest / REVIEW_SKILL / "agents"
        agents_dst.mkdir(exist_ok=True)
        for a in sorted(agents_src.glob("*.md")):
            shutil.copy2(a, agents_dst / a.name)
            agents.append(a.name)
        rewrite_skill_dir(dest / REVIEW_SKILL)
        skill_md = dest / REVIEW_SKILL / "SKILL.md"
        text = read_text(skill_md)
        if NOTE_MARK not in text:
            skill_md.write_text(text.rstrip("\n") + "\n" + NOTE, encoding="utf-8")
        say(f"  {REVIEW_SKILL}/agents: {len(agents)} reviewer role(s)")

    state = child(dest, STATE_DIR, internal=True)
    state.mkdir(exist_ok=True)
    if installer_src.resolve() != (state / "install.py").resolve():
        shutil.copy2(installer_src, state / "install.py")
    manifest = {
        "family": FAMILY,
        "version": plan["version"],
        "source": source,
        "skills": skills,
        "agents": agents,
        "dest": str(dest),
        "installed_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
    }
    manifest_path(dest).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def install_tree(plugin_root: Path, dest: Path, installer_src: Path, source: dict,
                 strict: bool = False, force_overwrite: bool = False) -> dict:
    return apply_install(plan_install(plugin_root, dest, strict, force_overwrite), installer_src, source)


def warn_duplicates(dest: Path) -> None:
    others = []
    for key, path in user_targets().items():
        try:
            if path.resolve() != dest.resolve() and manifest_path(path).is_file():
                others.append(f"{key}: {path}")
        except OSError:
            continue
    if others:
        say("Note: this family is also installed at " + "; ".join(others) + ".")
        say("      OpenCode reads ~/.config/opencode/skills, ~/.claude/skills and ~/.agents/skills;")
        say("      Gemini CLI reads ~/.gemini/skills and ~/.agents/skills. Keep one copy per agent")
        say("      to avoid duplicate skills (uninstall the other with --target or --dest).")


# ---------------------------------------------------------------- backups

def backup(dest: Path, created=(), kind: str = "update") -> Path:
    """Copy the installed family to the cache. created: names the next step will add, so a
    restore can remove them too. backup.json is written last and marks the backup complete."""
    manifest = load_manifest(dest)
    if not manifest:
        raise InstallError(f"nothing installed at {dest}")
    created = sorted(check_name(n) for n in created)
    version = check_version(manifest["version"])
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    out = cache_dir() / f"{stamp}-{kind}-{version}"
    out.mkdir(parents=True)
    missing = []
    for name in manifest["skills"]:
        src = child(dest, name)
        if not src.is_dir():
            say(f"  note: {name} was already missing from {dest}; not in the backup")
            missing.append(name)
            continue
        shutil.copytree(src, out / name)
    shutil.copytree(child(dest, STATE_DIR, internal=True), out / STATE_DIR)
    (out / "backup.json").write_text(json.dumps({
        "dest": str(dest), "kind": kind, "manifest": manifest, "created": created,
        "missing": missing, "used": False,
    }, indent=2) + "\n", encoding="utf-8")
    return out


def read_backup(bdir: Path, dest: Path | None = None) -> dict:
    """backup.json validated, and every listed folder present, before anything is deleted."""
    meta = read_json(bdir / "backup.json")
    if not isinstance(meta.get("manifest"), dict) or not isinstance(meta.get("dest"), str):
        raise InstallError(f"incomplete backup: {bdir}")
    check_manifest(meta["manifest"], bdir / "backup.json")
    for key in ("created", "missing"):
        names = meta.setdefault(key, [])
        if not isinstance(names, list):
            raise InstallError(f"{bdir}: '{key}' must be a list")
        for name in names:
            check_name(name)
    if dest is not None and Path(meta["dest"]).resolve() != dest.resolve():
        raise InstallError(f"backup {bdir.name} belongs to {meta['dest']}, not {dest}")
    for name in meta["manifest"]["skills"]:
        if name in meta["missing"]:
            continue
        if not (bdir / name / "SKILL.md").is_file():
            raise InstallError(f"backup {bdir.name} is incomplete: {name} missing")
    if not (bdir / STATE_DIR / "manifest.json").is_file():
        raise InstallError(f"backup {bdir.name} is incomplete: {STATE_DIR} missing")
    return meta


def backups_for(dest: Path) -> list[Path]:
    root = cache_dir()
    if not root.is_dir():
        return []
    found = []
    for d in root.iterdir():
        if not (d / "backup.json").is_file():
            continue
        try:
            if Path(read_json(d / "backup.json")["dest"]).resolve() == dest.resolve():
                found.append(d)
        except (InstallError, KeyError, TypeError, OSError):
            continue
    return sorted(found, key=lambda p: p.name)


def restore(dest: Path, bdir: Path) -> None:
    meta = read_backup(bdir, dest)
    current = load_manifest(dest) or {"skills": []}
    names = set(current["skills"]) | set(meta["manifest"]["skills"]) | set(meta.get("created", []))
    for name in sorted(names):
        child(dest, name)  # validate all before removing any
    for name in sorted(names):
        remove_child(dest, name)
    remove_child(dest, STATE_DIR, internal=True)
    for name in meta["manifest"]["skills"]:
        if name not in meta["missing"]:
            shutil.copytree(bdir / name, child(dest, name))
    shutil.copytree(bdir / STATE_DIR, child(dest, STATE_DIR, internal=True))


def mark_used(bdir: Path) -> None:
    meta = read_json(bdir / "backup.json")
    meta["used"] = True
    (bdir / "backup.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- release download

def safe_extract(zip_path: Path, out: Path) -> None:
    out = out.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            name = info.filename.replace("\\", "/")
            parts = [p for p in name.split("/") if p]
            if (name.startswith("/") or re.match(r"^[A-Za-z]:", name) or ".." in parts):
                raise InstallError(f"unsafe path in archive: {info.filename}")
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise InstallError(f"symlink in archive: {info.filename}")
            target = (out / name).resolve()
            if target != out and out not in target.parents:
                raise InstallError(f"unsafe path in archive: {info.filename}")
        zf.extractall(out)


def archive_url(ref: str) -> str:
    if not re.match(r"^[A-Za-z0-9._/-]+$", ref) or ".." in ref:
        raise InstallError(f"invalid ref: {ref!r}")
    kind = "tags" if re.match(r"^v?\d+\.\d+", ref) else "heads"
    return f"https://github.com/{REPO}/archive/refs/{kind}/{ref}.zip"


def release_root(extracted: Path) -> Path:
    tops = [p for p in extracted.iterdir() if p.is_dir()]
    for c in tops + [extracted]:
        if (c.joinpath(*PLUGIN_PARTS) / ".claude-plugin" / "plugin.json").is_file():
            return c
    raise InstallError("downloaded archive has no plugins/academic-writing/.claude-plugin/plugin.json")


# ---------------------------------------------------------------- commands

def cmd_install(args) -> int:
    src = source_root(args.source)
    if not src:
        raise InstallError("run install from a clone of the repository (or pass --source); "
                           "an installed copy updates with: install.py update")
    dest = resolve_dest(args)
    plan = plan_install(src.joinpath(*PLUGIN_PARTS), dest, force_overwrite=args.force_overwrite)
    if args.target == "claude" or ".claude" in dest.parts:
        say("Warning: Claude Code normally gets these skills from the plugin "
            "(/plugin install academic-writing@academic-writing-skills). With both, every skill "
            "appears twice.")
    old = plan["old"]
    if old and parse_version(plan["version"]) < parse_version(old["version"]):
        if not confirm(f"{dest} has {old['version']}; install older {plan['version']}?", args.yes):
            return 1
    if plan["removed"] and not confirm(
            f"This source no longer ships {', '.join(plan['removed'])}; remove from {dest}?", args.yes):
        return 1
    if plan["foreign"]:
        say(f"Overwriting folders not installed by this family: {', '.join(plan['foreign'])}")
    if old:
        say(f"Backup: {backup(dest, plan['created'], kind='install')}")
    say(f"Installing {FAMILY} {plan['version']} into {dest}")
    installer = src / "install.py"
    apply_install(plan, installer if installer.is_file() else this_file(),
                  {"repo": REPO, "ref": "local", "path": str(src)})
    warn_duplicates(dest)
    say(f"Done. Start a new agent session to load the skills. Update later with:\n"
        f"  python \"{(dest / STATE_DIR / 'install.py').as_posix()}\" update")
    return 0


def cmd_version(args) -> int:
    dest = resolve_dest(args)
    src = source_root(args.source)
    if src:
        say(f"this copy: {plugin_version(src.joinpath(*PLUGIN_PARTS))} ({src})")
    m = load_manifest(dest)
    if m:
        say(f"installed: {m.get('version')} at {dest} ({len(m['skills'])} skills, "
            f"from {m.get('source', {}).get('ref', '?')}, {m.get('installed_at', '?')})")
    else:
        say(f"installed: none at {dest}")
    return 0


def remote_version() -> str:
    try:
        data = json.loads(fetch(RAW_PLUGIN_JSON).decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise InstallError(f"could not read the latest version: {e}") from e
    return check_version(str(data.get("version", "")))


def cmd_check_update(args) -> int:
    dest = resolve_dest(args)
    m = load_manifest(dest)
    if m:
        current, where = m["version"], f"installed at {dest}"
    else:
        src = source_root(args.source)
        if not src:
            say(f"Nothing installed at {dest}.")
            return 1
        current, where = plugin_version(src.joinpath(*PLUGIN_PARTS)), f"this copy ({src})"
    latest = remote_version()
    if parse_version(latest) > parse_version(current):
        say(f"Update available: {current} -> {latest} ({where}). Run: install.py update")
    elif parse_version(latest) == parse_version(current):
        say(f"Up to date: {current} ({where}).")
    else:
        say(f"{where} has {current}, newer than main ({latest}).")
    return 0


def cmd_update(args) -> int:
    dest = resolve_dest(args)
    m = load_manifest(dest)
    if not m:
        raise InstallError(f"nothing installed at {dest}; run install first")
    current = m["version"]
    url = archive_url(args.ref)
    with tempfile.TemporaryDirectory(prefix="aws-update-") as tmp:
        tmp = Path(tmp)
        say(f"Downloading {url}")
        try:
            data = fetch(url)
        except (urllib.error.URLError, OSError) as e:
            raise InstallError(f"download failed: {e}") from e
        zpath = tmp / "release.zip"
        zpath.write_bytes(data)
        out = tmp / "x"
        out.mkdir()
        try:
            safe_extract(zpath, out)
        except zipfile.BadZipFile as e:
            raise InstallError(f"download is not a zip archive: {e}") from e
        root = release_root(out)
        plan = plan_install(root.joinpath(*PLUGIN_PARTS), dest, strict=True,
                            force_overwrite=args.force_overwrite)
        new_version = plan["version"]
        if plan["removed"] and not args.allow_removal:
            raise InstallError(f"release {new_version} lacks installed skill(s): "
                               f"{', '.join(plan['removed'])}; pass --allow-removal if that is intended")
        cmp_new, cmp_cur = parse_version(new_version), parse_version(current)
        if cmp_new < cmp_cur and not args.allow_downgrade:
            raise InstallError(f"release {new_version} is older than installed {current}; "
                               "pass --allow-downgrade to install it anyway")
        if cmp_new == cmp_cur and not args.force:
            say(f"Already at {current}. Pass --force to reinstall from {args.ref}.")
            return 0
        if not confirm(f"Replace {current} with {new_version} in {dest}?", args.yes):
            return 1
        bdir = backup(dest, plan["created"], kind="update")
        say(f"Backup: {bdir}")
        installer = root / "install.py"
        done = False
        try:
            apply_install(plan, installer if installer.is_file() else this_file(),
                          {"repo": REPO, "ref": args.ref, "url": url})
            done = True
        finally:
            if not done:
                say("Update did not finish; restoring the backup.")
                restore(dest, bdir)
    say(f"Updated {current} -> {new_version}. Start a new agent session. Undo with: install.py rollback")
    return 0


def cmd_rollback(args) -> int:
    dest = resolve_dest(args)
    found = backups_for(dest)
    if args.list:
        if not found:
            say(f"No backups for {dest} in {cache_dir()}.")
        for d in found:
            try:
                meta = read_json(d / "backup.json")
                used = " (restored)" if meta.get("used") else ""
                say(f"{d.name}  {meta.get('kind', '?')}  {meta['manifest'].get('version', '?')}{used}")
            except (InstallError, KeyError, TypeError):
                say(f"{d.name}  unreadable")
        return 0
    if args.to:
        if not BACKUP_ID_RE.match(args.to):
            raise InstallError(f"invalid backup id: {args.to!r} (see rollback --list)")
        matches = [d for d in found if d.name == args.to]
        if not matches:
            raise InstallError(f"no backup {args.to} for {dest} (see rollback --list)")
        bdir = matches[0]
    else:
        candidates = []
        for d in found:
            try:
                meta = read_json(d / "backup.json")
            except InstallError:
                continue
            if not meta.get("used") and meta.get("kind") != "rollback":
                candidates.append(d)
        if not candidates:
            raise InstallError(f"no unused backup for {dest} (see rollback --list, then --to <id>)")
        bdir = candidates[-1]
    meta = read_backup(bdir, dest)
    old = meta["manifest"]["version"]
    cur_m = load_manifest(dest)
    cur = cur_m["version"] if cur_m else "none"
    if not confirm(f"Restore {old} (backup {bdir.name}) over {cur} in {dest}?", args.yes):
        return 1
    if cur_m:
        snap = backup(dest, created=[n for n in meta["manifest"]["skills"] if n not in cur_m["skills"]],
                      kind="rollback")
        say(f"Current state saved: {snap.name} (undo with rollback --to {snap.name})")
    restore(dest, bdir)
    mark_used(bdir)
    say(f"Restored {old} in {dest}. Backup kept at {bdir}.")
    return 0


def cmd_uninstall(args) -> int:
    dest = resolve_dest(args)
    m = load_manifest(dest)
    if not m:
        raise InstallError(f"nothing installed at {dest}")
    names = m["skills"]
    for name in names:
        child(dest, name)
    if not confirm(f"Remove {len(names)} skills ({', '.join(names)}) and {STATE_DIR}/ from {dest}?",
                   args.yes):
        return 1
    for name in names:
        remove_child(dest, name)
    remove_child(dest, STATE_DIR, internal=True)
    say(f"Removed from {dest}. Other skills there were not touched. Backups stay in {cache_dir()}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="install.py", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, yes=True):
        sp.add_argument("--target", choices=sorted(PROJECT_TARGETS),
                        help="agents (default: Codex, Gemini CLI, OpenCode), claude, gemini, opencode")
        sp.add_argument("--project", metavar="DIR", help="install into DIR/.agents/skills (or the target's project folder)")
        sp.add_argument("--dest", metavar="DIR", help="any skills folder, e.g. ~/.hermes/skills")
        sp.add_argument("--source", metavar="DIR", help=argparse.SUPPRESS)
        if yes:
            sp.add_argument("--yes", "-y", action="store_true", help="do not ask for confirmation")

    ins = sub.add_parser("install", help="copy the skills into an agent's skills folder")
    common(ins)
    ins.add_argument("--force-overwrite", action="store_true",
                     help="replace same-named folders this installer did not create")
    common(sub.add_parser("version", help="show this copy's and the installed version"), yes=False)
    common(sub.add_parser("check-update", help="compare with the latest version on GitHub (read-only)"), yes=False)
    up = sub.add_parser("update", help="download a release, back up, replace")
    common(up)
    up.add_argument("--ref", default="main", help="branch or tag, e.g. main or v1.13.0 (default main)")
    up.add_argument("--allow-downgrade", action="store_true")
    up.add_argument("--allow-removal", action="store_true", help="accept a release that drops an installed skill")
    up.add_argument("--force", action="store_true", help="reinstall even if the version is unchanged")
    up.add_argument("--force-overwrite", action="store_true",
                    help="replace same-named folders this installer did not create")
    rb = sub.add_parser("rollback", help="restore the latest unused backup (current state is saved first)")
    common(rb)
    rb.add_argument("--list", action="store_true", help="list backups for this destination")
    rb.add_argument("--to", metavar="ID", help="restore this backup (an id from --list)")
    common(sub.add_parser("uninstall", help="remove this family's skills only"))
    return p


COMMANDS = {"install": cmd_install, "version": cmd_version, "check-update": cmd_check_update,
            "update": cmd_update, "rollback": cmd_rollback, "uninstall": cmd_uninstall}


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 10):
        print("install.py needs Python 3.10 or newer.", file=sys.stderr)
        return 1
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.cmd](args)
    except InstallError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
