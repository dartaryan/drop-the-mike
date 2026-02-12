# 🎤 DROP THE MIKE

**Split audio & video files for transcription — then analyze with AI.**

DROP THE MIKE is a desktop tool that splits long audio and video files into smaller MP3 parts, making them easy to upload to Google Gemini for transcription. After transcription, use the built-in Mike agent link to analyze and structure your transcripts.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)
[![Latest Release](https://img.shields.io/github/v/release/dartaryan/drop-the-mike?label=Download)](https://github.com/dartaryan/drop-the-mike/releases/latest)
[![Total Downloads](https://img.shields.io/github/downloads/dartaryan/drop-the-mike/total)](https://github.com/dartaryan/drop-the-mike/releases)

---

## Download & Install (Recommended)

**No technical knowledge required.** Everything is bundled — just download and run:

| Platform | Download |
|----------|----------|
| **Windows** | [**DropTheMike-Setup.exe**](https://github.com/dartaryan/drop-the-mike/releases/latest/download/DropTheMike-Setup.exe) |
| **macOS** | [**DropTheMike.dmg**](https://github.com/dartaryan/drop-the-mike/releases/latest/download/DropTheMike.dmg) |

The installer includes everything (Python runtime, FFmpeg, all dependencies). No separate installations needed.

> **Windows note:** If you see "Windows protected your PC" — click "More info" then "Run anyway". This is normal for unsigned software.

---

## Features

- **Audio & Video Support** — Upload MP3, WAV, M4A, MP4, AVI, MKV, MOV, and more. Video files are automatically converted to audio.
- **Smart Splitting** — Split into 2-10+ equal parts with a single click.
- **Output Folder** — Creates a dedicated folder for each split, keeping your files organized.
- **Re-Split** — If Gemini says files are too long, re-split into more parts with one click (automatically deletes old files).
- **Quality Options** — Keep original quality or compress to save space.
- **Bilingual UI** — Switch between Hebrew and English with one click.
- **Mike Agent Integration** — Built-in link to the Mike AI agent for transcript analysis.
- **Auto-Update** — The app checks for new versions automatically and notifies you.
- **Modern Green Theme** — Clean, modern design inspired by the [Hebrew Markdown Export](https://dartaryan.github.io/hebrew-markdown-export/) tool.

---

## Usage

### Workflow

1. **Open the app** and select an audio or video file
2. **Choose the number of parts** (smaller parts work better with Gemini)
3. **Click "Split File"** — files are saved in a `{filename}_split` folder
4. **Upload the parts to [Google Gemini](https://gemini.google.com/)** for transcription
5. **If files are too long**, click "Files too long? Split into more parts" to re-split
6. **After transcription**, click "Open Mike Agent" to analyze your transcripts with AI

### Mike Agent

Mike is an AI transcript intelligence agent that turns raw conversation transcripts into clean, structured documents. After transcribing your audio with Gemini:

1. Click **"Open Mike Agent"** in the app (or copy the link)
2. Upload your transcribed text files to Mike
3. Mike will analyze, structure, and extract insights from your conversations

> **Tip:** A paid Gemini account supports longer audio files. If using a free account, split into smaller parts.

---

## Manual Installation (Advanced)

If you prefer to run from source instead of using the installer:

### Prerequisites

1. **Python 3.10+** — Install from [Microsoft Store](https://apps.microsoft.com/detail/9PJPW5LDXLZ5) or [python.org](https://www.python.org/downloads/)
2. **FFmpeg** — Install via `winget install Gyan.FFmpeg` or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)

### Setup

```bash
# Clone the repository
git clone https://github.com/dartaryan/drop-the-mike.git
cd drop-the-mike

# Install Python dependencies
pip install -r requirements.txt
```

### Run

**Windows:** Double-click `drop_the_mike.bat`

**Manual:** `python drop_the_mike.py`

---

## Project Structure

```
drop-the-mike/
├── drop_the_mike.py        # Main application
├── drop_the_mike.bat       # Windows launcher (for manual install)
├── drop_the_mike.spec      # PyInstaller build spec
├── installer.iss           # Inno Setup installer script (Windows)
├── requirements.txt        # Python dependencies
├── mike-agent.md           # Mike agent documentation
├── index.html              # Website / instructions page
├── android-chrome-512x512.png  # App icon source
├── .github/workflows/      # CI/CD pipeline
│   └── build-and-release.yml
├── .gitignore
└── README.md
```

---

## Building from Source

To build the installers yourself:

```bash
# Install build tools
pip install pyinstaller pillow

# Build with PyInstaller
pyinstaller drop_the_mike.spec

# (Windows) Build installer with Inno Setup
iscc installer.iss
```

---

## Releasing a New Version

1. Update `APP_VERSION` in `drop_the_mike.py`
2. Commit and push changes
3. Create and push a version tag:
   ```bash
   git tag v1.1.0
   git push origin main --tags
   ```
4. GitHub Actions automatically builds Windows + macOS installers and creates a release

---

## Credits

Made with ❤️ by [Ben Akiva](https://github.com/dartaryan)

---

## License

MIT License — feel free to use, modify, and distribute.

FFmpeg is bundled under the LGPL license. See [ffmpeg.org/legal.html](https://www.ffmpeg.org/legal.html) for details.
