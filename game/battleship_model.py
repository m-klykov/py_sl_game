import random

class BattleshipGameModel:
    def __init__(self):
        self.board_size = 10  # Размер доски (10x10)
        self.board = [['~' for _ in range(self.board_size)] for _ in range(self.board_size)]  # Инициализация доски
        self.ships = []  # Список кораблей
        self.shots_fired = 0
        self.game_over = False
        self.create_ships()

    def create_ships(self):
        # Пример простых кораблей (по 3 клетки) - тут можно добавить более сложную логику
        self.ships.append(self.place_ship(4))
        for i in range(2):
            self.ships.append(self.place_ship(3))
        for i in range(3):
            self.ships.append(self.place_ship(3))
        for i in range(4):
            self.ships.append(self.place_ship(1))

    def place_ship(self, size):
        """Место для корабля. Простейший случай, без проверок на столкновения с другими кораблями."""
        placed = False
        while not placed:
            orientation = random.choice(['H', 'V'])  # Горизонтальное или вертикальное
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if self.can_place_ship(x, y, size, orientation):
                self.place_ship_on_board(x, y, size, orientation)
                placed = True

    def can_place_ship(self, x, y, size, orientation):
        """Проверяет, можно ли разместить корабль."""
        if orientation == 'H':
            if y + size > self.board_size:
                return False
            for i in range(size):
                if self.board[x][y + i] != '~':
                    return False
        elif orientation == 'V':
            if x + size > self.board_size:
                return False
            for i in range(size):
                if self.board[x + i][y] != '~':
                    return False
        return True

    def place_ship_on_board(self, x, y, size, orientation):
        """Размещает корабль на доске."""
        if orientation == 'H':
            for i in range(size):
                self.board[x][y + i] = 'S'  # 'S' - это клетка, занятую кораблем
        elif orientation == 'V':
            for i in range(size):
                self.board[x + i][y] = 'S'

    def make_move(self, x, y):
        """Процесс выстрела по клетке."""
        if self.board[x][y] == 'S':
            self.board[x][y] = 'X'  # Попадание (X)
            self.shots_fired += 1
            return 'hit'
        elif self.board[x][y] == '~':
            self.board[x][y] = 'O'  # Мимо (O)
            self.shots_fired += 1
            return 'miss'
        return 'invalid'

    def is_game_over(self):
        """Проверка, завершена ли игра (все корабли уничтожены)."""
        for row in self.board:
            if 'S' in row:
                return False
        self.game_over = True
        return True