import pygame
from .battleship_model import BattleshipGameModel
from .base import BaseMode

class BattleshipMode(BaseMode):
    def __init__(self, game):
        super().__init__(game)
        self.mode_name = 'Морской бой'
        self.model = BattleshipGameModel()
        self.selected_cell = (0, 0)  # Выбранная клетка для выстрела
        self.message = ''  # Сообщение о ходе игры

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            x, y = self.get_cell_from_mouse(mouse_pos)
            if 0 <= x < self.model.board_size and 0 <= y < self.model.board_size:
                result = self.model.make_move(x, y)
                if result == 'hit':
                    self.message = "Вы попали!"
                elif result == 'killed':
                    self.message = "Корабль потоплен!"
                elif result == 'miss':
                    self.message = "Мимо!"

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

        # Отображение информации о кораблях
        total, killed, wounded = self.model.get_ship_status()
        font = pygame.font.Font(None, 36)

        info_text = f"Всего кораблей: {total}, Потоплено: {killed}, Ранено: {wounded}"
        info_surface = font.render(info_text, True, (255, 255, 255))
        info_rect = info_surface.get_rect(center=(self.viewport.centerx, self.viewport.top + 5))
        self.game.screen.blit(info_surface, info_rect)

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
