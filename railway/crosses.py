import pygame
from node import Node

class Crosses:
    def __init__(self, nodes, cell_size):

        self.matrixes = []
        self.crashes = []
        self.last_point = None
        self.last_train = None

        mat = CrossMatrix()
        for row in nodes:
            x = row[0].getCanvasX(cell_size)
            mat.xs.append(x)

        for node in nodes[0]:
            y = node.getCanvasY(cell_size)
            mat.ys.append(y)

        self.matrixes.append(mat)


    # обнулить карту занятости
    def clear(self):
        for matrix in self.matrixes:
            matrix.bisy = {}

        self.crashes = []
        self.last_point = None
        self.last_train = None

    def new_train(self, train):
        self.last_point = None
        self.last_train = train

    def add_point(self, x, y):
        if self.last_point:
            for matr in self.matrixes:
                cr = (matr.
                      add_line(self, self.last_train, self.last_point, (x,y)))
                if cr:
                    self.crashes.append(cr)
        self.last_point = (x,y)

    def draw(self, screen):
        for matrix in self.matrixes:
            matrix.draw(screen)


class CrossMatrix:
    def __init__(self):
        self.xs = []
        self.ys = []
        self.bisy = {} # по по ключу (x,y) храним поезд

    def draw(self, screen):
        for x in self.xs:
            for y in self.ys:
                color = (255,255,255);
                if (x,y) in self.bisy:
                    color = self.bisy[(x,y)].color
                pygame.draw.circle(screen, color, (x, y), 3)

    # в масива xs или ys найти значение между v1 и v2
    def find_by_dim(self,arr, v1, v2):
        v1, v2 = min(v1,v2),max(v1,v2)
        for v in arr:
            if v1 < v < v2:
                return v
        return None

    def add_line(self, train, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        x = self.find_by_dim(self.xs,x1,x2)
        y = self.find_by_dim(self.ys,y1,y2)

        key = (x,y)
        if key in self.bisy:
            old_train = self.bisy[key]
            if train != old_train:
                return {
                    'x':x,
                    'y':y,
                    'train1':old_train,
                    'train2':train,
                }
        else:
            self.bisy[key] = train

        return None


