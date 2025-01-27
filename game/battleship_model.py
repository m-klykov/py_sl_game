import random

class BattleshipGameModel:
    def __init__(self):
        self.board_size = 10
        self.board = [['~' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.ships = []  # Список кораблей в формате: [(координаты клеток), потоплен ли]
        self.shots_fired = 0
        self.game_over = False
        self.create_ships()

    def create_ships(self):
        self.ships.append((self.place_ship(4), False))
        for _ in range(2):
            self.ships.append((self.place_ship(3), False))
        for _ in range(3):
            self.ships.append((self.place_ship(2), False))
        for _ in range(4):
            self.ships.append((self.place_ship(1), False))

    def place_ship(self, size):
        placed = False
        while not placed:
            orientation = random.choice(['H', 'V'])
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if self.can_place_ship(x, y, size, orientation):
                ship_coordinates = []
                for i in range(size):
                    if orientation == 'H':
                        self.board[x][y + i] = 'S'
                        ship_coordinates.append((x, y + i))
                    else:
                        self.board[x + i][y] = 'S'
                        ship_coordinates.append((x + i, y))
                placed = True
                return ship_coordinates

    def can_place_ship(self, x, y, size, orientation):
        if orientation == 'H' and y + size > self.board_size:
            return False
        if orientation == 'V' and x + size > self.board_size:
            return False
        for i in range(size):
            if orientation == 'H' and self.board[x][y + i] != '~':
                return False
            if orientation == 'V' and self.board[x + i][y] != '~':
                return False
        return True

    def make_move(self, x, y):
        if self.board[x][y] == 'S':
            self.board[x][y] = 'X'
            self.shots_fired += 1
            for i, ship in enumerate(self.ships):
                if (x, y) in ship[0]:
                    if all(self.board[cx][cy] == 'X' for cx, cy in ship[0]):
                        self.ships[i] = (ship[0], True)  # Обновляем статус корабля на "потоплен"
                        return 'killed'
                    return 'hit'
        elif self.board[x][y] == '~':
            self.board[x][y] = 'O'
            self.shots_fired += 1
            return 'miss'
        return 'invalid'

    def is_game_over(self):
        return all(ship[1] for ship in self.ships)

    def get_ship_status(self):
        """Возвращает количество потопленных, раненых и всего кораблей."""
        killed = sum(1 for ship in self.ships if ship[1])
        wounded = sum(1 for ship in self.ships if not ship[1] and any(self.board[cx][cy] == 'X' for cx, cy in ship[0]))
        total = len(self.ships)
        return total, killed, wounded