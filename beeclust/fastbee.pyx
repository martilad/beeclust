import random
import numpy as np
cimport numpy as np
cimport cython
from libc.stdlib cimport rand, RAND_MAX

cdef int CHOOSE = -1
cdef int EMPTY = 0
cdef int UP = 1
cdef int RIGHT = 2
cdef int DOWN = 3
cdef int LEFT = 4
cdef int WALL = 5
cdef int HEATER = 6
cdef int COOLER = 7
cdef int WALL_HIT = 8
cdef int BEE_MEET = 9
cdef int MOVE = 10
cdef int WAIT = 11

@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
@cython.nonecheck(False)
def fast_tick(map, heatmap, p_changedir, p_wall, p_meet, T_ideal, k_stay, min_wait):

    cdef np.ndarray[np.int64_t, ndim=2] _map = map
    cdef np.ndarray[np.double_t, ndim=2] _heatmap = heatmap

    cdef int a, b
    a = _map.shape[0]
    b = _map.shape[1]

    cdef np.ndarray[np.uint8_t, ndim=2] done = np.full((a, b), 0, dtype=np.uint8)

    cdef int moved = 0

    cdef int r, c, next_dir, nr, nc
    cdef float _p_changedir = p_changedir
    cdef float _p_wall = p_wall
    cdef float _p_meet = p_meet
    cdef float _T_ideal = T_ideal
    cdef float _k_stay = k_stay
    cdef int _min_wait = min_wait
    cdef float delta
    cdef int offset_r, offset_c, movement, wait_time

    for r in range(a):
        for c in range(b):
    
            if done[r, c] == 1:
                continue

            if _map[r, c] == -1:
                _map[r, c] = rand() % 4 + 1;

            elif 1 <= _map[r, c] <= 4:
                if  rand()/<float>RAND_MAX < _p_changedir:
                    next_dir = rand() % 3 + 1;
                    if next_dir == _map[r, c]:
                        next_dir = 4
                    _map[r, c] = next_dir

                if _map[r,c] == UP:
                    offset_r = -1
                    offset_c = 0
                elif _map[r,c] == RIGHT:
                    offset_r = 0
                    offset_c = 1
                elif _map[r,c] == DOWN:
                    offset_r = 1
                    offset_c = 0
                else:
                    offset_r = 0
                    offset_c = -1
        
                nr = offset_r + r
                nc = offset_c + c

                movement = WALL_HIT
                if 0 <= nr < a and 0 <= nc < b:
                    if 1 <= _map[nr, nc] <= 4 or _map[nr, nc] < 0:
                        movement = BEE_MEET
                    elif _map[nr, nc] == EMPTY:
                        movement = MOVE

                if movement == WALL_HIT:
                    if rand()/<float>RAND_MAX < _p_wall:
                        movement = WAIT
                    else:
                        _map[r, c] = (_map[r, c] + 1) % 4 + 1
                elif (movement == BEE_MEET
                        and rand()/<float>RAND_MAX < _p_meet):
                    movement = WAIT

                if movement == WAIT:
                    delta = abs(_heatmap[r, c] - _T_ideal)
                    wait_time = int(_k_stay / (1 + delta))
                    wait_time = max(_min_wait, wait_time)
                    _map[r, c] = -wait_time
                elif movement == MOVE:
                    moved += 1
                    _map[nr, nc] = _map[r, c]
                    _map[r, c] = EMPTY
                    done[nr, nc] = 1
            elif _map[r, c] < 0:
                _map[r, c] += 1
            done[r, c] = 1
    return moved, _map



def fast_swarms(map, bees):
    swarms = []
    s_set = set(bees)
    while len(s_set) > 0:
        # Call for each swarm
        swarms.append(stepping_on_bees(map, s_set))
    return swarms

# Find all bees in one swarm.
def stepping_on_bees(map, sSet):
    swarm = []
    s = sSet.pop()
    queue = [s]
    swarm.append(s)
    while len(queue) > 0:
        q = queue.pop(0)
        for pos in neighbors(q[0], q[1]):
            if is_in(pos[0], pos[1], map.shape[0], map.shape[1]) and pos in sSet:
                queue.append(pos)
                swarm.append(pos)
                sSet.remove(pos)
    return swarm

