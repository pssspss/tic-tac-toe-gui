"""Main Tkinter GUI interface module for Tic-Tac-Toe.

This module provides the desktop application entry and screen navigation.
Startup must always be guarded by main() and if __name__ == "__main__": main().
Importing this module must not launch Tk or create windows.
"""

import math
import os
import random
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# TODO(BACKEND): integrate GameEngine here
# TODO(BACKEND): request move from HeuristicAgent / QLearningAgent here
# TODO(BACKEND): load q_table.pkl when entering Q-learning mode

# ---------------------------------------------------------------------------
# Screen name constants
# ---------------------------------------------------------------------------
SPLASH = "splash"
MAIN_WINDOW = "main_window"
MAIN_MENU = "main_menu"
PLAY_GAME = "play_game"
SINGLE_PLAYER = "single_player"
AI_VS_AI = "ai_vs_ai"
SETTINGS = "settings"
COMING_SOON = "coming_soon"
GAME = "game"

# ---------------------------------------------------------------------------
# Design System Tokens (Notion doc: 2) Design System & Styling Tokens)
# ---------------------------------------------------------------------------
COLOR_CHALK = "#E8E8E8"
COLOR_CHALK_DIM = "#BFBFBF"
COLOR_TEXT_MUTED = "#9A9A9A"
COLOR_ACCENT = "#D4B07A"
COLOR_ACCENT_DIM = "#A98A5E"
COLOR_DANGER = "#D9534F"
COLOR_OVERLAY_BG = "#000000"

COLOR_BTN_BG = "#2B1A11"
COLOR_BTN_HOVER_BG = "#4E3322"
COLOR_BTN_FG = "#E8E8E8"
COLOR_BTN_HOVER_FG = "#D4B07A"
COLOR_FRAME_BG = "#1E120B"

FONT_TITLE = ("Helvetica", 30, "bold")
FONT_SUBTITLE = ("Helvetica", 13)
FONT_MENU_BTN = ("Helvetica", 17, "bold")
FONT_BODY = ("Helvetica", 14)
FONT_SMALL = ("Helvetica", 12)

# Placeholder messages (Phase 4 specs)
MSG_SETTINGS = "Currently in development phase."
MSG_COMING_SOON = "This feature will be implemented later."

# ---------------------------------------------------------------------------
# Game Modes and Data Schema (Notion doc: 4) In-Memory Data Schema Specifications)
# ---------------------------------------------------------------------------
MODE_HUMAN_VS_HUMAN = "human_vs_human"
MODE_HUMAN_VS_HEURISTIC = "human_vs_heuristic"
MODE_HUMAN_VS_QLEARNING = "human_vs_qlearning"
MODE_AI_VS_AI = "ai_vs_ai"

PLAYER_HUMAN = "human"
PLAYER_HEURISTIC_AI = "heuristic_ai"
PLAYER_QLEARNING_AI = "qlearning_ai"


class PlayerInfo:
    """In-memory player information matching Schema spec."""

    def __init__(self, label: str, player_type: str) -> None:
        self.label = label
        self.type = player_type
        self.symbol: str | None = None
        self.is_starter: bool = False

# ---------------------------------------------------------------------------
# Central Layout Computation
# ---------------------------------------------------------------------------
def compute_layout(width: int, height: int) -> dict:
    """Compute responsive screen geometry for menu columns, buttons, and boards.

    Returns a dict with:
        left_col_x0: Start x coordinate of the left panel column
        left_col_width: Total width allocated for the left column
        menu_width: Width of the button stack
        menu_x: Centered x coordinate for menu buttons inside the left column:
                menu_x = left_col_x0 + (left_col_width - menu_width) * 0.5
        menu_y: Top y offset for the button stack
        title_y: Top y coordinate for screen titles
        subtitle_y: Top y coordinate for screen subtitles
        ambient_size, ambient_cx, ambient_cy: Geometry for menu ambient board
        game_size, game_cx, game_cy: Geometry for centered gameplay board
    """
    w = max(320, width)
    h = max(240, height)

    # Title & Subtitle coordinates
    title_y = max(28, int(h * 0.04))
    subtitle_y = title_y + 42

    # Left column bounds (FC-style menu panel)
    left_col_x0 = max(28, int(w * 0.05))
    left_col_width = min(480, max(300, int(w * 0.35)))

    # Menu button stack: centered within left column
    menu_width = min(420, max(280, int(left_col_width * 0.90)))
    menu_x = int(left_col_x0 + (left_col_width - menu_width) * 0.5)
    menu_y = max(110, int(h * 0.20))

    # Ambient board placed in remaining right area
    right_area_x0 = left_col_x0 + left_col_width
    right_area_w = max(100, w - right_area_x0)
    ambient_size = min(420, max(200, int(min(right_area_w * 0.72, h * 0.54))))
    ambient_cx = right_area_x0 + right_area_w // 2
    ambient_cy = max(180, int(h * 0.52))

    # Gameplay board: truly centered on screen
    game_size = min(480, max(260, int(min(w * 0.52, h * 0.52))))
    game_cx = w // 2
    game_cy = max(180, int(h * 0.54))

    return {
        "left_col_x0": left_col_x0,
        "left_col_width": left_col_width,
        "menu_width": menu_width,
        "menu_x": menu_x,
        "menu_y": menu_y,
        "title_y": title_y,
        "subtitle_y": subtitle_y,
        "ambient_size": ambient_size,
        "ambient_cx": ambient_cx,
        "ambient_cy": ambient_cy,
        "game_size": game_size,
        "game_cx": game_cx,
        "game_cy": game_cy,
    }


# ---------------------------------------------------------------------------
# Asset paths (relative to this file, with PyInstaller standalone support)
# ---------------------------------------------------------------------------
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _ASSETS_DIR = os.path.join(sys._MEIPASS, "gui", "assets")
else:
    _ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

_SPLASH_BG_PATH = os.path.join(
    _ASSETS_DIR, "Splash background",
    "Generated Image September 12, 2026 - 10_50PM.jpg",
)
_MENU_BG_PATH = os.path.join(
    _ASSETS_DIR, "Menu background",
    "27707-background-1072764_1920.jpg",
)
_GAME_BG_PATH = os.path.join(
    _ASSETS_DIR, "Gameplay background",
    "Generated Image September 13, 2026 - 10_06PM.jpg",
)


# ---------------------------------------------------------------------------
# Asset manager
# ---------------------------------------------------------------------------
class AssetManager:
    """Loads and holds references to all GUI image assets.

    Images are loaded in discrete steps so the splash screen can show
    real progress. Each step is a callable that loads one asset.
    """

    def __init__(self) -> None:
        # Loaded PhotoImage references (populated by load steps)
        self.splash_bg: ImageTk.PhotoImage | None = None
        self.menu_bg: ImageTk.PhotoImage | None = None
        self.game_bg: ImageTk.PhotoImage | None = None

        # Ordered list of (label, load_function) pairs
        self._steps: list[tuple[str, callable]] = [
            ("Loading splash background…", self._load_splash_bg),
            ("Loading menu background…", self._load_menu_bg),
            ("Loading gameplay background…", self._load_game_bg),
        ]

    @property
    def total_steps(self) -> int:
        """Total number of asset-loading steps."""
        return len(self._steps)

    def get_step(self, index: int) -> tuple[str, callable]:
        """Return (label, load_fn) for the given step index."""
        return self._steps[index]

    # -- individual load functions ------------------------------------------

    def _load_image(self, path: str, size: tuple[int, int]) -> ImageTk.PhotoImage:
        """Load a JPEG from *path* and resize to *size*."""
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _load_splash_bg(self, width: int, height: int) -> None:
        self.splash_bg = self._load_image(_SPLASH_BG_PATH, (width, height))

    def _load_menu_bg(self, width: int, height: int) -> None:
        self.menu_bg = self._load_image(_MENU_BG_PATH, (width, height))

    def _load_game_bg(self, width: int, height: int) -> None:
        self.game_bg = self._load_image(_GAME_BG_PATH, (width, height))


