"""Smoke tests for gui.interface."""
import importlib
import os


def test_gui_interface_import_safe():
    """Verify importing gui.interface succeeds without launching Tk or blocking."""
    mod = importlib.import_module("gui.interface")
    assert hasattr(mod, "main")


def test_app_class_exists():
    """Verify App class is importable."""
    from gui.interface import App
    assert App is not None


def test_screen_constants_defined():
    """Verify all screen name constants are defined."""
    from gui import interface
    expected = [
        "SPLASH", "MAIN_WINDOW", "MAIN_MENU", "PLAY_GAME",
        "SINGLE_PLAYER", "AI_VS_AI", "SETTINGS", "COMING_SOON", "GAME",
    ]
    for name in expected:
        assert hasattr(interface, name), f"Missing screen constant: {name}"


def test_screen_classes_defined():
    """Verify all screen Frame classes are importable."""
    from gui.interface import (
        SplashScreen, MainWindowScreen, MainMenuScreen,
        PlayGameScreen, SinglePlayerScreen, AIVsAIScreen,
        SettingsScreen, ComingSoonScreen, GameScreen,
    )
    classes = [
        SplashScreen, MainWindowScreen, MainMenuScreen,
        PlayGameScreen, SinglePlayerScreen, AIVsAIScreen,
        SettingsScreen, ComingSoonScreen, GameScreen,
    ]
    for cls in classes:
        assert cls is not None


def test_asset_manager_importable():
    """Verify AssetManager class is importable and has expected attributes."""
    from gui.interface import AssetManager
    am = AssetManager()
    assert am.splash_bg is None
    assert am.menu_bg is None
    assert am.game_bg is None
    assert am.total_steps == 3


def test_asset_paths_exist():
    """Verify all asset image files exist on disk."""
    from gui.interface import _SPLASH_BG_PATH, _MENU_BG_PATH, _GAME_BG_PATH
    assert os.path.isfile(_SPLASH_BG_PATH), f"Missing: {_SPLASH_BG_PATH}"
    assert os.path.isfile(_MENU_BG_PATH), f"Missing: {_MENU_BG_PATH}"
    assert os.path.isfile(_GAME_BG_PATH), f"Missing: {_GAME_BG_PATH}"


def test_design_tokens_defined():
    """Verify design system color and font tokens are defined (Phase 3)."""
    from gui import interface
    assert interface.COLOR_CHALK == "#E8E8E8"
    assert interface.COLOR_CHALK_DIM == "#BFBFBF"
    assert interface.COLOR_ACCENT == "#D4B07A"
    assert interface.COLOR_BTN_BG == "#2B1A11"
    assert interface.COLOR_BTN_HOVER_BG == "#4E3322"
    assert interface.FONT_TITLE[1] >= 24
    assert interface.FONT_MENU_BTN[1] >= 14


def test_menu_template_inheritance():
    """Verify MenuTemplateScreen and that menu screens inherit from it (Phase 3)."""
    from gui.interface import (
        BaseScreen, MenuTemplateScreen,
        MainWindowScreen, MainMenuScreen,
        PlayGameScreen, SinglePlayerScreen,
        AIVsAIScreen, SettingsScreen, ComingSoonScreen,
    )
    assert issubclass(MenuTemplateScreen, BaseScreen)
    menu_screens = [
        MainWindowScreen, MainMenuScreen,
        PlayGameScreen, SinglePlayerScreen,
        AIVsAIScreen, SettingsScreen, ComingSoonScreen,
    ]
    for cls in menu_screens:
        assert issubclass(cls, MenuTemplateScreen), f"{cls.__name__} does not inherit from MenuTemplateScreen"


def test_placeholder_messages():
    """Verify placeholder messages match exact Phase 4 specifications."""
    from gui.interface import MSG_SETTINGS, MSG_COMING_SOON
    assert MSG_SETTINGS == "Currently in development phase."
    assert MSG_COMING_SOON == "This feature will be implemented later."


def test_game_modes_and_schema():
    """Verify game mode constants and PlayerInfo class match specifications (Phase 5)."""
    from gui.interface import (
        MODE_HUMAN_VS_HUMAN, MODE_HUMAN_VS_HEURISTIC,
        MODE_HUMAN_VS_QLEARNING, MODE_AI_VS_AI,
        PLAYER_HUMAN, PLAYER_HEURISTIC_AI, PLAYER_QLEARNING_AI,
        PlayerInfo, GameScreen, BaseScreen,
    )
    assert MODE_HUMAN_VS_HUMAN == "human_vs_human"
    assert MODE_HUMAN_VS_HEURISTIC == "human_vs_heuristic"
    assert MODE_HUMAN_VS_QLEARNING == "human_vs_qlearning"
    assert MODE_AI_VS_AI == "ai_vs_ai"

    p = PlayerInfo("Test Player", PLAYER_HUMAN)
    assert p.label == "Test Player"
    assert p.type == PLAYER_HUMAN
    assert p.symbol is None
    assert p.is_starter is False

    assert issubclass(GameScreen, BaseScreen)


def test_compute_layout_geometry():
    """Verify compute_layout calculates centering and dimensions accurately."""
    from gui.interface import compute_layout

    for w, h in [(1920, 1080), (1366, 768), (1280, 720)]:
        layout = compute_layout(w, h)
        # Required formula: menu_x = left_col_x0 + (left_col_width - menu_width) * 0.5
        expected_menu_x = int(layout["left_col_x0"] + (layout["left_col_width"] - layout["menu_width"]) * 0.5)
        assert layout["menu_x"] == expected_menu_x
        assert layout["menu_x"] >= layout["left_col_x0"]
        assert layout["menu_x"] + layout["menu_width"] <= layout["left_col_x0"] + layout["left_col_width"]

        # Board centering: strictly centered horizontally
        assert layout["game_cx"] == w // 2
        assert layout["ambient_size"] > 0
        assert layout["game_size"] > 0
        assert layout["title_y"] > 0
        assert layout["subtitle_y"] > layout["title_y"]


def test_app_transition_method():
    """Verify App class has transition_to method for smooth screen switches."""
    from gui.interface import App
    assert hasattr(App, "transition_to")
    assert callable(getattr(App, "transition_to"))
