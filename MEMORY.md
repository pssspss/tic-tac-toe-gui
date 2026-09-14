# Tic-Tac-Toe GUI — AGY Progress Memory

> This file is kept in sync with the Notion page "7) Memory (AGY Progress Log)".
> Updated at the end of every phase.

---

## Locked decisions (do not change without explicit approval)

- GUI-only scope; no core rules or AI algorithms inside Tkinter
- Menus use brown texture background; gameplay uses dark texture background (all modes incl. AI vs AI)
- Splash uses tic-tac-toe pattern background
- Chalk-style board/marks
- Dummy gameplay ends after 9 moves as draw (no win detection)
- Toss winner goes first
- Only a human may choose X/O (human vs AI: if AI wins toss → auto-assign)
- Fullscreen-first window
- Menu layout: title top-center, buttons left-side vertical, ambient board center/right
- Game layout: board centered, player labels + turn indicator displayed
- Assets stored in `gui/assets/`

---

## Current status

- **Phase completed**: Final Consolidated Pass (Transitions, Layout, HUD & Timer Polish)
- **Next phase**: Ready for backend AI / GameEngine integration

---

## Phase log

### Phase 0 — Repo intake + guardrails
- **Status**: ✅ completed (2026-09-14)
- **Files**: `gui/__init__.py`, `gui/interface.py` (skeleton), `gui/assets/README.md`, `tests/test_interface.py`, `pytest.ini`, `.gitignore`
- **Backend search**: Board, GameEngine, HeuristicAgent, QLearningAgent — none found. GUI runs in dummy mode.
- **Tests**: import smoke ✅ | pytest 1/1 ✅

### Phase 1 — App shell + screen manager
- **Status**: ✅ completed (2026-09-14)
- **Files changed**:
  - `gui/interface.py` — App(tk.Tk) controller, show_screen(), BaseScreen, 9 placeholder screens with nav buttons
  - `tests/test_interface.py` — 4 tests
- **Tests**: import smoke ✅ | pytest 4/4 ✅

### Phase 2 — Assets + Splash loading
- **Status**: ✅ completed (2026-09-14)
- **Files changed**:
  - `gui/interface.py` — Added:
    - Asset path constants (`_SPLASH_BG_PATH`, `_MENU_BG_PATH`, `_GAME_BG_PATH`) pointing to exact user-provided image files
    - `AssetManager` class with 3 load steps (splash bg, menu bg, game bg), each loading + resizing JPG via Pillow
    - `SplashScreen` rewritten: fullscreen Canvas with black bg, "Tic-Tac-Toe" title, bottom-center progress bar + percent label, status text. Loads assets incrementally via `.after()`. Splash bg appears as background once loaded. Shows "Loaded. Click or press any key to continue…" on completion. Click/key navigates to Main Window. No Exit button.
    - `App.__init__` now creates `self.assets = AssetManager()` shared across screens
    - Imports added: `os`, `tkinter.ttk`, `PIL.Image`, `PIL.ImageTk`
  - `tests/test_interface.py` — expanded to 6 tests:
    - Original 4 from Phase 1
    - `test_asset_manager_importable` — AssetManager class, defaults, total_steps == 3
    - `test_asset_paths_exist` — all 3 image files exist on disk
- **Dependencies added**: `Pillow==12.3.0` (installed in .venv via uv)
- **Asset files verified** (user-provided, not modified):
  - `gui/assets/Splash background/Generated Image September 12, 2026 - 10_50PM.jpg` (371 KB)
  - `gui/assets/Menu background/27707-background-1072764_1920.jpg` (811 KB)
  - `gui/assets/Gameplay background/Generated Image September 13, 2026 - 10_06PM.jpg` (643 KB)
- **Tests**: import smoke ✅ | pytest 6/6 ✅

