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

# Screen name constants
SPLASH = "splash"
MAIN_WINDOW = "main_window"
MAIN_MENU = "main_menu"
PLAY_GAME = "play_game"
SINGLE_PLAYER = "single_player"
AI_VS_AI = "ai_vs_ai"
SETTINGS = "settings"
COMING_SOON = "coming_soon"
GAME = "game"

# Design System Tokens
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

# Placeholder messages
MSG_SETTINGS = "Currently in development phase."
MSG_COMING_SOON = "This feature will be implemented later."

# Game Modes and Data Schema
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


def compute_layout(width: int, height: int) -> dict:
    """Compute responsive screen geometry for menu columns, buttons, and boards."""
    w, h = max(320, width), max(240, height)
    title_y = max(28, int(h * 0.04))
    left_col_x0 = max(28, int(w * 0.05))
    left_col_width = min(520, max(320, int(w * 0.36)))
    menu_width = min(460, max(300, int(left_col_width * 0.92)))
    right_area_x0 = left_col_x0 + left_col_width
    right_area_w = max(100, w - right_area_x0)

    return {
        "left_col_x0": left_col_x0,
        "left_col_width": left_col_width,
        "menu_width": menu_width,
        "menu_x": int(left_col_x0 + (left_col_width - menu_width) * 0.5),
        "menu_y": max(95, int(h * 0.16)),
        "title_y": title_y,
        "subtitle_y": title_y + 42,
        "ambient_size": min(420, max(200, int(min(right_area_w * 0.72, h * 0.54)))),
        "ambient_cx": right_area_x0 + right_area_w // 2,
        "ambient_cy": max(180, int(h * 0.52)),
        "game_size": min(480, max(260, int(min(w * 0.52, h * 0.52)))),
        "game_cx": w // 2,
        "game_cy": max(180, int(h * 0.54)),
    }


# Asset paths
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _ASSETS_DIR = os.path.join(sys._MEIPASS, "gui", "assets")
else:
    _ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

_SPLASH_BG_PATH = os.path.join(_ASSETS_DIR, "Splash background", "Generated Image September 12, 2026 - 10_50PM.jpg")
_MENU_BG_PATH = os.path.join(_ASSETS_DIR, "Menu background", "27707-background-1072764_1920.jpg")
_GAME_BG_PATH = os.path.join(_ASSETS_DIR, "Gameplay background", "Generated Image September 13, 2026 - 10_06PM.jpg")


