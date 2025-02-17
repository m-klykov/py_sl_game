import pygame
import math
from track import Track, CurvedTrack

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.outs = {
            (-1, 0): [],
            (1, 0): [],
            (0, -1): [],
            (0, 1): []
        }
        self.active_track_index = {}  # Текущий активный путь в каждом направлении
        self.semaphore_states = {}  # Состояния семафоров (True - зелёный, False - красный)
        self.blocked_dirs = {}  # Каие напралления стрелок заблокированы поездами
        self.color = (0, 0, 0)  # Цвет узла
        self.is_station = False  # Является ли узел станцией

    def getCanvasX(self, cell_size):
        return self.x * cell_size + cell_size // 2

    def getCanvasY(self, cell_size):
        return self.y * cell_size + cell_size // 2

    def get_dir_tracks(self, direction):
        """Получить список доступных треков по направлению"""
        return [track for track in self.outs[direction] if track.enabled]

    def is_station_bisy(self):
        for direction in self.outs:
            active_tracks =  self.get_dir_tracks(direction)
            if active_tracks:
                track = active_tracks[0]
                return track.bisy
        return True

    def is_terminal(self):
        """Проверяет, является ли узел конечным (имеет ровно один активный исходящий путь)."""
        active_directions = 0
        for direction in self.outs:
            if self.get_dir_tracks(direction):
                active_directions += 1
        return active_directions == 1

    def get_active_track(self, direction):
        """Возвращает текущий активный путь в указанном направлении."""
        if direction not in self.active_track_index:
            self.active_track_index[direction] = 0
        active_tracks = self.get_dir_tracks(direction)
        if active_tracks:
            return active_tracks[self.active_track_index[direction] % len(active_tracks)]
        return None

    def toggle_active_track(self, direction):
        """Переключает активный путь в указанном направлении."""
        active_tracks = self.get_dir_tracks(direction)
        if len(active_tracks) > 1:
            self.active_track_index[direction] = (self.active_track_index.get(direction, 0) + 1) % len(active_tracks)

    def can_add_track(self, direction):
        """Проверяет, можно ли добавить путь в указанном направлении."""
        if self.is_station:
            # Для станции общее количество путей не должно превышать 1
            total_tracks = 0
            for direction in self.outs:
                total_tracks += len(self.get_dir_tracks(direction))
            return total_tracks < 1
        else:
            # Для обычного узла в указанном направлении не должно быть больше одного пути
            return len(self.get_dir_tracks(direction)) < 2

    def draw_arrow(self, screen, direction, cell_size):
        """Рисует стрелку в указанном направлении."""
        x, y = self.getCanvasX(cell_size), self.getCanvasY(cell_size)
        track = self.get_active_track(direction)
        dx, dy = track.get_vector_for_node(self)
        end_x = x + dx * cell_size // 3
        end_y = y + dy * cell_size // 3
        color = (255, 0, 0)
        if self.blocked_dirs.get(direction):
            color = (200,200,200)
        pygame.draw.line(screen, color, (x, y), (end_x, end_y), 4)

    def draw_semaphore(self, screen, direction, cell_size):
        """Рисует семафор в указанном направлении."""
        dx, dy = direction
        x, y = self.getCanvasX(cell_size), self.getCanvasY(cell_size)
        semaphore_x = x + dx * cell_size // 8
        semaphore_y = y + dy * cell_size // 8
        color = (0, 255, 0) if self.semaphore_states.get(direction, True) else (255, 0, 0)
        if self.blocked_dirs.get(direction):
            color = (200,200,200)
        pygame.draw.circle(screen, color, (semaphore_x, semaphore_y), 5)
        pygame.draw.line(screen, color, (x, y), (semaphore_x, semaphore_y), 1)

    def has_semaphore(self, direction):
        active_tracks = self.get_dir_tracks(direction)
        if len(active_tracks) != 1:
            return False

        opos_tracks = self.get_dir_tracks((-direction[0], -direction[1]))
        if len(opos_tracks) != 1:
            return False

        act_track = self.get_active_track(direction)
        return isinstance(act_track, CurvedTrack)

    def is_semaphore_open(self, direction):
        return (not self.has_semaphore(direction)
        or self.semaphore_states.get(direction, True))

    def handle_click(self, mouse_x, mouse_y, cell_size):
        """Обрабатывает клик мыши в режиме управления."""
        x, y = self.getCanvasX(cell_size), self.getCanvasY(cell_size)
        for direction in self.outs:
            if self.blocked_dirs.get(direction):
                continue
            active_tracks = self.get_dir_tracks(direction)
            if len(active_tracks) > 1:
                end_x = x + direction[0] * cell_size // 3
                end_y = y + direction[1] * cell_size // 3
                if math.hypot(mouse_x - end_x, mouse_y - end_y) < 20:
                    self.toggle_active_track(direction)
            elif self.has_semaphore(direction):
                semaphore_x = x + direction[0] * cell_size // 8
                semaphore_y = y + direction[1] * cell_size // 8
                if math.hypot(mouse_x - semaphore_x, mouse_y - semaphore_y) < 10:
                    self.semaphore_states[direction] = not self.semaphore_states.get(direction, True)

    def draw(self, screen, construction_mode, cell_size):
        """Рисует узел, стрелки и семафоры."""
        if self.is_station:
            # Рисуем станцию
            pygame.draw.circle(screen, self.color, (self.getCanvasX(cell_size), self.getCanvasY(cell_size)), 8)
        elif self.is_terminal():
            # Рисуем терминальный узел
            pygame.draw.circle(screen, self.color, (self.getCanvasX(cell_size), self.getCanvasY(cell_size)), 5)

        if not construction_mode:
            for direction in self.outs:
                active_tracks = self.get_dir_tracks(direction)
                if len(active_tracks) > 1:
                    self.draw_arrow(screen, direction, cell_size)
                elif self.has_semaphore(direction):
                    self.draw_semaphore(screen, direction, cell_size)