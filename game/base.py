import pygame

class BaseMode:
    def __init__(self, game, next_mode=''):
        self.game = game
        self.mode_name = ''
        self.viewport = game.getViewport()
        self.font = pygame.font.Font(None, 48)
        self.start_text = self.font.render("Нажмите, чтобы начать игру", True, (255, 255, 255))
        self.start_text_rect = self.start_text.get_rect(center=self.viewport.center)
        self.next_mode = next_mode

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.viewport.collidepoint(mouse_pos):
                if self.start_text_rect.collidepoint(mouse_pos):
                    return self.next_mode
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.start_text_rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Изменяем курсор на указатель
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Восстанавливаем обычный курсор
        elif event.type == pygame.KEYDOWN:
            return self.next_mode
        return None

    def update(self):
        pass

    def draw(self):
        self.viewport = self.game.getViewport()
        pygame.draw.rect(self.game.screen, (20, 20, 20), self.viewport)

        # Проверяем, находится ли курсор над текстом
        mouse_pos = pygame.mouse.get_pos()
        if self.start_text_rect.collidepoint(mouse_pos):
            # Полупрозрачный фон (RGBA, где A - альфа-канал для прозрачности)
            background = pygame.Surface(self.start_text_rect.size, pygame.SRCALPHA)
            background.fill((0, 255, 0, 128))  # Полупрозрачный зеленый фон (R, G, B, A)
            self.game.screen.blit(background, self.start_text_rect.topleft)

        self.game.screen.blit(self.start_text, self.start_text_rect)