# ---------------------------------------------------------------------------
# App controller
# ---------------------------------------------------------------------------
class App(tk.Tk):
    """Root Tkinter window and screen manager."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Tic-Tac-Toe")

        # Fullscreen-first window
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        # Asset manager (shared across screens)
        self.assets = AssetManager()

        # Track currently displayed screen
        self._current_screen_name: str | None = None

        # Container frame that holds all screens
        self._container = tk.Frame(self)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        # Registry of screen name -> Frame instance
        self._screens: dict[str, tk.Frame] = {}

        # Build all screens and stack them in the container
        screen_classes = {
            SPLASH: SplashScreen,
            MAIN_WINDOW: MainWindowScreen,
            MAIN_MENU: MainMenuScreen,
            PLAY_GAME: PlayGameScreen,
            SINGLE_PLAYER: SinglePlayerScreen,
            AI_VS_AI: AIVsAIScreen,
            SETTINGS: SettingsScreen,
            COMING_SOON: ComingSoonScreen,
            GAME: GameScreen,
        }
        for name, cls in screen_classes.items():
            frame = cls(parent=self._container, app=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self._screens[name] = frame

        # Dual-curtain transition panels for smooth horizontal wipes
        self._curtain_left = tk.Frame(self, bg="#0F0906")
        self._curtain_right = tk.Frame(self, bg="#0F0906")
        self._transitioning = False

        # Start on the splash screen
        self.show_screen(SPLASH)

    def transition_to(self, name: str, **kwargs) -> None:
        """Smoothly transition to the named screen with an animated dual-curtain wipe.

        Two rich dark panels smoothly close in from the edges over ~100ms,
        the target screen is swapped cleanly at midpoint, and the curtains
        part smoothly back to the edges over ~100ms (total ~200ms).
        """
        if self._transitioning:
            self.show_screen(name, **kwargs)
            return

        self._transitioning = True
        steps = 6
        step_interval = 16

        def _close(step: int = 1) -> None:
            frac = step / steps
            self._curtain_left.place(relx=0, rely=0, relwidth=frac * 0.5, relheight=1)
            self._curtain_right.place(relx=1.0 - frac * 0.5, rely=0, relwidth=frac * 0.5, relheight=1)
            self._curtain_left.lift()
            self._curtain_right.lift()
            if step < steps:
                self.after(step_interval, lambda: _close(step + 1))
            else:
                self.after(20, _swap_and_open)

        def _swap_and_open() -> None:
            try:
                self.show_screen(name, **kwargs)
                self._curtain_left.lift()
                self._curtain_right.lift()
                self.after(20, lambda: _open(steps))
            except Exception:
                self._curtain_left.place_forget()
                self._curtain_right.place_forget()
                self._transitioning = False
                raise

        def _open(step: int) -> None:
            frac = step / steps
            self._curtain_left.place(relx=0, rely=0, relwidth=frac * 0.5, relheight=1)
            self._curtain_right.place(relx=1.0 - frac * 0.5, rely=0, relwidth=frac * 0.5, relheight=1)
            if step > 0:
                self.after(step_interval, lambda: _open(step - 1))
            else:
                self._curtain_left.place_forget()
                self._curtain_right.place_forget()
                self._transitioning = False

        _close(1)

    def show_screen(self, name: str, **kwargs) -> None:
        """Raise the named screen to the top.

        Args:
            name: One of the screen name constants.
            **kwargs: Optional data passed to the screen's on_show method.
        """
        # Notify previous screen it is being hidden (e.g. to pause animations)
        if self._current_screen_name and self._current_screen_name in self._screens:
            prev_frame = self._screens[self._current_screen_name]
            if hasattr(prev_frame, "on_hide"):
                prev_frame.on_hide()

        self._current_screen_name = name
        frame = self._screens[name]
        if hasattr(frame, "on_show"):
            frame.on_show(**kwargs)
        frame.tkraise()


# ---------------------------------------------------------------------------
# Base screen
# ---------------------------------------------------------------------------
class BaseScreen(tk.Frame):
    """Common base for all screens."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent)
        self.app = app

    def on_show(self, **kwargs) -> None:
        """Hook called when the screen is raised to top."""
        pass

    def on_hide(self) -> None:
        """Hook called when navigating away from this screen."""
        pass


