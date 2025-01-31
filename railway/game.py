import pygame
import json
import math
from node import Node
from track import Track, CurvedTrack
from train import Train

class Game:
    def __init__(self, grid_size_x, grid_size_y, cell_size):
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        self.cell_size = cell_size
        self.screen_size_x = grid_size_x * cell_size
        self.screen_size_y = grid_size_y * cell_size
        self.construction_mode = True
        self.nodes = [[Node(x, y) for y in range(grid_size_y)] for x in range(grid_size_x)]
        self.tracks = []
        self.trains = []
        self.init_tracks()
        self.load_state()

    def init_tracks(self):
        """Инициализирует пути между узлами."""
        for x in range(self.grid_size_x):
            for y in range(self.grid_size_y):
                if x < self.grid_size_x - 1:
                    self.tracks.append(Track(self.nodes[x][y], self.nodes[x + 1][y]))
                if y < self.grid_size_y - 1:
                    self.tracks.append(Track(self.nodes[x][y], self.nodes[x][y + 1]))
                if x < self.grid_size_x - 1 and y < self.grid_size_y - 1:
                    self.tracks.append(CurvedTrack(self.nodes[x][y], self.nodes[x + 1][y + 1], 'hor'))
                    self.tracks.append(CurvedTrack(self.nodes[x][y], self.nodes[x + 1][y + 1], 'vert'))
                if x < self.grid_size_x - 1 and y > 0:
                    self.tracks.append(CurvedTrack(self.nodes[x][y], self.nodes[x + 1][y - 1], 'hor'))
                    self.tracks.append(CurvedTrack(self.nodes[x][y], self.nodes[x + 1][y - 1], 'vert'))

        for track in self.tracks:
            track.assign_to_nodes()

    def save_state(self, filename="save.json"):
        """Сохраняет состояние игры в файл."""
        data = {
            "nodes": [],
            "tracks": [],
            "trains": [],
            "construction_mode": self.construction_mode
        }

        # Сохраняем узлы
        for row in self.nodes:
            for node in row:
                node_data = {
                    "x": node.x,
                    "y": node.y,
                    "color": node.color
                }
                data["nodes"].append(node_data)

        # Сохраняем пути
        for track in self.tracks:
            track_data = {
                "node1": [track.node1.x, track.node1.y],
                "node2": [track.node2.x, track.node2.y],
                "enabled": track.enabled,
                "type": "CurvedTrack" if isinstance(track, CurvedTrack) else "Track",
                "direction": track.direction if isinstance(track, CurvedTrack) else ''
            }
            data["tracks"].append(track_data)

        # Сохраняем поезда
        for train in self.trains:
            train_data = {
                "start_node": [train.start_node.x, train.start_node.y],
                "color": train.color,
                "progress": train.progress,
                "is_active": train.is_active
            }
            data["trains"].append(train_data)

        # Записываем данные в файл
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_state(self, filename="save.json"):
        """Загружает состояние игры из файла."""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return  # Файл не существует

        # Восстанавливаем узлы
        for node_data in data["nodes"]:
            x, y = node_data["x"], node_data["y"]
            node = self.nodes[x][y]
            node.color = node_data["color"]

        # Восстанавливаем пути
        self.tracks.clear()
        for track_data in data["tracks"]:
            node1 = self.nodes[track_data["node1"][0]][track_data["node1"][1]]
            node2 = self.nodes[track_data["node2"][0]][track_data["node2"][1]]
            if track_data["type"] == "CurvedTrack":
                track = CurvedTrack(node1, node2, track_data["direction"])
            else:
                track = Track(node1, node2)
            track.enabled = track_data["enabled"]
            track.assign_to_nodes()
            self.tracks.append(track)

        # Восстанавливаем поезда
        self.trains.clear()
        for train_data in data["trains"]:
            start_node = self.nodes[train_data["start_node"][0]][train_data["start_node"][1]]
            train = Train(start_node, train_data["color"])
            train.progress = train_data["progress"]
            train.is_active = train_data["is_active"]
            self.trains.append(train)

        # Восстанавливаем режим
        self.construction_mode = data["construction_mode"]

    def run(self):
        """Запускает игру."""
        pygame.init()
        screen = pygame.display.set_mode((self.screen_size_x, self.screen_size_y))
        pygame.display.set_caption("Railway Simulator")
        clock = pygame.time.Clock()

        running = True
        while running:
            screen.fill((255, 255, 255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_state()
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.construction_mode = not self.construction_mode
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.construction_mode:
                        # В режиме конструирования переключаем пути
                        for track in self.tracks:
                            if track.is_hovered(*pygame.mouse.get_pos(), self.cell_size):
                                track.toggle()
                    else:
                        # В режиме управления переключаем стрелки и семафоры
                        for row in self.nodes:
                            for node in row:
                                node.handle_click(*pygame.mouse.get_pos(), self.cell_size)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Правая кнопка мыши
                    if not self.construction_mode:
                        for row in self.nodes:
                            for node in row:
                                if node.is_terminal() and math.hypot(node.getCanvasX(self.cell_size) - pygame.mouse.get_pos()[0],
                                                                     node.getCanvasY(self.cell_size) - pygame.mouse.get_pos()[1]) < 10:
                                    # Создаём поезд с цветом узла
                                    self.trains.append(Train(node, node.color))

            mouse_pos = pygame.mouse.get_pos()

            if self.construction_mode:
                # В режиме конструирования отображаем все пути
                for track in self.tracks:
                    track.draw(screen, mouse_pos, self.construction_mode, self.cell_size)
            else:
                # В режиме управления отображаем только активные пути
                for track in self.tracks:
                    if track.enabled:
                        track.draw(screen, mouse_pos, self.construction_mode, self.cell_size)

            for row in self.nodes:
                for node in row:
                    node.draw(screen, self.construction_mode, self.cell_size)

            # Обновляем и рисуем поезда
            for train in self.trains:
                train.update(self.nodes)
                train.draw(screen, self.cell_size)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()