import pygame
import math

# Константы
GRID_SIZE_X = 10  # Размер сетки
GRID_SIZE_Y = 6  # Размер сетки
CELL_SIZE = 100  # Размер клетки
SCREEN_SIZE_X = GRID_SIZE_X * CELL_SIZE
SCREEN_SIZE_Y = GRID_SIZE_Y * CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
# LIGHT_GRAY = (245, 245, 245)
LIGHT_GRAY = (250, 250, 250)
PALE_RED = (255, 230, 230)
RED = (255, 0, 0)

# Глобальная переменная для режима
construction_mode = True  # Начинаем в режиме конструирования

def sign(a):
    """Возвращает -1, 0 или 1 в зависимости от знака a."""
    if a < 0:
        return -1
    elif a > 0:
        return 1
    else:
        return 0

def draw_grid(screen):
    """Рисует сетку узлов."""
    for x in range(0, SCREEN_SIZE_X, CELL_SIZE):
        for y in range(0, SCREEN_SIZE_Y, CELL_SIZE):
            pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)

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

    def getCanvasX(self):
        return self.x * CELL_SIZE + CELL_SIZE // 2

    def getCanvasY(self):
        return self.y * CELL_SIZE + CELL_SIZE // 2

    def is_terminal(self):
        """Проверяет, является ли узел конечным (имеет ровно один активный исходящий путь)."""
        active_directions = 0
        for direction in self.outs:
            active_tracks = [track for track in self.outs[direction] if track.enabled]
            if active_tracks:
                active_directions += 1
        return active_directions == 1

    def draw(self, screen):
        """Рисует узел, только если он является конечным."""
        if self.is_terminal():
            pygame.draw.circle(screen, BLACK, (self.getCanvasX(), self.getCanvasY()), 5)

class Track:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.n1_dx = sign(node2.x - node1.x)
        self.n1_dy = sign(node2.y - node1.y)
        self.n2_dx = -self.n1_dx
        self.n2_dy = -self.n1_dy
        self.enabled = False

    def assign_to_nodes(self):
        self.node1.outs[(self.n1_dx,self.n1_dy)].append(self)
        self.node2.outs[(self.n2_dx,self.n2_dy)].append(self)

    def get_color(self, is_hovered):
        """Возвращает цвет пути в зависимости от его состояния и наведения."""
        if self.enabled:
            return RED if is_hovered else BLACK
        else:
            return PALE_RED if is_hovered else LIGHT_GRAY

    def draw(self, screen, mouse_pos):
        color = self.get_color(self.is_hovered(*mouse_pos))
        pygame.draw.line(screen, color,
                         (self.node1.getCanvasX(), self.node1.getCanvasY()),
                         (self.node2.getCanvasX(), self.node2.getCanvasY()), 3)

    def is_hovered(self, x, y):
        """Проверяет, находится ли курсор рядом с прямым путём."""
        x1, y1 = self.node1.getCanvasX(), self.node1.getCanvasY()
        x2, y2 = self.node2.getCanvasX(), self.node2.getCanvasY()
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
        # Если путь уже активен, его можно выключить без ограничений
        if self.enabled:
            self.enabled = False
        else:
            # Если путь неактивен, проверяем ограничение на количество активных путей
            active_tracks_node1 = [track for track in self.node1.outs[(self.n1_dx, self.n1_dy)] if track.enabled]
            active_tracks_node2 = [track for track in self.node2.outs[(self.n2_dx, self.n2_dy)] if track.enabled]

            # Если в обоих направлениях меньше двух активных путей, включаем путь
            if len(active_tracks_node1) < 2 and len(active_tracks_node2) < 2:
                self.enabled = True

class CurvedTrack(Track):
    def __init__(self, node1, node2, direction):
        super().__init__(node1, node2)
        self.direction = direction
        if self.direction == 'hor':
            self.n1_dx = 1
            self.n1_dy = 0
            self.n2_dx = 0
            self.n2_dy = sign(node1.y - node2.y)
        elif self.direction == 'vert':
            self.n1_dx = 0
            self.n1_dy = sign(node2.y - node1.y)
            self.n2_dx = -1
            self.n2_dy = 0

    def draw(self, screen, mouse_pos):
        color = self.get_color(self.is_hovered(*mouse_pos))

        x1, y1 = self.node1.getCanvasX(), self.node1.getCanvasY()
        x2, y2 = self.node2.getCanvasX(), self.node2.getCanvasY()

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

        radius = CELL_SIZE
        arc_rect = (center_x - radius, center_y - radius, radius * 2, radius * 2)
        pygame.draw.arc(screen, color, arc_rect, start_angle, end_angle, 3)

    def is_hovered(self, x, y):
        """Проверяет, находится ли курсор рядом с дугой и внутри ограничивающего прямоугольника."""
        # Определяем центр окружности
        center_x = self.node1.getCanvasX() if self.direction == 'hor' else self.node2.getCanvasX()
        center_y = self.node2.getCanvasY() if self.direction == 'hor' else self.node1.getCanvasY()

        # Проверяем попадание курсора в прямоугольник между node1 и node2
        x_min, x_max = min(self.node1.getCanvasX(), self.node2.getCanvasX()), max(self.node1.getCanvasX(), self.node2.getCanvasX())
        y_min, y_max = min(self.node1.getCanvasY(), self.node2.getCanvasY()), max(self.node1.getCanvasY(), self.node2.getCanvasY())

        if not (x_min <= x <= x_max and y_min <= y <= y_max):
            return False  # Если курсор за границами прямоугольника, не учитывать его

        # Проверяем расстояние до окружности
        dx, dy = x - center_x, y - center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return abs(distance - CELL_SIZE) < 5  # Проверяем, насколько точка близка к радиусу дуги

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE_X, SCREEN_SIZE_Y))
pygame.display.set_caption("Railway Simulator")
clock = pygame.time.Clock()

# Создание узлов и путей
nodes = [[Node(x, y) for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]
tracks = []

for x in range(GRID_SIZE_X):
    for y in range(GRID_SIZE_Y):
        if x < GRID_SIZE_X - 1:
            tracks.append(Track(nodes[x][y], nodes[x + 1][y]))
        if y < GRID_SIZE_Y - 1:
            tracks.append(Track(nodes[x][y], nodes[x][y + 1]))
        if x < GRID_SIZE_X - 1 and y < GRID_SIZE_Y - 1:
            tracks.append(CurvedTrack(nodes[x][y], nodes[x + 1][y + 1], 'hor'))
            tracks.append(CurvedTrack(nodes[x][y], nodes[x + 1][y + 1], 'vert'))
        if x < GRID_SIZE_X - 1 and y > 0:
            tracks.append(CurvedTrack(nodes[x][y], nodes[x + 1][y - 1], 'hor'))
            tracks.append(CurvedTrack(nodes[x][y], nodes[x + 1][y - 1], 'vert'))

for track in tracks:
    track.assign_to_nodes()

# Главный цикл
running = True
while running:
    screen.fill(WHITE)
    # draw_grid(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for track in tracks:
                if track.is_hovered(*event.pos):
                    # print(track.node1.outs)
                    track.toggle()

    mouse_pos = pygame.mouse.get_pos()

    for track in tracks:
        track.draw(screen, mouse_pos)

    for row in nodes:
        for node in row:
            node.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
