# 🎤 DROP THE MIKE

**Split audio & video files for transcription — then analyze with AI.**

DROP THE MIKE is a desktop tool that splits long audio and video files into smaller MP3 parts, making them easy to upload to Google Gemini for transcription. After transcription, use the built-in Mike agent link to analyze and structure your transcripts.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## Features

- **Audio & Video Support** — Upload MP3, WAV, M4A, MP4, AVI, MKV, MOV, and more. Video files are automatically converted to audio.
- **Smart Splitting** — Split into 2-10+ equal parts with a single click.
- **Output Folder** — Creates a dedicated folder for each split, keeping your files organized.
- **Re-Split** — If Gemini says files are too long, re-split into more parts with one click (automatically deletes old files).
- **Quality Options** — Keep original quality or compress to save space.
- **Bilingual UI** — Switch between Hebrew and English with one click.
- **Mike Agent Integration** — Built-in link to the Mike AI agent for transcript analysis.
- **Modern Green Theme** — Clean, modern design inspired by the [Hebrew Markdown Export](https://dartaryan.github.io/hebrew-markdown-export/) tool.

---

## Prerequisites

1. **Python 3.10+** — Install from [Microsoft Store](https://apps.microsoft.com/detail/9PJPW5LDXLZ5) or [python.org](https://www.python.org/downloads/)
2. **FFmpeg** — Required for audio/video processing.

### Installing FFmpeg

**Option A — Download manually:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Extract `ffmpeg.exe` and `ffprobe.exe`
3. Place them in the same folder as `drop_the_mike.py`

**Option B — Install via package manager:**
```bash
# Windows (winget)
winget install Gyan.FFmpeg

# Windows (chocolatey)
choco install ffmpeg

# Windows (scoop)
scoop install ffmpeg
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/dartaryan/drop-the-mike.git
cd drop-the-mike

# Install Python dependencies
pip install -r requirements.txt
```

---

## Usage

### Quick Start (Windows)

Double-click **`drop_the_mike.bat`** — it will install dependencies automatically on first run.

### Manual Start

```bash
python drop_the_mike.py
```

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

## Project Structure

```
drop-the-mike/
├── drop_the_mike.py      # Main application
├── drop_the_mike.bat     # Windows launcher
├── requirements.txt      # Python dependencies
├── mike-agent.md         # Mike agent documentation
├── .gitignore
└── README.md
```

---

## Credits

Made with ❤️ by [Ben Akiva](https://github.com/dartaryan)

---

## License

MIT License — feel free to use, modify, and distribute.