# ---------------------------------------------------------------------------
# Splash screen (Phase 2: real asset loading with progress)
# ---------------------------------------------------------------------------
class SplashScreen(BaseScreen):
    """Splash / loading screen with progress bar tied to real asset loading."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app)
        self.configure(bg="#000000")

        # Canvas fills the entire screen for the background image
        self._canvas = tk.Canvas(self, highlightthickness=0, bg="#000000")
        self._canvas.pack(fill="both", expand=True)

        # Background image id (set after loading splash bg)
        self._bg_image_id: int | None = None

        # Title text
        self._canvas.create_text(
            0, 0, text="Tic-Tac-Toe", anchor="n",
            font=("Helvetica", 48, "bold"), fill=COLOR_CHALK,
            tags="title",
        )

        # Progress bar (ttk style on a canvas window)
        self._progress_var = tk.DoubleVar(value=0.0)
        self._progress_bar = ttk.Progressbar(
            self._canvas, variable=self._progress_var,
            maximum=100, length=400, mode="determinate",
        )
        self._progress_window = self._canvas.create_window(
            0, 0, window=self._progress_bar, anchor="s", tags="progress",
        )

        # Percent label
        self._percent_label_id = self._canvas.create_text(
            0, 0, text="0%", anchor="n",
            font=("Helvetica", 14), fill=COLOR_CHALK_DIM,
            tags="percent",
        )

        # Status text (loading step label / "Click or press any key…")
        self._status_id = self._canvas.create_text(
            0, 0, text="", anchor="n",
            font=("Helvetica", 12), fill=COLOR_TEXT_MUTED,
            tags="status",
        )

        # Track load progress
        self._current_step = 0
        self._loading_done = False

        # Reposition elements when canvas resizes
        self._canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event) -> None:
        """Reposition text and progress bar when canvas size changes."""
        cx = event.width // 2
        cy = event.height

        # Title: top-center with padding
        self._canvas.coords("title", cx, 60)

        # Progress bar: bottom-center, 80px from bottom
        self._canvas.coords("progress", cx, cy - 80)
        bar_len = max(300, int(event.width * 0.4))
        self._progress_bar.configure(length=bar_len)

        # Percent text: just below the progress bar
        self._canvas.coords("percent", cx, cy - 55)

        # Status text: below percent
        self._canvas.coords("status", cx, cy - 30)

        # Scale background image if already loaded
        if self._bg_image_id and self.app.assets.splash_bg:
            self._canvas.coords(self._bg_image_id, event.width // 2, event.height // 2)

    def on_show(self, **kwargs) -> None:
        """Begin asset loading when the splash screen is shown."""
        if not self._loading_done and self._current_step == 0:
            self.after(300, self._load_next_step)

    def _load_next_step(self) -> None:
        """Load the next asset and update progress."""
        assets = self.app.assets

        if self._current_step >= assets.total_steps:
            self._loading_done = True
            self._progress_var.set(100.0)
            self._canvas.itemconfig(self._percent_label_id, text="100%")
            self._canvas.itemconfig(
                self._status_id,
                text="Loaded. Click or press any key to continue…",
                fill=COLOR_ACCENT,
                font=("Helvetica", 14, "bold"),
            )
            self._canvas.bind("<Button-1>", self._continue)
            self.app.bind("<Key>", self._continue)
            return

        label, load_fn = assets.get_step(self._current_step)
        self._canvas.itemconfig(self._status_id, text=label)

        self.update_idletasks()
        w = self.winfo_width() or self.app.winfo_screenwidth()
        h = self.winfo_height() or self.app.winfo_screenheight()

        load_fn(w, h)

        if self._current_step == 0 and assets.splash_bg:
            self._bg_image_id = self._canvas.create_image(
                w // 2, h // 2, image=assets.splash_bg, anchor="center",
            )
            self._canvas.tag_lower(self._bg_image_id)

        self._current_step += 1
        pct = (self._current_step / assets.total_steps) * 100
        self._progress_var.set(pct)
        self._canvas.itemconfig(self._percent_label_id, text=f"{int(pct)}%")

        self.after(200, self._load_next_step)

    def _continue(self, event=None) -> None:
        """Navigate to Main Window after user interaction."""
        self._canvas.unbind("<Button-1>")
        self.app.unbind("<Key>")
        self.app.transition_to(MAIN_WINDOW)


# ---------------------------------------------------------------------------
# Reusable Menu Template Screen (Phase 3)
# ---------------------------------------------------------------------------
class MenuTemplateScreen(BaseScreen):
    """Reusable base screen for all menu and mode selection screens.

    Layout rules (from specs):
    - Background: brown texture image
    - Title: top-center
    - Left side: vertical menu buttons with hover effects
    - Center/right: ambient, non-interactive 3x3 chalk board loop
    """

    def __init__(
        self,
        parent: tk.Frame,
        app: App,
        title: str = "",
        subtitle: str = "",
    ) -> None:
        super().__init__(parent, app)
        self.title_text = title
        self.subtitle_text = subtitle
        self.configure(bg=COLOR_FRAME_BG)

        # Main background canvas fills the entire screen
        self._canvas = tk.Canvas(self, highlightthickness=0, bg=COLOR_FRAME_BG)
        self._canvas.pack(fill="both", expand=True)

        self._bg_image_id: int | None = None

        # Title text (top-center)
        self._title_id = self._canvas.create_text(
            0, 0, text=self.title_text, anchor="n",
            font=FONT_TITLE, fill=COLOR_CHALK, tags="title",
        )

        # Optional subtitle text
        self._subtitle_id = self._canvas.create_text(
            0, 0, text=self.subtitle_text, anchor="n",
            font=FONT_SUBTITLE, fill=COLOR_ACCENT, tags="subtitle",
        )

        # Left menu buttons container frame
        self._menu_frame = tk.Frame(self._canvas, bg=COLOR_FRAME_BG, bd=0)
        self._menu_window_id = self._canvas.create_window(
            0, 0, window=self._menu_frame, anchor="nw", tags="menu_window",
        )

        # Ambient board state
        self._board_size = 320
        self._board_cx = 0
        self._board_cy = 0
        self._anim_timer: str | None = None
        self._anim_step = 0
        self._current_marks: list[tuple[int, int, str]] = []
        self._active = False

        # Engaging 9-move sequence for ambient dummy play (loops smoothly)
        self._ambient_sequence: list[tuple[int, int, str]] = [
            (1, 1, "X"),  # center
            (0, 0, "O"),  # top-left
            (0, 2, "X"),  # top-right
            (2, 0, "O"),  # bottom-left (block)
            (2, 2, "X"),  # bottom-right (threaten col 2)
            (1, 2, "O"),  # mid-right (block)
            (2, 1, "X"),  # bottom-mid (threaten row 2)
            (1, 0, "O"),  # mid-left
            (0, 1, "X"),  # top-mid
        ]

        # Bind canvas resize and destroy cleanup
        self._canvas.bind("<Configure>", self._on_resize)
        self.bind("<Destroy>", lambda e: self.stop_ambient_loop())

    def add_menu_button(
        self,
        text: str,
        command: callable,
        accent: bool = False,
    ) -> tk.Button:
        """Create and pack an enlarged, styled menu button in the left panel.

        Follows Design System rules: flat look, hover tint, accent highlights,
        with comfortable touch targets and clear visibility.
        """
        btn_bg = COLOR_BTN_BG
        btn_fg = COLOR_ACCENT if accent else COLOR_BTN_FG

        btn = tk.Button(
            self._menu_frame,
            text=text,
            font=FONT_MENU_BTN,
            bg=btn_bg,
            fg=btn_fg,
            activebackground=COLOR_BTN_HOVER_BG,
            activeforeground=COLOR_BTN_HOVER_FG,
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#42291A",
            highlightcolor=COLOR_ACCENT,
            cursor="hand2",
            command=command,
        )
        btn.pack(fill="x", pady=9, ipady=12, padx=8)

        def _on_enter(event):
            btn.configure(bg=COLOR_BTN_HOVER_BG, fg=COLOR_BTN_HOVER_FG)

        def _on_leave(event):
            btn.configure(bg=btn_bg, fg=btn_fg)

        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)
        return btn

    def _ensure_menu_bg(self) -> None:
        """Ensure menu background texture is loaded and rendered on canvas."""
        assets = self.app.assets
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1024
        h = self.winfo_height() or self.app.winfo_screenheight() or 768

        if assets.menu_bg is None and os.path.isfile(_MENU_BG_PATH):
            assets._load_menu_bg(w, h)

        if assets.menu_bg and self._bg_image_id is None:
            self._bg_image_id = self._canvas.create_image(
                w // 2, h // 2, image=assets.menu_bg, anchor="center", tags="menu_bg",
            )
            self._canvas.tag_lower(self._bg_image_id)

    def _on_resize(self, event) -> None:
        """Reposition elements when the screen dimensions change."""
        w = event.width
        h = event.height
        if w < 100 or h < 100:
            return

        cx = w // 2
        layout = compute_layout(w, h)

        # Background image center
        if self._bg_image_id and self.app.assets.menu_bg:
            self._canvas.coords(self._bg_image_id, cx, h // 2)

        # Title top-center
        self._canvas.coords("title", cx, layout["title_y"])
        if self.subtitle_text:
            self._canvas.coords("subtitle", cx, layout["subtitle_y"])
        else:
            self._canvas.coords("subtitle", -1000, -1000)

        # Left menu buttons container (centered in left column)
        self._menu_frame.configure(width=layout["menu_width"])
        self._canvas.coords("menu_window", layout["menu_x"], layout["menu_y"])

        # Ambient 3x3 board in center/right area
        self._board_size = layout["ambient_size"]
        self._board_cx = layout["ambient_cx"]
        self._board_cy = layout["ambient_cy"]

        self._draw_ambient_board()

    def set_subtitle(self, text: str) -> None:
        """Update the subtitle text on the canvas and adjust position."""
        self.subtitle_text = text
        self._canvas.itemconfig(self._subtitle_id, text=text)
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1024
        h = self.winfo_height() or self.app.winfo_screenheight() or 768
        layout = compute_layout(w, h)
        cx = w // 2
        if text:
            self._canvas.coords("subtitle", cx, layout["subtitle_y"])
        else:
            self._canvas.coords("subtitle", -1000, -1000)

    def _draw_ambient_board(self) -> None:
        """Draw or redraw the ambient chalk board grid and all active marks."""
        self._canvas.delete("ambient_grid")
        self._canvas.delete("ambient_mark")

        if self._board_size <= 0:
            return

        cx = self._board_cx
        cy = self._board_cy
        size = self._board_size
        half = size // 2
        cell = size // 3

        x0 = cx - half
        y0 = cy - half
        x1 = x0 + size
        y1 = y0 + size

        # 2 vertical chalk lines (stroke width 7 matching gameplay board)
        self._canvas.create_line(
            x0 + cell, y0, x0 + cell, y1,
            fill=COLOR_CHALK, width=7, capstyle="round", tags="ambient_grid",
        )
        self._canvas.create_line(
            x0 + 2 * cell, y0, x0 + 2 * cell, y1,
            fill=COLOR_CHALK, width=7, capstyle="round", tags="ambient_grid",
        )

        # 2 horizontal chalk lines (stroke width 7 matching gameplay board)
        self._canvas.create_line(
            x0, y0 + cell, x1, y0 + cell,
            fill=COLOR_CHALK, width=7, capstyle="round", tags="ambient_grid",
        )
        self._canvas.create_line(
            x0, y0 + 2 * cell, x1, y0 + 2 * cell,
            fill=COLOR_CHALK, width=7, capstyle="round", tags="ambient_grid",
        )

        # Redraw existing marks
        for row, col, symbol in self._current_marks:
            self._draw_mark(row, col, symbol)

    def _draw_mark(self, row: int, col: int, symbol: str) -> None:
        """Draw a single chalk X or O mark at (row, col) with stroke width 7."""
        cx = self._board_cx
        cy = self._board_cy
        half = self._board_size // 2
        cell = self._board_size // 3

        cell_x = (cx - half) + col * cell
        cell_y = (cy - half) + row * cell

        pad = max(10, int(cell * 0.22))
        x1 = cell_x + pad
        y1 = cell_y + pad
        x2 = cell_x + cell - pad
        y2 = cell_y + cell - pad

        if symbol == "X":
            self._canvas.create_line(
                x1, y1, x2, y2,
                fill=COLOR_CHALK, width=7, capstyle="round", tags="ambient_mark",
            )
            self._canvas.create_line(
                x1, y2, x2, y1,
                fill=COLOR_CHALK, width=7, capstyle="round", tags="ambient_mark",
            )
        elif symbol == "O":
            self._canvas.create_oval(
                x1, y1, x2, y2,
                outline=COLOR_CHALK, width=7, tags="ambient_mark",
            )

    def _step_ambient_animation(self) -> None:
        """Advance ambient loop by placing the next mark, or reset and loop endlessly."""
        if not self._active:
            return

        if self._anim_step < len(self._ambient_sequence):
            row, col, symbol = self._ambient_sequence[self._anim_step]
            self._current_marks.append((row, col, symbol))
            self._draw_mark(row, col, symbol)
            self._anim_step += 1
            # Next move after 650ms
            self._anim_timer = self.after(650, self._step_ambient_animation)
        else:
            # All 9 moves placed: hold for 1400ms, then reset and seamlessly loop
            self._anim_step = 0
            self._current_marks.clear()
            self._anim_timer = self.after(1400, self._reset_and_restart_ambient)

    def _reset_and_restart_ambient(self) -> None:
        """Clear board and restart ambient animation sequence endlessly."""
        if not self._active:
            return
        self._canvas.delete("ambient_mark")
        # Brief pause on empty board (400ms) before starting move sequence again
        self._anim_timer = self.after(400, self._step_ambient_animation)

    def start_ambient_loop(self) -> None:
        """Start or resume the ambient animation loop."""
        self._active = True
        self.stop_ambient_loop()
        self._active = True
        self._anim_timer = self.after(400, self._step_ambient_animation)

    def stop_ambient_loop(self) -> None:
        """Cancel any scheduled ambient animation timer safely."""
        self._active = False
        if self._anim_timer is not None:
            try:
                self.after_cancel(self._anim_timer)
            except Exception:
                pass
            self._anim_timer = None

    def on_show(self, **kwargs) -> None:
        """Ensure background is loaded and start ambient animation loop."""
        self._active = True
        self._ensure_menu_bg()
        self.start_ambient_loop()

    def on_hide(self) -> None:
        """Stop ambient animation loop when navigating away."""
        self._active = False
        self.stop_ambient_loop()


# ---------------------------------------------------------------------------
# Menu Screens (Phase 3 implementations using MenuTemplateScreen)
# ---------------------------------------------------------------------------
class MainWindowScreen(MenuTemplateScreen):
    """Main Window screen (top-level menu)."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="TIC-TAC-TOE", subtitle="Main Window")
        self.add_menu_button("Main Menu", lambda: self.app.transition_to(MAIN_MENU))
        self.add_menu_button("Settings", lambda: self.app.transition_to(SETTINGS))
        self.add_menu_button("Exit", self.app.destroy, accent=True)


