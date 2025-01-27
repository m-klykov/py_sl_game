import pygame
import random
from .base import BaseMode

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


class BattleshipMode(BaseMode):
    def __init__(self, game):
        super().__init__(game)
        self.model = BattleshipGameModel()
        self.selected_cell = (0, 0)  # Выбранная клетка для выстрела
        self.message = ''  # Сообщение о ходе игры

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            x, y = self.get_cell_from_mouse(mouse_pos)
            if 0 <= x < self.model.board_size and 0 <= y < self.model.board_size:
                result = self.model.make_move(x, y)
                self.message = f"Результат выстрела: {result}"
                if self.model.is_game_over():
                    self.message = "Игра окончена!"
                    return "game_over"  # Игра окончена

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_cell = (max(0, self.selected_cell[0] - 1), self.selected_cell[1])
            elif event.key == pygame.K_RIGHT:
                self.selected_cell = (min(self.model.board_size - 1, self.selected_cell[0] + 1), self.selected_cell[1])
            elif event.key == pygame.K_UP:
                self.selected_cell = (self.selected_cell[0], max(0, self.selected_cell[1] - 1))
            elif event.key == pygame.K_DOWN:
                self.selected_cell = (self.selected_cell[0], min(self.model.board_size - 1, self.selected_cell[1] + 1))
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                x, y = self.selected_cell
                result = self.model.make_move(x, y)
                if self.model.is_game_over():
                    return "game_over"  # Игра окончена
        return None

    def update(self):
        pass

    def getCellSize(self):
        cell_size = self.viewport.height // (self.model.board_size+1)
        size = cell_size*self.model.board_size
        self.v_left = (self.viewport.width-size) //2
        self.v_top = self.viewport.top+(self.viewport.height-size) //3
        return cell_size

    def draw(self):
        self.viewport = self.game.getViewport()
        pygame.draw.rect(self.game.screen, (20, 20, 20), self.viewport)

        # Отображаем доску
        cell_size = self.getCellSize()
        for i in range(self.model.board_size):
            for j in range(self.model.board_size):
                cell_rect = pygame.Rect(self.v_left + i * cell_size, self.v_top + j * cell_size, cell_size, cell_size)
                if self.model.board[i][j] == 'S':
                    pygame.draw.rect(self.game.screen, (255, 0, 0), cell_rect)  # Корабли красные
                elif self.model.board[i][j] == 'X':
                    pygame.draw.rect(self.game.screen, (0, 255, 0), cell_rect)  # Попадания зеленые
                elif self.model.board[i][j] == 'O':
                    pygame.draw.rect(self.game.screen, (0, 0, 255), cell_rect)  # Мимо синие
                pygame.draw.rect(self.game.screen, (255, 255, 255), cell_rect, 1)

        # Отображаем выбранную клетку
        x, y = self.selected_cell
        highlight_rect = pygame.Rect(self.v_left + x * cell_size, self.v_top +  y * cell_size, cell_size, cell_size)
        pygame.draw.rect(self.game.screen, (255, 255, 0), highlight_rect, 3)  # Желтая рамка для выделенной клетки

        # Отображаем сообщение о ходе игры
        font = pygame.font.Font(None, 36)
        message_text = font.render(self.message, True, (255, 255, 255))
        message_rect = message_text.get_rect(
            center=(self.viewport.centerx, self.viewport.bottom - 30))
        self.game.screen.blit(message_text, message_rect)

    def get_cell_from_mouse(self, mouse_pos):
        """Преобразует позицию мыши в индекс клетки доски."""
        cell_size = self.getCellSize()
        x = (mouse_pos[0]-self.v_left) // cell_size
        y = (mouse_pos[1]-self.v_top) // cell_size
        return x, y
