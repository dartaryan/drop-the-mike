# One-Click Installation for a Python Desktop App on Windows

This guide provides a complete, practical blueprint for turning a Python/customtkinter desktop application into a professional one-click installer for non-technical Windows users. **The recommended end-to-end workflow is: PyInstaller (onedir) → Inno Setup installer → GitHub Actions CI → GitHub Releases hosting → download button on GitHub Pages.** Total first-time setup takes roughly 4–8 hours. Every tool recommended below is free, open-source, and battle-tested in production.

The document covers bundling your `.py` into a standalone `.exe`, packaging FFmpeg binaries legally, creating a polished Windows installer, automating builds with GitHub Actions, and hosting downloads — with code examples you can copy-paste today.

---

## 1. Bundling a Python app into a standalone .exe

### Comparing the four major tools in 2025–2026

| Feature | PyInstaller 6.18 | Nuitka 4.0 | cx_Freeze 8.5 | py2exe 0.14 |
|---|---|---|---|---|
| **Python support** | 3.8–3.14 | 3.4–3.14 | 3.10–3.14 | 3.9–3.13 |
| **Runs without Python?** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Single-file .exe** | ✅ `--onefile` | ✅ `--onefile` | ❌ Folder only | ⚠️ Limited on 3.12+ |
| **CustomTkinter docs** | ✅ Official wiki + community | ⚠️ YAML config + issues | ❌ Minimal | ❌ None |
| **Build speed** | ⚡ ~20 seconds | 🐢 Minutes (compiles to C) | ⚡ Fast | ⚡ Fast |
| **Startup speed** | 🐢 Slower (especially onefile) | ⚡ Fast | ⚡ Fast | Moderate |
| **Typical output size** | 30–80 MB | 15–50+ MB | Similar to PyInstaller | Smaller |
| **AV false positives** | ⚠️ Common | ⚠️ Less common | ⚠️ Less common | ⚠️ Possible |
| **Community size** | 🏆 Largest (~12.8k GitHub stars) | Large (~14.4k stars) | Smaller (~1.5k) | Small (~964) |
| **C compiler needed** | ❌ No | ✅ Yes (MSVC/MinGW/Zig) | ❌ No | ❌ No |
| **License** | GPLv2 (free for all) | AGPLv3 (free; commercial add-on) | PSF | MPL |

All four tools produce executables that **run without Python installed** on the target machine — they bundle the CPython interpreter and all dependencies. Every tool is free for commercial use.

**PyInstaller** is the clear winner for this use case. It has the largest community, the most customtkinter-specific documentation (including an official wiki page), and requires no C compiler. Nuitka is a strong second choice if startup speed or mild code obfuscation matters — it compiles Python to C then to native machine code — but its build times are ~20× longer and it requires installing MSVC or MinGW. cx_Freeze works but lacks single-file mode and has minimal customtkinter documentation. py2exe is Windows-only, has a shrinking community, and deprecated its CLI in v0.13.

