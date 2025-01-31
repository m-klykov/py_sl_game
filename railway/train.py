import pygame
import math
from track import Track, CurvedTrack

class Train:
    def __init__(self, start_node, color):
        self.current_node = start_node
        self.color = color  # Цвет поезда
        self.is_active = True  # Активен ли поезд
        self.current_track = None  # Текущий участок пути
        self.progress = 0  # Прогресс движения между узлами (0..1)
        self.start_node = None  # Начальный узел текущего участка
        self.end_node = None  # Конечный узел текущего участка

        # Инициализация начального участка
        self.set_initial_track()

    def set_initial_track(self):
        """Устанавливает начальный участок пути."""
        for direction in self.current_node.outs:
            active_tracks = [track for track in self.current_node.outs[direction] if track.enabled]
            if active_tracks:
                self.current_track = active_tracks[0]
                self.start_node = self.current_node
                self.end_node = self.current_track.node1 if self.current_track.node2 == self.current_node else self.current_track.node2
                break

    def update(self, nodes):
        """Обновляет положение поезда."""
        if not self.is_active or not self.current_track:
            return

        # Определяем коэффициент скорости
        speed_coefficient = 1.0
        if isinstance(self.current_track, CurvedTrack):
            # Длина дуги больше, чем прямой участок, поэтому замедляем движение
            speed_coefficient = 0.7  # Можно настроить в зависимости от радиуса дуги

        # Двигаем поезд
        self.progress += 0.01 * speed_coefficient  # Скорость движения с учётом коэффициента
        if self.progress >= 1:
            # Поезд доехал до конца участка
            self.progress = 0

            # Определяем направление въезда в следующий узел
            entry_direction = self.current_track.get_exit_direction(self.end_node)

            # Проверяем семафор и стрелку
            if not self.check_semaphore(self.end_node, entry_direction):
                # Движение запрещено, разворачиваем поезд
                self.reverse_direction()
                return

            # Перемещаем поезд в следующий узел
            self.current_node = self.end_node

            # Определяем следующий участок пути
            self.set_next_track()

            # Если поезд достиг терминального узла
            if self.current_node.is_terminal():
                if self.color == self.current_node.color:
                    self.is_active = False  # Поезд достиг цели
                else:
                    self.reverse_direction()  # Меняем направление

    def set_next_track(self):
        """Определяет следующий участок пути с учётом стрелки."""
        # Получаем направление выезда из текущего узла
        exit_direction = (-self.current_track.get_exit_direction(self.end_node)[0],
                          -self.current_track.get_exit_direction(self.end_node)[1])

        # Получаем активный участок пути с учётом стрелки
        active_track = self.current_node.get_active_track(exit_direction)
        if active_track:
            self.current_track = active_track
            self.start_node = self.current_node
            self.end_node = self.current_track.node1 if self.current_track.node2 == self.current_node else self.current_track.node2
        else:
            # Если нет активного пути, разворачиваем поезд
            self.reverse_direction()

    def reverse_direction(self):
        """Разворачивает поезд на текущем участке пути."""
        self.start_node, self.end_node = self.end_node, self.start_node
        self.progress = 0  # Сбрасываем прогресс

    def check_semaphore(self, next_node, entry_direction):
        """Проверяет, можно ли двигаться в направлении следующего узла."""
        # Проверяем семафор
        if next_node.semaphore_states.get(entry_direction, True) == False:
            return False  # Семафор закрыт

        # Проверяем стрелку
        active_track = next_node.get_active_track(entry_direction)
        if active_track:
            if active_track.node1 != self.current_node and active_track.node2 != self.current_node:
                return False  # Стрелка направлена не туда

        return True

    def draw(self, screen, cell_size):
        """Рисует поезд."""
        if not self.is_active or not self.current_track:
            return

        # Получаем координаты поезда на участке пути
        if self.current_track.node1 == self.start_node:
            x, y = self.current_track.get_position_on_track(self.progress, cell_size)
        else:
            x, y = self.current_track.get_position_on_track(1 - self.progress, cell_size)
        pygame.draw.circle(screen, self.color, (x, y), 8)