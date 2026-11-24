<p align="left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.png">
    <img src="assets/header-light.png" width="600" height="160" alt="Wordflow logo and name">
  </picture>
</p>

<p align="center"><b>Writing and document design; a modern word processor built in pure Rust.</b></p>

Wordflow is part of the FlowApps suite. It is a fast, open-source word processor with a familiar
workflow: the ribbon, styles, tables, track changes, references and mail merge. It reads and writes
.docx and runs natively on macOS and Windows.

## Why Wordflow?

- **Free and open source** — MIT OR Apache-2.0
- **Your files** — opens and saves .docx (OOXML), plus .odt, .rtf, .html, .md, .tex and .txt
- **Familiar workflow** — ribbon tabs, styles gallery, track changes, comments, mail merge
- **Native desktop** — macOS (Apple Silicon) and Windows x64 builds
- **Private** — works offline; no accounts, no telemetry, no cloud

## Features

- **Review.** Track changes, comment balloons, accept/reject, spelling and grammar as you type.
- **References.** Tables of contents, footnotes, citations, index and captions.
- **Design.** Themes, style sets, watermarks, page colour and borders, dark mode.
- **Layout.** Drop caps, text wrapping, automatic hyphenation, line numbers, page borders.
- **File.** Templates, recent documents, document properties, export to PDF.

## Download and install

Download the installer for your system (latest version, 0.1.0 release candidate 1). Wordflow is also available through the [FlowApps launcher](https://github.com/reachneoagent-commits/FlowApps-Launcher/releases/latest).

| Platform | Download |
|---|---|
| macOS, Apple silicon (M1 or newer) | [DMG](https://github.com/reachneoagent-commits/wordflow/releases/download/v0.1.0-rc.1/wordflow-0.1.0-rc.1-macos-arm64.dmg) |
| Windows x64 | [Portable zip](https://github.com/reachneoagent-commits/wordflow/releases/download/v0.1.0-rc.1/wordflow-0.1.0-rc.1-windows-x64-portable.zip) (unzip and run) |

macOS on Intel and a Windows installer are not built yet. Older versions and checksums are on the [Releases page](https://github.com/reachneoagent-commits/wordflow/releases).

The app is not code-signed with a paid certificate, so macOS and Windows warn you the first time you open it. Every release lists SHA-256 checksums to check the files against.

- **Mac:** open the DMG and drag Wordflow to Applications. Then right-click Wordflow, choose Open, and click Open again.
- **Windows:** if SmartScreen appears, click More info, then Run anyway.

## Supported platforms

- **Desktop app:** macOS on Apple Silicon; Windows x64 (Intel Mac build planned)

## Build from source

You need [Rust](https://rustup.rs/) 1.95+. Then run:

```bash
cargo build --release -p wordflow
```

The desktop app binary is produced under `target/release/`. Language data (craft-i18n) is an optional build input; without it Wordflow builds with an English interface.

## About this fork

Wordflow is based on [WordCraft](https://github.com/storytold/wordcraft) by the ArtCraft team, rebranded as a FlowApps product. The original project is dual-licensed under MIT or Apache-2.0; that licensing is preserved here.

The ArtCraft name, wordmark and logos remain trademarks of the ArtCraft Team and are not used in Wordflow. Per the original NOTICE, forks and modified versions must remove them.

## Credits & Acknowledgments

Full third-party credits are in [`NOTICE`](NOTICE) and [`ATTRIBUTION.md`](ATTRIBUTION.md).

- **[WordCraft](https://github.com/storytold/wordcraft)** by the ArtCraft team: the original word processor engine, UI and file formats (MIT OR Apache-2.0).
- **[craft-libs](https://github.com/storytold/craft-libs)** by the ArtCraft team: the shared UI framework and file-format libraries this app is built on, plus [egui](https://github.com/emilk/egui) (MIT OR Apache-2.0).
- **FlowApps branding, logo and symbol:** Reach Neo (trademark of Reach Neo).
- Bundled fonts (Source Sans 3, Source Serif 4, Inter, JetBrains Mono) — SIL Open Font License 1.1.
- Language data from [craft-i18n](https://github.com/storytold/craft-i18n) — various open licenses.

Wordflow is not affiliated with or endorsed by ArtCraft or the WordCraft contributors.

## License

Wordflow is dual-licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option.

**Copyright (c) 2026 Reach Neo and the Wordflow contributors.**