class AssetManager:
    """Loads and holds references to all GUI image assets."""

    def __init__(self) -> None:
        self.splash_bg: ImageTk.PhotoImage | None = None
        self.menu_bg: ImageTk.PhotoImage | None = None
        self.game_bg: ImageTk.PhotoImage | None = None
        self._steps: list[tuple[str, callable]] = [
            ("Loading splash background…", self._load_splash_bg),
            ("Loading menu background…", self._load_menu_bg),
            ("Loading gameplay background…", self._load_game_bg),
        ]

    @property
    def total_steps(self) -> int:
        return len(self._steps)

    def get_step(self, index: int) -> tuple[str, callable]:
        return self._steps[index]

    def _load_image(self, path: str, size: tuple[int, int]) -> ImageTk.PhotoImage:
        img = Image.open(path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _load_splash_bg(self, width: int, height: int) -> None:
        self.splash_bg = self._load_image(_SPLASH_BG_PATH, (width, height))

    def _load_menu_bg(self, width: int, height: int) -> None:
        self.menu_bg = self._load_image(_MENU_BG_PATH, (width, height))

    def _load_game_bg(self, width: int, height: int) -> None:
        self.game_bg = self._load_image(_GAME_BG_PATH, (width, height))


def _draw_chalk_grid(canvas: tk.Canvas, cx: int, cy: int, size: int, tag: str) -> None:
    canvas.delete(tag)
    if size <= 0:
        return
    half, cell = size // 2, size // 3
    x0, y0 = cx - half, cy - half
    for i in (1, 2):
        canvas.create_line(x0 + i * cell, y0, x0 + i * cell, y0 + size, fill=COLOR_CHALK, width=7, capstyle="round", tags=tag)
        canvas.create_line(x0, y0 + i * cell, x0 + size, y0 + i * cell, fill=COLOR_CHALK, width=7, capstyle="round", tags=tag)


def _draw_chalk_mark(canvas: tk.Canvas, cx: int, cy: int, size: int, row: int, col: int, symbol: str, tag: str) -> None:
    half, cell = size // 2, size // 3
    pad = max(10, int(cell * 0.22))
    x1, y1 = (cx - half) + col * cell + pad, (cy - half) + row * cell + pad
    x2, y2 = x1 + cell - 2 * pad, y1 + cell - 2 * pad
    if symbol == "X":
        canvas.create_line(x1, y1, x2, y2, fill=COLOR_CHALK, width=7, capstyle="round", tags=tag)
        canvas.create_line(x1, y2, x2, y1, fill=COLOR_CHALK, width=7, capstyle="round", tags=tag)
    elif symbol == "O":
        canvas.create_oval(x1, y1, x2, y2, outline=COLOR_CHALK, width=7, tags=tag)


class App(tk.Tk):
    """Root Tkinter window and screen manager."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Tic-Tac-Toe")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.assets = AssetManager()
        self._current_screen_name: str | None = None

        self._container = tk.Frame(self)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        self._screens: dict[str, tk.Frame] = {}
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

        self._curtain_left = tk.Frame(self, bg="#0F0906")
        self._curtain_right = tk.Frame(self, bg="#0F0906")
        self._transitioning = False
        self.show_screen(SPLASH)

    def transition_to(self, name: str, **kwargs) -> None:
        """Smoothly transition to named screen with dual-curtain wipe."""
        if self._transitioning:
            self.show_screen(name, **kwargs)
            return

        self._transitioning = True
        steps, interval = 6, 16

        def _animate(step: int, closing: bool) -> None:
            frac = step / steps
            for c, rx in ((self._curtain_left, 0), (self._curtain_right, 1.0 - frac * 0.5)):
                c.place(relx=rx, rely=0, relwidth=frac * 0.5, relheight=1)
                c.lift()
            if closing:
                if step < steps:
                    self.after(interval, lambda: _animate(step + 1, True))
                else:
                    self.show_screen(name, **kwargs)
                    self.after(20, lambda: _animate(steps, False))
            else:
                if step > 0:
                    self.after(interval, lambda: _animate(step - 1, False))
                else:
                    self._curtain_left.place_forget()
                    self._curtain_right.place_forget()
                    self._transitioning = False

        _animate(1, True)

    def show_screen(self, name: str, **kwargs) -> None:
        if self._current_screen_name in self._screens:
            prev = self._screens[self._current_screen_name]
            if hasattr(prev, "on_hide"):
                prev.on_hide()
        self._current_screen_name = name
        frame = self._screens[name]
        if hasattr(frame, "on_show"):
            frame.on_show(**kwargs)
        frame.tkraise()


class BaseScreen(tk.Frame):
    """Common base for all screens."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent)
        self.app = app

    def on_show(self, **kwargs) -> None:
        pass

    def on_hide(self) -> None:
        pass


class SplashScreen(BaseScreen):
    """Splash screen with asset-loading progress bar."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app)
        self.configure(bg="#000000")
        self._canvas = tk.Canvas(self, highlightthickness=0, bg="#000000")
        self._canvas.pack(fill="both", expand=True)
        self._bg_image_id: int | None = None

        self._canvas.create_text(0, 0, text="Tic-Tac-Toe", anchor="n", font=("Helvetica", 48, "bold"), fill=COLOR_CHALK, tags="title")
        self._progress_var = tk.DoubleVar(value=0.0)
        self._progress_bar = ttk.Progressbar(self._canvas, variable=self._progress_var, maximum=100, length=400, mode="determinate")
        self._progress_window = self._canvas.create_window(0, 0, window=self._progress_bar, anchor="s", tags="progress")
        self._percent_label_id = self._canvas.create_text(0, 0, text="0%", anchor="n", font=("Helvetica", 14), fill=COLOR_CHALK_DIM, tags="percent")
        self._status_id = self._canvas.create_text(0, 0, text="", anchor="n", font=("Helvetica", 12), fill=COLOR_TEXT_MUTED, tags="status")

        self._current_step = 0
        self._loading_done = False
        self._canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event) -> None:
        cx, cy = event.width // 2, event.height
        self._canvas.coords("title", cx, 60)
        self._canvas.coords("progress", cx, cy - 80)
        self._progress_bar.configure(length=max(300, int(event.width * 0.4)))
        self._canvas.coords("percent", cx, cy - 55)
        self._canvas.coords("status", cx, cy - 30)
        if self._bg_image_id and self.app.assets.splash_bg:
            self._canvas.coords(self._bg_image_id, cx, cy // 2)

    def on_show(self, **kwargs) -> None:
        if not self._loading_done and self._current_step == 0:
            self.after(300, self._load_next_step)

    def _load_next_step(self) -> None:
        assets = self.app.assets
        if self._current_step >= assets.total_steps:
            self._loading_done = True
            self._progress_var.set(100.0)
            self._canvas.itemconfig(self._percent_label_id, text="100%")
            self._canvas.itemconfig(self._status_id, text="Loaded. Click or press any key to continue…", fill=COLOR_ACCENT, font=("Helvetica", 14, "bold"))
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
            self._bg_image_id = self._canvas.create_image(w // 2, h // 2, image=assets.splash_bg, anchor="center")
            self._canvas.tag_lower(self._bg_image_id)

        self._current_step += 1
        pct = (self._current_step / assets.total_steps) * 100
        self._progress_var.set(pct)
        self._canvas.itemconfig(self._percent_label_id, text=f"{int(pct)}%")
        self.after(200, self._load_next_step)

    def _continue(self, event=None) -> None:
        self._canvas.unbind("<Button-1>")
        self.app.unbind("<Key>")
        self.app.transition_to(MAIN_WINDOW)


class MenuTemplateScreen(BaseScreen):
    """Reusable base screen for all menu and mode selection screens."""

    def __init__(self, parent: tk.Frame, app: App, title: str = "", subtitle: str = "") -> None:
        super().__init__(parent, app)
        self.title_text = title
        self.subtitle_text = subtitle
        self.configure(bg=COLOR_FRAME_BG)

        self._canvas = tk.Canvas(self, highlightthickness=0, bg=COLOR_FRAME_BG)
        self._canvas.pack(fill="both", expand=True)
        self._bg_image_id: int | None = None

        self._title_id = self._canvas.create_text(0, 0, text=self.title_text, anchor="n", font=FONT_TITLE, fill=COLOR_CHALK, tags="title")
        self._subtitle_id = self._canvas.create_text(0, 0, text=self.subtitle_text, anchor="n", font=FONT_SUBTITLE, fill=COLOR_ACCENT, tags="subtitle")

        self._menu_frame = tk.Frame(self._canvas, bg=COLOR_FRAME_BG, bd=0)
        self._menu_window_id = self._canvas.create_window(0, 0, window=self._menu_frame, anchor="nw", tags="menu_window")

        self._board_size = 320
        self._board_cx = 0
        self._board_cy = 0
        self._anim_timer: str | None = None
        self._anim_step = 0
        self._current_marks: list[tuple[int, int, str]] = []
        self._active = False

        self._ambient_sequence: list[tuple[int, int, str]] = [
            (1, 1, "X"), (0, 0, "O"), (0, 2, "X"), (2, 0, "O"),
            (2, 2, "X"), (1, 2, "O"), (2, 1, "X"), (1, 0, "O"), (0, 1, "X"),
        ]

        self._canvas.bind("<Configure>", self._on_resize)
        self.bind("<Destroy>", lambda e: self.stop_ambient_loop())

    def add_menu_button(self, text: str, command: callable, accent: bool = False, pady: int = 9, ipady: int = 12) -> tk.Button:
        btn_bg = COLOR_BTN_BG
        btn_fg = COLOR_ACCENT if accent else COLOR_BTN_FG
        btn = tk.Button(
            self._menu_frame, text=text, font=FONT_MENU_BTN, bg=btn_bg, fg=btn_fg,
            activebackground=COLOR_BTN_HOVER_BG, activeforeground=COLOR_BTN_HOVER_FG,
            bd=0, relief="flat", highlightthickness=1, highlightbackground="#42291A",
            highlightcolor=COLOR_ACCENT, cursor="hand2", command=command, wraplength=440, justify="center",
        )
        btn.pack(fill="x", pady=pady, ipady=ipady, padx=8)
        btn.bind("<Enter>", lambda e: btn.configure(bg=COLOR_BTN_HOVER_BG, fg=COLOR_BTN_HOVER_FG))
        btn.bind("<Leave>", lambda e: btn.configure(bg=btn_bg, fg=btn_fg))
        return btn

    def _ensure_menu_bg(self) -> None:
        assets = self.app.assets
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1024
        h = self.winfo_height() or self.app.winfo_screenheight() or 768
        if assets.menu_bg is None and os.path.isfile(_MENU_BG_PATH):
            assets._load_menu_bg(w, h)
        if assets.menu_bg and self._bg_image_id is None:
            self._bg_image_id = self._canvas.create_image(w // 2, h // 2, image=assets.menu_bg, anchor="center", tags="menu_bg")
            self._canvas.tag_lower(self._bg_image_id)

    def _on_resize(self, event) -> None:
        w, h = event.width, event.height
        if w < 100 or h < 100:
            return
        cx, layout = w // 2, compute_layout(w, h)
        if self._bg_image_id and self.app.assets.menu_bg:
            self._canvas.coords(self._bg_image_id, cx, h // 2)

        self._canvas.coords("title", cx, layout["title_y"])
        if self.subtitle_text:
            self._canvas.coords("subtitle", cx, layout["subtitle_y"])
        else:
            self._canvas.coords("subtitle", -1000, -1000)

        self._menu_frame.configure(width=layout["menu_width"])
        self._canvas.coords("menu_window", layout["menu_x"], layout["menu_y"])

        self._board_size = layout["ambient_size"]
        self._board_cx = layout["ambient_cx"]
        self._board_cy = layout["ambient_cy"]
        self._draw_ambient_board()

    def set_subtitle(self, text: str) -> None:
        self.subtitle_text = text
        self._canvas.itemconfig(self._subtitle_id, text=text)
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1024
        h = self.winfo_height() or self.app.winfo_screenheight() or 768
        layout = compute_layout(w, h)
        self._canvas.coords("subtitle", w // 2, layout["subtitle_y"]) if text else self._canvas.coords("subtitle", -1000, -1000)

    def _draw_ambient_board(self) -> None:
        _draw_chalk_grid(self._canvas, self._board_cx, self._board_cy, self._board_size, "ambient_grid")
        self._canvas.delete("ambient_mark")
        for row, col, symbol in self._current_marks:
            self._draw_mark(row, col, symbol)

    def _draw_mark(self, row: int, col: int, symbol: str) -> None:
        _draw_chalk_mark(self._canvas, self._board_cx, self._board_cy, self._board_size, row, col, symbol, "ambient_mark")

    def _step_ambient_animation(self) -> None:
        if not self._active:
            return
        if self._anim_step < len(self._ambient_sequence):
            row, col, symbol = self._ambient_sequence[self._anim_step]
            self._current_marks.append((row, col, symbol))
            self._draw_mark(row, col, symbol)
            self._anim_step += 1
            self._anim_timer = self.after(650, self._step_ambient_animation)
        else:
            self._anim_step = 0
            self._current_marks.clear()
            self._anim_timer = self.after(1400, self._reset_and_restart_ambient)

    def _reset_and_restart_ambient(self) -> None:
        if not self._active:
            return
        self._canvas.delete("ambient_mark")
        self._anim_timer = self.after(400, self._step_ambient_animation)

    def start_ambient_loop(self) -> None:
        self.stop_ambient_loop()
        self._active = True
        self._anim_timer = self.after(400, self._step_ambient_animation)

    def stop_ambient_loop(self) -> None:
        self._active = False
        if self._anim_timer is not None:
            try:
                self.after_cancel(self._anim_timer)
            except Exception:
                pass
            self._anim_timer = None

    def on_show(self, **kwargs) -> None:
        self._active = True
        self._ensure_menu_bg()
        self.start_ambient_loop()

    def on_hide(self) -> None:
        self.stop_ambient_loop()


class MainWindowScreen(MenuTemplateScreen):
    """Main Window screen (top-level menu)."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="TIC-TAC-TOE", subtitle="Main Window")
        self.add_menu_button("Main Menu", lambda: self.app.transition_to(MAIN_MENU))
        self.add_menu_button("Settings", lambda: self.app.transition_to(SETTINGS))
        self.add_menu_button("Exit", self.app.destroy, accent=True)


class MainMenuScreen(MenuTemplateScreen):
    """Main Menu screen with direct game mode and navigation choices."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="MAIN MENU")
        buttons = [
            ("Human vs Heuristic", lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_HEURISTIC), False),
            ("Human vs Reinforcement Learning", lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_QLEARNING), False),
            ("Heuristic Function vs Reinforcement Learning", lambda: self.app.transition_to(GAME, mode=MODE_AI_VS_AI), False),
            ("Train Q-Learning", lambda: self.app.transition_to(COMING_SOON, return_to=MAIN_MENU, feature="Train Q-Learning"), False),
            ("Evaluation", lambda: self.app.transition_to(COMING_SOON, return_to=MAIN_MENU, feature="Evaluation"), False),
            ("← Back", lambda: self.app.transition_to(MAIN_WINDOW), True),
        ]
        for text, cmd, accent in buttons:
            self.add_menu_button(text, cmd, accent=accent, pady=6, ipady=9)


class PlayGameScreen(MenuTemplateScreen):
    """Play Game mode selection screen with all game modes on a single page."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="PLAY GAME")
        self.add_menu_button("Human vs Heuristic", lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_HEURISTIC))
        self.add_menu_button("Human vs Reinforcement Learning", lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_QLEARNING))
        self.add_menu_button("Heuristic Function vs Reinforcement Learning", lambda: self.app.transition_to(GAME, mode=MODE_AI_VS_AI))
        self.add_menu_button("← Back", lambda: self.app.transition_to(MAIN_MENU), accent=True)


