#!/usr/bin/env python3
"""Turn a WordCraft checkout into Wordflow.

Every change Wordflow makes to a file that upstream owns is made here, never by hand, so that
after merging a new upstream release the whole rebrand can be applied again:

    python3 rebrand/apply.py            # apply (safe to run any number of times)
    python3 rebrand/apply.py --check    # exit 1 if anything is still un-rebranded

Three kinds of change:
  * text edits (names, ids, links) made with find-and-replace below;
  * code changes too big for that (removing the Discord button) kept as patches in
    rebrand/patches/, applied with a three-way merge so small upstream changes still fit;
  * our app icons, copied from rebrand/app-icon/ over upstream's.

Files that only Wordflow has (rebrand/, brand/, docs/UPSTREAM.md, README.md, our release
workflows, assets/header-*.png) are ordinary files and are not touched by this script.

A step that can no longer find the upstream text it edits stops with an error naming the file, so
a changed upstream line is noticed instead of silently skipped. See docs/UPSTREAM.md.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "rebrand"

NAME = "Wordflow"
BUNDLE = "com.wordflow.app"
REPO = "reachneoagent-commits/wordflow"
REPO_URL = f"https://github.com/{REPO}"
PUBLISHER = "Reach Neo"

UP_NAME = "WordCraft"
UP_BUNDLE = "ai.storyteller.wordcraft"
UP_COMMUNITY = "Community: https://discord.gg/artcraft · https://getartcraft.com/apps/wordcraft · https://github.com/storytold/wordcraft"

CHECK = "--check" in sys.argv
changed: list[str] = []
problems: list[str] = []


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, old: str, new: str) -> None:
    if old == new:
        return
    changed.append(str(path.relative_to(ROOT)))
    if not CHECK:
        path.write_text(new, encoding="utf-8", newline="")


def edit(rel: str, pattern: str, repl: str, done: str, *, count: int = 0, flags: int = 0) -> None:
    """Replace `pattern` in one file. `done` is text that is present once the edit has been made;
    if neither the pattern nor `done` is found, upstream changed the line and we stop."""
    path = ROOT / rel
    if not path.exists():
        problems.append(f"{rel}: file is gone (upstream moved or removed it)")
        return
    old = read(path)
    new, n = re.subn(pattern, repl, old, count=count, flags=flags)
    if n == 0 and done not in old:
        problems.append(f"{rel}: could not find /{pattern}/ to edit, and {done!r} is not there either")
        return
    write(path, old, new)


def lit(s: str) -> str:
    return re.escape(s)


# --------------------------------------------------------------------------------------------
# 1. The app itself: window title, app id, version and log lines, crash reports.
#    The binary, crate and log-file names stay `wordcraft` (renaming them buys nothing and
#    would touch hundreds of files on every merge).
# --------------------------------------------------------------------------------------------
def app() -> None:
    rel = "apps/wordcraft/src/main.rs"
    edit(rel, lit("wordcraft — the WordCraft desktop app"), "wordflow — the Wordflow desktop app", "the Wordflow desktop app")
    edit(rel, lit('crash::install("WordCraft",'), 'crash::install("Wordflow",', 'crash::install("Wordflow",')
    edit(rel, lit('println!("wordcraft {} ({})"'), 'println!("wordflow {} ({})"', 'println!("wordflow {} ({})"')
    edit(rel, lit('log::info!("WordCraft {} ({}), log file'), 'log::info!("Wordflow {} ({}), log file', 'log::info!("Wordflow {} ({}), log file')
    edit(rel, lit('.with_title("WordCraft")'), '.with_title("Wordflow")', '.with_title("Wordflow")')
    edit(rel, lit(f'"{UP_BUNDLE}"'), f'"{BUNDLE}"', f'"{BUNDLE}"')
    edit(rel, r'run_native\(\n(\s+)"WordCraft",', r'run_native(\n\1"Wordflow",', '"Wordflow",\n        options,')


# --------------------------------------------------------------------------------------------
# 2. Links: the AI-agent server and the About box point at our repository, not ArtCraft's
#    site and Discord.
# --------------------------------------------------------------------------------------------
def links() -> None:
    edit(
        "crates/mcp/src/server.rs",
        r'format!\(\n\s+"\{INSTRUCTIONS\} Backend: \{\}\. ' + lit(UP_COMMUNITY) + r'",\n\s+self\.backend\.describe\(\)\n\s+\)',
        f'format!("{{INSTRUCTIONS}} Backend: {{}}. Source: {REPO_URL}", self.backend.describe())',
        f"Source: {REPO_URL}",
    )
    edit("crates/mcp/src/tests/oracle.rs", lit(UP_COMMUNITY), f"Source: {REPO_URL}", f"Source: {REPO_URL}")

    rel = "crates/ui-egui/src/credits.rs"
    edit(rel, r"\(site,\n/// Discord, source\)", "(site,\n/// source)", "(site,\n/// source)")
    edit(
        rel,
        r"\.links\(\[\n\s+AboutLink::new\(tl!\(\"getartcraft\.com/apps/wordcraft\"\).*?\n\s+\]\)",
        '.links([AboutLink::new(\n'
        f'        tl!("Source code: github.com/{REPO}").to_string(),\n'
        f'        "{REPO_URL}",\n'
        "    )])",
        f'tl!("Source code: github.com/{REPO}")',
        flags=re.S,
    )


# --------------------------------------------------------------------------------------------
# 3. Installers. Our own release workflow builds the Mac app and Windows zip itself, but the
#    upstream packaging files are kept correct too, so nothing ships under WordCraft's name.
#    The executable stays `wordcraft(.exe)`, so registry paths that name it stay as they are.
#    Windows installer ids (UpgradeCode, Guid) are left as upstream's: changing them would stop
#    already-installed copies from upgrading.
# --------------------------------------------------------------------------------------------
def installers() -> None:
    rel = "packaging/macos/Info.plist.in"
    for key in ("CFBundleDisplayName", "CFBundleName"):
        edit(rel, rf"(<key>{key}</key>\n\s*<string>){UP_NAME}(</string>)", rf"\g<1>{NAME}\2", f"<key>{key}</key>\n  <string>{NAME}</string>")
    edit(rel, lit(f"<string>{UP_BUNDLE}</string>"), f"<string>{BUNDLE}</string>", f"<string>{BUNDLE}</string>")
    edit(rel, r"<key>WordCraft(Version|BuildCommit)</key>", r"<key>Wordflow\1</key>", "<key>WordflowVersion</key>")
    edit(rel, lit("Copyright © the WordCraft authors."), f"Copyright © {PUBLISHER}.", f"Copyright © {PUBLISHER}.")

    path = ROOT / "packaging/windows/wordcraft.wxs"
    if not path.exists():
        problems.append("packaging/windows/wordcraft.wxs: file is gone")
        return
    old = read(path)
    new = old.replace("Learning Machines LLC", PUBLISHER)
    new = new.replace("https://getartcraft.com/apps/wordcraft", REPO_URL)
    new = new.replace("https://discord.gg/artcraft", REPO_URL)
    new = new.replace('<Directory Id="CraftSuiteFolder" Name="ArtCraft">', '<Directory Id="CraftSuiteFolder" Name="FlowApps">')
    # Every shown name, product name, ProgId and registry key; `WordcraftExe`-style ids and
    # `wordcraft.exe` are other spellings and are left alone.
    new = new.replace(UP_NAME, NAME)
    if PUBLISHER not in new or "FlowApps" not in new:
        problems.append("packaging/windows/wordcraft.wxs: publisher or install folder line not found")
    write(path, old, new)


# --------------------------------------------------------------------------------------------
# 4. Code changes kept as patches: no Discord button, link or setting anywhere; and the
#    title bar keeps clear of the macOS window buttons.
# --------------------------------------------------------------------------------------------
def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def patches() -> None:
    for patch in sorted((HERE / "patches").glob("*.patch")):
        rel = str(patch.relative_to(ROOT))
        if git("apply", "--reverse", "--check", rel).returncode == 0:
            continue  # already applied
        changed.append(f"{rel} (not applied)")
        if CHECK:
            continue
        if git("apply", rel).returncode == 0:
            continue
        r = git("apply", "--3way", rel)
        if r.returncode != 0:
            problems.append(f"{rel}: does not apply cleanly; fix the conflict markers it left, then refresh the patch (docs/UPSTREAM.md)\n{r.stderr.strip()}")


# --------------------------------------------------------------------------------------------
# 5. Our app icons over upstream's (same file names, so nothing else changes).
# --------------------------------------------------------------------------------------------
def icons() -> None:
    src = HERE / "app-icon"
    for f in sorted(p for p in src.rglob("*") if p.is_file()):
        dest = ROOT / "assets/app-icon" / f.relative_to(src)
        if dest.exists() and dest.read_bytes() == f.read_bytes():
            continue
        changed.append(str(dest.relative_to(ROOT)))
        if not CHECK:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dest)


# --------------------------------------------------------------------------------------------
# 6. Notes for people and coding agents, the NOTICE addition, and merge rules.
# --------------------------------------------------------------------------------------------
AGENT_MARK = "<!-- Wordflow (rebrand/apply.py) -->"
AGENT_NOTE = f"""{AGENT_MARK}
# Wordflow