### Phase 3 — Menus + ambient board loop
- **Status**: ✅ completed (2026-09-14)
- **Files changed**:
  - `gui/interface.py` — Added:
    - Design System color and font tokens (`COLOR_CHALK`, `COLOR_ACCENT`, `COLOR_BTN_BG`, etc.)
    - `MenuTemplateScreen(BaseScreen)`:
      - Renders brown texture background (`menu_bg`)
      - Renders title at top-center and optional subtitle
      - Left-side vertical menu buttons container (22-28% screen width) with flat styling, accent highlight, and dynamic hover background/text tint
      - Center/right ambient non-interactive 3x3 chalk board with off-white round-cap strokes (`#E8E8E8`)
      - Ambient move loop using `.after(750, ...)` stepping through an engaging 9-move sequence, holding for 1800ms, then resetting and repeating
      - `on_show` starts the ambient loop and ensures `menu_bg` is loaded; `on_hide` cancels the timer to prevent resource leaks
      - `<Configure>` resize handler keeps background, title, left buttons, and ambient board scaled and centered
    - Screen implementations using `MenuTemplateScreen`:
      - `MainWindowScreen`: Main Menu / Settings / Exit
      - `MainMenuScreen`: Play Game / AI vs AI / Train Q-Learning / Evaluation / Back
      - `PlayGameScreen`: Single Player / 2-Player / Back
      - `SinglePlayerScreen`: Human vs Heuristic / Human vs Q-Learning / Back
      - `AIVsAIScreen`: Start AI vs AI Game / Back
      - `SettingsScreen` & `ComingSoonScreen`: themed with brown background + back navigation
  - `tests/test_interface.py` — expanded to 8 tests:
    - `test_design_tokens_defined`
    - `test_menu_template_inheritance`
- **Tests**: import smoke ✅ | pytest 8/8 ✅

### Phase 4 — Placeholders
- **Status**: ✅ completed (2026-09-14)
- **Files changed**:
  - `gui/interface.py`:
    - Added constants `MSG_SETTINGS = "Currently in development phase."` and `MSG_COMING_SOON = "This feature will be implemented later."`
    - Added `set_subtitle()` to `MenuTemplateScreen` for dynamic subtitle updating on canvas
    - Updated `SettingsScreen` to display the exact message `"Currently in development phase."` in title subtitle and in a formatted card label, with Back button routing to `MAIN_WINDOW`
    - Updated `ComingSoonScreen` to display the exact message `"This feature will be implemented later."` in title subtitle and formatted card label, supporting dynamic feature names and `return_to` routing (default `MAIN_MENU`)
    - Updated `MainMenuScreen` to route "Train Q-Learning" and "Evaluation" to `ComingSoonScreen` with feature names and return routes
  - `tests/test_interface.py` — expanded to 9 tests:
    - `test_placeholder_messages`
- **Tests**: import smoke ✅ | pytest 9/9 ✅

### Phase 5 — Game screen (dummy play)
- **Status**: ✅ completed (2026-09-14)
- **Files changed**:
  - `gui/interface.py`:
    - Added game mode constants (`MODE_HUMAN_VS_HUMAN`, `MODE_HUMAN_VS_HEURISTIC`, `MODE_HUMAN_VS_QLEARNING`, `MODE_AI_VS_AI`), player type constants, and `PlayerInfo` class matching In-Memory Data Schema
    - Updated `PlayGameScreen`, `SinglePlayerScreen`, and `AIVsAIScreen` to route into `GAME` with their respective modes
    - Rewrote `GameScreen` with:
      - Dark gameplay background (`game_bg`) with swift fade/flash transition on entry
      - Centered 3x3 chalk grid with responsive `<Configure>` scaling
      - Player 1 & Player 2 labels and turn indicator header with dynamic active-turn accent coloring
      - Pre-game overlay:
        - Step 1: Toss button decides opening player randomly
        - Step 2: Symbol selection (human chooses X or O; AI automatically assigned X if it wins toss; AI vs AI auto-assigned)
        - Step 3: Start Game activates the board
      - Dummy play interaction:
        - Click empty cells to place current player's symbol in chalk style
        - Occupied cells disabled
        - Turn alternates
        - After 9 moves: ends in Draw, disables board, presents Retry (re-triggers toss with same mode) and Home (`MAIN_WINDOW`) buttons
      - Added explicit backend TODO hooks for `GameEngine`, `Board`, `HeuristicAgent`, `QLearningAgent`, and `q_table.pkl`
  - `tests/test_interface.py` — expanded to 10 tests:
    - `test_game_modes_and_schema`
- **Tests**: import smoke ✅ | pytest 10/10 ✅