class SinglePlayerScreen(MenuTemplateScreen):
    """Single Player opponent selection screen (Legacy redirect to PlayGameScreen)."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="PLAY GAME")
        self.add_menu_button("Human vs Heuristic", lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_HEURISTIC))
        self.add_menu_button("Human vs Reinforcement Learning", lambda: self.app.transition_to(GAME, mode=MODE_HUMAN_VS_QLEARNING))
        self.add_menu_button("Heuristic Function vs Reinforcement Learning", lambda: self.app.transition_to(GAME, mode=MODE_AI_VS_AI))
        self.add_menu_button("← Back", lambda: self.app.transition_to(MAIN_MENU), accent=True)


class AIVsAIScreen(MenuTemplateScreen):
    """AI vs AI visual selection screen."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="AI VS AI")
        self.add_menu_button("Heuristic Function vs Reinforcement Learning", lambda: self.app.transition_to(GAME, mode=MODE_AI_VS_AI))
        self.add_menu_button("← Back", lambda: self.app.transition_to(MAIN_MENU), accent=True)


class SettingsScreen(MenuTemplateScreen):
    """Settings screen placeholder."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="SETTINGS", subtitle=MSG_SETTINGS)
        self._msg_label = tk.Label(self._menu_frame, text=MSG_SETTINGS, font=FONT_BODY, bg=COLOR_FRAME_BG, fg=COLOR_CHALK_DIM, wraplength=260, justify="center")
        self._msg_label.pack(pady=(14, 20), padx=8)
        self.add_menu_button("← Back", lambda: self.app.transition_to(MAIN_WINDOW), accent=True)

    def on_show(self, **kwargs) -> None:
        super().on_show(**kwargs)
        self.set_subtitle(MSG_SETTINGS)


class ComingSoonScreen(MenuTemplateScreen):
    """Reusable 'Coming Soon' placeholder screen."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app, title="COMING SOON", subtitle=MSG_COMING_SOON)
        self._return_screen = MAIN_MENU
        self._msg_label = tk.Label(self._menu_frame, text=MSG_COMING_SOON, font=FONT_BODY, bg=COLOR_FRAME_BG, fg=COLOR_CHALK_DIM, wraplength=260, justify="center")
        self._msg_label.pack(pady=(14, 20), padx=8)
        self.add_menu_button("← Back", self._on_back, accent=True)

    def on_show(self, return_to: str = MAIN_MENU, feature: str | None = None, **kwargs) -> None:
        super().on_show(**kwargs)
        self._return_screen = return_to
        msg = f"{feature}\n\n{MSG_COMING_SOON}" if feature else MSG_COMING_SOON
        sub = f"{feature} — {MSG_COMING_SOON}" if feature else MSG_COMING_SOON
        self.set_subtitle(sub)
        self._msg_label.configure(text=msg)

    def _on_back(self) -> None:
        self.app.transition_to(self._return_screen)


