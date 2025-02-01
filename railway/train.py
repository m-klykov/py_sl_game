import pygame
import math
from node import Node
from vagon import Vagon

class Train:
    def __init__(self, start_node, color, vagon_count=2):
        self.is_active = True # Поезд активен
        self.color = color  # Цвет поезда
        self.start_node = start_node  # Исходная станция
        self.vagons = []
        for i in range(vagon_count):
            vagon = Vagon(self,start_node, color, i==0)
            if i==0 and vagon_count>1:
                vagon.is_pre_tail = True

            self.vagons.append(vagon)


    def update(self, nodes):
        """Обновляет положение поезда."""
        if not self.is_active:
            return

        for vagon in self.vagons:
            vagon.update(nodes)

    def reverse_direction(self):
        """Разворачиваем поезд по команде первого вагона"""
        first_vagon = None
        last_vagon = None
        need_pretail = False
        for vagon in self.vagons:
            vagon.is_pre_tail = False

            if vagon.is_active:
                vagon.reverse_direction()
                if not first_vagon:
                    first_vagon = vagon
                last_vagon = vagon
            else:
                if first_vagon:
                    # у нас неактивный элемент после активных,
                    # это возможно недосозданый хвост
                    need_pretail = True

        if not first_vagon:
            return

        if first_vagon.is_head:
            # поезд ехал носом
            first_vagon.is_head = False
            last_vagon.is_head = True
        else:
            #поезд ехал задом
            last_vagon.is_head = False
            first_vagon.is_head = True
            if need_pretail:
                last_vagon.is_pre_tail = True


    def vagon_out(self,sor_vagon):
        """головной вагон доехал до целм"""
        first_vagon = None
        last_vagon = None
        for vagon in self.vagons:
            if vagon.is_active:
                if not first_vagon:
                    first_vagon = vagon
                last_vagon = vagon

        if not first_vagon or first_vagon==last_vagon:
            # поезд уехад
            self.is_active = False
        else:
            sor_vagon.is_active = False
            sor_vagon.is_head = False

            new_first_vagon = None
            new_last_vagon = None
            for vagon in self.vagons:
                if vagon.is_active:
                    if not new_first_vagon:
                        new_first_vagon = vagon
                    new_last_vagon = vagon

            if first_vagon == sor_vagon:
                # едем передом
                new_first_vagon.is_head = True
            else:
                new_last_vagon.is_head = True


    def vagon_len_out(self,sor_vagon):
        """вагон прошел путь на длину вагона от начала отрезка"""

        first_unactive = None
        unact_cnt = 0
        for vagon in self.vagons:
            if not vagon.is_active:
                unact_cnt += 1
                if not first_unactive:
                    first_unactive = vagon

        if first_unactive:
            first_unactive.is_active = True
            sor_vagon.is_pre_tail = False
            if unact_cnt>1:
                first_unactive.is_pre_tail = True


    def draw(self, screen, cell_size):
        """Рисует поезд."""
        if not self.is_active:
            return

        for vagon in self.vagons:
            vagon.draw(screen, cell_size)
