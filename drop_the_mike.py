"""
DROP THE MIKE - Audio & Video Splitter for Transcription
Design: Green theme inspired by Hebrew Markdown Export
Bilingual: Hebrew / English
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import subprocess
import json
import threading
import webbrowser
import shutil
import urllib.request
from typing import Optional, List, Callable


# ============================================================================
# CONSTANTS
# ============================================================================
APP_VERSION = "1.0.0"
GITHUB_OWNER = "dartaryan"
GITHUB_REPO = "drop-the-mike"
MIKE_AGENT_URL = "https://gemini.google.com/gem/124_L6lakUi2fZtfW7ETr38BB-RY2y3t8?usp=sharing"
GITHUB_URL = "https://github.com/dartaryan"

VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.flv', '.m4v'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma'}


# ============================================================================
# INTERNATIONALIZATION
# ============================================================================
STRINGS = {
    "app_title": {"en": "DROP THE MIKE", "he": "DROP THE MIKE"},
    "subtitle": {"en": "Split audio & video for transcription", "he": "פיצול אודיו ווידאו לתמלול"},
    "lang_toggle": {"en": "עברית", "he": "English"},

    # Instructions - Phase 1 (before split)
    "instructions_title": {"en": "HOW IT WORKS", "he": "איך זה עובד"},
    "instruction_step1": {
        "en": "1. Upload an audio or video file",
        "he": "1. העלה קובץ אודיו או וידאו"
    },
    "instruction_step2": {
        "en": "2. Choose number of parts (tip: smaller parts work better with Gemini)",
        "he": "2. בחר מספר חלקים (טיפ: חלקים קטנים יותר עובדים טוב יותר עם ג'ימיני)"
    },
    "instruction_step3": {
        "en": "3. Split and upload the parts to Gemini for transcription",
        "he": "3. פצל והעלה את החלקים ל-ג'ימיני לתמלול"
    },
    "instruction_step4": {
        "en": "4. Send the transcripts to Mike agent for analysis",
        "he": "4. שלח את התמלולים לסוכן מייק לניתוח"
    },
    "skip_to_mike": {
        "en": "Short recording? Skip straight to Mike \u2192",
        "he": "\u2190 הקלטה קצרה? אפשר לגשת ישירות למייק"
    },

    # Instructions - Phase 2 (after split)
    "post_split_title": {"en": "NEXT STEPS", "he": "מה עכשיו?"},
    "post_step1": {
        "en": "1. Upload the split audio files to Gemini for transcription",
        "he": "1. העלה את קבצי האודיו המפוצלים ל-ג'ימיני לתמלול"
    },
    "post_step2": {
        "en": "2. After transcription, open Mike agent and upload the text files",
        "he": "2. אחרי התמלול, פתח את סוכן מייק והעלה את קבצי הטקסט"
    },
    "post_tip1": {
        "en": "Tip: If Gemini says the file is too long, use the re-split button below",
        "he": "טיפ: אם ג'ימיני אומר שהקובץ ארוך מדי, השתמש בכפתור הפיצול מחדש למטה"
    },
    "post_tip2": {
        "en": "Tip: A Gemini paid account supports longer audio files",
        "he": "טיפ: חשבון ג'ימיני בתשלום תומך בקבצי אודיו ארוכים יותר"
    },

    # File selection
    "select_file": {"en": "SELECT FILE", "he": "בחירת קובץ"},
    "browse": {"en": "Browse Files", "he": "עיון בקבצים"},
    "browse_hint": {
        "en": "Click Browse to select an audio or video file",
        "he": "לחץ על עיון כדי לבחור קובץ אודיו או וידאו"
    },
    "file_loaded": {"en": "File loaded successfully", "he": "הקובץ נטען בהצלחה"},

    # Settings
    "settings": {"en": "SETTINGS", "he": "הגדרות"},
    "num_parts": {"en": "Number of Parts", "he": "מספר חלקים"},
    "quality": {"en": "Output Quality", "he": "איכות פלט"},
    "output_folder": {"en": "Output Folder", "he": "תיקיית פלט"},
    "same_as_input": {"en": "Same as input file", "he": "אותה תיקייה כמו קובץ המקור"},
    "change": {"en": "Change", "he": "שנה"},

    # Quality options
    "q_original": {"en": "Original (No re-encoding)", "he": "מקורי (ללא קידוד מחדש)"},
    "q_high": {"en": "High (320 kbps)", "he": "גבוה (320 kbps)"},
    "q_good": {"en": "Good (256 kbps)", "he": "טוב (256 kbps)"},
    "q_medium": {"en": "Medium (192 kbps)", "he": "בינוני (192 kbps)"},
    "q_compact": {"en": "Compact (128 kbps)", "he": "דחוס (128 kbps)"},
    "q_small": {"en": "Small (96 kbps)", "he": "קטן (96 kbps)"},

    # Preview
    "preview": {"en": "OUTPUT PREVIEW", "he": "תצוגה מקדימה"},
    "preview_hint": {"en": "Select a file to see output preview", "he": "בחר קובץ כדי לראות תצוגה מקדימה"},

    # Actions
    "split_file": {"en": "SPLIT FILE", "he": "פצל קובץ"},
    "processing": {"en": "Processing...", "he": "...מעבד"},
    "clear": {"en": "Clear", "he": "נקה"},
    "open_folder": {"en": "Open Output Folder", "he": "פתח תיקיית פלט"},

    # Re-split
    "resplit": {
        "en": "Files too long? Split into more parts",
        "he": "הקבצים ארוכים מדי? פצל ליותר חלקים"
    },

    # Mike agent
    "open_mike": {"en": "Open Mike Agent", "he": "פתח את הסוכן מייק"},
    "copy_link": {"en": "Copy Link", "he": "העתק קישור"},
    "link_copied": {"en": "Link copied to clipboard!", "he": "הקישור הועתק!"},

    # Progress
    "complete": {"en": "Complete!", "he": "!הושלם"},
    "processing_part": {
        "en": "Processing part {current} of {total}...",
        "he": "...{total} מתוך {current} מעבד חלק"
    },
    "split_success": {
        "en": "Successfully split into {n} parts!",
        "he": "!פוצל בהצלחה ל-{n} חלקים"
    },
    "files_saved_to": {
        "en": "Files saved to:",
        "he": ":הקבצים נשמרו ב"
    },
    "split_error": {
        "en": "Failed to split file:",
        "he": ":פיצול הקובץ נכשל"
    },
    "file_read_error": {
        "en": "Could not read file:",
        "he": ":לא ניתן לקרוא את הקובץ"
    },

    # Footer
    "made_with": {"en": "Made with", "he": "נוצר עם"},
    "by": {"en": "by Ben Akiva", "he": "על ידי Ben Akiva"},

    # Auto-update
    "update_available": {
        "en": "New version {version} is available!",
        "he": "!{version} גרסה חדשה זמינה"
    },
    "update_download": {"en": "Download Update", "he": "הורד עדכון"},
    "update_dismiss": {"en": "Dismiss", "he": "סגור"},
}


def t(key: str, lang: str, **kwargs) -> str:
    """Get translated string with proper RTL handling for Hebrew"""
    s = STRINGS.get(key, {}).get(lang, key)
    for k, v in kwargs.items():
        s = s.replace(f"{{{k}}}", str(v))
    # Prepend RTL mark for Hebrew so numbers and punctuation render correctly
    if lang == "he" and s and s != key:
        s = "\u200F" + s
    return s


# ============================================================================
# DESIGN SYSTEM - Light Green Theme (Hebrew Markdown Export inspired)
# ============================================================================
class Colors:
    """Light green theme color palette"""
    BG_BASE = "#FFFFFF"
    BG_SURFACE = "#F0FDF4"
    BG_ELEVATED = "#ecfdf5"
    BG_INPUT = "#FFFFFF"

    PRIMARY = "#10B981"
    PRIMARY_HOVER = "#059669"
    ACCENT = "#6EE7B7"
    ACCENT_HOVER = "#34D399"
    DARK_GREEN = "#064E3B"

    TEXT_PRIMARY = "#064E3B"
    TEXT_SECONDARY = "#047857"
    TEXT_MUTED = "#6B7280"
    TEXT_DISABLED = "#9CA3AF"

    BORDER = "#d1fae5"
    BORDER_FOCUS = "#10B981"

    SUCCESS = "#10B981"
    ERROR = "#ef4444"
    WARNING = "#b45309"

    # Button-specific
    BTN_SECONDARY_BG = "#F0FDF4"
    BTN_SECONDARY_HOVER = "#d1fae5"
    BTN_SECONDARY_TEXT = "#047857"


class Fonts:
    """Typography settings"""
    FAMILY_SANS = "Segoe UI"
    FAMILY_SERIF = "Georgia"

    HEADER_LARGE = (FAMILY_SANS, 26, "bold")
    HEADER_MEDIUM = (FAMILY_SANS, 18, "bold")
    HEADER_SMALL = (FAMILY_SANS, 13, "bold")
    BODY = (FAMILY_SANS, 11, "normal")
    BODY_SMALL = (FAMILY_SANS, 10, "normal")
    BUTTON = (FAMILY_SANS, 11, "bold")
    EMOJI = (FAMILY_SANS, 20, "normal")


# ============================================================================
# FFMPEG UTILITIES
# ============================================================================
def get_script_dir() -> str:
    """Get the directory where this script is located"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def _get_binary_path(name: str) -> str:
    """Get path to a bundled binary (ffmpeg or ffprobe), cross-platform."""
    exe = f'{name}.exe' if sys.platform == 'win32' else name
    script_dir = get_script_dir()
    locations = [
        os.path.join(script_dir, exe),
        os.path.join(script_dir, 'ffmpeg', exe),
    ]
    if hasattr(sys, '_MEIPASS'):
        locations.append(os.path.join(sys._MEIPASS, 'ffmpeg', exe))
    # Fallback: rely on system PATH
    locations.append(name)
    for path in locations:
        if path and (os.path.exists(path) or path == name):
            return path
    return name