- **Official docs**: [pyinstaller.org](https://pyinstaller.org/en/stable/) · [nuitka.net](https://nuitka.net/user-documentation/) · [cx-freeze.readthedocs.io](https://cx-freeze.readthedocs.io/en/latest/) · [pypi.org/project/py2exe](https://pypi.org/project/py2exe/)

### The customtkinter bundling problem (and how to solve it)

CustomTkinter ships with non-Python data files — `.json` theme files (like `blue.json`), `.otf` fonts, and image assets. PyInstaller's auto-detection **does not find these files**, causing a `FileNotFoundError: blue.json` crash at runtime. The official CustomTkinter wiki at [github.com/TomSchimansky/CustomTkinter/wiki/Packaging](https://github.com/TomSchimansky/CustomTkinter/wiki/Packaging) documents this issue and originally recommended `--onedir` mode only. Community workarounds now make `--onefile` work too.

**Recommended command (`--onedir` mode — officially supported):**

```bash
pyinstaller --noconfirm --onedir --windowed \
  --collect-all customtkinter \
  --name "MyApp" \
  --icon=icon.ico \
  your_app.py
```

The `--collect-all customtkinter` flag grabs every `.py`, `.json`, `.otf`, and asset file from the customtkinter package automatically. This is the simplest, most reliable approach.

**`--onefile` mode (community workaround):**

Add this at the **top** of your Python script, before `import customtkinter`:

```python
import os, sys

if getattr(sys, 'frozen', False):
    # Running inside PyInstaller bundle
    os.chdir(sys._MEIPASS)
```

Then build:

```bash
pyinstaller --noconfirm --onefile --windowed \
  --collect-all customtkinter \
  --name "MyApp" \
  --icon=icon.ico \
  your_app.py
```

**Advanced approach using a .spec file** (full control):

```python
# MyApp.spec
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

a = Analysis(
    ['your_app.py'],
    datas=collect_data_files('customtkinter') + [('assets/', 'assets/')],
    hiddenimports=collect_submodules('customtkinter'),
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas,
          name='MyApp', console=False, icon='icon.ico')
```

Build with: `pyinstaller MyApp.spec`

### Single-file vs. folder distribution

| Aspect | `--onefile` | `--onedir` |
|---|---|---|
| **Distribution** | Single .exe, easy to share casually | Folder with many files — needs an installer |
| **Startup time** | Slower (extracts to temp dir every launch) | Faster (no extraction) |
| **AV false positives** | More likely to trigger | Slightly less suspicious |
| **CustomTkinter** | Requires code workaround (above) | Works directly with `--collect-all` |
| **Best for** | Quick sharing, portable use | **Installer-based distribution (recommended)** |

**Bottom line**: Use `--onedir` and wrap the output folder in an Inno Setup installer. This gives non-technical users a single installer `.exe` while avoiding the startup delays and AV issues of `--onefile`. The installer handles the "one-click" experience.

### Nuitka alternative command (if needed)

```bash
python -m nuitka --standalone \
  --enable-plugin=tk-inter \
  --include-package-data=customtkinter \
  --windows-disable-console \
  --windows-icon-from-ico=icon.ico \
  --output-filename=MyApp.exe \
  your_app.py
```

Nuitka requires a C compiler: on Windows, MinGW64 is auto-downloaded if absent (but doesn't work with Python 3.13+ — use MSVC or Zig instead). Build times are measured in minutes, not seconds.

---

## 2. Bundling FFmpeg inside the package

### Embedding vs. shipping alongside

Both approaches work. With PyInstaller `--add-binary`, you can embed `ffmpeg.exe` directly inside the bundle:

```bash
pyinstaller --onedir --windowed --collect-all customtkinter \
  --add-binary "ffmpeg/ffmpeg.exe;ffmpeg" \
  --add-binary "ffmpeg/ffprobe.exe;ffmpeg" \
  --name "MyApp" your_app.py
```

Or in a `.spec` file:

```python
a = Analysis(['your_app.py'],
    binaries=[('ffmpeg/ffmpeg.exe', 'ffmpeg'), ('ffmpeg/ffprobe.exe', 'ffmpeg')],
    datas=collect_data_files('customtkinter'),
)
```

**However, the best practice for installer-based distribution is to skip `--add-binary` entirely** and simply ship `ffmpeg.exe` alongside your app in the installer. This keeps your build simpler and lets you update FFmpeg independently of the app.

### Referencing FFmpeg at runtime

```python
import os, sys

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        # PyInstaller --onedir: exe sits in the app folder
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, 'ffmpeg', 'ffmpeg.exe')

# For pydub:
from pydub import AudioSegment
AudioSegment.converter = get_ffmpeg_path()

# For subprocess calls:
import subprocess
subprocess.run([get_ffmpeg_path(), '-i', 'input.mp3', 'output.wav'])
```

For `--onefile` mode, replace `os.path.dirname(sys.executable)` with `sys._MEIPASS` (the temporary extraction directory).

### FFmpeg licensing — what you need to know

FFmpeg's license depends on how it was compiled. This distinction is critical for redistribution:

- **LGPL builds** (compiled without `--enable-gpl`): Your application can remain proprietary/closed-source. You must include a notice stating "This software uses FFmpeg licensed under LGPLv2.1," provide the FFmpeg source code or a link to it, and not prohibit reverse engineering in your EULA.
- **GPL builds** (compiled with `--enable-gpl`, which enables x264/x265/xvid): Your entire application must be GPL-compatible if distributed together.
- **Nonfree builds** (compiled with `--enable-nonfree`): **Not redistributable at all.**

**For audio-only processing, LGPL builds include all common codecs** — MP3, AAC, Opus, Vorbis, FLAC, WAV — without needing any GPL libraries. This is the safest choice for proprietary apps.

Official licensing details: [ffmpeg.org/legal.html](https://www.ffmpeg.org/legal.html)

### Where to get FFmpeg binaries and their sizes

| Source | License options | Format | Typical size |
|---|---|---|---|
| **BtbN/FFmpeg-Builds** (GitHub) | GPL, **LGPL**, Nonfree | Static Win64 | LGPL: ~50–80 MB |
| **gyan.dev** | GPLv3 only | Static Win64 | Essentials: ~31 MB (.7z) |
| **Custom minimal build** | Configurable | Static | **2–5 MB** (audio-only) |

**For LGPL compliance**, use BtbN's LGPL builds: [github.com/BtbN/FFmpeg-Builds/releases](https://github.com/BtbN/FFmpeg-Builds/releases). Look for filenames like `ffmpeg-master-latest-win64-lgpl.zip`. The gyan.dev builds at [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) are all GPLv3 due to bundled x264/x265.

### Minimal audio-only FFmpeg build

For audio-only conversion, a custom-compiled FFmpeg can shrink to **2–5 MB** by disabling all video codecs:

```bash
./configure \
  --disable-programs --enable-ffmpeg --enable-ffprobe \
  --disable-doc --disable-network --disable-devices \
  --disable-everything \
  --enable-demuxer=mp3,aac,flac,ogg,wav,matroska,mov \
  --enable-decoder=mp3,aac,flac,vorbis,opus,pcm_s16le \
  --enable-encoder=libmp3lame,aac,flac,libopus,pcm_s16le \
  --enable-muxer=mp3,adts,flac,ogg,wav \
  --enable-parser=aac,mpegaudio,flac,vorbis,opus \
  --enable-protocol=file,pipe \
  --enable-filter=aresample,anull \
  --extra-ldflags=-static
```

Cross-compiling for Windows requires MinGW. For most projects, the prebuilt LGPL static binary from BtbN (~50–80 MB) is the pragmatic choice — the size gets compressed by Inno Setup anyway.

### Lightweight FFmpeg alternatives

**There are no practical alternatives for general audio format conversion.** SoX ("Sound eXchange") handles some audio formats but lacks native MP3 encoding and has a smaller codec library. Python's built-in `wave` module only reads/writes WAV. Libraries like `soundfile` (libsndfile bindings) support WAV/FLAC/OGG but not MP3/AAC. **FFmpeg remains the standard** for any app needing broad audio/video format support.

---

## 3. Creating a Windows installer

### Comparing Inno Setup, NSIS, and WiX

| Feature | Inno Setup 6.7 | NSIS 3.10 | WiX v5 |
|---|---|---|---|
| **Output format** | EXE installer | EXE installer | MSI installer |
| **Learning curve** | ✅ Easy (INI-like syntax) | Medium (assembly-like scripting) | Hard (verbose XML, MSI internals) |
| **Professional look** | ✅✅✅ Modern wizard + dark mode | ✅✅ Good with Modern UI plugin | ✅✅ Native Windows appearance |
| **Desktop shortcuts** | ✅ Built-in `[Icons]` section | ✅ Must be scripted | ✅ XML element |
| **Start Menu entries** | ✅ Built-in | ✅ Must be scripted | ✅ XML element |
| **Uninstaller** | ✅ Automatic | ⚠️ Must be set up manually | ✅ Automatic (MSI) |
| **Installer overhead** | Small | ~34 KB (smallest) | Medium |
| **Best for** | Simple-to-medium apps | Advanced customization | Enterprise/GPO deployment |
| **License** | Free, open-source | zlib/libpng (very permissive) | MS-RL |

**Inno Setup is the clear recommendation.** It produces professional-looking installers with minimal effort, includes dark mode support (v6.6+), auto-generates uninstallers, and has a Script Wizard that creates working `.iss` files interactively. NSIS is more flexible but requires more manual scripting. WiX produces MSI packages preferred in enterprise environments but has a steep learning curve that's overkill for this use case.

- **Inno Setup**: [jrsoftware.org/isinfo.php](https://jrsoftware.org/isinfo.php) · [Docs](https://jrsoftware.org/ishelp/)
- **NSIS**: [nsis.sourceforge.io](https://nsis.sourceforge.io/) · [Docs](https://nsis.sourceforge.io/Docs/)
- **WiX Toolset**: [wixtoolset.org](https://wixtoolset.org/) · [Docs](https://wixtoolset.org/docs/)

### Complete Inno Setup script

This `.iss` script packages your PyInstaller output folder (containing `MyApp.exe`) alongside an `ffmpeg/` subfolder. It creates a Desktop shortcut, Start Menu entry, uninstaller, custom icon, and optional license page.

```iss
; ============================================================
; Inno Setup Script — MyApp with bundled FFmpeg
; Requires Inno Setup 6.x+ (https://jrsoftware.org/isinfo.php)
; ============================================================

#define MyAppName      "MyApp"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "Your Name"
#define MyAppURL       "https://yoursite.com"
#define MyAppExeName   "MyApp.exe"

; Point this to your PyInstaller dist output folder
#define SourceDir      "C:\MyProject\dist\MyApp"

[Setup]
AppId={{GENERATE-A-UNIQUE-GUID-HERE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=.\Output
OutputBaseFilename=MyApp-Setup-{#MyAppVersion}
SetupIconFile={#SourceDir}\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
PrivilegesRequired=admin
; Optional license page — remove or comment out if not needed:
LicenseFile={#SourceDir}\LICENSE.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main application (all PyInstaller --onedir output files)
Source: "{#SourceDir}\{#MyAppExeName}"; DestDir: "{app}"; \
    Flags: ignoreversion
Source: "{#SourceDir}\*"; DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs; \
    Excludes: "ffmpeg\*"

; FFmpeg binaries
Source: "{#SourceDir}\ffmpeg\ffmpeg.exe"; DestDir: "{app}\ffmpeg"; \
    Flags: ignoreversion
Source: "{#SourceDir}\ffmpeg\ffprobe.exe"; DestDir: "{app}\ffmpeg"; \
    Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; Comment: "Launch {#MyAppName}"
; Start Menu uninstall shortcut
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Desktop shortcut (optional, user-selectable)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    Tasks: desktopicon; WorkingDir: "{app}"

[Run]
; Launch app after install
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
    Flags: nowait postinstall skipifsilent
```

**To compile:** Install Inno Setup, open this `.iss` file in the IDE, and press **Ctrl+F9**. Or use the CLI: `iscc.exe MyApp.iss`. The installer `.exe` appears in the `.\Output\` folder. Key constants: `{app}` = install directory, `{autopf}` = Program Files, `{group}` = Start Menu folder, `{autodesktop}` = Desktop.

---

## 4. Hosting and distribution via GitHub Releases

### Key facts about GitHub Release assets

GitHub Releases provide free, permanent hosting for binary files attached to tagged versions. **Each individual asset must be under 2 GB.** Up to 1,000 assets per release are allowed. There's no bandwidth limit or expiration — release assets persist indefinitely (unlike Actions artifacts, which expire after 90 days). Files larger than 25 MB must be uploaded via the GitHub CLI or REST API rather than the browser UI.

### URL patterns every developer should memorize

**Direct download for a specific version:**
```
https://github.com/{OWNER}/{REPO}/releases/download/{TAG}/{FILENAME}
```

**Latest release permalink (auto-redirects to newest):**
```
https://github.com/{OWNER}/{REPO}/releases/latest/download/{FILENAME}
```

This `/latest/download/` permalink performs a **302 redirect** to the actual versioned URL. It is the most important URL for download buttons. The asset filename must remain consistent across releases for it to work.

**Latest release page:**
```
https://github.com/{OWNER}/{REPO}/releases/latest
```

**REST API for latest release info (includes download counts):**
```
GET https://api.github.com/repos/{OWNER}/{REPO}/releases/latest
```

Works without authentication for public repos (60 requests/hour rate limit). The response includes `tag_name`, `assets[].browser_download_url`, and `assets[].download_count`.

- **Docs**: [About Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) · [Linking to Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases)

### Complete GitHub Actions workflow

This workflow triggers when you push a version tag, builds the `.exe` with PyInstaller, compiles an Inno Setup installer, and uploads both to a new GitHub Release:

```yaml
# .github/workflows/build-and-release.yml
name: Build and Release Windows Installer

on:
  push:
    tags:
      - 'v*.*.*'    # Triggers on v1.0.0, v2.1.3, etc.

permissions:
  contents: write    # Required for creating releases

jobs:
  build:
    name: Build Windows Installer
    runs-on: windows-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller customtkinter
          pip install -r requirements.txt

      - name: Extract version from tag
        id: version
        shell: bash
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Build with PyInstaller
        run: |
          pyinstaller --noconfirm --onedir --windowed ^
            --collect-all customtkinter ^
            --name "MyApp" ^
            --icon=assets/icon.ico ^
            main.py
        shell: cmd

      - name: Download FFmpeg LGPL static build
        run: |
          curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl.zip
          7z x ffmpeg.zip -offmpeg_temp
          mkdir dist\MyApp\ffmpeg
          copy ffmpeg_temp\ffmpeg-master-latest-win64-lgpl\bin\ffmpeg.exe dist\MyApp\ffmpeg\
          copy ffmpeg_temp\ffmpeg-master-latest-win64-lgpl\bin\ffprobe.exe dist\MyApp\ffmpeg\
        shell: cmd

      - name: Compile Inno Setup installer
        run: |
          iscc /DMyAppVersion=${{ steps.version.outputs.VERSION }} installer.iss
        shell: cmd

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.ref_name }}
          name: "Release ${{ github.ref_name }}"
          body: |
            ## MyApp ${{ steps.version.outputs.VERSION }}
            Download `MyApp-Setup-${{ steps.version.outputs.VERSION }}.exe` and run the installer.
          files: |
            Output/MyApp-Setup-*.exe
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**How to trigger this workflow:**

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

Key actions used: `actions/checkout@v4`, `actions/setup-python@v5`, `softprops/action-gh-release@v2`. Inno Setup is **pre-installed** on `windows-latest` runners, so `iscc` works directly without a special action.

- **softprops/action-gh-release docs**: [github.com/softprops/action-gh-release](https://github.com/softprops/action-gh-release)

---

## 5. Download button on a static website (GitHub Pages)

### Static permalink approach (simplest, recommended)

No JavaScript required. Use the `/releases/latest/download/` URL directly:

```html
<a href="https://github.com/OWNER/REPO/releases/latest/download/MyApp-Setup.exe"
   class="download-btn">
  ⬇ Download MyApp for Windows
</a>

<style>
.download-btn {
  display: inline-block;
  padding: 16px 32px;
  background-color: #2ea44f;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 18px;
  font-weight: 600;
}
.download-btn:hover { background-color: #2c974b; }
</style>
```

The user clicks, the browser performs a transparent 302 redirect, and the download starts. The user never sees the GitHub UI. **The asset filename must be consistent across releases** for this link to work — use a fixed name like `MyApp-Setup.exe` or parameterize only the version in the Inno Setup `OutputBaseFilename`.

### Dynamic button with version number and download count

Fetch the latest release info from the GitHub API to display the current version:

```html
<div id="download-section">
  <a id="download-btn" href="#" class="download-btn">
    ⬇ Download MyApp <span id="version">...</span>
  </a>
  <p id="download-info"></p>
</div>

<script>
(async function() {
  const OWNER = 'your-username';
  const REPO  = 'your-repo';
  const ASSET_PATTERN = /MyApp-Setup.*\.exe$/i;

  try {
    const res = await fetch(
      `https://api.github.com/repos/${OWNER}/${REPO}/releases/latest`
    );
    const release = await res.json();
    const asset = release.assets.find(a => ASSET_PATTERN.test(a.name));

    document.getElementById('download-btn').href = asset.browser_download_url;
    document.getElementById('version').textContent = release.tag_name;

    const sizeMB = (asset.size / 1048576).toFixed(1);
    const downloads = release.assets.reduce((s, a) => s + a.download_count, 0);
    document.getElementById('download-info').textContent =
      `${sizeMB} MB · ${downloads.toLocaleString()} downloads`;
  } catch (e) {
    // Fallback to static permalink
    document.getElementById('download-btn').href =
      `https://github.com/${OWNER}/${REPO}/releases/latest/download/MyApp-Setup.exe`;
    document.getElementById('version').textContent = '';
  }
})();
</script>
```

**Rate limit caveat**: Unauthenticated GitHub API requests are limited to **60 per hour per IP**. For a low-to-medium traffic site this is fine. For high traffic, cache the API response or stick with the static permalink approach and update the version number manually.

### Jekyll shortcut (if using GitHub Pages with Jekyll)

Jekyll-based GitHub Pages sites get free access to release data via `site.github`:

```liquid
{% assign release = site.github.latest_release %}
{% assign asset = release.assets | first %}

<a href="{{ asset.browser_download_url }}" class="download-btn">
  ⬇ Download MyApp {{ release.tag_name }}
</a>
```

No client-side API calls, no rate limits. Data refreshes when the site rebuilds.

### Shields.io badges for README and website

```markdown
[![Latest Release](https://img.shields.io/github/v/release/OWNER/REPO?label=Download)](https://github.com/OWNER/REPO/releases/latest/download/MyApp-Setup.exe)

[![Total Downloads](https://img.shields.io/github/downloads/OWNER/REPO/total)](https://github.com/OWNER/REPO/releases)
```

---

## 6. Alternative approaches worth considering

### Windows Package Manager (winget)

Publishing to winget lets users install your app with `winget install YourPublisher.MyApp`. The process is free and open: you fork the [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs) repository (9,000+ packages), add a YAML manifest pointing to your installer's download URL, and submit a pull request. Automated validation checks the SHA-256 hash and that the installer supports silent mode. Human moderators approve the PR, typically within hours to days.

For automation, the **WinGet Releaser** GitHub Action ([vedantmgoyal9/winget-releaser](https://github.com/vedantmgoyal9/winget-releaser)) can automatically submit new winget PRs when you publish a GitHub Release. This is a good secondary distribution channel. Accepted installer formats include EXE, MSI, and MSIX — a PyInstaller + Inno Setup `.exe` qualifies.

- **Docs**: [learn.microsoft.com/en-us/windows/package-manager](https://learn.microsoft.com/en-us/windows/package-manager/)

### Microsoft Store (surprisingly practical now)

As of September 2025, **individual developer registration is free** (previously $19). Company accounts remain $99 one-time. The Store accepts Win32 `.exe` and `.msi` installers directly, or you can wrap your PyInstaller output in an MSIX package for additional benefits: **zero antivirus false positives**, free code signing by Microsoft, free CDN hosting, and automatic updates handled by Windows.

A detailed guide for packaging a PyInstaller app as MSIX exists at [82phil.github.io/python/2025/04/24/msix_pyinstaller.html](https://82phil.github.io/python/2025/04/24/msix_pyinstaller.html). The process requires the Windows SDK for `makeappx.exe` and `signtool.exe`, plus an `AppxManifest.xml` describing your app.

**Verdict**: Worth pursuing as a secondary channel after your primary GitHub-based distribution is working. The "free code signing + no AV false positives" benefit alone makes MSIX valuable.

### Electron or Tauri wrapper — not recommended here

Tauri 2.0 can work with Python via a "sidecar" approach (bundling a PyInstaller binary alongside the Tauri app), but this adds **three languages** to your stack (Python + JavaScript + Rust), introduces IPC overhead for cross-process communication, and doesn't reduce bundle size since you're still shipping the Python runtime. The development effort to rewrite a 1,500-line customtkinter UI as a web frontend is substantial.

For a tool targeting HR professionals and journalists, the **additional complexity is not justified**. A polished Inno Setup installer achieves the same "professional app" impression that Electron/Tauri would provide, without the architectural overhead.

### Auto-updater solutions

| Solution | Status | Approach | Best for |
|---|---|---|---|
| **Custom GitHub API check** | ✅ DIY, ~50 lines | Query `/releases/latest`, compare versions, prompt user | Simple apps, MVP |
| **tufup** | ✅ Active, MIT license | TUF-signed metadata, binary delta patches | Production apps needing secure updates |
| **MSIX via Store** | ✅ Built into Windows | Automatic, silent updates | Store-distributed apps |
| **PyUpdater** | ❌ Archived since 2022 | — | Do not use |

The simplest auto-update approach is a background check against the GitHub API:

```python
import requests
from packaging import version

CURRENT_VERSION = "1.2.0"

def check_for_update():
    try:
        r = requests.get(
            "https://api.github.com/repos/OWNER/REPO/releases/latest",
            timeout=10
        )
        latest = r.json()["tag_name"].lstrip("v")
        if version.parse(latest) > version.parse(CURRENT_VERSION):
            download_url = next(
                a["browser_download_url"]
                for a in r.json()["assets"]
                if a["name"].endswith(".exe")
            )
            return {"update_available": True, "version": latest, "url": download_url}
    except Exception:
        pass
    return {"update_available": False}
```

Call this in a background thread at startup. If an update exists, show a notification in your customtkinter GUI with a button that downloads the new installer and launches it via `os.startfile()`.

For a more robust solution, **tufup** ([github.com/dennisvang/tufup](https://github.com/dennisvang/tufup)) implements TUF-signed secure updates with binary delta patches, reducing download sizes for minor updates.

---

## 7. Recommended end-to-end workflow

Here is the simplest, most practical pipeline from source code to one-click download:

### Step-by-step tool chain

```
your_app.py (Python 3.11 + customtkinter)
    │
    ▼  PyInstaller --onedir --collect-all customtkinter
    │
dist/MyApp/  (folder with MyApp.exe + dependencies)
    │
    ├── Copy ffmpeg.exe + ffprobe.exe into dist/MyApp/ffmpeg/
    │
    ▼  Inno Setup (iscc.exe installer.iss)
    │
MyApp-Setup-1.0.0.exe  (single installer, ~40-80 MB)
    │
    ▼  git tag v1.0.0 && git push origin v1.0.0
    │
GitHub Actions → builds + uploads to GitHub Release
    │
    ▼
GitHub Releases hosts the .exe permanently
    │
    ▼
GitHub Pages site with download button → /releases/latest/download/MyApp-Setup.exe
```

### Tool recommendations and one-time setup

| Step | Tool | Install | One-time setup effort |
|---|---|---|---|
| **Bundle to .exe** | PyInstaller 6.x | `pip install pyinstaller` | 30 min (write command + test) |
| **FFmpeg binaries** | BtbN LGPL static build | Download from GitHub | 15 min |
| **Windows installer** | Inno Setup 6.7 | [jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php) | 1–2 hr (write `.iss` script) |
| **CI/CD** | GitHub Actions | Built into GitHub | 1–2 hr (write workflow YAML) |
| **Hosting** | GitHub Releases | Built into GitHub | 15 min |
| **Download page** | GitHub Pages | Enable in repo settings | 30 min–1 hr |
| **Auto-update** | Custom GitHub API check | ~50 lines of Python | 30 min |

**Estimated total first-time setup: 4–8 hours.** Subsequent releases take under 1 minute — just `git tag v1.1.0 && git push origin v1.1.0` and the pipeline runs automatically.

### Local development build commands (quick reference)

```bash
# 1. Install tools
pip install pyinstaller customtkinter

# 2. Build the app
pyinstaller --noconfirm --onedir --windowed \
  --collect-all customtkinter \
  --add-data "assets;assets" \
  --name "MyApp" --icon=assets/icon.ico main.py

# 3. Copy FFmpeg into the output
mkdir dist\MyApp\ffmpeg
copy ffmpeg\ffmpeg.exe dist\MyApp\ffmpeg\
copy ffmpeg\ffprobe.exe dist\MyApp\ffmpeg\

# 4. Build the installer
iscc installer.iss

# 5. Test the installer
.\Output\MyApp-Setup-1.0.0.exe
```

### Future enhancements (in order of impact)

Once the basic pipeline is running, consider these improvements in roughly this priority order. First, **add code signing** (via a certificate from Certum at ~€69/yr for open-source, or free via Microsoft Store) to eliminate Windows SmartScreen warnings. Second, **submit to winget** for CLI-savvy power users — automatable with the WinGet Releaser GitHub Action. Third, **publish to the Microsoft Store** as an MSIX package for automatic updates and zero AV false positives (individual registration is now free). Fourth, **add delta updates** with tufup if your user base grows and you ship frequent updates.

---

## Conclusion

The Python desktop app distribution problem has a clean, proven solution in 2026. **PyInstaller + Inno Setup + GitHub Actions + GitHub Releases** forms a zero-cost, fully automated pipeline that produces professional installers indistinguishable from commercial software. PyInstaller's `--collect-all customtkinter` flag solves the framework's data-file bundling problem in one line. Inno Setup's modern wizard with dark mode support creates installers that look polished to non-technical users. GitHub Actions automates the entire build-to-release process with a single `git push`.

The biggest remaining friction point is **antivirus false positives** on unsigned PyInstaller executables. Code signing (paid) or Microsoft Store MSIX packaging (free) eliminates this. For a ~1,500-line app targeting HR professionals and journalists, resist the temptation to over-engineer with Electron/Tauri — the native Python toolchain handles this use case well, and the total pipeline setup takes a single afternoon.