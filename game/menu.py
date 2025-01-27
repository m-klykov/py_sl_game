import pygame
from .base import BaseMode

class MainMenu(BaseMode):
    def __init__(self, game):
        super().__init__(game)
        self.mode_name = 'Головне меню'
        self.menu_items = [
            {'mode': 'level1', 'text': 'Уровень 1'},
            {'mode': 'level2', 'text': 'Уровень 2'},
            {'mode': 'level3', 'text': 'Уровень 3'}
        ]
        self.selected_item = 0  # Индекс выбранного пункта меню

        # Создаем список для отрисовки текста каждого пункта меню
        self.menu_texts = [self.font.render(item['text'], True, (255, 255, 255)) for item in self.menu_items]
        self.menu_rects = [text.get_rect(center=(self.viewport.centerx, self.viewport.top + 50 + i * 60)) for i, text in enumerate(self.menu_texts)]


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    return self.menu_items[i]['mode']  # Переход к соответствующему режиму
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_item = i  # Выбираем элемент при наведении мыши
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)  # Перемещаемся вниз
            elif event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)  # Перемещаемся вверх
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.menu_items[self.selected_item]['mode']  # Переход к выбранному пункту
        return None

    def draw(self):
        self.viewport = self.game.getViewport()
        pygame.draw.rect(self.game.screen, (20, 20, 20), self.viewport)

        # Отображаем пункты меню
        for i, rect in enumerate(self.menu_rects):
            if i == self.selected_item:
                # Подсвечиваем выбранный пункт меню (полупрозрачный фон)
                background = pygame.Surface(rect.size, pygame.SRCALPHA)
                background.fill((0, 255, 0, 128))  # Полупрозрачный фон
                self.game.screen.blit(background, rect.topleft)

            self.game.screen.blit(self.menu_texts[i], rect)
