""" Calculate the double pendulum angles and speeds """
from __future__ import division

import copy
import math

import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as plt

g = 9.8


class InitState:
    def __init__(self, phi: float = 0, length: float = 1.0, weight: float = 1, angular_speed: float = 1.0):
        self.phi = phi
        self.length = length
        self.weight = weight
        self.angular_speed = angular_speed


class NormalPendulums:
    def __init__(self, time_step, arm1: InitState, arm2: InitState, betta: float = 0.1):
        """"""
        self.dt = time_step
        self.phi = np.array([[arm1.phi, arm2.phi]]).transpose()
        self.angular_speed = np.array([[arm1.angular_speed, arm2.angular_speed]]).transpose()
        self.angular_speed_sq = np.array([[arm2.angular_speed**2, arm1.angular_speed**2]]).transpose()

        m1 = arm1.weight
        m2 = arm2.weight
        a = arm1.length
        b = arm2.length
        phi1 = arm1.phi
        phi2 = arm2.phi

        self.A = [[(m1 + m2)*a**2, m2*a*b*np.cos(phi1-phi2)],
                  [m2*a*b*np.cos(phi1-phi2), m2*b**2]]
        self.B = [[betta, 0],
                  [0, betta]]
        self.C = [[g * a * (m1 + m2), 0],
                  [0, g * b * m2]]
        self.d = -m2*a*b*math.sin(phi2 - phi1)

    def __acc(self):
        """"""
        return -(np.dot(np.dot(LA.inv(self.A), self.B), self.angular_speed) +
                 np.dot(np.dot(LA.inv(self.A), self.C), np.sin(self.phi)) +
                 self.d*np.dot(LA.inv(self.A), self.angular_speed_sq))

    def get_next_state(self):
        """ Numerically solve the system angles for a single time step """
        acc = self.__acc()
        self.angular_speed = self.angular_speed + acc * self.dt
        self.phi = self.phi + self.angular_speed * self.dt

        return self.phi, self.angular_speed

    def get_current_state(self):
        return self.phi, self.angular_speed


class SmallAnglesPendulums:
    def __init__(self, time_step, arm1: InitState, arm2: InitState, betta: float = 0.1):

        self.dt = time_step
        self.phi = np.array([[arm1.phi, arm2.phi]]).transpose()
        self.angular_speed = np.array([[arm1.angular_speed, arm2.angular_speed]]).transpose()
        self.arm1 = arm1
        self.arm2 = arm2
        self.betta = betta

        m1 = arm1.weight
        m2 = arm2.weight
        a = arm1.length
        b = arm2.length

        self.A = [[(m1 + m2) * a ** 2, m2 * a * b],
                  [m2 * a * b, m2 * b ** 2]]
        self.B = [[0, 0],
                  [self.betta*a, self.betta*b]]
        self.C = [[g * a * (m1 + m2), 0],
                  [0, g * b * m2]]



    def __acc(self):
        """compute the phi_dot_dot"""
        return -(np.dot(np.dot(LA.inv(self.A), self.B), self.angular_speed) +
                 np.dot(np.dot(LA.inv(self.A), self.C), self.phi))

    def get_next_state(self):
        """ Numerically solve the system angles for a single time step """
        acc = self.__acc()
        self.angular_speed = self.angular_speed + acc * self.dt
        self.phi = self.phi + self.angular_speed * self.dt

        return self.phi, self.angular_speed

    def get_current_state(self):
        return self.phi, self.angular_speed

    def get_current_energy(self):
        return 0.5*(self.angular_speed.transpose()@self.A@self.angular_speed +
                 self.phi.transpose()@self.C@self.phi)[0][0]

    def get_timestep(self):
        return self.dt

    def attenuation_analysis(self, bettaBegin: float = 0.1, bettaEnd: float = 0.2, bettaStep: float = 0.01):
        time = []
        betta = []
        curBetta = bettaBegin
        while curBetta < bettaEnd:
            pend = SmallAnglesPendulums(self.dt, self.arm1, self.arm2, curBetta)
            time.append(get_attenuation_time(pend))
            betta.append(curBetta)
            curBetta += bettaStep

        time = np.array(time)
        betta = np.array(betta)
        plt.plot(betta, time)
        plt.xlabel(r'$\beta$', rotation=0)
        plt.ylabel(r'$time$', rotation=90)
        plt.show()


def get_attenuation_time(pend: SmallAnglesPendulums):
    E_0 = pend.get_current_energy()
    E = E_0
    time = 0
    dt = 1 / 60
    while E_0/E < math.e:
        pend.get_next_state()
        E = pend.get_current_energy()
        time += dt
    return time


def show_plots(pendulums, duration: float = 40.0):
    """ Make plots without animation """
    t = np.arange(0, duration, pendulums.dt)

    phis, phis_dot = pendulums.get_current_state()
    phis.reshape((2,))
    phis_dot.reshape((2,))

    phis1, phis2 = [phis[0]], [phis[1]]
    phis1_dot, phis2_dot = [phis_dot[0]], [phis_dot[1]]

    size = t.size
    i = 1
    while i < size:
        phis, phis_dot = pendulums.get_next_state()
        phis.reshape((2,))
        phis_dot.reshape((2,))

        phis1.append(phis[0])
        phis2.append(phis[1])

        phis1_dot.append(phis_dot[0])
        phis2_dot.append(phis_dot[1])

        i += 1

    phis1 = np.array(phis1)
    phis2 = np.array(phis2)

    phis1_dot = np.array(phis1_dot)
    phis2_dot = np.array(phis2_dot)

    fig, (phi1_plt, phi1_dot_plt, phi2_plt, phi2_dot_plt) = plt.subplots(4, 1)

    fig.suptitle(r'$\varphi$ and $\dot \varphi$ plots')

    phi1_plt.plot(t, phis1)
    phi1_plt.set_ylabel(r'$\varphi_1$', rotation=0)

    phi1_dot_plt.plot(t, phis1_dot)
    phi1_dot_plt.set_ylabel(r'$\dot \varphi_1$', rotation=0)

    phi2_plt.plot(t, phis2)
    phi2_plt.set_ylabel(r'$\varphi_2$', rotation=0)

    phi2_dot_plt.plot(t, phis2_dot)
    phi2_dot_plt.set_ylabel(r'$\dot \varphi_2$', rotation=0)

    plt.show()

