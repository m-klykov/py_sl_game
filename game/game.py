import pygame
import sys
from game.base import BaseMode
from game.menu import MainMenu
from game.alert import AlertBox
from game.battleship_mode import BattleshipMode

GAME_NAME = "Моя гра";
WIN_WIDTH = 800
WIN_HEIGHT = 800


class Game:
    def __init__(self):
        pygame.init()

        # Инициализация экрана
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.is_fullscreen = True

        # Основные цвета
        self.bg_color = (30, 30, 30)  # Темно-серый фон
        self.status_bar_color = (50, 50, 50)  # Цвет строки состояния
        self.text_color = (255, 255, 255)  # Белый текст
        self.hover_color = (100, 100, 100)  # Подсветка при наведении

        # Размеры строки состояния
        self.status_bar_height = 50

        # Шрифт для текста
        self.font = pygame.font.Font(None, 36)

        self.alert = None

        self.last_mode = '';

        # Текущий режим игры
        self.switch_mode('start')

    def show_alert(self, message):
        self.alert = AlertBox(self, message)

    def switch_mode(self, mode):
        if mode=='start':
            self.current_mode = BaseMode(self,'main_menu')
        elif mode=='main_menu':
            self.current_mode = MainMenu(self)
        elif mode=='battleship':
            self.current_mode = BattleshipMode(self)
        else:
            self.show_alert('Режим "'+mode+'"')
            return

        self.last_mode = mode

    def toggle_fullscreen(self):
        """Переключение между полноэкранным и оконным режимами."""
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.is_fullscreen = not self.is_fullscreen

    def draw_status_bar(self):
        """Отображает строку состояния с заголовком и кнопками."""
        pygame.draw.rect(self.screen, self.status_bar_color, (0, 0, self.screen.get_width(), self.status_bar_height))

        # Заголовок игры по центру
        title = self.current_mode.mode_name
        if not title:
            title = GAME_NAME
        title_text = self.font.render(title, True, self.text_color)
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, self.status_bar_height // 2))
        self.screen.blit(title_text, title_rect)

        # Кнопка выхода (крестик)
        exit_rect = pygame.Rect(self.screen.get_width() - 42, 9, 32, 32)
        if exit_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, self.hover_color, exit_rect.inflate(10, 10), border_radius=5)
        pygame.draw.line(self.screen, self.text_color, (exit_rect.left, exit_rect.top),
                         (exit_rect.right, exit_rect.bottom), 3)
        pygame.draw.line(self.screen, self.text_color, (exit_rect.right, exit_rect.top),
                         (exit_rect.left, exit_rect.bottom), 3)

        # Кнопка перехода в оконный режим (квадратик)
        toggle_rect = pygame.Rect(exit_rect.left - 52, 9, 32, 32)
        if toggle_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, self.hover_color, toggle_rect.inflate(10, 10), border_radius=5)
        pygame.draw.rect(self.screen, self.text_color, toggle_rect, 3)

        # Перезапуск уровня (кружок)
        circle_center = (toggle_rect.left - 42, self.status_bar_height // 2)  # Центр круга
        circle_radius = 16  # Радиус круга
        circle_rect = pygame.Rect(circle_center[0] - circle_radius, circle_center[1] - circle_radius,
                                  2 * circle_radius, 2 * circle_radius)
        if circle_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.circle(self.screen, self.hover_color, circle_center,
                               circle_radius + 5)  # Увеличение радиуса при наведении
        pygame.draw.circle(self.screen, self.text_color, circle_center, circle_radius, 3)  # Основной круг

        return exit_rect, toggle_rect, circle_rect

    # вернуть область отображения игрі
    def getViewport(self):
        return pygame.Rect(0, self.status_bar_height, self.screen.get_width(),
                           self.screen.get_height() - self.status_bar_height)

    def run(self):
        """Основной игровой цикл."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.alert:
                    if self.alert.handle_event(event):
                        self.alert = None  # Закрытие алерта при клике
                else:

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()

                        # Проверка кликов по кнопкам
                        exit_rect, toggle_rect, reset_rect = self.draw_status_bar()
                        if exit_rect.collidepoint(mouse_pos):
                            self.running = False
                        elif toggle_rect.collidepoint(mouse_pos):
                            self.toggle_fullscreen()
                        elif reset_rect.collidepoint(mouse_pos):
                            if self.last_mode:
                                self.switch_mode(self.last_mode)

                    # Передача событий текущему режиму
                    result = self.current_mode.handle_event(event)
                    if result:
                        self.switch_mode(result)

            # Обновление экрана
            self.screen.fill(self.bg_color)


            # Отрисовка строки состояния
            self.draw_status_bar()

            # обновление режима
            if not self.alert:
                self.current_mode.update()

            # Отрисовка текущего режима
            self.current_mode.draw()

            if self.alert:
                self.alert.show()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()