def get_ffmpeg_path() -> str:
    """Get FFmpeg path - checks multiple locations (cross-platform)"""
    return _get_binary_path('ffmpeg')


def get_ffprobe_path() -> str:
    """Get FFprobe path - checks multiple locations (cross-platform)"""
    return _get_binary_path('ffprobe')


# ============================================================================
# AUTO-UPDATE CHECKER
# ============================================================================
def check_for_update() -> Optional[dict]:
    """Check GitHub Releases for a newer version. Returns update info or None."""
    try:
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        latest_tag = data.get("tag_name", "").lstrip("v")
        if not latest_tag:
            return None
        # Simple version comparison (works for semver like 1.0.0 < 1.1.0)
        current_parts = [int(x) for x in APP_VERSION.split(".")]
        latest_parts = [int(x) for x in latest_tag.split(".")]
        if latest_parts > current_parts:
            # Find the right download asset for this platform
            assets = data.get("assets", [])
            if sys.platform == "win32":
                pattern = ".exe"
            elif sys.platform == "darwin":
                pattern = ".dmg"
            else:
                pattern = ""
            download_url = ""
            for asset in assets:
                if pattern and asset["name"].endswith(pattern):
                    download_url = asset["browser_download_url"]
                    break
            if not download_url:
                download_url = data.get("html_url", "")
            return {
                "version": latest_tag,
                "download_url": download_url,
                "release_url": data.get("html_url", ""),
            }
    except Exception:
        pass
    return None


def is_video_file(file_path: str) -> bool:
    """Check if a file is a video based on extension"""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in VIDEO_EXTENSIONS


def get_audio_info(file_path: str) -> dict:
    """Get audio/video file information using FFprobe"""
    cmd = [
        get_ffprobe_path(),
        '-v', 'error',
        '-show_entries', 'format=duration,size,bit_rate',
        '-show_entries', 'stream=codec_name,sample_rate,channels,codec_type',
        '-of', 'json',
        file_path
    ]
    try:
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        result = subprocess.run(cmd, capture_output=True, text=True, check=True,
                                creationflags=creation_flags)
        data = json.loads(result.stdout)

        format_info = data.get('format', {})
        # Find the audio stream
        streams = data.get('streams', [{}])
        audio_stream = {}
        for s in streams:
            if s.get('codec_type') == 'audio':
                audio_stream = s
                break
        if not audio_stream and streams:
            audio_stream = streams[0]

        duration = float(format_info.get('duration', 0))
        size = int(format_info.get('size', 0))
        bitrate = int(format_info.get('bit_rate', 0)) // 1000 if format_info.get('bit_rate') else 0

        return {
            'duration': duration,
            'duration_str': format_duration(duration),
            'size': size,
            'size_str': format_size(size),
            'bitrate': bitrate,
            'codec': audio_stream.get('codec_name', 'unknown'),
            'sample_rate': audio_stream.get('sample_rate', 'unknown'),
            'channels': audio_stream.get('channels', 0),
            'is_video': is_video_file(file_path)
        }
    except Exception as e:
        return {'error': str(e)}