class MainMenuScreen(MenuTemplateScreen):
    """Main Menu screen with game mode and navigation choices."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="MAIN MENU")
        self.add_menu_button("Play Game", lambda: self.app.transition_to(PLAY_GAME))
        self.add_menu_button("AI vs AI", lambda: self.app.transition_to(AI_VS_AI))
        self.add_menu_button(
            "Train Q-Learning",
            lambda: self.app.transition_to(COMING_SOON, return_to=MAIN_MENU, feature="Train Q-Learning"),
        )
        self.add_menu_button(
            "Evaluation",
            lambda: self.app.transition_to(COMING_SOON, return_to=MAIN_MENU, feature="Evaluation"),
        )
        self.add_menu_button("← Back", lambda: self.app.transition_to(MAIN_WINDOW), accent=True)


class PlayGameScreen(MenuTemplateScreen):
    """Play Game mode selection screen (Single Player vs 2-Player)."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="PLAY GAME")
        self.add_menu_button("Single Player", lambda: self.app.transition_to(SINGLE_PLAYER))
        self.add_menu_button("2-Player", lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_HUMAN))
        self.add_menu_button("← Back", lambda: self.app.transition_to(MAIN_MENU), accent=True)


class SinglePlayerScreen(MenuTemplateScreen):
    """Single Player opponent selection screen (Heuristic vs Q-Learning)."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="SINGLE PLAYER")
        self.add_menu_button(
            "Human vs Heuristic",
            lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_HEURISTIC),
        )
        self.add_menu_button(
            "Human vs Q-Learning",
            lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_QLEARNING),
        )
        self.add_menu_button("← Back", lambda: self.app.transition_to(PLAY_GAME), accent=True)


class AIVsAIScreen(MenuTemplateScreen):
    """AI vs AI visual selection screen."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="AI VS AI")
        self.add_menu_button(
            "Start AI vs AI Game",
            lambda: self.app.transition_to(GAME, mode=MODE_AI_VS_AI),
        )
        self.add_menu_button("← Back", lambda: self.app.transition_to(MAIN_MENU), accent=True)