This repository is **Wordflow**, a fork of WordCraft. Read `docs/UPSTREAM.md` first. In short:

- Never hand-edit a file that came from upstream to change branding, ids, links or icons: add the
  change to `rebrand/apply.py` (or a patch in `rebrand/patches/`) and run it, so it survives the
  next upstream merge.
- Wordflow's own files are `rebrand/`, `brand/`, `docs/UPSTREAM.md`, `README.md`,
  `assets/header-*.png` and `.github/workflows/release.yml` / `windows-release.yml`.
- Crate, binary and environment-variable names stay `wordcraft*` / `WORDCRAFT_*`.

"""

NOTICE_ADD = """
Wordflow

Wordflow is a modified version of WordCraft, made by Reach Neo as part of the FlowApps suite.
It changes the name, icon, identifiers and links and removes the Discord button;
rebrand/apply.py lists every change. Wordflow is not affiliated with or endorsed by the
ArtCraft Team. The Wordflow name and mark (brand/, assets/app-icon/) are not covered by the
license above.
"""

ATTRS_ADD = """
# Wordflow (rebrand/apply.py): files we replace whole keep our version in a merge.
# Needs `git config merge.ours.driver true` once per clone (docs/UPSTREAM.md).
README.md merge=ours
.github/workflows/release.yml merge=ours
.github/workflows/windows-release.yml merge=ours
assets/app-icon/** merge=ours
"""


def notes() -> None:
    path = ROOT / "CLAUDE.md"
    old = read(path)
    if AGENT_MARK not in old:
        write(path, old, AGENT_NOTE + old)
    for rel, add, done in (("NOTICE", NOTICE_ADD, "Wordflow is a modified version"), (".gitattributes", ATTRS_ADD, "merge=ours")):
        path = ROOT / rel
        old = read(path) if path.exists() else ""
        if done not in old:
            write(path, old, old.rstrip("\n") + "\n" + add)


def rustfmt() -> None:
    if CHECK or not changed or not shutil.which("cargo"):
        return
    subprocess.run(["cargo", "fmt", "--all"], cwd=ROOT, check=False)


def main() -> int:
    patches()
    app()
    links()
    installers()
    icons()
    notes()
    rustfmt()

    for p in problems:
        print(f"error: {p}", file=sys.stderr)
    if CHECK:
        for c in changed:
            print(f"not rebranded: {c}")
        return 1 if (changed or problems) else 0
    print(f"{len(changed)} change(s) made" if changed else "already rebranded: nothing to change")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