def format_duration(seconds: float) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_size(bytes_size: int) -> str:
    """Format file size in bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def split_audio(
    input_file: str,
    output_dir: str,
    num_parts: int,
    bitrate: int,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[str]:
    """Split audio/video file into equal MP3 parts"""
    info = get_audio_info(input_file)
    if 'error' in info:
        raise Exception(f"Failed to read file: {info['error']}")

    total_duration = info['duration']
    part_duration = total_duration / num_parts

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    is_video = is_video_file(input_file)

    output_files = []

    for i in range(num_parts):
        if progress_callback:
            progress_callback(i + 1, num_parts, f"Processing part {i + 1} of {num_parts}...")

        start_time = i * part_duration
        output_file = os.path.join(output_dir, f"{base_name}_part{i+1}.mp3")

        cmd = [
            get_ffmpeg_path(),
            '-i', input_file,
            '-ss', str(start_time),
        ]

        if i < num_parts - 1:
            cmd.extend(['-t', str(part_duration)])

        # Strip video if input is a video file
        if is_video:
            cmd.extend(['-vn'])

        input_ext = os.path.splitext(input_file)[1].lower()
        if bitrate > 0:
            cmd.extend(['-b:a', f'{bitrate}k'])
        elif is_video or input_ext != '.mp3':
            fallback = f"{info['bitrate']}k" if info.get('bitrate') else '192k'
            cmd.extend(['-b:a', fallback])
        else:
            cmd.extend(['-acodec', 'copy'])

        cmd.extend(['-y', output_file])

        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                creationflags=creation_flags
            )
            output_files.append(output_file)
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg error on part {i+1}: {e.stderr.decode() if e.stderr else str(e)}")

    if progress_callback:
        progress_callback(num_parts, num_parts, "Complete!")

    return output_files


# ============================================================================
# CUSTOM WIDGETS
# ============================================================================
class GreenButton(ctk.CTkButton):
    """Green primary button"""
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', Colors.PRIMARY)
        kwargs.setdefault('hover_color', Colors.PRIMARY_HOVER)
        kwargs.setdefault('text_color', "#ffffff")
        kwargs.setdefault('font', Fonts.BUTTON)
        kwargs.setdefault('corner_radius', 25)
        kwargs.setdefault('height', 40)
        kwargs.setdefault('border_width', 2)
        kwargs.setdefault('border_color', Colors.ACCENT)
        super().__init__(master, **kwargs)


class SecondaryButton(ctk.CTkButton):
    """Light secondary button"""
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', Colors.BTN_SECONDARY_BG)
        kwargs.setdefault('hover_color', Colors.BTN_SECONDARY_HOVER)
        kwargs.setdefault('text_color', Colors.BTN_SECONDARY_TEXT)
        kwargs.setdefault('font', Fonts.BUTTON)
        kwargs.setdefault('corner_radius', 25)
        kwargs.setdefault('height', 36)
        kwargs.setdefault('border_width', 1)
        kwargs.setdefault('border_color', Colors.BORDER)
        super().__init__(master, **kwargs)


class Card(ctk.CTkFrame):
    """Card container with surface background and green top accent"""
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', Colors.BG_SURFACE)
        kwargs.setdefault('corner_radius', 16)
        kwargs.setdefault('border_width', 1)
        kwargs.setdefault('border_color', Colors.BORDER)
        super().__init__(master, **kwargs)


# ============================================================================
# MAIN APPLICATION
# ============================================================================
class DropTheMikeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Language state
        self.lang = "he"

        # Configure window
        self.title("DROP THE MIKE")
        self.geometry("700x800")
        self.minsize(600, 650)
        self.configure(fg_color=Colors.BG_BASE)

        # Set appearance - LIGHT mode
        ctk.set_appearance_mode("light")

        # State
        self.selected_file: Optional[str] = None
        self.output_dir: Optional[str] = None
        self.file_info: dict = {}
        self.is_processing = False
        self._last_output_dir: Optional[str] = None
        self._last_output_files: List[str] = []
        self._last_split_parts: int = 3
        self._split_done = False

        # Widget registry for i18n updates: list of (widget, string_key, config_key)
        self._i18n_registry: List[tuple] = []
        # Labels that need RTL/LTR alignment updates
        self._directional_labels: List = []

        # Build UI
        self._create_ui()

        # Center window
        self._center_window()

        # Check for updates in background
        self._update_bar = None
        threading.Thread(target=self._check_update_background, daemon=True).start()

    def _center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    # ------------------------------------------------------------------
    # AUTO-UPDATE
    # ------------------------------------------------------------------
    def _check_update_background(self):
        """Run update check in background thread, then schedule UI update."""
        result = check_for_update()
        if result:
            self.after(0, lambda: self._show_update_bar(result))

    def _show_update_bar(self, info: dict):
        """Show a non-intrusive update notification bar at the top of the window."""
        if self._update_bar is not None:
            return
        bar = ctk.CTkFrame(self, fg_color="#065f46", corner_radius=0, height=40)
        bar.pack(fill="x", side="top", before=self.scroll_frame)
        bar.pack_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(expand=True)

        msg = t("update_available", self.lang, version=info["version"])
        label = ctk.CTkLabel(inner, text=msg, text_color="#a7f3d0",
                             font=(Fonts.FAMILY_SANS, 12, "bold"))
        label.pack(side="left", padx=(10, 8))

        dl_btn = ctk.CTkButton(
            inner, text=t("update_download", self.lang),
            fg_color="#10b981", hover_color="#059669", text_color="#ffffff",
            font=(Fonts.FAMILY_SANS, 11, "bold"), width=120, height=26,
            corner_radius=13,
            command=lambda: webbrowser.open(info["download_url"])
        )
        dl_btn.pack(side="left", padx=4)

        dismiss_btn = ctk.CTkButton(
            inner, text=t("update_dismiss", self.lang),
            fg_color="transparent", hover_color="#047857", text_color="#6ee7b7",
            font=(Fonts.FAMILY_SANS, 11), width=60, height=26,
            corner_radius=13,
            command=lambda: self._dismiss_update_bar()
        )
        dismiss_btn.pack(side="left", padx=4)

        self._update_bar = bar

    def _dismiss_update_bar(self):
        """Hide the update notification bar."""
        if self._update_bar:
            self._update_bar.destroy()
            self._update_bar = None

    def _register_i18n(self, widget, key: str, config_key: str = "text"):
        """Register a widget for language updates"""
        self._i18n_registry.append((widget, key, config_key))

    @property
    def _anchor(self) -> str:
        """Get text anchor based on language direction"""
        return "e" if self.lang == "he" else "w"

    @property
    def _justify(self) -> str:
        """Get text justify based on language direction"""
        return "right" if self.lang == "he" else "left"

    @property
    def _pack_side(self) -> str:
        """Get pack side for directional elements"""
        return "right" if self.lang == "he" else "left"

    @property
    def _pack_side_opp(self) -> str:
        """Get opposite pack side"""
        return "left" if self.lang == "he" else "right"

    def _refresh_ui(self):
        """Update all registered widgets with current language and alignment"""
        anchor = self._anchor
        justify = self._justify

        for widget, key, config_key in self._i18n_registry:
            try:
                widget.configure(**{config_key: t(key, self.lang)})
            except Exception:
                pass

        # Update alignment on all directional labels
        for widget in self._directional_labels:
            try:
                widget.configure(anchor=anchor, justify=justify)
            except Exception:
                pass

        # Update quality menu options
        quality_options = self._get_quality_options()
        self.quality_menu.configure(values=quality_options)
        self.quality_var.set(quality_options[0])

        # Re-pack directional labels with correct anchor
        for widget in self._directional_labels:
            try:
                pack_info = widget.pack_info()
                widget.pack_configure(anchor=anchor)
            except Exception:
                pass

        # Update preview
        self._update_preview()

        # Refresh instructions
        self._update_instructions()

    def _toggle_language(self):
        """Toggle between Hebrew and English"""
        self.lang = "en" if self.lang == "he" else "he"
        self._refresh_ui()

    def _get_quality_options(self) -> list:
        """Get quality options in current language"""
        keys = ["q_original", "q_high", "q_good", "q_medium", "q_compact", "q_small"]
        return [t(k, self.lang) for k in keys]

    def _create_ui(self):
        """Create all UI components"""
        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.BG_BASE,
            scrollbar_button_color=Colors.ACCENT,
            scrollbar_button_hover_color=Colors.PRIMARY
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        self._create_header()

        # Instructions Card (Phase 1)
        self._create_instructions_card()

        # File Selection Card
        self._create_file_card()

        # Settings Card
        self._create_settings_card()

        # Output Preview Card
        self._create_preview_card()

        # Action Buttons
        self._create_actions()

        # Progress Section
        self._create_progress()

        # Post-split section (hidden initially)
        self._create_post_split_section()

        # Footer
        self._create_footer()

    # ------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------
    def _create_header(self):
        """Create header with title, subtitle, and language toggle"""
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        # Top accent line
        accent_line = ctk.CTkFrame(header_frame, fg_color=Colors.PRIMARY, height=3, corner_radius=2)
        accent_line.pack(fill="x", pady=(0, 12))

        # Top row: title + lang toggle
        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.pack(fill="x")

        title = ctk.CTkLabel(
            top_row,
            text="🎤 DROP THE MIKE",
            font=Fonts.HEADER_LARGE,
            text_color=Colors.DARK_GREEN
        )
        title.pack(side="left", padx=(5, 0))

        # Language toggle button
        self.lang_btn = SecondaryButton(
            top_row,
            text=t("lang_toggle", self.lang),
            command=self._toggle_language,
            width=80,
            height=32,
            corner_radius=16,
            border_color=Colors.PRIMARY,
            text_color=Colors.PRIMARY
        )
        self.lang_btn.pack(side="right", padx=(0, 5))
        self._register_i18n(self.lang_btn, "lang_toggle")

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text=t("subtitle", self.lang),
            font=Fonts.BODY,
            text_color=Colors.TEXT_SECONDARY
        )
        self.subtitle_label.pack(pady=(5, 0))
        self._register_i18n(self.subtitle_label, "subtitle")
        self._directional_labels.append(self.subtitle_label)

        # Bottom accent line
        accent_line2 = ctk.CTkFrame(header_frame, fg_color=Colors.PRIMARY, height=3, corner_radius=2)
        accent_line2.pack(fill="x", pady=(12, 0))

    # ------------------------------------------------------------------
    # INSTRUCTIONS (Phase 1 - before split)
    # ------------------------------------------------------------------
    def _create_instructions_card(self):
        """Create initial instructions card"""
        self.instructions_card = Card(self.scroll_frame)
        self.instructions_card.pack(fill="x", pady=(0, 10))

        # Green top accent
        accent = ctk.CTkFrame(self.instructions_card, fg_color=Colors.PRIMARY, height=4, corner_radius=0)
        accent.pack(fill="x", side="top")

        inner = ctk.CTkFrame(self.instructions_card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        a = self._anchor
        j = self._justify

        self.lbl_instructions_title = ctk.CTkLabel(
            inner,
            text=t("instructions_title", self.lang),
            font=Fonts.HEADER_SMALL,
            text_color=Colors.PRIMARY,
            anchor=a, justify=j
        )
        self.lbl_instructions_title.pack(anchor=a, fill="x")
        self._register_i18n(self.lbl_instructions_title, "instructions_title")
        self._directional_labels.append(self.lbl_instructions_title)

        steps_frame = ctk.CTkFrame(inner, fg_color="transparent")
        steps_frame.pack(fill="x", pady=(8, 0))

        for key in ["instruction_step1", "instruction_step2", "instruction_step3", "instruction_step4"]:
            lbl = ctk.CTkLabel(steps_frame, text=t(key, self.lang),
                               font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, anchor=a, justify=j)
            lbl.pack(anchor=a, fill="x", pady=2)
            self._register_i18n(lbl, key)
            self._directional_labels.append(lbl)
            setattr(self, f"lbl_{key.split('_', 1)[1]}", lbl)

        separator = ctk.CTkFrame(inner, fg_color=Colors.BORDER, height=1)
        separator.pack(fill="x", pady=(12, 8))

        self.btn_skip_to_mike = ctk.CTkButton(
            inner,
            text=t("skip_to_mike", self.lang),
            font=(Fonts.FAMILY_SANS, 11, "bold"),
            fg_color="transparent",
            hover_color=Colors.BG_ELEVATED,
            text_color=Colors.PRIMARY,
            anchor=a,
            corner_radius=8,
            height=32,
            command=lambda: webbrowser.open(MIKE_AGENT_URL)
        )
        self.btn_skip_to_mike.pack(anchor=a, fill="x")
        self._register_i18n(self.btn_skip_to_mike, "skip_to_mike")
        self._directional_labels.append(self.btn_skip_to_mike)

    # ------------------------------------------------------------------
    # FILE SELECTION
    # ------------------------------------------------------------------
    def _create_file_card(self):
        """Create file selection card"""
        card = Card(self.scroll_frame)
        card.pack(fill="x", pady=(0, 10))

        accent = ctk.CTkFrame(card, fg_color=Colors.PRIMARY, height=4, corner_radius=0)
        accent.pack(fill="x", side="top")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        a = self._anchor

        self.lbl_select_file = ctk.CTkLabel(
            inner,
            text=t("select_file", self.lang),
            font=Fonts.HEADER_SMALL,
            text_color=Colors.PRIMARY,
            anchor=a
        )
        self.lbl_select_file.pack(anchor=a, fill="x")
        self._register_i18n(self.lbl_select_file, "select_file")
        self._directional_labels.append(self.lbl_select_file)

        # Drop zone
        self.drop_zone = ctk.CTkFrame(
            inner,
            fg_color=Colors.BG_ELEVATED,
            corner_radius=12,
            height=65,
            border_width=1,
            border_color=Colors.BORDER
        )
        self.drop_zone.pack(fill="x", pady=(10, 0))
        self.drop_zone.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(
            self.drop_zone,
            text=t("browse_hint", self.lang),
            font=Fonts.BODY,
            text_color=Colors.TEXT_DISABLED
        )
        self.drop_label.pack(expand=True)
        self._register_i18n(self.drop_label, "browse_hint")

        # Browse button
        self.btn_browse = GreenButton(
            inner,
            text=t("browse", self.lang),
            command=self._browse_file,
            width=130
        )
        self.btn_browse.pack(anchor="e", pady=(10, 0))
        self._register_i18n(self.btn_browse, "browse")

        # File info (hidden until file loaded)
        self.file_info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        self.file_info_frame.pack(fill="x", pady=(10, 0))

        self.file_name_label = ctk.CTkLabel(
            self.file_info_frame,
            text="",
            font=(Fonts.FAMILY_SANS, 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor=a
        )
        self.file_name_label.pack(anchor=a, fill="x")
        self._directional_labels.append(self.file_name_label)

        self.file_details_label = ctk.CTkLabel(
            self.file_info_frame,
            text="",
            font=Fonts.BODY_SMALL,
            text_color=Colors.TEXT_SECONDARY,
            anchor=a
        )
        self.file_details_label.pack(anchor=a, fill="x", pady=(2, 0))
        self._directional_labels.append(self.file_details_label)

        self.file_info_frame.pack_forget()

    # ------------------------------------------------------------------
    # SETTINGS
    # ------------------------------------------------------------------
    def _create_settings_card(self):
        """Create settings card"""
        card = Card(self.scroll_frame)
        card.pack(fill="x", pady=(0, 10))

        accent = ctk.CTkFrame(card, fg_color=Colors.PRIMARY, height=4, corner_radius=0)
        accent.pack(fill="x", side="top")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        a = self._anchor

        self.lbl_settings = ctk.CTkLabel(
            inner,
            text=t("settings", self.lang),
            font=Fonts.HEADER_SMALL,
            text_color=Colors.PRIMARY,
            anchor=a
        )
        self.lbl_settings.pack(anchor=a, fill="x")
        self._register_i18n(self.lbl_settings, "settings")
        self._directional_labels.append(self.lbl_settings)

        settings_frame = ctk.CTkFrame(inner, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(10, 0))

        # --- Number of parts ---
        parts_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        parts_frame.pack(fill="x", pady=(0, 12))

        parts_label_frame = ctk.CTkFrame(parts_frame, fg_color="transparent")
        parts_label_frame.pack(fill="x")

        self.lbl_num_parts = ctk.CTkLabel(
            parts_label_frame,
            text=t("num_parts", self.lang),
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY
        )
        self.lbl_num_parts.pack(side="left")
        self._register_i18n(self.lbl_num_parts, "num_parts")

        self.parts_value_label = ctk.CTkLabel(
            parts_label_frame,
            text="3",
            font=(Fonts.FAMILY_SANS, 14, "bold"),
            text_color=Colors.PRIMARY
        )
        self.parts_value_label.pack(side="right")

        self.parts_slider = ctk.CTkSlider(
            parts_frame,
            from_=2,
            to=10,
            number_of_steps=8,
            command=self._on_parts_change,
            fg_color=Colors.BORDER,
            progress_color=Colors.PRIMARY,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.DARK_GREEN,
            height=16
        )
        self.parts_slider.set(3)
        self.parts_slider.pack(fill="x", pady=(5, 0))

        # --- Quality ---
        quality_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        quality_frame.pack(fill="x", pady=(0, 12))

        self.lbl_quality = ctk.CTkLabel(
            quality_frame,
            text=t("quality", self.lang),
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY,
            anchor=a
        )
        self.lbl_quality.pack(anchor=a, fill="x")
        self._register_i18n(self.lbl_quality, "quality")
        self._directional_labels.append(self.lbl_quality)

        quality_options = self._get_quality_options()
        self.quality_var = ctk.StringVar(value=quality_options[0])

        self.quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            variable=self.quality_var,
            values=quality_options,
            fg_color=Colors.BG_ELEVATED,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.DARK_GREEN,
            dropdown_fg_color=Colors.BG_SURFACE,
            dropdown_hover_color=Colors.BG_ELEVATED,
            dropdown_text_color=Colors.TEXT_PRIMARY,
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY,
            width=250,
            height=32,
            corner_radius=8
        )
        self.quality_menu.pack(anchor=a, pady=(5, 0))

        # --- Output folder ---
        output_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        output_frame.pack(fill="x")

        self.lbl_output_folder = ctk.CTkLabel(
            output_frame,
            text=t("output_folder", self.lang),
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY,
            anchor=a
        )
        self.lbl_output_folder.pack(anchor=a, fill="x")
        self._register_i18n(self.lbl_output_folder, "output_folder")
        self._directional_labels.append(self.lbl_output_folder)

        output_select_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_select_frame.pack(fill="x", pady=(5, 0))

        self.output_path_label = ctk.CTkLabel(
            output_select_frame,
            text=t("same_as_input", self.lang),
            font=Fonts.BODY_SMALL,
            text_color=Colors.TEXT_DISABLED,
            anchor="w"
        )
        self.output_path_label.pack(side="left", fill="x", expand=True)
        self._register_i18n(self.output_path_label, "same_as_input")

        self.btn_change_output = SecondaryButton(
            output_select_frame,
            text=t("change", self.lang),
            command=self._browse_output,
            width=80,
            height=28
        )
        self.btn_change_output.pack(side="right")
        self._register_i18n(self.btn_change_output, "change")

    # ------------------------------------------------------------------
    # OUTPUT PREVIEW
    # ------------------------------------------------------------------
    def _create_preview_card(self):
        """Create output preview card"""
        card = Card(self.scroll_frame)
        card.pack(fill="x", pady=(0, 10))

        accent = ctk.CTkFrame(card, fg_color=Colors.PRIMARY, height=4, corner_radius=0)
        accent.pack(fill="x", side="top")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        a = self._anchor
        j = self._justify

        self.lbl_preview = ctk.CTkLabel(
            inner,
            text=t("preview", self.lang),
            font=Fonts.HEADER_SMALL,
            text_color=Colors.PRIMARY,
            anchor=a
        )
        self.lbl_preview.pack(anchor=a, fill="x")
        self._register_i18n(self.lbl_preview, "preview")
        self._directional_labels.append(self.lbl_preview)

        self.preview_content = ctk.CTkLabel(
            inner,
            text=t("preview_hint", self.lang),
            font=Fonts.BODY_SMALL,
            text_color=Colors.TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        self.preview_content.pack(anchor="w", fill="x", pady=(8, 0))

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------
    def _create_actions(self):
        """Create action buttons"""
        actions_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 10))

        # Split button (big primary button)
        self.split_btn = GreenButton(
            actions_frame,
            text=t("split_file", self.lang),
            command=self._start_split,
            state="disabled",
            height=48,
            font=(Fonts.FAMILY_SANS, 14, "bold"),
            corner_radius=25
        )
        self.split_btn.pack(fill="x")
        self._register_i18n(self.split_btn, "split_file")

        # Secondary actions row
        secondary_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        secondary_frame.pack(fill="x", pady=(8, 0))

        self.btn_clear = SecondaryButton(
            secondary_frame,
            text=t("clear", self.lang),
            command=self._clear_all,
            width=100
        )
        self.btn_clear.pack(side="left")
        self._register_i18n(self.btn_clear, "clear")

        self.btn_open_folder = SecondaryButton(
            secondary_frame,
            text=t("open_folder", self.lang),
            command=self._open_output_folder,
            width=160,
            state="disabled"
        )
        self.btn_open_folder.pack(side="right")
        self._register_i18n(self.btn_open_folder, "open_folder")

    # ------------------------------------------------------------------
    # PROGRESS
    # ------------------------------------------------------------------
    def _create_progress(self):
        """Create progress section (hidden until split starts)"""
        self.progress_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x")

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            fg_color=Colors.BORDER,
            progress_color=Colors.PRIMARY,
            height=8,
            corner_radius=4
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=Fonts.BODY_SMALL,
            text_color=Colors.TEXT_MUTED
        )
        self.progress_label.pack(anchor="w", pady=(5, 0))

        self.progress_frame.pack_forget()

    # ------------------------------------------------------------------
    # POST-SPLIT SECTION (hidden initially)
    # ------------------------------------------------------------------
    def _create_post_split_section(self):
        """Create the post-split instructions, re-split button, and Mike agent buttons"""
        self.post_split_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.post_split_frame.pack(fill="x", pady=(5, 0))

        a = self._anchor
        j = self._justify

        # --- Post-split instructions card ---
        self.post_card = Card(self.post_split_frame)
        self.post_card.pack(fill="x", pady=(0, 10))

        accent = ctk.CTkFrame(self.post_card, fg_color=Colors.PRIMARY, height=4, corner_radius=0)
        accent.pack(fill="x", side="top")

        inner = ctk.CTkFrame(self.post_card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        self.lbl_post_title = ctk.CTkLabel(
            inner,
            text=t("post_split_title", self.lang),
            font=Fonts.HEADER_SMALL,
            text_color=Colors.DARK_GREEN,
            anchor=a
        )
        self.lbl_post_title.pack(anchor=a, fill="x")
        self._register_i18n(self.lbl_post_title, "post_split_title")
        self._directional_labels.append(self.lbl_post_title)

        steps_frame = ctk.CTkFrame(inner, fg_color="transparent")
        steps_frame.pack(fill="x", pady=(8, 0))

        self.lbl_post_step1 = ctk.CTkLabel(steps_frame, text=t("post_step1", self.lang),
                                             font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, anchor=a, justify=j)
        self.lbl_post_step1.pack(anchor=a, fill="x", pady=2)
        self._register_i18n(self.lbl_post_step1, "post_step1")
        self._directional_labels.append(self.lbl_post_step1)

        self.lbl_post_step2 = ctk.CTkLabel(steps_frame, text=t("post_step2", self.lang),
                                             font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, anchor=a, justify=j)
        self.lbl_post_step2.pack(anchor=a, fill="x", pady=2)
        self._register_i18n(self.lbl_post_step2, "post_step2")
        self._directional_labels.append(self.lbl_post_step2)

        # Tips
        tips_frame = ctk.CTkFrame(inner, fg_color="#FFFBEB", corner_radius=10,
                                   border_width=1, border_color="#FDE68A")
        tips_frame.pack(fill="x", pady=(10, 0))

        tips_inner = ctk.CTkFrame(tips_frame, fg_color="transparent")
        tips_inner.pack(fill="x", padx=12, pady=10)

        self.lbl_post_tip1 = ctk.CTkLabel(tips_inner, text=t("post_tip1", self.lang),
                                            font=Fonts.BODY_SMALL, text_color=Colors.WARNING, anchor=a, justify=j)
        self.lbl_post_tip1.pack(anchor=a, fill="x", pady=1)
        self._register_i18n(self.lbl_post_tip1, "post_tip1")
        self._directional_labels.append(self.lbl_post_tip1)

        self.lbl_post_tip2 = ctk.CTkLabel(tips_inner, text=t("post_tip2", self.lang),
                                            font=Fonts.BODY_SMALL, text_color=Colors.WARNING, anchor=a, justify=j)
        self.lbl_post_tip2.pack(anchor=a, fill="x", pady=1)
        self._register_i18n(self.lbl_post_tip2, "post_tip2")
        self._directional_labels.append(self.lbl_post_tip2)

        # --- Mike agent buttons ---
        mike_frame = ctk.CTkFrame(inner, fg_color="transparent")
        mike_frame.pack(fill="x", pady=(12, 0))

        self.btn_open_mike = GreenButton(
            mike_frame,
            text=t("open_mike", self.lang),
            command=lambda: webbrowser.open(MIKE_AGENT_URL),
            width=180,
            height=40
        )
        self.btn_open_mike.pack(side="left", padx=(0, 8))
        self._register_i18n(self.btn_open_mike, "open_mike")

        self.btn_copy_link = SecondaryButton(
            mike_frame,
            text=t("copy_link", self.lang),
            command=self._copy_mike_link,
            width=130,
            height=40,
            border_color=Colors.PRIMARY,
            text_color=Colors.PRIMARY
        )
        self.btn_copy_link.pack(side="left")
        self._register_i18n(self.btn_copy_link, "copy_link")

        # --- Re-split button ---
        self.btn_resplit = SecondaryButton(
            self.post_split_frame,
            text=t("resplit", self.lang),
            command=self._resplit,
            height=38,
            border_color=Colors.WARNING,
            text_color=Colors.WARNING,
            hover_color="#FEF3C7"
        )
        self.btn_resplit.pack(fill="x", pady=(0, 5))
        self._register_i18n(self.btn_resplit, "resplit")

        # Hide the whole section initially
        self.post_split_frame.pack_forget()

    # ------------------------------------------------------------------
    # FOOTER
    # ------------------------------------------------------------------
    def _create_footer(self):
        """Create footer with credits"""
        self.footer_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.footer_frame.pack(fill="x", pady=(15, 5))

        # Separator line
        sep = ctk.CTkFrame(self.footer_frame, fg_color=Colors.BORDER, height=1)
        sep.pack(fill="x", pady=(0, 12))

        # Credits row
        credits_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        credits_frame.pack()

        heart_text = ctk.CTkLabel(
            credits_frame,
            text="Made with ❤️ by Ben Akiva",
            font=Fonts.BODY_SMALL,
            text_color=Colors.TEXT_MUTED
        )
        heart_text.pack(side="left", padx=(0, 8))

        # GitHub link button
        github_btn = ctk.CTkButton(
            credits_frame,
            text="GitHub",
            font=(Fonts.FAMILY_SANS, 10, "bold"),
            fg_color="transparent",
            hover_color=Colors.BG_ELEVATED,
            text_color=Colors.PRIMARY,
            width=60,
            height=24,
            corner_radius=12,
            command=lambda: webbrowser.open(GITHUB_URL)
        )
        github_btn.pack(side="left")

    # ------------------------------------------------------------------
    # INSTRUCTIONS UPDATE
    # ------------------------------------------------------------------
    def _update_instructions(self):
        """Show/hide instructions based on state"""
        if self._split_done:
            self.instructions_card.pack_forget()
            self.post_split_frame.pack(fill="x", pady=(5, 0))
            # Make sure footer is always at the bottom
            self.footer_frame.pack_forget()
            self.footer_frame.pack(fill="x", pady=(15, 5))
        else:
            self.post_split_frame.pack_forget()
            # Re-show instructions card if not already visible
            try:
                self.instructions_card.pack(fill="x", pady=(0, 10),
                                            after=self.scroll_frame.winfo_children()[0])  # after header
            except Exception:
                pass

    # ------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------
    def _browse_file(self):
        """Open file browser for audio/video files"""
        file_path = filedialog.askopenfilename(
            title="Select Audio or Video File",
            filetypes=[
                ("Media Files", "*.mp3 *.wav *.m4a *.ogg *.flac *.aac *.wma *.mp4 *.avi *.mkv *.mov *.webm *.wmv *.flv *.m4v"),
                ("Audio Files", "*.mp3 *.wav *.m4a *.ogg *.flac *.aac *.wma"),
                ("Video Files", "*.mp4 *.avi *.mkv *.mov *.webm *.wmv *.flv *.m4v"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path: str):
        """Load selected file"""
        self.selected_file = file_path
        self.file_info = get_audio_info(file_path)

        if 'error' in self.file_info:
            messagebox.showerror("Error", f"{t('file_read_error', self.lang)}\n{self.file_info['error']}")
            return

        self.file_name_label.configure(text=os.path.basename(file_path))
        file_type = "Video" if self.file_info.get('is_video') else "Audio"
        details = f"{file_type}  |  Duration: {self.file_info['duration_str']}  |  Size: {self.file_info['size_str']}"
        if self.file_info['bitrate']:
            details += f"  |  {self.file_info['bitrate']} kbps"
        self.file_details_label.configure(text=details)
        self.file_info_frame.pack(fill="x", pady=(10, 0))

        self.drop_label.configure(text=t("file_loaded", self.lang), text_color=Colors.PRIMARY)
        self.split_btn.configure(state="normal")
        self._update_preview()

        # Reset split state
        self._split_done = False
        self._update_instructions()

    def _browse_output(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir = folder
            display_path = folder if len(folder) < 40 else "..." + folder[-37:]
            self.output_path_label.configure(text=display_path, text_color=Colors.TEXT_PRIMARY)
            self._update_preview()

    def _on_parts_change(self, value):
        """Handle parts slider change"""
        parts = int(value)
        self.parts_value_label.configure(text=str(parts))
        self._update_preview()

    def _update_preview(self):
        """Update output preview"""
        if not self.selected_file:
            self.preview_content.configure(text=t("preview_hint", self.lang))
            return

        num_parts = int(self.parts_slider.get())
        base_name = os.path.splitext(os.path.basename(self.selected_file))[0]

        if 'duration' in self.file_info:
            part_duration = self.file_info['duration'] / num_parts
            part_duration_str = format_duration(part_duration)
        else:
            part_duration_str = "??:??"

        preview_lines = [f"📁 {base_name}_split/"]
        for i in range(min(num_parts, 4)):
            preview_lines.append(f"    🎵 {base_name}_part{i+1}.mp3  ({part_duration_str})")
        if num_parts > 4:
            preview_lines.append(f"    ... +{num_parts - 4} more files")

        self.preview_content.configure(text="\n".join(preview_lines))

    def _get_bitrate(self) -> int:
        """Get selected bitrate from quality option"""
        quality = self.quality_var.get()
        # Match by the bitrate number in the string
        if "320" in quality:
            return 320
        elif "256" in quality:
            return 256
        elif "192" in quality:
            return 192
        elif "128" in quality:
            return 128
        elif "96" in quality:
            return 96
        return 0  # Original

    def _start_split(self):
        """Start the split operation"""
        if not self.selected_file or self.is_processing:
            return

        self.is_processing = True
        self.split_btn.configure(state="disabled", text=t("processing", self.lang))
        self.progress_frame.pack(fill="x")
        self.progress_bar.set(0)
        self.progress_label.configure(text="")

        thread = threading.Thread(target=self._do_split, daemon=True)
        thread.start()

    def _do_split(self):
        """Perform the split operation in a background thread"""
        try:
            num_parts = int(self.parts_slider.get())
            self._last_split_parts = num_parts
            bitrate = self._get_bitrate()
            base_dir = self.output_dir or os.path.dirname(self.selected_file)

            # Create a dedicated subfolder
            base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
            output_dir = os.path.join(base_dir, f"{base_name}_split")

            def progress_callback(current, total, message):
                progress = current / total
                self.after(0, lambda: self._update_progress(progress, message))

            output_files = split_audio(
                self.selected_file,
                output_dir,
                num_parts,
                bitrate,
                progress_callback
            )

            self.after(0, lambda: self._split_complete(output_files, output_dir))

        except Exception as e:
            self.after(0, lambda: self._split_error(str(e)))

    def _update_progress(self, progress: float, message: str):
        """Update progress bar"""
        self.progress_bar.set(progress)
        self.progress_label.configure(text=message)

    def _split_complete(self, output_files: List[str], output_dir: str):
        """Handle split completion"""
        self.is_processing = False
        self.split_btn.configure(state="normal", text=t("split_file", self.lang))
        self.progress_bar.set(1)
        self.progress_label.configure(
            text=f"{t('complete', self.lang)} {len(output_files)} files created."
        )

        self._last_output_dir = output_dir
        self._last_output_files = output_files
        self.btn_open_folder.configure(state="normal")

        # Show post-split instructions
        self._split_done = True
        self._update_instructions()

        messagebox.showinfo(
            "DROP THE MIKE",
            f"{t('split_success', self.lang, n=len(output_files))}\n\n"
            f"{t('files_saved_to', self.lang)}\n{output_dir}"
        )

    def _split_error(self, error_message: str):
        """Handle split error"""
        self.is_processing = False
        self.split_btn.configure(state="normal", text=t("split_file", self.lang))
        self.progress_frame.pack_forget()

        messagebox.showerror(
            "Error",
            f"{t('split_error', self.lang)}\n\n{error_message}"
        )

    def _resplit(self):
        """Re-split with one more part"""
        if not self.selected_file or self.is_processing:
            return

        # Increase parts count
        new_parts = self._last_split_parts + 1
        if new_parts > 20:
            new_parts = 20  # reasonable max

        # Update slider (max is 10 on slider, but we allow higher for re-split)
        if new_parts <= 10:
            self.parts_slider.set(new_parts)
            self.parts_value_label.configure(text=str(new_parts))

        self._last_split_parts = new_parts
        self.parts_value_label.configure(text=str(new_parts))

        # Delete old split files
        if self._last_output_dir and os.path.exists(self._last_output_dir):
            for f in self._last_output_files:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except Exception:
                    pass

        # Hide post-split section during processing
        self._split_done = False
        self._update_instructions()

        # Start split with new part count
        self.is_processing = True
        self.split_btn.configure(state="disabled", text=t("processing", self.lang))
        self.progress_frame.pack(fill="x")
        self.progress_bar.set(0)
        self.progress_label.configure(text="")

        thread = threading.Thread(target=self._do_resplit, daemon=True)
        thread.start()

    def _do_resplit(self):
        """Perform re-split in background thread"""
        try:
            num_parts = self._last_split_parts
            bitrate = self._get_bitrate()
            base_dir = self.output_dir or os.path.dirname(self.selected_file)
            base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
            output_dir = os.path.join(base_dir, f"{base_name}_split")

            def progress_callback(current, total, message):
                progress = current / total
                self.after(0, lambda: self._update_progress(progress, message))

            output_files = split_audio(
                self.selected_file,
                output_dir,
                num_parts,
                bitrate,
                progress_callback
            )

            self.after(0, lambda: self._split_complete(output_files, output_dir))

        except Exception as e:
            self.after(0, lambda: self._split_error(str(e)))

    def _copy_mike_link(self):
        """Copy Mike agent URL to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(MIKE_AGENT_URL)
        # Brief feedback
        original_text = self.btn_copy_link.cget("text")
        self.btn_copy_link.configure(text=t("link_copied", self.lang))
        self.after(2000, lambda: self.btn_copy_link.configure(text=t("copy_link", self.lang)))

    def _clear_all(self):
        """Clear all selections and reset state"""
        self.selected_file = None
        self.output_dir = None
        self.file_info = {}
        self._split_done = False
        self._last_output_files = []
        self._last_output_dir = None
        self._last_split_parts = 3

        self.drop_label.configure(text=t("browse_hint", self.lang), text_color=Colors.TEXT_DISABLED)
        self.file_info_frame.pack_forget()
        self.file_name_label.configure(text="")
        self.file_details_label.configure(text="")
        self.output_path_label.configure(text=t("same_as_input", self.lang), text_color=Colors.TEXT_DISABLED)
        self.preview_content.configure(text=t("preview_hint", self.lang))
        self.split_btn.configure(state="disabled", text=t("split_file", self.lang))
        self.btn_open_folder.configure(state="disabled")
        self.progress_frame.pack_forget()
        self.progress_bar.set(0)
        self.progress_label.configure(text="")
        self.parts_slider.set(3)
        self.parts_value_label.configure(text="3")
        quality_options = self._get_quality_options()
        self.quality_var.set(quality_options[0])

        self._update_instructions()

    def _open_output_folder(self):
        """Open the output folder in file explorer"""
        if self._last_output_dir and os.path.exists(self._last_output_dir):
            if sys.platform == 'win32':
                os.startfile(self._last_output_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', self._last_output_dir])
            else:
                subprocess.run(['xdg-open', self._last_output_dir])


# ============================================================================
# ENTRY POINT
# ============================================================================
def main():
    app = DropTheMikeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