class SettingsScreen(MenuTemplateScreen):
    """Settings screen placeholder."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(
            parent, app,
            title="SETTINGS",
            subtitle=MSG_SETTINGS,
        )
        self._msg_label = tk.Label(
            self._menu_frame,
            text=MSG_SETTINGS,
            font=FONT_BODY,
            bg=COLOR_FRAME_BG,
            fg=COLOR_CHALK_DIM,
            wraplength=260,
            justify="center",
        )
        self._msg_label.pack(pady=(14, 20), padx=8)
        self.add_menu_button("← Back", lambda: self.app.transition_to(MAIN_WINDOW), accent=True)

    def on_show(self, **kwargs) -> None:
        super().on_show(**kwargs)
        self.set_subtitle(MSG_SETTINGS)


class ComingSoonScreen(MenuTemplateScreen):
    """Reusable 'Coming Soon' placeholder screen."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(
            parent, app,
            title="COMING SOON",
            subtitle=MSG_COMING_SOON,
        )
        self._return_screen = MAIN_MENU
        self._msg_label = tk.Label(
            self._menu_frame,
            text=MSG_COMING_SOON,
            font=FONT_BODY,
            bg=COLOR_FRAME_BG,
            fg=COLOR_CHALK_DIM,
            wraplength=260,
            justify="center",
        )
        self._msg_label.pack(pady=(14, 20), padx=8)
        self.add_menu_button("← Back", self._on_back, accent=True)

    def on_show(self, return_to: str = MAIN_MENU, feature: str | None = None, **kwargs) -> None:
        """Configure return route and feature message upon show."""
        super().on_show(**kwargs)
        self._return_screen = return_to
        if feature:
            self.set_subtitle(f"{feature} — {MSG_COMING_SOON}")
            self._msg_label.configure(text=f"{feature}\n\n{MSG_COMING_SOON}")
        else:
            self.set_subtitle(MSG_COMING_SOON)
            self._msg_label.configure(text=MSG_COMING_SOON)

    def _on_back(self) -> None:
        self.app.transition_to(self._return_screen)