class GameScreen(BaseScreen):
    """Interactive gameplay screen with centered 3x3 chalk board and pre-game setup."""

    def __init__(self, parent: tk.Frame, app: App) -> None:
        super().__init__(parent, app)
        self.configure(bg="#0F0F0F")
        self._canvas = tk.Canvas(self, highlightthickness=0, bg="#0F0F0F")
        self._canvas.pack(fill="both", expand=True)
        self._bg_image_id: int | None = None

        self.current_mode = MODE_HUMAN_VS_HEURISTIC
        self._players: list[PlayerInfo] = []
        self._current_player_idx = 0
        self._toss_winner_idx: int | None = None
        self._move_count = 0
        self._cells: list[str | None] = [None] * 9
        self._game_active = False
        self._game_over = False

        self._board_size = 400
        self._board_cx = 0
        self._board_cy = 0

        self._canvas.create_text(35, 28, text="", anchor="nw", font=FONT_SMALL, fill=COLOR_TEXT_MUTED, tags="mode_label")
        self._canvas.create_text(0, 30, text="", anchor="n", font=FONT_TITLE, fill=COLOR_ACCENT, tags="turn_indicator")
        self._canvas.create_text(0, 0, text="", anchor="w", font=FONT_BODY, fill=COLOR_CHALK, tags="player1_label")
        self._canvas.create_text(0, 0, text="", anchor="e", font=FONT_BODY, fill=COLOR_CHALK, tags="player2_label")
        self._canvas.create_text(0, 0, text="", anchor="n", font=FONT_SUBTITLE, fill=COLOR_CHALK_DIM, tags="board_hint")

        self._home_btn = tk.Button(
            self._canvas, text="🏠 Home", font=FONT_SMALL, bg=COLOR_BTN_BG, fg=COLOR_BTN_FG,
            activebackground=COLOR_BTN_HOVER_BG, activeforeground=COLOR_BTN_HOVER_FG,
            bd=0, relief="flat", highlightthickness=1, highlightbackground="#3A281E",
            cursor="hand2", command=lambda: self.app.transition_to(MAIN_WINDOW),
        )
        self._home_window = self._canvas.create_window(0, 0, window=self._home_btn, anchor="ne", tags="home_btn")

        self._overlay_frame = tk.Frame(self._canvas, bg="#1E140F", bd=2, relief="solid", highlightthickness=2, highlightbackground=COLOR_ACCENT)
        self._overlay_window: int | None = None

        self._canvas.bind("<Configure>", self._on_resize)
        self._canvas.bind("<Button-1>", self._on_canvas_click)

    def on_show(self, mode: str = MODE_HUMAN_VS_HEURISTIC, **kwargs) -> None:
        self.current_mode = mode
        self._ensure_game_bg()
        self._play_swift_transition()
        self.setup_game(mode)

    def _play_swift_transition(self) -> None:
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1920
        h = self.winfo_height() or self.app.winfo_screenheight() or 1080
        flash = self._canvas.create_rectangle(0, 0, w, h, fill="#050302", tags="flash_overlay")
        self.after(90, lambda: self._canvas.delete("flash_overlay"))

    def _ensure_game_bg(self) -> None:
        assets = self.app.assets
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1024
        h = self.winfo_height() or self.app.winfo_screenheight() or 768
        if assets.game_bg is None and os.path.isfile(_GAME_BG_PATH):
            assets._load_game_bg(w, h)
        if assets.game_bg and self._bg_image_id is None:
            self._bg_image_id = self._canvas.create_image(w // 2, h // 2, image=assets.game_bg, anchor="center", tags="game_bg")
            self._canvas.tag_lower(self._bg_image_id)

    def setup_game(self, mode: str) -> None:
        self.current_mode = mode
        self._cells = [None] * 9
        self._move_count = 0
        self._game_active = False
        self._game_over = False
        self._toss_winner_idx = None

        mode_map = {
            MODE_HUMAN_VS_HUMAN: (("Player 1", PLAYER_HUMAN), ("Player 2", PLAYER_HUMAN), "Mode: 2-Player (Human vs Human)"),
            MODE_HUMAN_VS_HEURISTIC: (("Player (Human)", PLAYER_HUMAN), ("AI (Heuristic)", PLAYER_HEURISTIC_AI), "Mode: Human vs Heuristic AI"),
            MODE_HUMAN_VS_QLEARNING: (("Player (Human)", PLAYER_HUMAN), ("AI (Reinforcement Learning)", PLAYER_QLEARNING_AI), "Mode: Human vs Reinforcement Learning AI"),
            MODE_AI_VS_AI: (("AI 1 (Heuristic Function)", PLAYER_HEURISTIC_AI), ("AI 2 (Reinforcement Learning)", PLAYER_QLEARNING_AI), "Mode: Heuristic Function vs Reinforcement Learning AI"),
        }
        p1_cfg, p2_cfg, mode_desc = mode_map.get(mode, mode_map[MODE_HUMAN_VS_HEURISTIC])
        self._players = [PlayerInfo(*p1_cfg), PlayerInfo(*p2_cfg)]

        self._canvas.itemconfig("mode_label", text=mode_desc)
        self._canvas.itemconfig("turn_indicator", text="Pre-Game Toss", fill=COLOR_CHALK_DIM)
        self._canvas.itemconfig("board_hint", text="Complete pre-game toss to begin.")
        self._draw_board()
        self._show_toss_overlay()

    def _clear_overlay(self) -> None:
        for child in self._overlay_frame.winfo_children():
            child.destroy()

    def _make_overlay_btn(self, parent, text: str, cmd: callable, fg: str = COLOR_ACCENT, **pack_opts) -> tk.Button:
        btn = tk.Button(
            parent, text=text, font=FONT_MENU_BTN, bg=COLOR_BTN_BG, fg=fg,
            activebackground=COLOR_BTN_HOVER_BG, activeforeground=COLOR_BTN_HOVER_FG,
            bd=0, relief="flat", highlightthickness=1, highlightbackground="#4A3225",
            cursor="hand2", command=cmd,
        )
        btn.pack(**pack_opts)
        return btn

    def _show_toss_overlay(self) -> None:
        self._clear_overlay()
        p1, p2 = self._players
        tk.Label(self._overlay_frame, text="PRE-GAME SETUP", font=("Helvetica", 18, "bold"), bg="#1E140F", fg=COLOR_CHALK).pack(pady=(16, 4), padx=28)
        tk.Label(self._overlay_frame, text=f"Match: {p1.label} vs {p2.label}", font=FONT_SUBTITLE, bg="#1E140F", fg=COLOR_ACCENT).pack(pady=(0, 14))
        tk.Label(self._overlay_frame, text="Step 1: Toss a coin to determine who plays first.\nToss winner always makes the opening move.", font=FONT_BODY, bg="#1E140F", fg=COLOR_CHALK_DIM, justify="center").pack(pady=(0, 18), padx=20)
        self._make_overlay_btn(self._overlay_frame, "🪙 Flip Coin", self._execute_toss, pady=(0, 16), ipady=8, ipadx=24)
        self._display_overlay()

    def _execute_toss(self) -> None:
        self._toss_winner_idx = random.choice([0, 1])
        winner, other = self._players[self._toss_winner_idx], self._players[1 - self._toss_winner_idx]
        winner.is_starter, other.is_starter = True, False

        self._clear_overlay()
        tk.Label(self._overlay_frame, text="COIN TOSS IN PROGRESS", font=("Helvetica", 18, "bold"), bg="#1E140F", fg=COLOR_ACCENT).pack(pady=(16, 4), padx=28)
        status_lbl = tk.Label(self._overlay_frame, text="Flipping coin to determine starter...", font=FONT_SUBTITLE, bg="#1E140F", fg=COLOR_CHALK_DIM)
        status_lbl.pack(pady=(0, 10))

        coin_cv = tk.Canvas(self._overlay_frame, width=160, height=130, bg="#1E140F", highlightthickness=0)
        coin_cv.pack(pady=(0, 14))

        def _animate_flip(frame: int = 0) -> None:
            if not self.winfo_ismapped():
                return
            coin_cv.delete("all")
            ry = max(4, int(44 * abs(math.cos(frame * 0.35))))
            coin_cv.create_oval(36, 65 - ry, 124, 65 + ry, fill="#E5C158" if (frame // 4) % 2 == 0 else "#C59B63", outline="#8A6233", width=3)
            if frame < 20:
                self.after(35, lambda: _animate_flip(frame + 1))
            else:
                coin_cv.delete("all")
                coin_cv.create_oval(36, 21, 124, 109, fill="#F2D06B", outline="#8A6233", width=4)
                coin_cv.create_text(80, 65, text="★", fill="#42291A", font=("Helvetica", 22, "bold"))
                status_lbl.configure(text="✨ Landed! Announcing winner...", fg=COLOR_ACCENT)
                self.after(500, lambda: self._show_toss_winner_result(winner, other))

        _animate_flip(0)

    def _show_toss_winner_result(self, winner: PlayerInfo, other: PlayerInfo) -> None:
        self._clear_overlay()
        tk.Label(self._overlay_frame, text="TOSS RESULT", font=("Helvetica", 18, "bold"), bg="#1E140F", fg=COLOR_ACCENT).pack(pady=(16, 6), padx=28)

        human_can_choose = (self.current_mode == MODE_HUMAN_VS_HUMAN) or (winner.type == PLAYER_HUMAN)

        if human_can_choose:
            tk.Label(self._overlay_frame, text=f"🎉 {winner.label} won the toss!\n\nToss winner plays first. Choose your symbol:", font=FONT_BODY, bg="#1E140F", fg=COLOR_CHALK, justify="center").pack(pady=(0, 18), padx=20)
            btn_box = tk.Frame(self._overlay_frame, bg="#1E140F")
            btn_box.pack(pady=(0, 18))
            self._make_overlay_btn(btn_box, "Play as X", lambda: self._on_symbol_chosen("X"), fg=COLOR_CHALK, side="left", padx=12, ipady=10, ipadx=22)
            self._make_overlay_btn(btn_box, "Play as O", lambda: self._on_symbol_chosen("O"), fg=COLOR_CHALK, side="left", padx=12, ipady=10, ipadx=22)
        else:
            winner.symbol, other.symbol = "X", "O"
            tk.Label(self._overlay_frame, text=f"{winner.label} won the toss and plays first!\n\n(AI won toss — Auto-assigned: {winner.label} = 'X', {other.label} = 'O')", font=FONT_BODY, bg="#1E140F", fg=COLOR_CHALK, justify="center").pack(pady=(0, 18), padx=20)
            self._make_overlay_btn(self._overlay_frame, "Start Game →", self._start_gameplay, pady=(0, 18), ipady=10, ipadx=28)

    def _on_symbol_chosen(self, chosen: str) -> None:
        winner = self._players[self._toss_winner_idx]
        other = self._players[1 - self._toss_winner_idx]
        winner.symbol = chosen
        other.symbol = "O" if chosen == "X" else "X"

        self._clear_overlay()
        tk.Label(self._overlay_frame, text="SYMBOLS ASSIGNED", font=("Helvetica", 18, "bold"), bg="#1E140F", fg=COLOR_ACCENT).pack(pady=(16, 6), padx=28)
        tk.Label(self._overlay_frame, text=f"{winner.label}: '{winner.symbol}' (First Move)\n{other.label}: '{other.symbol}'\n\nReady to play!", font=FONT_BODY, bg="#1E140F", fg=COLOR_CHALK, justify="center").pack(pady=(0, 20), padx=24)
        self._make_overlay_btn(self._overlay_frame, "Start Game →", self._start_gameplay, pady=(0, 18), ipady=8, ipadx=24)

    def _start_gameplay(self) -> None:
        self._dismiss_overlay()
        self._current_player_idx = self._toss_winner_idx
        self._game_active = True
        self._game_over = False
        self._canvas.itemconfig("board_hint", text="Click an empty cell on the chalk board to place your mark.")
        self._update_header()

    def _display_overlay(self) -> None:
        w = self.winfo_width() or self.app.winfo_screenwidth() or 1024
        h = self.winfo_height() or self.app.winfo_screenheight() or 768
        cx, cy = w // 2, h // 2
        if self._overlay_window is None:
            self._overlay_window = self._canvas.create_window(cx, cy, window=self._overlay_frame, anchor="center", tags="overlay")
        else:
            self._canvas.coords(self._overlay_window, cx, cy)
            self._canvas.itemconfig(self._overlay_window, state="normal")

    def _dismiss_overlay(self) -> None:
        if self._overlay_window is not None:
            self._canvas.itemconfig(self._overlay_window, state="hidden")

    def _on_canvas_click(self, event) -> None:
        if not self._game_active or self._game_over:
            return

        origin_x = self._board_cx - self._board_size // 2
        origin_y = self._board_cy - self._board_size // 2
        cell = self._board_size // 3

        col = (event.x - origin_x) // cell
        row = (event.y - origin_y) // cell

        if 0 <= row < 3 and 0 <= col < 3:
            idx = row * 3 + col
            if self._cells[idx] is not None:
                return

            current_player = self._players[self._current_player_idx]
            self._cells[idx] = current_player.symbol
            self._move_count += 1
            self._draw_mark(row, col, current_player.symbol)

            # ponytail: dummy gameplay rules end after 9 moves as Draw; upgrade to full GameEngine win evaluation when backend is integrated.
            if self._move_count >= 9:
                self._game_over = True
                self._game_active = False
                self._update_header()
                self._canvas.itemconfig("board_hint", text="Game ended in Draw. Choose Retry or Home.")
                self._show_post_game_overlay()
            else:
                self._current_player_idx = 1 - self._current_player_idx
                self._update_header()

    def _show_post_game_overlay(self) -> None:
        self._clear_overlay()
        tk.Label(self._overlay_frame, text="GAME OVER", font=("Helvetica", 20, "bold"), bg="#1E140F", fg=COLOR_ACCENT).pack(pady=(16, 4), padx=32)
        tk.Label(self._overlay_frame, text="Result: DRAW", font=("Helvetica", 18, "bold"), bg="#1E140F", fg=COLOR_CHALK).pack(pady=(0, 8))
        tk.Label(self._overlay_frame, text="All 9 moves played without a winner (dummy rules).", font=FONT_BODY, bg="#1E140F", fg=COLOR_CHALK_DIM, justify="center").pack(pady=(0, 18), padx=20)

        btn_box = tk.Frame(self._overlay_frame, bg="#1E140F")
        btn_box.pack(pady=(0, 18))
        self._make_overlay_btn(btn_box, "🔄 Retry", lambda: self.setup_game(self.current_mode), fg=COLOR_ACCENT, side="left", padx=12, ipady=10, ipadx=24)
        self._make_overlay_btn(btn_box, "🏠 Home", lambda: self.app.transition_to(MAIN_WINDOW), fg=COLOR_CHALK, side="left", padx=12, ipady=10, ipadx=24)
        self._display_overlay()

    def _draw_board(self) -> None:
        _draw_chalk_grid(self._canvas, self._board_cx, self._board_cy, self._board_size, "game_grid")
        self._canvas.delete("game_mark")
        for idx, mark in enumerate(self._cells):
            if mark is not None:
                self._draw_mark(idx // 3, idx % 3, mark)

    def _draw_mark(self, row: int, col: int, symbol: str) -> None:
        _draw_chalk_mark(self._canvas, self._board_cx, self._board_cy, self._board_size, row, col, symbol, "game_mark")

    def _on_resize(self, event) -> None:
        w, h = event.width, event.height
        if w < 100 or h < 100:
            return
        cx, layout = w // 2, compute_layout(w, h)
        if self._bg_image_id and self.app.assets.game_bg:
            self._canvas.coords(self._bg_image_id, cx, h // 2)

        self._board_size, self._board_cx, self._board_cy = layout["game_size"], layout["game_cx"], layout["game_cy"]
        self._canvas.coords("turn_indicator", cx, layout["title_y"])

        board_top = self._board_cy - self._board_size // 2
        self._canvas.coords("player1_label", cx - self._board_size // 2, board_top - 16)
        self._canvas.coords("player2_label", cx + self._board_size // 2, board_top - 16)
        self._canvas.coords("board_hint", cx, self._board_cy + self._board_size // 2 + 20)
        self._canvas.coords("home_btn", w - 24, 24)

        if self._overlay_window is not None:
            self._canvas.coords(self._overlay_window, cx, h // 2)

        self._draw_board()
        self._update_header()

    def _update_header(self) -> None:
        if not self._players:
            return
        p1, p2 = self._players
        if self._game_over:
            turn_str, turn_color = "Game Over — Draw!", COLOR_ACCENT
        elif self._game_active:
            curr = self._players[self._current_player_idx]
            turn_str, turn_color = f"Turn {self._move_count + 1}/9: {curr.label} ({curr.symbol})", COLOR_ACCENT
        else:
            turn_str, turn_color = "Pre-Game Setup", COLOR_CHALK_DIM

        self._canvas.itemconfig("turn_indicator", text=turn_str, fill=turn_color)
        p1_sym = f"[{p1.symbol}]" if p1.symbol else ""
        p2_sym = f"[{p2.symbol}]" if p2.symbol else ""
        self._canvas.itemconfig("player1_label", text=f"Player 1: {p1.label} {p1_sym}",
                                fill=COLOR_ACCENT if (self._game_active and self._current_player_idx == 0) else COLOR_CHALK)
        self._canvas.itemconfig("player2_label", text=f"Player 2: {p2.label} {p2_sym}",
                                fill=COLOR_ACCENT if (self._game_active and self._current_player_idx == 1) else COLOR_CHALK)


def main() -> None:
    """Launch the Tic-Tac-Toe GUI application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
