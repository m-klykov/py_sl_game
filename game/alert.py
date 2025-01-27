import pygame

class AlertBox:
    def __init__(self, game, message, width=400, height=200):
        self.game = game
        self.message = message
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(message, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(
            center=(self.game.screen.get_width() // 2, self.game.screen.get_height() // 2))

    def show(self):
        brd = 20
        alert_rect = pygame.Rect(self.text_rect.x - brd,
                                 self.text_rect.y - brd,
                                 self.text_rect.width + brd*2,
                                 self.text_rect.height + brd*2)

        background = pygame.Surface(
            (self.game.screen.get_width(), self.game.screen.get_height()),
            pygame.SRCALPHA)
        background.fill((0, 0, 0, 80))  # Полупрозрачный черній фон (R, G, B, A)
        self.game.screen.blit(background, (0,0))

        # Отрисовываем фон всплывающего окна
        pygame.draw.rect(self.game.screen, (0, 0, 0), alert_rect)  # Черный фон
        pygame.draw.rect(self.game.screen, (10, 10, 10), alert_rect, 5)  # рамка

        # Отображаем сообщение
        self.game.screen.blit(self.text_surface, self.text_rect)

        pygame.display.update()

    def handle_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN
        or event.type == pygame.KEYDOWN):
            return True  # Закрытие окна по клику мыши

        return False