class GameScreen(BaseScreen):
    """Interactive gameplay screen with centered 3x3 chalk board and pre-game setup."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app)
        self.configure(bg="#0F0F0F")

        # Main canvas fills screen
        self._canvas = tk.Canvas(self, highlightthickness=0, bg="#0F0F0F")
        self._canvas.pack(fill="both", expand=True)

        self._bg_image_id: int | None = None

        # Game state (In-Memory Data Schema)
        self.current_mode = MODE_HUMAN_VS_HUMAN
        self._players: list[PlayerInfo] = []
        self._current_player_idx = 0
        self._toss_winner_idx: int | None = None
        self._move_count = 0
        self._cells: list[str | None] = [None] * 9
        self._game_active = False
        self._game_over = False

        # Board layout coordinates
        self._board_size = 400
        self._board_cx = 0
        self._board_cy = 0

        # Canvas UI text elements
        # Top-left Mode label
        self._canvas.create_text(
            35, 28, text="", anchor="nw",
            font=FONT_SMALL, fill=COLOR_TEXT_MUTED, tags="mode_label",
        )

        # Top-center Turn indicator
        self._canvas.create_text(
            0, 30, text="", anchor="n",
            font=FONT_TITLE, fill=COLOR_ACCENT, tags="turn_indicator",
        )

        # Player 1 badge (above board left)
        self._canvas.create_text(
            0, 0, text="", anchor="w",
            font=FONT_BODY, fill=COLOR_CHALK, tags="player1_label",
        )

        # Player 2 badge (above board right)
        self._canvas.create_text(
            0, 0, text="", anchor="e",
            font=FONT_BODY, fill=COLOR_CHALK, tags="player2_label",
        )

        # Hint text below board
        self._canvas.create_text(
            0, 0, text="", anchor="n",
            font=FONT_SUBTITLE, fill=COLOR_CHALK_DIM, tags="board_hint",
        )

        # Top-right Home button
        self._home_btn = tk.Button(
            self._canvas,
            text="🏠 Home",
            font=FONT_SMALL,
            bg=COLOR_BTN_BG,
            fg=COLOR_BTN_FG,
            activebackground=COLOR_BTN_HOVER_BG,
            activeforeground=COLOR_BTN_HOVER_FG,
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3A281E",
            cursor="hand2",
            command=lambda: self.app.transition_to(MAIN_WINDOW),
        )
        self._home_window = self._canvas.create_window(
            0, 0, window=self._home_btn, anchor="ne", tags="home_btn",
        )

        # Pre-game & Post-game overlay frame
        self._overlay_frame = tk.Frame(
            self._canvas,
            bg="#1E140F",
            bd=2,
            relief="solid",
            highlightthickness=2,
            highlightbackground=COLOR_ACCENT,
        )
        self._overlay_window: int | None = None

        # Bindings
        self._canvas.bind("<Configure>", self._on_resize)
        self._canvas.bind("<Button-1>", self._on_canvas_click)

    def on_show(self, mode: str = MODE_HUMAN_VS_HUMAN, **kwargs) -> None:
        """Initialize game mode, trigger swift transition, and launch pre-game setup."""
        self.current_mode = mode
        self._ensure_game_bg()
        self._play_swift_transition()
        self.setup_game(mode)

    def _play_swift_transition(self) -> None:
        """Swift fade/flash when switching to gameplay background."""
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1920
        h = self.winfo_height() or self.app.winfo_screenheight() or 1080
        flash_id = self._canvas.create_rectangle(
            0, 0, w, h, fill="#050302", tags="flash_overlay",
        )
        self.after(90, lambda: self._canvas.delete("flash_overlay"))

    def _ensure_game_bg(self) -> None:
        """Ensure dark gameplay background is loaded and rendered on canvas."""
        assets = self.app.assets
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1024
        h = self.winfo_height() or self.app.winfo_screenheight() or 768

        if assets.game_bg is None and os.path.isfile(_GAME_BG_PATH):
            assets._load_game_bg(w, h)

        if assets.game_bg and self._bg_image_id is None:
            self._bg_image_id = self._canvas.create_image(
                w // 2, h // 2, image=assets.game_bg, anchor="center", tags="game_bg",
            )
            self._canvas.tag_lower(self._bg_image_id)

    def setup_game(self, mode: str) -> None:
        """Reset board state and start pre-game setup (Toss & Symbol selection)."""
        self.current_mode = mode
        self._cells = [None] * 9
        self._move_count = 0
        self._game_active = False
        self._game_over = False
        self._toss_winner_idx = None

        # Build player models per mode (from Schema spec)
        if mode == MODE_HUMAN_VS_HUMAN:
            self._players = [
                PlayerInfo("Player 1", PLAYER_HUMAN),
                PlayerInfo("Player 2", PLAYER_HUMAN),
            ]
            mode_desc = "Mode: 2-Player (Human vs Human)"
        elif mode == MODE_HUMAN_VS_HEURISTIC:
            self._players = [
                PlayerInfo("Player (Human)", PLAYER_HUMAN),
                PlayerInfo("AI (Heuristic)", PLAYER_HEURISTIC_AI),
            ]
            mode_desc = "Mode: Single Player (Human vs Heuristic AI)"
        elif mode == MODE_HUMAN_VS_QLEARNING:
            # TODO(BACKEND): load q_table.pkl when entering Q-learning mode
            self._players = [
                PlayerInfo("Player (Human)", PLAYER_HUMAN),
                PlayerInfo("AI (Q-Learning)", PLAYER_QLEARNING_AI),
            ]
            mode_desc = "Mode: Single Player (Human vs Q-Learning AI)"
        else:  # MODE_AI_VS_AI
            # TODO(BACKEND): initialize GameEngine and AI vs AI battle
            self._players = [
                PlayerInfo("AI 1 (Heuristic)", PLAYER_HEURISTIC_AI),
                PlayerInfo("AI 2 (Q-Learning)", PLAYER_QLEARNING_AI),
            ]
            mode_desc = "Mode: AI vs AI (Demonstration)"

        self._canvas.itemconfig("mode_label", text=mode_desc)
        self._canvas.itemconfig("turn_indicator", text="Pre-Game Toss", fill=COLOR_CHALK_DIM)
        self._canvas.itemconfig("board_hint", text="Complete pre-game toss to begin.")

        self._draw_board()
        self._show_toss_overlay()

    def _show_toss_overlay(self) -> None:
        """Display Step 1 of pre-game setup: Coin Toss."""
        for child in self._overlay_frame.winfo_children():
            child.destroy()

        p1, p2 = self._players

        tk.Label(
            self._overlay_frame,
            text="PRE-GAME SETUP",
            font=("Helvetica", 18, "bold"),
            bg="#1E140F",
            fg=COLOR_CHALK,
        ).pack(pady=(16, 4), padx=28)

        tk.Label(
            self._overlay_frame,
            text=f"Match: {p1.label} vs {p2.label}",
            font=FONT_SUBTITLE,
            bg="#1E140F",
            fg=COLOR_ACCENT,
        ).pack(pady=(0, 14))

        tk.Label(
            self._overlay_frame,
            text="Step 1: Toss a coin to determine who plays first.\nToss winner always makes the opening move.",
            font=FONT_BODY,
            bg="#1E140F",
            fg=COLOR_CHALK_DIM,
            justify="center",
        ).pack(pady=(0, 18), padx=20)

        toss_btn = tk.Button(
            self._overlay_frame,
            text="🪙 Flip Coin",
            font=FONT_MENU_BTN,
            bg=COLOR_BTN_BG,
            fg=COLOR_ACCENT,
            activebackground=COLOR_BTN_HOVER_BG,
            activeforeground=COLOR_BTN_HOVER_FG,
            bd=0, relief="flat", highlightthickness=1,
            highlightbackground="#4A3225",
            cursor="hand2",
            command=self._execute_toss,
        )
        toss_btn.pack(pady=(0, 16), ipady=8, ipadx=24)

        self._display_overlay()

    def _execute_toss(self) -> None:
        """Play an animated 3D coin flip before deciding and revealing toss winner."""
        self._toss_winner_idx = random.choice([0, 1])
        winner = self._players[self._toss_winner_idx]
        other = self._players[1 - self._toss_winner_idx]
        winner.is_starter = True
        other.is_starter = False

        for child in self._overlay_frame.winfo_children():
            child.destroy()

        tk.Label(
            self._overlay_frame,
            text="COIN TOSS IN PROGRESS",
            font=("Helvetica", 18, "bold"),
            bg="#1E140F",
            fg=COLOR_ACCENT,
        ).pack(pady=(16, 4), padx=28)

        status_lbl = tk.Label(
            self._overlay_frame,
            text="Flipping coin to determine starter...",
            font=FONT_SUBTITLE,
            bg="#1E140F",
            fg=COLOR_CHALK_DIM,
        )
        status_lbl.pack(pady=(0, 10))

        coin_cv = tk.Canvas(
            self._overlay_frame,
            width=160,
            height=130,
            bg="#1E140F",
            highlightthickness=0,
        )
        coin_cv.pack(pady=(0, 14))

        total_frames = 26
        angle_state = [0.0]

        def _animate_flip(frame: int = 0) -> None:
            if not self.winfo_ismapped():
                return
            coin_cv.delete("all")
            cx, cy = 80, 65
            r = 44

            speed = max(0.12, (total_frames - frame) / total_frames * 0.48)
            angle_state[0] += speed
            ang = angle_state[0]
            scale_y = abs(math.cos(ang))
            ry = max(3, int(r * scale_y))

            # Gold medallion colors
            face_color = "#E5C158" if math.sin(ang) > 0 else "#C59B63"
            edge_color = "#8A6233"

            coin_cv.create_oval(
                cx - r, cy - ry, cx + r, cy + ry,
                fill=face_color, outline=edge_color, width=3,
            )
            if ry > 12:
                symbol = "★" if math.sin(ang) > 0 else "✦"
                coin_cv.create_text(
                    cx, cy, text=symbol,
                    fill="#42291A",
                    font=("Helvetica", max(10, int(18 * scale_y)), "bold"),
                )

            if frame < total_frames:
                self.after(35, lambda: _animate_flip(frame + 1))
            else:
                # Landed coin
                coin_cv.delete("all")
                coin_cv.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill="#F2D06B", outline="#8A6233", width=4,
                )
                coin_cv.create_text(
                    cx, cy, text="★",
                    fill="#42291A", font=("Helvetica", 22, "bold"),
                )
                status_lbl.configure(text="✨ Landed! Announcing winner...", fg=COLOR_ACCENT)
                self.after(550, lambda: self._show_toss_winner_result(winner, other))

        _animate_flip(0)

    def _show_toss_winner_result(self, winner: PlayerInfo, other: PlayerInfo) -> None:
        """Display Toss Result and proceed to symbol selection or auto-assignment."""
        for child in self._overlay_frame.winfo_children():
            child.destroy()

        tk.Label(
            self._overlay_frame,
            text="TOSS RESULT",
            font=("Helvetica", 18, "bold"),
            bg="#1E140F",
            fg=COLOR_ACCENT,
        ).pack(pady=(16, 6), padx=28)

        # Symbol selection rule (locked):
        # Only a human may choose X/O.
        # - Human vs Human: toss winner chooses.
        # - Human vs AI: if human wins toss -> human chooses; else auto-assign.
        # - AI vs AI: auto-assign.
        human_can_choose = False
        if self.current_mode == MODE_HUMAN_VS_HUMAN:
            human_can_choose = True
        elif winner.type == PLAYER_HUMAN:
            human_can_choose = True

        if human_can_choose:
            tk.Label(
                self._overlay_frame,
                text=f"🎉 {winner.label} won the toss!\n\nToss winner plays first. Choose your symbol:",
                font=FONT_BODY,
                bg="#1E140F",
                fg=COLOR_CHALK,
                justify="center",
            ).pack(pady=(0, 18), padx=20)

            btn_box = tk.Frame(self._overlay_frame, bg="#1E140F")
            btn_box.pack(pady=(0, 18))

            x_btn = tk.Button(
                btn_box,
                text="Play as X",
                font=FONT_MENU_BTN,
                bg=COLOR_BTN_BG,
                fg=COLOR_CHALK,
                activebackground=COLOR_BTN_HOVER_BG,
                activeforeground=COLOR_ACCENT,
                bd=0, relief="flat", highlightthickness=1,
                highlightbackground="#4A3225",
                cursor="hand2",
                command=lambda: self._on_symbol_chosen("X"),
            )
            x_btn.pack(side="left", padx=12, ipady=10, ipadx=22)

            o_btn = tk.Button(
                btn_box,
                text="Play as O",
                font=FONT_MENU_BTN,
                bg=COLOR_BTN_BG,
                fg=COLOR_CHALK,
                activebackground=COLOR_BTN_HOVER_BG,
                activeforeground=COLOR_ACCENT,
                bd=0, relief="flat", highlightthickness=1,
                highlightbackground="#4A3225",
                cursor="hand2",
                command=lambda: self._on_symbol_chosen("O"),
            )
            o_btn.pack(side="left", padx=12, ipady=10, ipadx=22)
        else:
            # Auto-assign: starter=X, other=O
            winner.symbol = "X"
            other.symbol = "O"

            tk.Label(
                self._overlay_frame,
                text=f"{winner.label} won the toss and plays first!\n\n(AI won toss — Auto-assigned: {winner.label} = 'X', {other.label} = 'O')",
                font=FONT_BODY,
                bg="#1E140F",
                fg=COLOR_CHALK,
                justify="center",
            ).pack(pady=(0, 18), padx=20)

            start_btn = tk.Button(
                self._overlay_frame,
                text="Start Game →",
                font=FONT_MENU_BTN,
                bg=COLOR_BTN_BG,
                fg=COLOR_ACCENT,
                activebackground=COLOR_BTN_HOVER_BG,
                activeforeground=COLOR_BTN_HOVER_FG,
                bd=0, relief="flat", highlightthickness=1,
                highlightbackground="#4A3225",
                cursor="hand2",
                command=self._start_gameplay,
            )
            start_btn.pack(pady=(0, 18), ipady=10, ipadx=28)

    def _on_symbol_chosen(self, chosen: str) -> None:
        """Handle human symbol choice (X or O)."""
        winner = self._players[self._toss_winner_idx]
        other = self._players[1 - self._toss_winner_idx]

        winner.symbol = chosen
        other.symbol = "O" if chosen == "X" else "X"

        for child in self._overlay_frame.winfo_children():
            child.destroy()

        tk.Label(
            self._overlay_frame,
            text="SYMBOLS ASSIGNED",
            font=("Helvetica", 18, "bold"),
            bg="#1E140F",
            fg=COLOR_ACCENT,
        ).pack(pady=(16, 6), padx=28)

        tk.Label(
            self._overlay_frame,
            text=f"{winner.label}: '{winner.symbol}' (First Move)\n{other.label}: '{other.symbol}'\n\nReady to play!",
            font=FONT_BODY,
            bg="#1E140F",
            fg=COLOR_CHALK,
            justify="center",
        ).pack(pady=(0, 20), padx=24)

        start_btn = tk.Button(
            self._overlay_frame,
            text="Start Game →",
            font=FONT_MENU_BTN,
            bg=COLOR_BTN_BG,
            fg=COLOR_ACCENT,
            activebackground=COLOR_BTN_HOVER_BG,
            activeforeground=COLOR_BTN_HOVER_FG,
            bd=0, relief="flat", highlightthickness=1,
            highlightbackground="#4A3225",
            cursor="hand2",
            command=self._start_gameplay,
        )
        start_btn.pack(pady=(0, 18), ipady=8, ipadx=24)

    def _start_gameplay(self) -> None:
        """Dismiss overlay, activate board, and begin turn 1."""
        self._dismiss_overlay()
        self._current_player_idx = self._toss_winner_idx
        self._game_active = True
        self._game_over = False
        self._canvas.itemconfig("board_hint", text="Click an empty cell on the chalk board to place your mark.")
        self._update_header()

    def _display_overlay(self) -> None:
        """Show overlay window centered on canvas."""
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1024
        h = self.winfo_height() or self.app.winfo_screenheight() or 768
        cx = w // 2
        cy = h // 2
        if self._overlay_window is None:
            self._overlay_window = self._canvas.create_window(
                cx, cy, window=self._overlay_frame, anchor="center", tags="overlay",
            )
        else:
            self._canvas.coords(self._overlay_window, cx, cy)
            self._canvas.itemconfig(self._overlay_window, state="normal")

    def _dismiss_overlay(self) -> None:
        """Hide overlay window."""
        if self._overlay_window is not None:
            self._canvas.itemconfig(self._overlay_window, state="hidden")

    def _on_canvas_click(self, event) -> None:
        """Handle clicks on the centered 3x3 board."""
        if not self._game_active or self._game_over:
            return

        cx = self._board_cx
        cy = self._board_cy
        half = self._board_size // 2
        cell = self._board_size // 3

        origin_x = cx - half
        origin_y = cy - half

        col = (event.x - origin_x) // cell
        row = (event.y - origin_y) // cell

        if 0 <= row < 3 and 0 <= col < 3:
            idx = row * 3 + col
            # Disable occupied cells (ignore click)
            if self._cells[idx] is not None:
                return

            current_player = self._players[self._current_player_idx]
            self._cells[idx] = current_player.symbol
            self._move_count += 1
            self._draw_mark(row, col, current_player.symbol)

            # TODO(BACKEND): notify GameEngine of move (row, col)
            # TODO(BACKEND): evaluate GameEngine for real win/loss

            if self._move_count >= 9:
                # Dummy gameplay rule: ends after 9 moves as Draw
                self._game_over = True
                self._game_active = False
                self._update_header()
                self._canvas.itemconfig("board_hint", text="Game ended in Draw. Choose Retry or Home.")
                self._show_post_game_overlay()
            else:
                # Alternate turns
                self._current_player_idx = 1 - self._current_player_idx
                # TODO(BACKEND): if next player is AI, trigger HeuristicAgent / QLearningAgent move
                self._update_header()

    def _show_post_game_overlay(self) -> None:
        """Display post-game result (Draw) and Retry / Home options."""
        for child in self._overlay_frame.winfo_children():
            child.destroy()

        tk.Label(
            self._overlay_frame,
            text="GAME OVER",
            font=("Helvetica", 20, "bold"),
            bg="#1E140F",
            fg=COLOR_ACCENT,
        ).pack(pady=(16, 4), padx=32)

        tk.Label(
            self._overlay_frame,
            text="Result: DRAW",
            font=("Helvetica", 18, "bold"),
            bg="#1E140F",
            fg=COLOR_CHALK,
        ).pack(pady=(0, 8))

        tk.Label(
            self._overlay_frame,
            text="All 9 moves played without a winner (dummy rules).",
            font=FONT_BODY,
            bg="#1E140F",
            fg=COLOR_CHALK_DIM,
            justify="center",
        ).pack(pady=(0, 18), padx=20)

        btn_box = tk.Frame(self._overlay_frame, bg="#1E140F")
        btn_box.pack(pady=(0, 18))

        retry_btn = tk.Button(
            btn_box,
            text="🔄 Retry",
            font=FONT_MENU_BTN,
            bg=COLOR_BTN_BG,
            fg=COLOR_ACCENT,
            activebackground=COLOR_BTN_HOVER_BG,
            activeforeground=COLOR_BTN_HOVER_FG,
            bd=0, relief="flat", highlightthickness=1,
            highlightbackground="#4A3225",
            cursor="hand2",
            command=lambda: self.setup_game(self.current_mode),
        )
        retry_btn.pack(side="left", padx=12, ipady=10, ipadx=24)

        home_btn = tk.Button(
            btn_box,
            text="🏠 Home",
            font=FONT_MENU_BTN,
            bg=COLOR_BTN_BG,
            fg=COLOR_CHALK,
            activebackground=COLOR_BTN_HOVER_BG,
            activeforeground=COLOR_BTN_HOVER_FG,
            bd=0, relief="flat", highlightthickness=1,
            highlightbackground="#4A3225",
            cursor="hand2",
            command=lambda: self.app.transition_to(MAIN_WINDOW),
        )
        home_btn.pack(side="left", padx=12, ipady=10, ipadx=24)

        self._display_overlay()

    def _draw_board(self) -> None:
        """Draw or redraw centered 3x3 chalk grid and current marks."""
        self._canvas.delete("game_grid")
        self._canvas.delete("game_mark")

        if self._board_size <= 0:
            return

        cx = self._board_cx
        cy = self._board_cy
        size = self._board_size
        half = size // 2
        cell = size // 3

        x0 = cx - half
        y0 = cy - half
        x1 = x0 + size
        y1 = y0 + size

        # 2 vertical chalk lines
        self._canvas.create_line(
            x0 + cell, y0, x0 + cell, y1,
            fill=COLOR_CHALK, width=7, capstyle="round", tags="game_grid",
        )
        self._canvas.create_line(
            x0 + 2 * cell, y0, x0 + 2 * cell, y1,
            fill=COLOR_CHALK, width=7, capstyle="round", tags="game_grid",
        )

        # 2 horizontal chalk lines
        self._canvas.create_line(
            x0, y0 + cell, x1, y0 + cell,
            fill=COLOR_CHALK, width=7, capstyle="round", tags="game_grid",
        )
        self._canvas.create_line(
            x0, y0 + 2 * cell, x1, y0 + 2 * cell,
            fill=COLOR_CHALK, width=7, capstyle="round", tags="game_grid",
        )

        # Draw marks
        for idx, mark in enumerate(self._cells):
            if mark is not None:
                r = idx // 3
                c = idx % 3
                self._draw_mark(r, c, mark)

    def _draw_mark(self, row: int, col: int, symbol: str) -> None:
        """Draw chalk mark (X or O) at cell (row, col)."""
        cx = self._board_cx
        cy = self._board_cy
        half = self._board_size // 2
        cell = self._board_size // 3

        cell_x = (cx - half) + col * cell
        cell_y = (cy - half) + row * cell

        pad = max(12, int(cell * 0.22))
        x1 = cell_x + pad
        y1 = cell_y + pad
        x2 = cell_x + cell - pad
        y2 = cell_y + cell - pad

        if symbol == "X":
            self._canvas.create_line(
                x1, y1, x2, y2,
                fill=COLOR_CHALK, width=7, capstyle="round", tags="game_mark",
            )
            self._canvas.create_line(
                x1, y2, x2, y1,
                fill=COLOR_CHALK, width=7, capstyle="round", tags="game_mark",
            )
        elif symbol == "O":
            self._canvas.create_oval(
                x1, y1, x2, y2,
                outline=COLOR_CHALK, width=7, tags="game_mark",
            )

    def _on_resize(self, event) -> None:
        """Reposition board and status elements on window resize."""
        w = event.width
        h = event.height
        if w < 100 or h < 100:
            return

        cx = w // 2
        layout = compute_layout(w, h)

        # Background image center
        if self._bg_image_id and self.app.assets.game_bg:
            self._canvas.coords(self._bg_image_id, cx, h // 2)

        # Mode label (top-left)
        self._canvas.coords("mode_label", 30, 25)

        # Turn indicator (top-center)
        self._canvas.coords("turn_indicator", cx, 30)

        # Home button (top-right)
        self._canvas.coords("home_btn", w - 30, 25)

        # Board sizing and centering
        self._board_size = layout["game_size"]
        self._board_cx = layout["game_cx"]
        self._board_cy = layout["game_cy"]

        half = self._board_size // 2
        origin_y = self._board_cy - half

        # Player 1 label (above board, left-aligned with grid)
        self._canvas.coords("player1_label", cx - half, origin_y - 28)

        # Player 2 label (above board, right-aligned with grid)
        self._canvas.coords("player2_label", cx + half, origin_y - 28)

        # Hint text (below board)
        self._canvas.coords("board_hint", cx, self._board_cy + half + 28)

        # Overlay window centering
        if self._overlay_window is not None:
            self._canvas.coords(self._overlay_window, cx, h // 2)

        self._draw_board()
        self._update_header()

    def _update_header(self) -> None:
        """Update turn indicator and player labels."""
        if not self._players:
            return

        p1, p2 = self._players

        if self._game_over:
            turn_str = "Game Over — Draw!"
            turn_color = COLOR_ACCENT
        elif self._game_active:
            curr = self._players[self._current_player_idx]
            turn_str = f"Turn {self._move_count + 1}/9: {curr.label} ({curr.symbol})"
            turn_color = COLOR_ACCENT
        else:
            turn_str = "Pre-Game Setup"
            turn_color = COLOR_CHALK_DIM

        self._canvas.itemconfig("turn_indicator", text=turn_str, fill=turn_color)

        p1_sym = f"[{p1.symbol}]" if p1.symbol else ""
        p2_sym = f"[{p2.symbol}]" if p2.symbol else ""

        p1_text = f"Player 1: {p1.label} {p1_sym}"
        p2_text = f"Player 2: {p2.label} {p2_sym}"

        p1_color = COLOR_ACCENT if (self._game_active and self._current_player_idx == 0) else COLOR_CHALK
        p2_color = COLOR_ACCENT if (self._game_active and self._current_player_idx == 1) else COLOR_CHALK

        self._canvas.itemconfig("player1_label", text=p1_text, fill=p1_color)
        self._canvas.itemconfig("player2_label", text=p2_text, fill=p2_color)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Launch the Tic-Tac-Toe GUI application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
