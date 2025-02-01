import pygame
import math

class Track:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.n1_dx = self.sign(node2.x - node1.x)
        self.n1_dy = self.sign(node2.y - node1.y)
        self.n2_dx = -self.n1_dx
        self.n2_dy = -self.n1_dy
        self.enabled = False
        self.blocked = False
        self.bisy = False # занято поездом

    @staticmethod
    def sign(a):
        """Возвращает -1, 0 или 1 в зависимости от знака a."""
        if a < 0:
            return -1
        elif a > 0:
            return 1
        else:
            return 0

    def get_exit_direction(self, current_node):
        """Возвращает направление выезда из текущего узла."""
        if current_node == self.node1:
            return (self.n1_dx, self.n1_dy)
        else:
            return (self.n2_dx, self.n2_dy)

    def assign_to_nodes(self):
        self.node1.outs[(self.n1_dx, self.n1_dy)].append(self)
        self.node2.outs[(self.n2_dx, self.n2_dy)].append(self)

    def get_vector_for_node(self, node):
        if node == self.node1:
            dx1, dy1, dx2, dy2 = self.n1_dx, self.n1_dy, self.n2_dx, self.n2_dy
        else:
            dx1, dy1, dx2, dy2 = self.n2_dx, self.n2_dy, self.n1_dx, self.n1_dy

        if dy1 == 0:
            return dx1, -dy2 / 5
        else:
            return -dx2 / 5, dy1

    def get_color(self, is_hovered, construction_mode):
        """Возвращает цвет пути в зависимости от его состояния и наведения."""
        if self.enabled:
            return (255, 0, 0) if is_hovered and construction_mode else (140, 140, 140)
        else:
            return (255, 100, 100) if is_hovered else (240, 240, 240)

    def draw(self, screen, mouse_pos, construction_mode, cell_size):
        color = self.get_color(self.is_hovered(*mouse_pos, cell_size), construction_mode)
        width = 8 if self.enabled else 3
        pygame.draw.line(screen, color,
                         (self.node1.getCanvasX(cell_size), self.node1.getCanvasY(cell_size)),
                         (self.node2.getCanvasX(cell_size), self.node2.getCanvasY(cell_size)), width)

    def get_other_node(self, node):
        return self.node1 if self.node2 == node else self.node2

    def is_hovered(self, x, y, cell_size):
        """Проверяет, находится ли курсор рядом с прямым путём."""
        if self.blocked or self.bisy:
            return False

        x1, y1 = self.node1.getCanvasX(cell_size), self.node1.getCanvasY(cell_size)
        x2, y2 = self.node2.getCanvasX(cell_size), self.node2.getCanvasY(cell_size)
        if self.node1.x == self.node2.x:
            if not (min(y1, y2) <= y <= max(y1, y2)):
                return False
        else:
            if not (min(x1, x2) <= x <= max(x1, x2)):
                return False
        # Расстояние от точки до линии
        line_length = math.hypot(x2 - x1, y2 - y1)
        distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / line_length
        return distance < 5

    def toggle(self):
        """Переключает состояние пути, если это возможно."""
        if self.blocked or self.bisy:
            return

        if self.enabled:
            self.enabled = False
        else:
            # Проверяем, можно ли добавить путь в обоих узлах
            if self.node1.can_add_track((self.n1_dx, self.n1_dy)) and \
                    self.node2.can_add_track((self.n2_dx, self.n2_dy)):
                self.enabled = True

    def get_position_on_track(self, progress, cell_size):
        """Возвращает координаты поезда на участке пути."""
        x1, y1 = self.node1.getCanvasX(cell_size), self.node1.getCanvasY(cell_size)
        x2, y2 = self.node2.getCanvasX(cell_size), self.node2.getCanvasY(cell_size)
        x = x1 + (x2 - x1) * progress
        y = y1 + (y2 - y1) * progress
        return int(x), int(y)


class CurvedTrack(Track):
    def __init__(self, node1, node2, direction):
        super().__init__(node1, node2)
        self.direction = direction
        if self.direction == 'hor':
            self.n1_dx = 1
            self.n1_dy = 0
            self.n2_dx = 0
            self.n2_dy = self.sign(node1.y - node2.y)
        elif self.direction == 'vert':
            self.n1_dx = 0
            self.n1_dy = self.sign(node2.y - node1.y)
            self.n2_dx = -1
            self.n2_dy = 0

    def draw(self, screen, mouse_pos, construction_mode, cell_size):
        color = self.get_color(self.is_hovered(*mouse_pos, cell_size), construction_mode)

        x1, y1 = self.node1.getCanvasX(cell_size), self.node1.getCanvasY(cell_size)
        x2, y2 = self.node2.getCanvasX(cell_size), self.node2.getCanvasY(cell_size)

        width = 8 if self.enabled else 3

        if y2 > y1:
            if self.direction == 'hor':
                center_x, center_y = x1, y2
                start_angle, end_angle = 0, math.pi / 2
            else:
                center_x, center_y = x2, y1
                start_angle, end_angle = math.pi, math.pi * 3 / 2
        else:
            if self.direction == 'hor':
                center_x, center_y = x1, y2
                start_angle, end_angle = -math.pi / 2, 0
            else:
                center_x, center_y = x2, y1
                start_angle, end_angle = math.pi / 2, math.pi

        radius = cell_size + width //2


        arc_rect = (center_x - radius, center_y - radius, radius * 2, radius * 2)
        pygame.draw.arc(screen, color, arc_rect, start_angle, end_angle, width)

    def is_hovered(self, x, y, cell_size):
        """Проверяет, находится ли курсор рядом с дугой и внутри ограничивающего прямоугольника."""
        if self.blocked or self.bisy:
            return False

        center_x = self.node1.getCanvasX(cell_size) if self.direction == 'hor' else self.node2.getCanvasX(cell_size)
        center_y = self.node2.getCanvasY(cell_size) if self.direction == 'hor' else self.node1.getCanvasY(cell_size)

        x_min, x_max = min(self.node1.getCanvasX(cell_size), self.node2.getCanvasX(cell_size)), max(
            self.node1.getCanvasX(cell_size), self.node2.getCanvasX(cell_size))
        y_min, y_max = min(self.node1.getCanvasY(cell_size), self.node2.getCanvasY(cell_size)), max(
            self.node1.getCanvasY(cell_size), self.node2.getCanvasY(cell_size))

        if not (x_min <= x <= x_max and y_min <= y <= y_max):
            return False

        dx, dy = x - center_x, y - center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return abs(distance - cell_size) < 5

    def get_position_on_track(self, progress, cell_size):
        """Возвращает координаты поезда на дуге."""
        x1, y1 = self.node1.getCanvasX(cell_size), self.node1.getCanvasY(cell_size)
        x2, y2 = self.node2.getCanvasX(cell_size), self.node2.getCanvasY(cell_size)

        if y2 > y1:
            if self.direction == 'hor':
                center_x, center_y = x1, y2
                start_angle, end_angle = math.pi / 2, 0
            else:
                center_x, center_y = x2, y1
                start_angle, end_angle = math.pi, math.pi * 3 / 2
        else:
            if self.direction == 'hor':
                center_x, center_y = x1, y2
                start_angle, end_angle = -math.pi / 2, 0
            else:
                center_x, center_y = x2, y1
                start_angle, end_angle = math.pi, math.pi / 2

        angle = start_angle + (end_angle - start_angle) * progress
        radius = cell_size
        x = center_x + radius * math.cos(angle)
        y = center_y - radius * math.sin(angle)
        return int(x), int(y)
