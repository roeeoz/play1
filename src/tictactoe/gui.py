import tkinter as tk

from .engine import new_board, apply_move, check_winner, is_draw, valid_moves

_PLAYER_COLORS = {'X': 'blue', 'O': 'red'}


class GameController:
    def __init__(self, root):
        self.board = new_board()
        self.current_player = 'X'
        self._status_text = ''

        self.status = tk.Label(root, font=('TkDefaultFont', 14))
        self.status.grid(row=0, column=0, columnspan=3, pady=6)

        self.buttons = []
        for i in range(9):
            row, col = divmod(i, 3)
            btn = tk.Button(
                root,
                text='',
                font=('TkDefaultFont', 28),
                width=5,
                height=2,
                command=lambda pos=i: self._on_click(pos),
            )
            btn.grid(row=row + 1, column=col, padx=2, pady=2)
            self.buttons.append(btn)

        for col in range(3):
            root.columnconfigure(col, minsize=120)
        for row in range(1, 4):
            root.rowconfigure(row, minsize=120)

        self._set_status("Player X's turn", _PLAYER_COLORS['X'])

    def _set_status(self, text, fg='black'):
        self._status_text = text
        self.status.config(text=text, fg=fg)

    def _on_click(self, pos):
        if pos not in valid_moves(self.board):
            return
        self.board = apply_move(self.board, pos, self.current_player)
        color = _PLAYER_COLORS[self.current_player]
        self.buttons[pos].config(text=self.current_player, fg=color)

        winner = check_winner(self.board)
        if winner:
            self._set_status(f"Player {winner} wins!", _PLAYER_COLORS[winner])
            self._disable_all()
            return

        if is_draw(self.board):
            self._set_status("It's a draw!", 'black')
            self._disable_all()
            return

        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self._set_status(
            f"Player {self.current_player}'s turn",
            _PLAYER_COLORS[self.current_player],
        )

    def _disable_all(self):
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)


def launch_game() -> None:
    """Create the Tk root window, build the board UI, and enter mainloop.
    Returns only when the window is closed."""
    root = tk.Tk()
    root.title("Tic Tac Toe")
    GameController(root)
    root.mainloop()
