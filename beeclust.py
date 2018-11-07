import numpy as np


# Constants for map
class MapConst:
    EMPTY = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    WALL = 5
    HEATER = 6
    COOLER = 7
    CHOOSE = -1


# Check type of property, and check if it is in list of types.
def check_type(value, t, name):
    if type(value) not in t:
        raise TypeError("{} is not type {}.".format(name, str(t)))


# Check bound of numeric values.
def check_bound(value, min_v, max_v, text):
    if min_v is not None:
        if value < min_v:
            raise ValueError(text)
    if max_v is not None:
        if value > max_v:
            raise ValueError(text)


class BeeClust:
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

        self.p_changedir = float(p_changedir)
        self.p_wall = float(p_wall)
        self.p_meet = float(p_meet)
        self.k_temp = float(k_temp)
        self.k_stay = int(k_stay)
        self.T_ideal = int(T_ideal)
        self.T_heater = int(T_heater)
        self.T_cooler = int(T_cooler)
        self.T_env = int(T_env)
        self.min_wait = int(min_wait)
        self.map = map
        self.heatmap = None
        self.recalculate_heat()

    # Return list of bees in map.
    @property
    def bees(self):
        return [(x, y) for x, y in self.find_points((self.map != MapConst.EMPTY) &
                                                    (self.map != MapConst.WALL) &
                                                    (self.map != MapConst.HEATER) &
                                                    (self.map != MapConst.COOLER))]

    # Compute bees score.
    @property
    def score(self):
        score = 0.
        cnt = 0
        for bee in self.bees:
            score += self.heatmap[bee]
            cnt += 1
        return score / cnt if cnt > 0 else 0

    # Return swarms of bees in map.
    @property
    def swarms(self):
        swarms = []
        s_set = set(self.bees)
        while len(s_set) > 0:
            # Call for each swarm
            swarms.append(self.stepping_on_bees(s_set))
        return swarms

    # Find all bees in one swarm.
    def stepping_on_bees(self, sSet):
        swarm = []
        s = sSet.pop()
        queue = [s]
        swarm.append(s)
        while len(queue) > 0:
            q = queue.pop(0)
            for pos in BeeClust.neighbors(q[0], q[1]):
                if BeeClust.is_in(pos[0], pos[1], self.map.shape[0], self.map.shape[1]) and pos in sSet:
                    queue.append(pos)
                    swarm.append(pos)
                    sSet.remove(pos)
        return swarm

    # Neighbors in map on one step.
    @staticmethod
    def neighbors(x, y):
        return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    # Do one simulation step.
    def tick(self):
        move = 0
        for i, bee in enumerate(self.bees):
            if (self.map[bee] == MapConst.UP or
                    self.map[bee] == MapConst.RIGHT or
                    self.map[bee] == MapConst.LEFT or
                    self.map[bee] == MapConst.DOWN):
                self.change_dir(bee, self.map[bee])
            if self.map[bee] == MapConst.UP:
                move += self.move_to(bee, bee[0] - 1, bee[1], MapConst.UP, MapConst.DOWN, i)
                continue
            if self.map[bee] == MapConst.RIGHT:
                move += self.move_to(bee, bee[0], bee[1] + 1, MapConst.RIGHT, MapConst.LEFT, i)
                continue
            if self.map[bee] == MapConst.LEFT:
                move += self.move_to(bee, bee[0], bee[1] - 1, MapConst.LEFT, MapConst.RIGHT, i)
                continue
            if self.map[bee] == MapConst.DOWN:
                move += self.move_to(bee, bee[0] + 1, bee[1], MapConst.DOWN, MapConst.UP, i)
                continue
            if self.map[bee] == MapConst.CHOOSE:
                self.map[bee] = np.random.choice([MapConst.UP, MapConst.RIGHT, MapConst.LEFT, MapConst.DOWN])
                continue
            if self.map[bee] < -1:
                self.map[bee] += 1
                continue
            print("Something wrong")
        return move

    # Change direction of bee based directions and probability of change direction.
    def change_dir(self, bee, act_dir):
        lst = [MapConst.UP, MapConst.RIGHT, MapConst.LEFT, MapConst.DOWN]
        if np.random.random() < self.p_changedir:
            lst.remove(act_dir)
            self.map[bee] = np.random.choice(lst)

    # Do move on position if correct and empty or do some other action.
    def move_to(self, bee, x, y, act_dir, opt_dir, index):
        if (not BeeClust.is_in(x, y, self.map.shape[0], self.map.shape[1])) or self.map[x][y] == MapConst.WALL or \
                self.map[x][y] == MapConst.HEATER or self.map[x][y] == MapConst.COOLER:
            if np.random.random() < self.p_wall:
                self.map[bee] = -self.time_to_stay(bee)
                return 0
            self.map[bee] = opt_dir
            return 0
        if BeeClust.is_in(x, y, self.map.shape[0], self.map.shape[1]) and self.map[x][y] == MapConst.EMPTY:
            self.map[bee] = 0
            self.map[x][y] = act_dir
            self.bees[index] = (x, y)
            return 1
        else:
            if np.random.random() < self.p_meet:
                self.map[bee] = -self.time_to_stay(bee)
            return 0

    # Counts stop time to stop.
    def time_to_stay(self, bee):
        return max(int(self.k_stay / (1 + abs(self.T_ideal - self.heatmap[bee]))), self.min_wait)

    # All bees will forget their waiting times and the direction they were going through.
    # In the next step they randomly draw the direction and move in again in the next step.
    def forget(self):
        print(self.map)
        self.map[((self.map <= -1) | (self.map == MapConst.UP) |
                  (self.map == MapConst.DOWN) | (self.map == MapConst.RIGHT) | (self.map == MapConst.LEFT))] = -1
        print(self.map)

    # Forcing b.heatmap to be recalculated (for example, after changing b.map without creating a new simulation)
    def recalculate_heat(self):
        self.heatmap = BeeClust.add_points_to_array(
            BeeClust.add_points_to_array(
                BeeClust.add_points_to_array(
                    self.calculate_heat(
                        self.bfs_from_points(self.map.shape, BeeClust.find_points(self.map == MapConst.HEATER)),
                        self.bfs_from_points(self.map.shape, BeeClust.find_points(self.map == MapConst.COOLER))),
                    self.map == MapConst.WALL,
                    np.nan),
                self.map == MapConst.HEATER,
                self.T_heater),
            self.map == MapConst.COOLER,
            self.T_cooler)

    # Change value in array based on mask on new value.
    @staticmethod
    def add_points_to_array(array, mask, value):
        array[mask] = value
        return array

    # Return the coordinates of the point on the base of the mask.
    @staticmethod
    def find_points(mask):
        return np.array(np.where(mask)).T

    # Run BFS from all specific points. This will return map with count distance from nearest specific point.
    def bfs_from_points(self, shape, points):
        dist_from_points = np.full(shape, -1)
        for i, j in points:
            dist_from_points[i][j] = 0
        points_to_do = points.tolist()
        while points_to_do:
            point = points_to_do.pop(0)
            for p in self.neighborhood(point[0], point[1], self.map.shape[0], self.map.shape[1]):
                if dist_from_points[p[0]][p[1]] == -1:
                    dist_from_points[p[0]][p[1]] = dist_from_points[point[0]][point[1]] + 1
                    points_to_do.append(p)
        return dist_from_points

    # Return neighborhood in 8 direction when the point is not wall, heater, cooler.
    def neighborhood(self, x, y, maxX, maxY):
        neighborhood = []
        dx = -1
        dy = -1
        for i in range(3):
            for j in range(3):
                if dx == 0 and dy == 0:
                    dy += 1
                    continue
                if self.is_in_not_hate(x + dx, y + dy, maxX, maxY):
                    neighborhood.append((x + dx, y + dy))
                dy += 1
            dx += 1
            dy = -1
        return neighborhood

    # Hate point for temperature. WALL, HEATER, COOLER.
    def is_in_not_hate(self, x, y, maxX, maxY):
        return (BeeClust.is_in(x, y, maxX, maxY) and self.map[x][y] != MapConst.WALL and
                self.map[x][y] != MapConst.HEATER and self.map[x][y] != MapConst.COOLER)

    # True if point is in map.
    @staticmethod
    def is_in(x, y, maxX, maxY):
        return 0 <= x < maxX and 0 <= y < maxY

    # Count time which stay bee when stop.
    def count_stay_time(self, T_local):
        return max(int(self.k_stay / (1 + abs(self.T_ideal - T_local))), self.min_wait)

    # Calculate heat in heat map.
    def calculate_heat(self, dist_heater, dist_cooler):
        return self.T_env + self.k_temp * (np.maximum(
            self.calculate_heating(dist_heater),
            np.full(self.map.shape, 0)) - np.maximum(
            self.calculate_cooling(dist_cooler),
            np.full(self.map.shape, 0)))

    # Calculate cooling on heat map.
    def calculate_cooling(self, dist_cooler):
        return (np.divide(np.full(self.map.shape, 1),
                          dist_cooler,
                          out=np.full(self.map.shape, 0.),
                          where=dist_cooler != 0)) * (self.T_env - self.T_cooler)

    # Calculate heating on heat map
    def calculate_heating(self, dist_heater):
        return (np.divide(np.full(self.map.shape, 1),
                          dist_heater,
                          out=np.full(self.map.shape, 0.),
                          where=dist_heater != 0)) * (self.T_heater - self.T_env)
