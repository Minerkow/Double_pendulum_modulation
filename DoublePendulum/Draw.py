""" Some classes for drawing """
from __future__ import division
import pygame as pg
import math


class Point:
    """ 2D point """

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

    def __mul__(self, k):
        return Point(self.x * k, self.y * k)

    def __truediv__(self, k):
        return Point(self.x / k, self.y / k)

    def __call__(self):
        return (self.x, self.y)

    def __str__(self):
        return '({0},{1})'.format(self.x, self.y)


class ScreenTrans:
    """ Screen transformation """

    def __init__(self, piv_x, piv_y):
        """ piv_x, piv_y: Coordinates of the point (in the screen reference) to
        be considered the origin """
        self.piv_x = piv_x
        self.piv_y = piv_y

    def trans(self, p):
        """ ScreenPoint to point """
        return Point(p.x - self.piv_x, self.piv_y + p.y)

    def itrans(self, p):
        """ Point to ScreenPoint """
        return Point(p.x + self.piv_x, self.piv_y - p.y)


class Draw:
    """ Draw on screen using an arbitrary frame of reference """

    def __init__(self, screen, piv_x, piv_y):
        """ piv_x, piv_y: Coordinates of the point (in the screen reference) to
        be considered the origin """
        self.screen = screen
        self.T = ScreenTrans(piv_x, piv_y)

    def draw_line(self, color, p1: Point, p2: Point, width):
        """ Draw a line segment from p1 to p2, given color """
        _p1 = self.T.itrans(p1)
        _p2 = self.T.itrans(p2)
        pg.draw.line(self.screen, color, _p1(), _p2(), 2)

    def draw_circle(self, color, center, radius, width):
        """ Draw a circle given center, radius and color """
        _c = self.T.itrans(center)
        pg.draw.circle(self.screen, color, _c(), radius, width)

    def draw_rectangle(self, color, left_angle: Point, width, height):
        """Draw a rectangle given left top angle, width, height and color"""
        _lta = self.T.itrans(left_angle)
        pg.draw.rect(self.screen, color, (_lta()[0], _lta()[1], width, height))

    def draw_isosceles_triangle(self, color, center: Point, edge):
        """Draw isosceles triangle"""
        _c = self.T.itrans(center)
        R = edge * math.sqrt(3) / 3
        pg.draw.polygon(self.screen, color,
                        [(_c.x, _c.y + R), (_c.x - edge / 2, _c.y - R / 2), (_c.x + edge / 2, _c.y - R / 2)])

    def draw_antialiased_line(self, color, last_pos: Point, current_pos: Point):
        """"""
        _p1 = self.T.itrans(last_pos)
        _p2 = self.T.itrans(current_pos)
        pg.draw.line(self.screen, color, (_p1.x, _p1.y), (_p2.x, _p2.y), width=4)

