# Keeping up with upstream

Wordflow is a fork of [WordCraft](https://github.com/storytold/wordcraft) (MIT or Apache-2.0).
This is how we take their updates without losing our name, icon and links.

## The one rule

**Every change Wordflow makes to a file that came from upstream is made by `rebrand/apply.py`,
never by hand.** The script can be run again at any time, so after a merge we can take upstream's
version of any conflicted file and re-apply our changes in one step.

## What lives where

| Ours (upstream has no such file, or we replace theirs whole) | Upstream's, changed only by `rebrand/apply.py` |
|---|---|
| `rebrand/` (script, patches, icons, `upstream.json`) | everything under `crates/`, `apps/`, `packaging/` |
| `brand/` (logos, `.ai` source) | `assets/app-icon/` (file names theirs, artwork ours, from `rebrand/app-icon/`) |
| `docs/UPSTREAM.md`, `README.md`, `assets/header-*.png` | `CLAUDE.md`, `NOTICE`, `.gitattributes`, `ATTRIBUTION.md` |
| `.github/workflows/release.yml`, `windows-release.yml` | |

The script makes three kinds of change:

- **Text edits** (find and replace): window title, bundle id `com.wordflow.app`, version and log
  lines, crash reports, About box and AI-agent links, Mac `Info.plist.in`, Windows installer names.
- **Patches** in `rebrand/patches/`, for code changes too big for find and replace: no Discord
  button, link, keytip or setting anywhere, and the title bar keeps clear of the macOS window
  buttons. Applied with a three-way merge, so they still fit when upstream edits nearby lines.
- **Icons**: `rebrand/app-icon/` copied over upstream's files of the same names.

Left alone on purpose: crate and binary names (`wordcraft*`), environment variables
(`WORDCRAFT_*`), log-file and settings-folder names, the MCP server name, licences and credits,
upstream's docs, and the Windows installer ids (changing them would stop installed copies from
upgrading).

## Which upstream version we follow

WordCraft cuts releases on side branches, so their release tags are not on `main`. Wordflow
follows their `main`; `rebrand/upstream.json` records the upstream commit we last merged.

## Merging upstream

Set the clone up once, so upstream's tags arrive as `upstream/v…` and never collide with ours:

```bash
git remote add upstream https://github.com/storytold/wordcraft.git
git config remote.upstream.tagOpt --no-tags
git config --add remote.upstream.fetch '+refs/tags/*:refs/tags/upstream/*'
git config merge.ours.driver true
```

Never push the `upstream/*` tags. Then:

```bash
git fetch upstream
git checkout -b upstream-sync
git merge upstream/main
```

If there are conflicts:

1. For a file in the right-hand column above, take theirs: `git checkout --theirs -- <file>`.
2. For a file we deleted that they changed ("deleted by us"): keep it deleted, `git rm <file>`.
3. For `README.md` or our workflows, keep ours: `git checkout --ours -- <file>`.

Then re-apply the rebrand and check it:

```bash
python3 rebrand/apply.py
python3 rebrand/apply.py --check     # prints nothing and exits 0 when everything is rebranded
```

If the script stops with `could not find … to edit`, upstream changed that line: look at it now and
update the pattern in `rebrand/apply.py`. If a patch leaves conflict markers, resolve them in the
file, then refresh the patch so the next merge applies cleanly:

```bash
git diff <upstream commit> -- <the patch's files> > rebrand/patches/01-no-discord-and-mac-title-bar.patch
```

Build and test, set the new commit and date in `rebrand/upstream.json`, commit and open a pull
request:

```bash
cargo build --locked -p wordcraft -p wordcraft-cli
cargo test --locked -p wordcraft-ui-egui -p wordcraft-mcp --no-fail-fast
```

Run the app once and look at it before releasing: tests don't see icons or the title bar.

### Known work for the next merge

Tried on 2026-11-26 against upstream `main` (81 commits ahead): the patch and every other edit
applied, except three places upstream changed:

- `apps/wordcraft/src/main.rs`: the window title and `run_native` name now come from
  `wordcraft_ui_egui::os_window::name_for(...)` (a new "Nightly" identity), so the name edit moves
  to `crates/ui-egui/src/os_window.rs`.
- `crates/ui-egui/src/credits.rs`: a second, Nightly-only About box with Discord and ArtCraft links.
- `crates/ui-egui/src/chrome/tests.rs`: upstream edited the Discord test the patch deletes
  (conflict; keep it deleted).

## Releasing

Actions → Release builds the macOS DMG and the Windows portable zip and publishes a GitHub
release. The FlowApps launcher installs and updates Wordflow from those releases.
