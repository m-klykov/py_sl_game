import pygame
import json
import math
import random
from node import Node
from railway.crosses import T_CRAFT
from track import Track, CurvedTrack
from train import Train
from crosses import Crosses

class Game:
    def __init__(self, grid_size_x, grid_size_y, cell_size):
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        self.cell_size = cell_size
        self.screen_size_x = grid_size_x * cell_size
        self.screen_size_y = grid_size_y * cell_size
        self.construction_mode = True
        self.nodes = [[Node(x, y) for y in range(grid_size_y)] for x in range(grid_size_x)]
        self.crosses = Crosses(self.nodes,cell_size)
        self.tracks = []
        self.trains = []
        self.colors = [
            (255, 0, 0),  # Красный
            (0, 255, 0),  # Зелёный
            (0, 0, 255),  # Синий
            (255, 255, 0),  # Жёлтый
            (255, 0, 255),  # Пурпурный
            (0, 255, 255),  # Голубой
            (128, 0, 128),  # Фиолетовый
            (255, 165, 0)  # Оранжевый
        ]
        self.init_tracks()
        self.init_stations()  # Инициализация станций
        self.tr_started = 0 # обшее число поездов
        # self.load_state()

    def init_stations(self):
        """Выбирает 8 случайных узлов по периметру и назначает им цвета."""
        perimeter_nodes = []

        # Собираем узлы по периметру
        for x in range(self.grid_size_x):
            for y in range(self.grid_size_y):
                if x == 0 or x == self.grid_size_x - 1 or y == 0 or y == self.grid_size_y - 1:
                    perimeter_nodes.append(self.nodes[x][y])

        # Выбираем 8 случайных узлов из периметра
        self.stations = random.sample(perimeter_nodes, 8)

        for i, node in enumerate(self.stations):
            node.color = self.colors[i]  # Назначаем уникальный цвет
            node.is_station = True  # Помечаем узел как станцию
            good_tracks = []
            for dir in node.outs:
                for track in node.outs[dir]:
                    oth_node = track.get_other_node(node)
                    x, y = oth_node.x, oth_node.y
                    if (x > 0 and x < self.grid_size_x - 1
                    and y>0 and  y < self.grid_size_y - 1):
                        good_tracks.append(track)
            track = random.choice(good_tracks)
            track.enabled = True
            track.blocked = True

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
                    "color": node.color,
                    "is_station": node.is_station
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
            node.is_station = node_data["is_station"]

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

    def startCraftTrain(self,node):
        train_color = (80,80,20)
        self.trains.append(Train(node, train_color, 2, T_CRAFT))

    # Запустить очередной случайны поезд
    def startRandomNexrTrain(self):
        max_statuin_cnt = self.tr_started // 5 + 2
        colors = []
        stations = []
        cnt = 0
        for node in self.stations:
            if cnt>=max_statuin_cnt:
                break;
            stations.append(node)
            colors.append(node.color)
            cnt += 1

        cur_station = random.choice(stations)
        if cur_station.is_station_bisy():
            return

        available_colors = [color for color in colors if color != cur_station.color]
        train_color = random.choice(available_colors)
        self.trains.append(Train(cur_station, train_color, random.randint(2, 5)))
        self.tr_started += 1

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
                    # self.save_state()
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
                                if (node.is_station and node.is_terminal()
                                and math.hypot(
                                        node.getCanvasX(self.cell_size) - pygame.mouse.get_pos()[0],
                                        node.getCanvasY(self.cell_size) - pygame.mouse.get_pos()[1]) < 10):
                                    # Создаём поезд случайного цвета, отличного от цвета станции
                                    self.startCraftTrain(node)

            mouse_pos = pygame.mouse.get_pos()

            if self.construction_mode:
                # В режиме конструирования отображаем все пути
                for track in self.tracks:
                    track.draw(screen, mouse_pos, self.construction_mode, self.cell_size)
            else:
                # В режиме управления отображаем только активные пути

                if not self.trains or random.random() < 0.001 / (len(self.trains)+1):
                    self.startRandomNexrTrain()

                for track in self.tracks:
                    if track.enabled:
                        track.draw(screen, mouse_pos, self.construction_mode, self.cell_size)
                    track.bisy = False

            for row in self.nodes:
                for node in row:
                    node.draw(screen, self.construction_mode, self.cell_size)
                    if not self.construction_mode:
                        node.blocked_dirs = {} #обнуление блоеироаок стрелок

            self.crosses.clear()

            # Обновляем и рисуем поезда
            for train in self.trains:
                if not self.construction_mode:
                    train.update(self.nodes)
                    if not train.is_active:
                        self.trains.remove(train)

                self.crosses.new_train(train)
                train.draw(screen, self.cell_size, self.crosses)

            self.crosses.draw(screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()