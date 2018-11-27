import numpy as np
from enum import Enum, IntEnum
import random
from .fastbee import fast_tick, fast_recalculate_heat, fast_swarms
from .helpers import check_bound, check_type


class MapConst:
    """
    Map constansts
    """
    EMPTY = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    WALL = 5
    HEATER = 6
    COOLER = 7
    CHOOSE = -1


class BeeClust:
    """
    Beeclust class
    """
    def __init__(self, map, p_changedir=0.2, p_wall=0.8, p_meet=0.8, k_temp=0.9,
                 k_stay=50, T_ideal=35, T_heater=40, T_cooler=5, T_env=22, min_wait=2):
        """
        Init
        """

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
        Return list of bees in map.
        """
        indices = np.where((self.map < 0)
                              | ((1 <= self.map) & (self.map <= 4)))
        return list(zip(indices[0], indices[1]))

    @property
    def score(self):
        """
        Compute bees score.
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
        Return swarms of bees in map.
        """
        return fast_swarms(self.map)

    def tick(self):
        """
        Do one simulation step.
        """
        moved, self.map = fast_tick(self.map, self.heatmap, 
            self.p_changedir, self.p_wall, 
            self.p_meet, self.T_ideal, 
            self.k_stay, self.min_wait)
        return moved

    def forget(self):
        """
        All bees will forget their waiting times and the direction they were going through.
        n the next step they randomly draw the direction and move in again in the next step.
        """
        self.map[((self.map <= -1) | (self.map == MapConst.UP) |
                  (self.map == MapConst.DOWN) | (self.map == MapConst.RIGHT) | (self.map == MapConst.LEFT))] = -1

    def recalculate_heat(self):
        """
        Forcing b.heatmap to be recalculated (for example, after changing b.map without creating a new simulation)
        """
        self.heatmap = fast_recalculate_heat(self.map, self.T_env, self.T_cooler, self.T_heater, self.k_temp)
