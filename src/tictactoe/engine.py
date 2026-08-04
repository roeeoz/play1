_WINNING_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def new_board() -> list:
    """Return a fresh 9-element list of None representing an empty 3x3 board."""
    return [None] * 9


def apply_move(board: list, pos: int, player: str) -> list:
    """Return a new board list with player placed at pos.

    Raises ValueError if pos is already occupied or out of range 0-8.
    """
    if pos < 0 or pos > 8:
        raise ValueError(f"pos {pos} is out of range 0-8")
    if board[pos] is not None:
        raise ValueError(f"pos {pos} is already occupied")
    new = list(board)
    new[pos] = player
    return new


def check_winner(board: list) -> "str | None":
    """Return 'X' or 'O' if that player has three in a row, else None."""
    for a, b, c in _WINNING_LINES:
        if board[a] is not None and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_draw(board: list) -> bool:
    """Return True if all 9 positions are filled and there is no winner."""
    return not valid_moves(board) and check_winner(board) is None


def valid_moves(board: list) -> "list[int]":
    """Return a list of position indices (0-8) that are currently None."""
    return [i for i, cell in enumerate(board) if cell is None]
