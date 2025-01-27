import pygame
import sys

class BaseMode:
    def __init__(self, game):
        self.game = game
        self.viewport = game.getViewport()
        self.font = pygame.font.Font(None, 48)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.viewport.collidepoint(mouse_pos):
                text_rect = self.get_start_text_rect()
                if text_rect.collidepoint(mouse_pos):
                    return "switch_mode"
        return None

    def update(self):
        pass

    def draw(self):
        self.viewport = self.game.getViewport()
        pygame.draw.rect(self.game.screen, (20, 20, 20), self.viewport)
        start_text = self.font.render("Нажмите, чтобы начать игру", True, (255, 255, 255))
        text_rect = self.get_start_text_rect()
        self.game.screen.blit(start_text, text_rect)

    def get_start_text_rect(self):
        start_text = self.font.render("Нажмите, чтобы начать игру", True, (255, 255, 255))
        return start_text.get_rect(center=self.viewport.center)