# Neighbors in map on one step.
def neighbors(x, y):
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def fast_recalculate_heat(map, T_env, T_cooler, T_heater, k_temp):
    cdef np.ndarray[np.int64_t, ndim=2] _map = map
    cdef double _T_env = T_env
    cdef double _T_cooler = T_cooler
    cdef double _T_heater = T_heater
    cdef double _k_temp = k_temp
    cdef int a, b
    a = _map.shape[0]
    b = _map.shape[1]
    cdef np.ndarray[np.int64_t, ndim=2] heatmap = np.zeros((a, b), dtype=np.int64)

    return add_points_to_array(
            add_points_to_array(
                add_points_to_array(
                    calculate_heat(
                        bfs_from_points(a, b, find_points(_map == HEATER, _map, HEATER), _map),
                        bfs_from_points(a, b, find_points(_map == COOLER, _map, COOLER), _map), 
                        _map, T_env, T_cooler, T_heater, _k_temp),
                    map == WALL,
                    999999999),
                map == HEATER,
                T_heater),
            map == COOLER,
            T_cooler)


# Change value in array based on mask on new value.

def add_points_to_array(array, mask, value):
    array[mask] = value
    return array

# Return the coordinates of the point on the base of the mask.

cdef find_points(mask, map, value):
    cdef int maxSize = 1000
    cdef int size = 0
    cdef np.ndarray[np.int64_t, ndim=2] points = np.zeros((2, maxSize), dtype=np.int64)

    return np.array(
        np.where(mask)
        ).T

# Run BFS from all specific points. This will return map with count distance from nearest specific point.
@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef np.ndarray[np.int64_t, ndim=2] bfs_from_points(int a, int b, points, np.ndarray[np.int64_t, ndim=2] map):
    cdef np.ndarray[np.int64_t, ndim=2] dist_from_points = np.full((a, b), -1, dtype=np.int64)
    #dist_from_points = np.full(shape, -1)
    for i, j in points:
        dist_from_points[i][j] = 0
    points_to_do = points.tolist()
    while points_to_do:
        point = points_to_do.pop(0)
        for p in neighborhood(point[0], point[1], map.shape[0], map.shape[1], map):
            if dist_from_points[p[0]][p[1]] == -1:
                dist_from_points[p[0]][p[1]] = dist_from_points[point[0]][point[1]] + 1
                points_to_do.append(p)
    return dist_from_points

# Return neighborhood in 8 direction when the point is not wall, heater, cooler.
def neighborhood(x, y, maxX, maxY, map):
    neighborhood = []
    dx = -1
    dy = -1
    for i in range(3):
        for j in range(3):
            if dx == 0 and dy == 0:
                dy += 1
                continue
            if is_in_not_hate(x + dx, y + dy, maxX, maxY, map):
                neighborhood.append((x + dx, y + dy))
            dy += 1
        dx += 1
        dy = -1
    return neighborhood

# Hate point for temperature. WALL, HEATER, COOLER.
def is_in_not_hate(x, y, maxX, maxY, map):
    return (is_in(x, y, maxX, maxY) and map[x][y] != WALL and
            map[x][y] != HEATER and map[x][y] != COOLER)

# True if point is in map.
cdef int is_in(int x, int y, int maxX, int maxY):
    return 0 <= x < maxX and 0 <= y < maxY

# Calculate heat in heat map.
def calculate_heat(dist_heater, dist_cooler, map, T_env, T_cooler, T_heater, k_temp):
    return T_env + k_temp * (np.maximum(
        calculate_heating(dist_heater, map, T_env, T_heater),
        np.full(map.shape, 0)) - np.maximum(
        calculate_cooling(dist_cooler, map, T_env, T_cooler),
        np.full(map.shape, 0)))

# Calculate cooling on heat map.
def calculate_cooling(dist_cooler, map, T_env, T_cooler):
    return (np.divide(np.full(map.shape, 1),
                        dist_cooler,
                        out=np.full(map.shape, 0.),
                        where=dist_cooler != 0)) * (T_env - T_cooler)

# Calculate heating on heat map
def calculate_heating(dist_heater, map, T_env, T_heater):
    return (np.divide(np.full(map.shape, 1),
                        dist_heater,
                        out=np.full(map.shape, 0.),
                        where=dist_heater != 0)) * (T_heater - T_env)