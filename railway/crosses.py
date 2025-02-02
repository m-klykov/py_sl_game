import pygame
from node import Node

T_CRAFT = 3

class Crosses:
    def __init__(self, nodes, cell_size):

        self.matrixes = []
        self.crashes = 0
        self.last_point = None
        self.last_train = None

        # чекпоинты по узлам
        mat = CrossMatrix()
        for row in nodes:
            x = row[0].getCanvasX(cell_size)
            mat.xs.append(x)

        for node in nodes[0]:
            y = node.getCanvasY(cell_size)
            mat.ys.append(y)

        self.matrixes.append(mat)

        # промежутки по горизонталям
        mat = CrossMatrix()
        last_x = 0;
        for row in nodes:
            x = row[0].getCanvasX(cell_size)
            if last_x:
                mat.xs.append((last_x + x) // 2)
            last_x = x

        last_y = 0
        for node in nodes[0]:
            y = node.getCanvasY(cell_size)
            # mat.ys.append(y)
            if last_y:
                mat.ys.append(last_y + cell_size //8)
                mat.ys.append(y - cell_size //8)
            last_y = y

        self.matrixes.append(mat)

        # промежутки по вертикалям
        mat = CrossMatrix()
        last_x = 0
        for row in nodes:
            x = row[0].getCanvasX(cell_size)
            # mat.xs.append(x)
            if last_x:
                mat.xs.append(last_x + cell_size // 8)
                mat.xs.append(x - cell_size // 8)
            last_x = x

        last_y = 0;
        for node in nodes[0]:
            y = node.getCanvasY(cell_size)
            if last_y:
                mat.ys.append((last_y + y) // 2)
            last_y = y

        self.matrixes.append(mat)





    # обнулить карту занятости
    def clear(self):
        for matrix in self.matrixes:
            matrix.bisy = {}

        self.crashes = 0
        self.last_point = None
        self.last_train = None

    def new_train(self, train):
        self.last_point = None
        self.last_train = train

    def add_point(self, x, y):
        if self.last_point:
            for matr in self.matrixes:
                cr = matr.add_line(self.last_train, self.last_point, (x,y))
                self.crashes += cr
        self.last_point = (x,y)

    def draw(self, screen):
        for matrix in self.matrixes:
            matrix.draw(screen)


class CrossMatrix:
    def __init__(self):
        self.xs = []
        self.ys = []
        self.bisy = {} # по по ключу (x,y) храним поезд
        self.crashes = {} # по по ключу (x,y) храним место аварии

    def draw(self, screen):
        for x in self.xs:
            for y in self.ys:
                if (x,y) in self.crashes:
                    color = (80, 10, 10);
                    pygame.draw.circle(screen, color, (x, y), 12)
                else:
                    color = (255,255,255);
                    # color = (10,10,10);
                    if (x,y) in self.bisy:
                        color = self.bisy[(x,y)].color
                    pygame.draw.circle(screen, color, (x, y), 3)

    # в масива xs или ys найти значение между v1 и v2
    def find_by_dim(self,arr, v1, v2):
        v1, v2 = min(v1,v2),max(v1,v2)
        for v in arr:
            if v1-0.2 < v < v2+0.2:
                return v
        return None

    def add_line(self, train, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        x = self.find_by_dim(self.xs,x1,x2)
        y = self.find_by_dim(self.ys,y1,y2)

        if not x or not y:
            return 0

        key = (x,y)
        if key in self.crashes:
            if train.t_type == T_CRAFT:
                del self.crashes[key]
                return 0
            else:
                # поезд наехал на место ваврии
                train.do_crash()
                return 1

        if key in self.bisy:
            old_train = self.bisy[key]

            if train != old_train:
                # столкнулось 2 поезда
                train.do_crash()
                old_train.do_crash()
                self.crashes[(x,y)] = 1
                return 2
        else:
            self.bisy[key] = train

        return 0