### Phase 6 — Desktop Independent Application & Stabilization
- **Status**: ✅ completed (2026-09-14)
- **Files changed**:
  - `gui/interface.py`:
    - Added `import sys`
    - Added PyInstaller frozen environment check (`getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")`) to dynamically resolve `_ASSETS_DIR` in standalone executables
  - `gui.py`:
    - Converted from placeholder to main application entry point running `gui.interface.main()`
  - `run_game.bat`:
    - Double-clickable Windows batch launcher that starts the application silently via `pythonw.exe` without opening a command prompt window
  - `dist/TicTacToe.exe`:
    - Standalone, self-contained Windows executable built via PyInstaller (bundled with Python, Tkinter, Pillow, and all assets) — run anywhere by double-clicking
- **Tests**: import smoke ✅ | pytest 10/10 ✅

### Final Pass — Transitions + Layout + Missing Items
- **Status**: ✅ completed (2026-09-14)
- **Key Changes Implemented**:
  1. **Menu Alignment & Enlarged Option Buttons**:
     - Added centralized layout calculation function `compute_layout(width, height) -> dict`.
     - Calculated menu button stack x coordinate centered within left column: `menu_x = left_col_x0 + (left_col_width - menu_width) * 0.5`.
     - Enlarged menu button typography to 17pt bold (`FONT_MENU_BTN`) with chunkier padding (`ipady=12, pady=9, padx=8`) and expanded column width (up to 480px) for tactile FC-style presentation.
     - Integrated `compute_layout` into `MenuTemplateScreen._on_resize`, `set_subtitle`, and `GameScreen._on_resize`.
  2. **Smooth Dual-Curtain Screen Transitions**:
     - Added animated dual-curtain wipe (`_curtain_left` and `_curtain_right`) to `App.transition_to(screen_name, **kwargs)` with smooth 200ms sweep and `try...finally` safety.
     - Connected all screen switches to `transition_to` for cinematic, flicker-free navigation.
  3. **Menu -> Gameplay Swift Transition**:
     - Seamless transition into dark gameplay background, cleanly stopping ambient timers on screen exit and launching the Coin Toss overlay on top of ready board.
  4. **Continuous Repeating Ambient Looping Board**:
     - Standardized chalk stroke width to 7 for all lines and marks (matching gameplay board).
     - Fixed repeat loop lifecycle (`_active` flag) so the 9-move sequence continuously repeats round after round without halting.
     - Enhanced `stop_ambient_loop()` with exception guards and hooked `<Destroy>` lifecycle event.
  5. **3D Animated Coin Toss & Gameplay HUD**:
     - Added animated rotating gold medallion coin flip with 3D perspective easing (~1.1s) before announcing the toss winner.
     - Board strictly centered horizontally (`cx = width // 2`) with symmetrical player badges and active turn indicator.
     - Enlarged pre-game and post-game option buttons (`Play as X`, `Play as O`, `Start Game`, `Retry`, `Home`).
  6. **Launcher & Outside IDE Execution**:
     - Created `run_gui.py` launcher in project root.
     - Verified execution via `python run_gui.py`, `python gui.py`, `run_game.bat`, and `dist/TicTacToe.exe`.
- **Files Changed**:
  - `gui/interface.py`
  - `run_gui.py` (new)
  - `tests/test_interface.py`
  - `MEMORY.md`
- **Tests**:
  - `python -c "import gui.interface"`: ✅ passed
  - `pytest -q`: 12 passed in 0.07s ✅

