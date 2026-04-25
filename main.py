import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt


class TicTacToeGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic-tac-toe on PyQt5")
        self.setGeometry(100, 100, 300, 420)
        self.buttons = []
        self.current_player = "X"
        self.move_count = 0
        self.game_mode = "player"
        self.human_player = "X"
        self.computer_player = "O"

        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
        self.winner = None

        self.create_buttons()

        self.status_label = QLabel(self)
        self.status_label.setGeometry(0, 345, 300, 20)
        self.status_label.setAlignment(Qt.AlignCenter)

        self.reset_button = QPushButton("Новая игра", self)
        self.reset_button.setGeometry(90, 305, 120, 30)
        self.reset_button.clicked.connect(self.reset_game)
        self.reset_button.hide()

        self.stats_label = QLabel(self)
        self.stats_label.setGeometry(0, 370, 300, 20)
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.update_stats_label()

        self.ask_game_mode()
        self.update_turn_label()

    def create_buttons(self):
        for row in range(3):
            row_buttons = []
            for col in range(3):
                button = QPushButton(self)
                button.setText("")
                button.setGeometry(col * 100, row * 100, 100, 100)
                button.clicked.connect(self.on_click)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

    def ask_game_mode(self):
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Выбор режима")
        message_box.setText("С кем играть?")
        player_button = message_box.addButton("С игроком", QMessageBox.AcceptRole)
        computer_button = message_box.addButton("С компьютером", QMessageBox.ActionRole)
        message_box.exec_()

        if message_box.clickedButton() == computer_button:
            self.game_mode = "computer"
        else:
            self.game_mode = "player"

    def on_click(self):
        button = self.sender()

        if button.text() == "" and self.winner is None:
            button.setText(self.current_player)
            self.move_count += 1
            game_finished = self.check_winner()

            if not game_finished and self.game_mode == "computer" and self.current_player == self.computer_player:
                self.computer_move()

    def check_winner(self):
        buts = self.buttons
        if buts[0][0].text() == buts[1][1].text() == buts[2][2].text() and buts[0][0].text() != "":
            self.winner = buts[0][0].text()
            self.end_game(f"Победил игрок {self.winner}")
            return True
        elif buts[0][2].text() == buts[1][1].text() == buts[2][0].text() and buts[0][2].text() != "":
            self.winner = buts[0][2].text()
            self.end_game(f"Победил игрок {self.winner}")
            return True
        elif any(
            buts[0][i].text() == buts[1][i].text() == buts[2][i].text() and buts[0][i].text() != ""
            for i in range(3)
        ):
            for i in range(3):
                if buts[0][i].text() == buts[1][i].text() == buts[2][i].text() and buts[0][i].text() != "":
                    self.winner = buts[0][i].text()
                    break
            self.end_game(f"Победил игрок {self.winner}")
            return True
        elif any(
            buts[i][0].text() == buts[i][1].text() == buts[i][2].text() and buts[i][0].text() != ""
            for i in range(3)
        ):
            for i in range(3):
                if buts[i][0].text() == buts[i][1].text() == buts[i][2].text() and buts[i][0].text() != "":
                    self.winner = buts[i][0].text()
                    break
            self.end_game(f"Победил игрок {self.winner}")
            return True
        else:
            if any(buts[i][j].text() == "" for i in range(3) for j in range(3)):
                self.switch_player()
                self.update_turn_label()
                return False
            else:
                self.end_game("Ничья")
                return True

    def end_game(self, message):
        self.status_label.setText(message)
        if self.winner == "X":
            self.x_wins += 1
        elif self.winner == "O":
            self.o_wins += 1
        else:
            self.draws += 1
        self.update_stats_label()
        for row in self.buttons:
            for button in row:
                button.setEnabled(False)
        self.reset_button.show()

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def update_turn_label(self):
        if self.game_mode == "computer" and self.current_player == self.computer_player:
            self.status_label.setText("Ход компьютера")
        else:
            self.status_label.setText(f"Ход игрока {self.current_player}")

    def update_stats_label(self):
        total = self.x_wins + self.o_wins + self.draws
        self.stats_label.setText(f"X: {self.x_wins} | O: {self.o_wins} | Ничьи: {self.draws} | Игр: {total}")

    def reset_game(self):
        for row in self.buttons:
            for button in row:
                button.setText("")
                button.setEnabled(True)
        self.current_player = "X"
        self.move_count = 0
        self.winner = None
        self.reset_button.hide()
        self.ask_game_mode()
        self.update_turn_label()

    def get_board(self):
        return [[self.buttons[row][col].text() for col in range(3)] for row in range(3)]

    def get_available_moves(self, board):
        return [(row, col) for row in range(3) for col in range(3) if board[row][col] == ""]

    def get_winner_for_board(self, board):
        lines = []
        lines.extend(board)
        lines.extend([[board[row][col] for row in range(3)] for col in range(3)])
        lines.append([board[i][i] for i in range(3)])
        lines.append([board[i][2 - i] for i in range(3)])

        for line in lines:
            if line[0] != "" and line[0] == line[1] == line[2]:
                return line[0]

        if not self.get_available_moves(board):
            return "draw"

        return None

    def minimax(self, board, is_maximizing):
        result = self.get_winner_for_board(board)
        if result == self.computer_player:
            return 1
        if result == self.human_player:
            return -1
        if result == "draw":
            return 0

        if is_maximizing:
            best_score = -100
            for row, col in self.get_available_moves(board):
                board[row][col] = self.computer_player
                score = self.minimax(board, False)
                board[row][col] = ""
                if score > best_score:
                    best_score = score
            return best_score

        best_score = 100
        for row, col in self.get_available_moves(board):
            board[row][col] = self.human_player
            score = self.minimax(board, True)
            board[row][col] = ""
            if score < best_score:
                best_score = score
        return best_score

    def computer_move(self):
        board = self.get_board()
        best_score = -100
        best_move = None

        for row, col in self.get_available_moves(board):
            board[row][col] = self.computer_player
            score = self.minimax(board, False)
            board[row][col] = ""
            if score > best_score:
                best_score = score
                best_move = (row, col)

        if best_move is not None:
            row, col = best_move
            self.buttons[row][col].setText(self.computer_player)
            self.move_count += 1
            self.check_winner()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicTacToeGame()
    window.show()
    sys.exit(app.exec_())
