import pytest

from tictactoe import apply_move, check_winner, is_draw, new_board, valid_moves


class TestNewBoard:
    def test_length(self):
        assert len(new_board()) == 9

    def test_all_none(self):
        assert all(cell is None for cell in new_board())

    def test_returns_list(self):
        assert isinstance(new_board(), list)


class TestApplyMove:
    def test_places_symbol(self):
        board = apply_move(new_board(), 0, "X")
        assert board[0] == "X"

    def test_returns_new_list(self):
        original = new_board()
        result = apply_move(original, 4, "O")
        assert result is not original

    def test_does_not_mutate_input(self):
        original = new_board()
        snapshot = list(original)
        apply_move(original, 4, "X")
        assert original == snapshot

    def test_raises_on_occupied(self):
        board = apply_move(new_board(), 0, "X")
        with pytest.raises(ValueError):
            apply_move(board, 0, "O")

    def test_raises_on_negative_pos(self):
        with pytest.raises(ValueError):
            apply_move(new_board(), -1, "X")

    def test_raises_on_pos_above_8(self):
        with pytest.raises(ValueError):
            apply_move(new_board(), 9, "X")

    def test_other_positions_unchanged(self):
        board = apply_move(new_board(), 3, "O")
        assert board[0] is None
        assert board[8] is None


class TestCheckWinner:
    def _board_with_line(self, positions, player):
        board = new_board()
        for pos in positions:
            board[pos] = player
        return board

    # 8 winning lines × 2 players = 16 cases
    def test_row0_x(self):
        assert check_winner(self._board_with_line([0, 1, 2], "X")) == "X"

    def test_row0_o(self):
        assert check_winner(self._board_with_line([0, 1, 2], "O")) == "O"

    def test_row1_x(self):
        assert check_winner(self._board_with_line([3, 4, 5], "X")) == "X"

    def test_row1_o(self):
        assert check_winner(self._board_with_line([3, 4, 5], "O")) == "O"

    def test_row2_x(self):
        assert check_winner(self._board_with_line([6, 7, 8], "X")) == "X"

    def test_row2_o(self):
        assert check_winner(self._board_with_line([6, 7, 8], "O")) == "O"

    def test_col0_x(self):
        assert check_winner(self._board_with_line([0, 3, 6], "X")) == "X"

    def test_col0_o(self):
        assert check_winner(self._board_with_line([0, 3, 6], "O")) == "O"

    def test_col1_x(self):
        assert check_winner(self._board_with_line([1, 4, 7], "X")) == "X"

    def test_col1_o(self):
        assert check_winner(self._board_with_line([1, 4, 7], "O")) == "O"

    def test_col2_x(self):
        assert check_winner(self._board_with_line([2, 5, 8], "X")) == "X"

    def test_col2_o(self):
        assert check_winner(self._board_with_line([2, 5, 8], "O")) == "O"

    def test_diag_main_x(self):
        assert check_winner(self._board_with_line([0, 4, 8], "X")) == "X"

    def test_diag_main_o(self):
        assert check_winner(self._board_with_line([0, 4, 8], "O")) == "O"

    def test_diag_anti_x(self):
        assert check_winner(self._board_with_line([2, 4, 6], "X")) == "X"

    def test_diag_anti_o(self):
        assert check_winner(self._board_with_line([2, 4, 6], "O")) == "O"

    def test_empty_board_returns_none(self):
        assert check_winner(new_board()) is None

    def test_draw_board_returns_none(self):
        # X O X / O X O / O X O — no winner
        board = ["X", "O", "X", "O", "X", "O", "O", "X", "O"]
        assert check_winner(board) is None


class TestIsDraw:
    def test_empty_board_is_not_draw(self):
        assert is_draw(new_board()) is False

    def test_partial_board_is_not_draw(self):
        board = apply_move(new_board(), 0, "X")
        assert is_draw(board) is False

    def test_winner_present_is_not_draw(self):
        board = ["X", "X", "X", "O", "O", None, None, None, None]
        assert is_draw(board) is False

    def test_full_board_no_winner_is_draw(self):
        # X O X / O X O / O X O
        board = ["X", "O", "X", "O", "X", "O", "O", "X", "O"]
        assert is_draw(board) is True


class TestValidMoves:
    def test_empty_board_all_9(self):
        assert valid_moves(new_board()) == list(range(9))

    def test_one_move_made(self):
        board = apply_move(new_board(), 4, "X")
        moves = valid_moves(board)
        assert 4 not in moves
        assert len(moves) == 8

    def test_full_board_no_moves(self):
        board = ["X", "O", "X", "O", "X", "O", "O", "X", "O"]
        assert valid_moves(board) == []

    def test_correct_indices_returned(self):
        board = new_board()
        board[0] = "X"
        board[8] = "O"
        moves = valid_moves(board)
        assert 0 not in moves
        assert 8 not in moves
        assert len(moves) == 7
