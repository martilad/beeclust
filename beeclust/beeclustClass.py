import numpy as np
from enum import Enum, IntEnum
import random
from beeclust.fastbee import fast_tick, fast_recalculate_heat, fast_swarms
from beeclust.helpers import check_bound, check_type


class MapConst:
    """
    Constants use in map.
    """
    EMPTY = 0
    """Empty possition"""
    UP = 1
    """Bee which moves up"""
    RIGHT = 2
    """Bee which moves right"""
    DOWN = 3
    """Bee which moves down"""
    LEFT = 4
    """Bee which moves left"""
    WALL = 5
    """On this position is wall, which is thermal insulator"""
    HEATER = 6
    """On the position is the heater"""
    COOLER = 7
    """On the position is the cooler"""
    CHOOSE = -1
    """Bee which select new direction in the next tick"""


class BeeClust:
    """
    Beeclust class which simulated beeclust algorithm. 
    Class can be imported and simulation used in practice for working with simple autonomous robots. 

    map - 2D numpy array of simulation map

    p_changedir - probability that bee change the direction of move

    p_wall - probability of stop, when bee meet wall, heater or cooler

    p_meet - probalitity if stop, when bee meet other bee

    k_temp - the thermal conductivity of the environment

    k_stay - constant for counting time to stay

    T_ideal - temperature which bee prefer

    T_heater - temperature of heater

    T_cooler - temperature of cooler

    T_env - temperature of enviroment (temperature when there is no heaters and coolers)
    
    min_wait - minimum wait time when bee stop
    """
    def __init__(self, map, p_changedir=0.2, p_wall=0.8, p_meet=0.8, k_temp=0.9,
                 k_stay=50, T_ideal=35, T_heater=40, T_cooler=5, T_env=22, min_wait=2):

        check_type(map, [np.ndarray], "map")
        if len(map.shape) != 2:
            raise ValueError("map dim error, not 2D array")
        check_type(p_changedir, [float, int], "p_changedir")
        check_bound(p_changedir, 0, 1, "p_changedir must be positive value between 0-1 -> represent probability.")
        check_type(p_wall, [float, int], "p_wall")
        check_bound(p_wall, 0, 1, "p_wall must be positive value between 0-1 -> represent probability.")
        check_type(p_meet, [float, int], "p_meet")
        check_bound(p_meet, 0, 1, "p_meet must be positive value between 0-1 -> represent probability.")
        check_type(k_temp, [float, int], "k_temp")
        check_bound(k_temp, 0, None, "k_temp must be positive.")
        check_type(k_stay, [float, int], "k_stay")
        check_bound(k_stay, 0, None, "k_stay must be positive.")
        check_type(T_ideal, [float, int], "T_ideal")
        check_type(T_heater, [float, int], "T_heater")
        check_type(T_cooler, [float, int], "T_cooler")
        check_type(T_env, [float, int], "T_env")
        check_type(min_wait, [float, int], "min_wait")
        check_bound(min_wait, 0, None, "min_wait must be positive.")
        if T_heater < T_env:
            raise ValueError("T_heater must be greater or equal than T_env.")
        if T_cooler > T_env:
            raise ValueError("T_cooler must be lower or equal than T_env.")

        self.p_changedir = p_changedir
        self.p_wall = p_wall
        self.p_meet = p_meet
        self.k_temp = k_temp
        self.k_stay = k_stay
        self.T_ideal = T_ideal
        self.T_heater = T_heater
        self.T_cooler = T_cooler
        self.T_env = T_env
        self.min_wait = min_wait
        self.map = map.astype(np.int64)
        self.heatmap = None
        self.recalculate_heat()

    @property
    def bees(self):
        """
        Return list of bees positions in map as python list of lists.
        """
        indices = np.where((self.map < 0)
                              | ((1 <= self.map) & (self.map <= 4)))
        return list(zip(indices[0], indices[1]))

    @property
    def score(self):
        """
        Compute and return bees score. Score is represent as the average temperature of bees.
        """
        score = 0.
        cnt = 0
        for bee in self.bees:
            score += self.heatmap[bee]
            cnt += 1
        return score / cnt if cnt > 0 else 0

    @property
    def swarms(self):
        """
        Return swarms of bees in map. This is clums of bees. Is returned as list of lists of tuples. 
        Swarms are clumps of bees in four direction.
        """
        return fast_swarms(self.map)

    def tick(self):
        """
        Do one simulation step. Bees move or stop. Return number of bees which moded.
        """
        moved, self.map = fast_tick(self.map, self.heatmap, 
            self.p_changedir, self.p_wall, 
            self.p_meet, self.T_ideal, 
            self.k_stay, self.min_wait)
        return moved

    def recalculate_heat(self):
        """
        Forcing recalculating of heatmap (for example, after creating new map and place to the old simulation)
        """
        self.heatmap = fast_recalculate_heat(self.map, self.T_env, self.T_cooler, self.T_heater, self.k_temp)

    def forget(self):
        """
        All bees will forget their waiting times and the direction they were going through.
        The next step they randomly select the direction.
        """
        self.map[((self.map <= -1) | (self.map == MapConst.UP) |
                  (self.map == MapConst.DOWN) | (self.map == MapConst.RIGHT) | (self.map == MapConst.LEFT))] = -1