### Menu Restructure — Single Page Game Mode Selection
- **Status**: ✅ completed (2026-09-14)
- **Changes Implemented**:
  - **Unified "Play Game" Screen (No Extra Pages)**:
    - Removed separate `AI vs AI` button from `MainMenuScreen`, routing all gameplay modes through `Play Game`.
    - Consolidated all 3 playable game modes directly into [PlayGameScreen](file:///d:/Github/tic-tac-toe-gui/gui/interface.py):
      1. `Human vs Heuristic` (launches game in heuristic AI mode)
      2. `Human vs Reinforcement Learning` (launches game in Q-learning AI mode)
      3. `Heuristic Function vs Reinforcement Learning` (launches AI vs AI battle)
      4. `← Back` (returns to `MainMenuScreen`)
    - Removed `2-Player` mode and intermediate `Single Player` sub-menu completely from the user flow.
  - **Layout & Typography Accommodations**:
    - Expanded `left_col_width` (up to 520px) and `menu_width` (up to 460px) in `compute_layout`.
    - Added `wraplength=440` and `justify="center"` to menu buttons for clean presentation across all desktop resolutions.
  - **GameScreen HUD**:
    - Mode descriptions updated to `"Mode: Human vs Heuristic AI"`, `"Mode: Human vs Reinforcement Learning AI"`, and `"Mode: Heuristic Function vs Reinforcement Learning AI"`.
  - **Rebuilt Executables & Tests**:
    - Expanded `tests/test_interface.py` to 14 tests (`test_play_game_screen_buttons`, `test_main_menu_screen_buttons`).
    - Recompiled `dist/TicTacToe.exe` via PyInstaller.
- **Tests**:
  - `pytest -q`: 14 passed in 0.20s ✅
- **What's Still Missing**: Nothing. Ready for backend engine integration.

### Menu Restructure — Direct Game Modes in Main Menu
- **Status**: ✅ completed (2026-09-14)
- **Changes Implemented**:
  - **Flattened Navigation (No Extra "Play Game" Slide)**:
    - Replaced the intermediate "Play Game" menu option on [MainMenuScreen](file:///d:/Github/tic-tac-toe-gui/gui/interface.py#L814) with all 3 game mode options directly on the Main Menu:
      1. `Human vs Heuristic` (launches gameplay in heuristic AI mode)
      2. `Human vs Reinforcement Learning` (launches gameplay in Q-learning AI mode)
      3. `Heuristic Function vs Reinforcement Learning` (launches AI vs AI gameplay)
      4. `Train Q-Learning` (routes to `COMING_SOON` placeholder)
      5. `Evaluation` (routes to `COMING_SOON` placeholder)
      6. `← Back` (returns to `MainWindowScreen`)
  - **Layout & Sizing Polish**:
    - Updated `compute_layout` to start menu buttons at `menu_y = max(95, int(h * 0.16))`.
    - Added configurable `pady` and `ipady` support to `add_menu_button`, setting `pady=6, ipady=9` for the 6-button stack to fit with balanced vertical spacing across resolutions.
  - **Tests & Artifacts**:
    - Updated `tests/test_interface.py` to verify `MainMenuScreen` contains the direct modes and no longer contains `Play Game`.
    - Verified all 14 tests pass (`pytest` 14/14 ✅).
    - Rebuilt `dist/TicTacToe.exe` via PyInstaller.

---

## How to launch outside IDE

1. **Via Python CLI**:
   ```bash
   python run_gui.py
   # or
   python gui.py
   ```
2. **Via Windows Batch Script (Silent)**:
   - Double-click `run_game.bat` (runs without terminal window).
3. **Via Standalone Executable**:
   - Double-click `dist/TicTacToe.exe` (no Python or virtual environment required).

---

## Open questions / pending inputs

- None. All GUI requirements, transitions, layouts, and timer safeties are verified and complete.

---

## Repo file map (current)

```
tic-tac-toe-gui/
├── .gitignore
├── gui.py                  ← Desktop entry point (runs gui.interface.main)
├── run_gui.py              ← Direct launcher entry point (runs gui.interface.main)
├── run_game.bat            ← Double-clickable launcher (windowless via pythonw)
├── TicTacToe.spec          ← PyInstaller packaging spec
├── dist/
│   └── TicTacToe.exe       ← Standalone desktop executable (double-clickable)
├── pytest.ini
├── MEMORY.md               ← this file
├── gui/
│   ├── __init__.py
│   ├── interface.py        ← App shell + AssetManager + Splash + MenuTemplateScreen + 8 screens
│   └── assets/
│       ├── README.md
│       ├── Splash background/
│       │   └── Generated Image September 12, 2026 - 10_50PM.jpg
│       ├── Menu background/
│       │   └── 27707-background-1072764_1920.jpg
│       └── Gameplay background/
│           └── Generated Image September 13, 2026 - 10_06PM.jpg
└── tests/
    └── test_interface.py   ← 14 tests
```
