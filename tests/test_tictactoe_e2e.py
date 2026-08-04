"""End-to-end smoke test: drives complete game sequences through the GUI
controller and asserts that engine state and GUI state agree at game end.

Focused on cross-module integration only — unit-level mechanics are covered
by test_tictactoe_engine.py and test_tictactoe_gui.py.
"""
import sys
from unittest.mock import MagicMock, patch

if 'tkinter' not in sys.modules:
    _stub_tk = MagicMock()
    _stub_tk.DISABLED = 'disabled'
    _stub_tk.NORMAL = 'normal'
    sys.modules['tkinter'] = _stub_tk

import tkinter as tk  # noqa: E402

from tictactoe.engine import check_winner, is_draw  # noqa: E402
from tictactoe.gui import GameController  # noqa: E402

_tk_module = sys.modules['tkinter']


def _make_controller():
    mock_root = MagicMock()
    mock_label = MagicMock()
    mock_buttons = [MagicMock() for _ in range(9)]
    btn_iter = iter(mock_buttons)
    with patch.object(_tk_module, 'Label', return_value=mock_label), \
         patch.object(_tk_module, 'Button', side_effect=lambda *a, **kw: next(btn_iter)):
        controller = GameController(mock_root)
    return controller, mock_label, mock_buttons


class TestXWinsTopRow:
    """X wins via top row: X@0, O@3, X@1, O@4, X@2."""

    _MOVES = [0, 3, 1, 4, 2]

    def _play(self, controller):
        for pos in self._MOVES:
            controller._on_click(pos)

    def test_engine_reports_x_winner(self):
        controller, _, _ = _make_controller()
        self._play(controller)
        assert check_winner(controller.board) == 'X'

    def test_all_buttons_disabled(self):
        controller, _, mock_buttons = _make_controller()
        self._play(controller)
        for btn in mock_buttons:
            btn.config.assert_any_call(state=tk.DISABLED)

    def test_status_contains_x_and_win_indicator(self):
        controller, _, _ = _make_controller()
        self._play(controller)
        assert 'X' in controller._status_text
        assert 'win' in controller._status_text.lower()


class TestDrawSequence:
    """9-click draw: X@0,2,3,5,7 / O@1,4,6,8 — board full, no winner."""

    _MOVES = [0, 1, 2, 4, 3, 6, 5, 8, 7]

    def _play(self, controller):
        for pos in self._MOVES:
            controller._on_click(pos)

    def test_engine_reports_draw(self):
        controller, _, _ = _make_controller()
        self._play(controller)
        assert is_draw(controller.board)

    def test_all_buttons_disabled(self):
        controller, _, mock_buttons = _make_controller()
        self._play(controller)
        for btn in mock_buttons:
            btn.config.assert_any_call(state=tk.DISABLED)

    def test_status_contains_draw(self):
        controller, _, _ = _make_controller()
        self._play(controller)
        assert 'draw' in controller._status_text.lower()
