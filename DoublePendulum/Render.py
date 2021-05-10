""" Draw the connected pendulum """
from __future__ import division

import enum

from Draw import Point, Draw
import Calculation as Calculation
import pygame as pg
import math

fps = 45

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
dark_blue = (0, 0, 128)
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 200, 200)
grey = (84, 84, 84)

width = 800
height = 600

pend_indent = width / 3
p11 = Point(-pend_indent, 0)
p21 = Point(0, 0)
p31 = Point(pend_indent, 0)

pillar_center = Point(0, -150)
pillar_edge = 30
pillar_point = Point(pillar_center.x, pillar_center.y - pillar_edge * math.sqrt(3) / 3)
grip_radius = 5
arm_width = 100

color_circle1 = [red, pink]
color_circle2 = [green, blue]
color_line = [black, dark_blue]

pend_radius = 10


class RenderMode(enum.Enum):
    NORMAL_MODE = 0
    SMALL_ANGLES = 1
    DUO_MODE = 2


def main(phi1, phi2, angular_speed1, angular_speed2, weight1, weight2, length1, length2, betta, mode: RenderMode):
    """ Run the program """

    phi1 *= math.pi / 180
    phi2 *= math.pi / 180

    angular_speed1 *= math.pi / 180
    angular_speed2 *= math.pi / 180

    arm1 = Calculation.InitState(phi1, length1, weight1, angular_speed1)
    arm2 = Calculation.InitState(phi2, length2, weight2, angular_speed2)

    dt = 1 / fps

    pendulums = None
    its = 0

    if mode == RenderMode.SMALL_ANGLES:
        pendulums = [Calculation.SmallAnglesPendulums(dt, arm1, arm2, betta)]
        its = 1
    elif mode == RenderMode.NORMAL_MODE:
        pendulums = [Calculation.NormalPendulums(dt, arm1, arm2, betta)]
        its = 1
    elif mode == RenderMode.DUO_MODE:
        pendulums = [Calculation.SmallAnglesPendulums(dt, arm1, arm2, betta),
                     Calculation.NormalPendulums(dt, arm1, arm2, betta)]
        its = 2

    screen = pg.display.set_mode((width, height))

    canvas = Draw(screen, width / 2, height / 5)

    pg.init()
    clk = pg.time.Clock()
    end = False

    phis1, phis2 = [phi1], [phi2]
    phis1_dot, phis2_dot = [angular_speed1], [angular_speed2]

    t = [0.0]

    track = [[],[]]
    end_arm2 = [None, None]
    last_pos = [[],[]]

    while not end:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end = True
        screen.fill(white)

        canvas.draw_isosceles_triangle(red, pillar_center, pillar_edge)

        for j in range(its):
            phis = pendulums[j].get_next_state()[0].reshape((2,))

            phis1.append(phis[0])
            phis2.append(phis[1])

            phis_dot = pendulums[j].get_next_state()[1].reshape((2,))
            phis1_dot.append(phis_dot[0])
            phis2_dot.append(phis_dot[1])

            t.append(t[-1] + dt)

            last_pos[j] = end_arm2[j]
            end_arm1 = pillar_point + Point(math.sin(phis[0]) * length1, -math.cos(phis[0]) * length1)
            end_arm2[j] = end_arm1 + Point(math.sin(phis[1]) * length2, -math.cos(phis[1]) * length2)

            if last_pos[j] is not None:
                track[j].append(end_arm2[j])
                for i in range(track[j].__len__() - 1):
                    canvas.draw_antialiased_line(color_circle2[j], track[j][i], track[j][i + 1])

            canvas.draw_circle(color_circle1[j], end_arm1, grip_radius, 0)
            canvas.draw_circle(color_circle2[j], end_arm2[j], grip_radius, 0)

            canvas.draw_line(color_line[j], pillar_point, end_arm1, arm_width)
            canvas.draw_line(color_line[j], end_arm1, end_arm2[j], arm_width)

        pg.display.update()
        clk.tick(fps)

if __name__ == '__main__':
    phi1 = 10
    phi2 = 10
    angular_speed1 = 10
    angular_speed2 = 10
    weight1 = 1000
    weight2 = 10
    length1 = 100
    length2 = 100
    betta = 10000

    duration = 1000

    main(phi1, phi2, angular_speed1, angular_speed2, weight1, weight2, length1, length2, betta, RenderMode.DUO_MODE)
