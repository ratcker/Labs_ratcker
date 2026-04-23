import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt5.QtCore import Qt

class TicTacToeGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic-tac-toe on PyQt5")
        self.setGeometry(100, 100, 300, 420) # X, Y, ширина, высота
        self.buttons = []
        self.current_player = "X"
        self.move_count = 0 # Счетчик ходов
        self.create_buttons()
        self.status_label = QLabel(self)
        self.status_label.setGeometry(0, 345, 300, 20)
        self.status_label.setAlignment(Qt.AlignCenter)
        

        self.reset_button = QPushButton("Новая игра", self)
        self.reset_button.setGeometry(90, 305, 120, 30)
        self.reset_button.clicked.connect(self.reset_game)
        

        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
        self.winner = None
        self.reset_button.hide()
        self.stats_label = QLabel(self)
        self.stats_label.setGeometry(0, 370, 300, 20)
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.update_stats_label()

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
            
    def on_click(self):
        button = self.sender()
        if button.text() == "":
            button.setText(self.current_player)
            self.move_count += 1
            self.check_winner()

    def check_winner(self):
        buts = self.buttons
        if (buts[0][0].text()==buts[1][1].text()==buts[2][2].text() and (buts[0][0].text()!="")):
            self.winner = buts[0][0].text()
            self.end_game(f"Победил игрок {self.winner}")
            return 0
        elif (buts[0][2].text()==buts[1][1].text()==buts[2][0].text() and (buts[0][2].text()!="")):
            self.winner = buts[0][2].text()
            self.end_game(f"Победил игрок {self.winner}")
            return 0
        elif any((buts[0][i].text()==buts[1][i].text() and buts[1][i].text()==buts[2][i].text() and (buts[0][i].text()!="")) for i in range(3)):
            for i in range(3):
                if (buts[0][i].text()==buts[1][i].text() and buts[1][i].text()==buts[2][i].text() and (buts[0][i].text()!="")):
                    self.winner = buts[0][i].text()
                    break
            self.end_game(f"Победил игрок {self.winner}")
            return 0
        elif any((buts[i][0].text()==buts[i][1].text() and buts[i][1].text()==buts[i][2].text() and (buts[i][0].text()!="")) for i in range(3)):
            for i in range(3):
                if (buts[i][0].text()==buts[i][1].text() and buts[i][1].text()==buts[i][2].text() and (buts[i][0].text()!="")):
                    self.winner = buts[i][0].text()
                    break
            self.end_game(f"Победил игрок {self.winner}")
            return 0
        else:
            if any(buts[i][j].text()=="" for i in range(3) for j in range(3)):
                self.switch_player()
                return 0
            else:
                self.end_game("Ничья")

    def end_game(self, message):
        self.status_label.setText(message)
        if self.winner == 'X':
            self.x_wins+=1
        elif self.winner == 'O':
            self.o_wins+=1
        else:
            self.draws+=1
        self.update_stats_label()
        for row in self.buttons:
            for button in row:
                button.setEnabled(False)
        self.reset_button.show()

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

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
        self.status_label.setText("")
        self.reset_button.hide()
        self.winner = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicTacToeGame()
    window.show()
    sys.exit(app.exec_())
