import sys
from unittest.mock import MagicMock, patch

# Provide a minimal tkinter stub so gui.py can be imported in headless
# environments where python3-tk is absent. Real tkinter takes priority.
if 'tkinter' not in sys.modules:
    _stub_tk = MagicMock()
    _stub_tk.DISABLED = 'disabled'
    _stub_tk.NORMAL = 'normal'
    sys.modules['tkinter'] = _stub_tk

import tkinter as tk  # noqa: E402

from tictactoe.engine import new_board  # noqa: E402
from tictactoe.gui import GameController, launch_game  # noqa: E402

_tk_module = sys.modules['tkinter']


def _make_controller():
    """Return (controller, mock_label, mock_buttons) with no real display."""
    mock_root = MagicMock()
    mock_label = MagicMock()
    mock_buttons = [MagicMock() for _ in range(9)]

    btn_iter = iter(mock_buttons)

    with patch.object(_tk_module, 'Label', return_value=mock_label), \
         patch.object(_tk_module, 'Button', side_effect=lambda *a, **kw: next(btn_iter)):
        controller = GameController(mock_root)

    return controller, mock_label, mock_buttons


# ---------------------------------------------------------------------------
# 1. Initial state
# ---------------------------------------------------------------------------

class TestInitialState:
    def test_current_player_is_x(self):
        controller, _, _ = _make_controller()
        assert controller.current_player == 'X'

    def test_board_is_empty(self):
        controller, _, _ = _make_controller()
        assert controller.board == new_board()

    def test_nine_buttons_exist(self):
        controller, _, _ = _make_controller()
        assert len(controller.buttons) == 9

    def test_all_buttons_not_disabled(self):
        controller, _, mock_buttons = _make_controller()
        for btn in mock_buttons:
            for c in btn.config.call_args_list:
                assert c.kwargs.get('state') != tk.DISABLED, \
                    "Button must not be disabled at initialisation"

    def test_status_label_shows_x_turn(self):
        controller, _, _ = _make_controller()
        assert 'Player X' in controller._status_text
        assert 'turn' in controller._status_text


# ---------------------------------------------------------------------------
# 2. Single valid click
# ---------------------------------------------------------------------------

class TestValidClick:
    def test_places_symbol_on_board(self):
        controller, _, _ = _make_controller()
        controller._on_click(4)
        assert controller.board[4] == 'X'

    def test_button_text_updated(self):
        controller, _, mock_buttons = _make_controller()
        controller._on_click(4)
        mock_buttons[4].config.assert_any_call(text='X', fg='blue')

    def test_player_switches_to_o(self):
        controller, _, _ = _make_controller()
        controller._on_click(4)
        assert controller.current_player == 'O'

    def test_second_click_places_o(self):
        controller, _, mock_buttons = _make_controller()
        controller._on_click(4)
        controller._on_click(0)
        assert controller.board[0] == 'O'
        mock_buttons[0].config.assert_any_call(text='O', fg='red')


# ---------------------------------------------------------------------------
# 3. Clicking an occupied square
# ---------------------------------------------------------------------------

class TestOccupiedSquare:
    def test_board_unchanged(self):
        controller, _, _ = _make_controller()
        controller._on_click(4)
        board_snapshot = list(controller.board)
        controller._on_click(4)
        assert controller.board == board_snapshot

    def test_player_unchanged(self):
        controller, _, _ = _make_controller()
        controller._on_click(4)
        controller._on_click(4)
        assert controller.current_player == 'O'


# ---------------------------------------------------------------------------
# 4. Win sequence: X fills top row (positions 0, 1, 2)
#    Moves: X@0, O@3, X@1, O@4, X@2 → X wins
# ---------------------------------------------------------------------------

class TestWin:
    _MOVES = [0, 3, 1, 4, 2]

    def _play(self, controller):
        for pos in self._MOVES:
            controller._on_click(pos)

    def test_all_buttons_disabled_after_win(self):
        controller, _, mock_buttons = _make_controller()
        self._play(controller)
        for btn in mock_buttons:
            btn.config.assert_any_call(state=tk.DISABLED)

    def test_status_contains_winner(self):
        controller, _, _ = _make_controller()
        self._play(controller)
        assert 'X' in controller._status_text

    def test_status_indicates_win(self):
        controller, _, _ = _make_controller()
        self._play(controller)
        assert 'win' in controller._status_text.lower()


# ---------------------------------------------------------------------------
# 5. Draw sequence (9 moves, no winner)
#    Board: X O X X O X O X O  (X@0,2,3,5,7 / O@1,4,6,8)
#    Move order: X@0,O@1,X@2,O@4,X@3,O@6,X@5,O@8,X@7
# ---------------------------------------------------------------------------

class TestDraw:
    _MOVES = [0, 1, 2, 4, 3, 6, 5, 8, 7]

    def _play(self, controller):
        for pos in self._MOVES:
            controller._on_click(pos)

    def test_all_buttons_disabled_after_draw(self):
        controller, _, mock_buttons = _make_controller()
        self._play(controller)
        for btn in mock_buttons:
            btn.config.assert_any_call(state=tk.DISABLED)

    def test_status_contains_draw(self):
        controller, _, _ = _make_controller()
        self._play(controller)
        assert 'draw' in controller._status_text.lower()
