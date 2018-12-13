import random
import numpy as np
cimport numpy as np
cimport cython

from cpython cimport array
from libc.stdlib cimport rand, RAND_MAX
from collections import deque
import time
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

# Map constants
cdef int CHOOSE = -1
cdef int EMPTY = 0
cdef int UP = 1
cdef int RIGHT = 2
cdef int DOWN = 3
cdef int LEFT = 4
cdef int WALL = 5
cdef int HEATER = 6
cdef int COOLER = 7
# Move constants
cdef int WALL_HIT = 8
cdef int BEE_MEET = 9
cdef int MOVE = 10
cdef int WAIT = 11

@cython.boundscheck(False)
@cython.cdivision(True)
def fast_tick(map, heatmap, p_changedir, p_wall, p_meet, T_ideal, k_stay, min_wait):
    """Do one epoch in the map, for each bee do the operation"""
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
                # bee can moved in four direction
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

cdef struct cord:
    int x
    int y


cdef (int, int)packing_tuple(int x, int y):
    """Fast creation of tuple in Cython"""
    cdef (int, int) xy = (x, y)
    return xy

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def fast_swarms(map):
    """Find swarms of bees on map. Iterate over map and ahen find bee run BFS."""
    cdef np.ndarray[np.int64_t, ndim=2] _map = map
    cdef int a, b, x, y
    a = _map.shape[0]
    b = _map.shape[1]

    cdef np.ndarray[np.int64_t, ndim=2] points = np.full((2, a*b), -1, dtype=np.int64)
    cdef int queue_pos = 0
    cdef int queue_put = 0
    cdef np.ndarray[np.uint8_t, ndim=2] done = np.zeros((a, b), dtype=np.uint8)
    

    cdef int i, j
    cdef list swarms = []
    cdef list swarm 
    for i in range(a):
        for j in range(b):
            if done[i, j] == 1 or _is_bee(_map[i, j]) == 0:
                continue
            swarm = []
            swarm.append(packing_tuple(i, j))
            points[0, queue_put] = i
            points[1, queue_put] = j
            queue_put  = (queue_put + 1) % (a*b)
            done[i, j] = 1
            while queue_pos != queue_put:
                x = points[0, queue_pos]
                y = points[1, queue_pos]
                queue_pos = (queue_pos + 1) % (a*b)
                
                if is_in(x+1, y, a, b) and _is_bee(_map[x+1, y]) == 1 and done[x+1, y] != 1:
                    points[0, queue_put] = x+1
                    points[1, queue_put] = y
                    queue_put  = (queue_put + 1) % (a*b)
                    swarm.append(packing_tuple(x+1, y))
                    done[x+1, y] = 1

                if is_in(x-1, y, a, b) and _is_bee(_map[x-1, y]) == 1 and done[x-1, y] != 1:
                    points[0, queue_put] = x-1
                    points[1, queue_put] = y
                    queue_put  = (queue_put + 1) % (a*b)
                    swarm.append(packing_tuple(x-1, y))
                    done[x-1, y] = 1

                if is_in(x, y+1, a, b) and _is_bee(_map[x, y+1]) == 1 and done[x, y+1] != 1:
                    points[0, queue_put] = x
                    points[1, queue_put] = y+1
                    queue_put  = (queue_put + 1) % (a*b)
                    swarm.append(packing_tuple(x, y+1))
                    done[x, y+1] = 1

                if is_in(x, y-1, a, b) and _is_bee(_map[x, y-1]) == 1 and done[x, y-1] != 1:
                    points[0, queue_put] = x
                    points[1, queue_put] = y-1
                    queue_put = (queue_put + 1) % (a*b)
                    swarm.append(packing_tuple(x, y-1))
                    done[x, y-1] = 1

            swarms.append(swarm)
            
    return swarms


cdef int _is_bee(int value):
    """True if the value is bee"""
    return value < 0 or 1 <= value <= 4


@cython.boundscheck(False)
@cython.cdivision(True)
def fast_recalculate_heat(map, double _T_env, double _T_cooler, double _T_heater, double _k_temp):
    """Method for recalculating heatmap, it runs two BFS for creating distances from heaters and coolers.
        Next for each position calculate temp."""
    cdef np.ndarray[np.int64_t, ndim=2] _map = map
    cdef int a, b, i, j
    a = _map.shape[0]
    b = _map.shape[1]
    cdef np.ndarray[np.double_t, ndim=2] heatmap = np.zeros((a, b), dtype=np.double)
    cdef np.ndarray[np.int64_t, ndim=2] points = np.full((2, a*b+1), -1, dtype=np.int64)
    cdef np.ndarray[np.int64_t, ndim=2] dist_from_heater = np.full((a, b), -1, dtype=np.int64)
    cdef np.ndarray[np.int64_t, ndim=2] dist_from_cooler = np.full((a, b), -1, dtype=np.int64)
    cdef size = _find_points(_map, points, HEATER, a, b)
    _bfs_from_points(_map, a, b, HEATER, points, dist_from_heater, size)
    size = _find_points(_map, points, COOLER, a, b)
    _bfs_from_points(_map, a, b, COOLER, points, dist_from_cooler, size)

    cdef double head_const = _T_heater - _T_env
    cdef double cool_const = _T_env - _T_cooler
    for i in range(a):
        for j in range(b):
            if _map[i, j] == HEATER:
                heatmap[i, j] = _T_heater
                continue
            if _map[i, j] == COOLER:
                heatmap[i, j] = _T_cooler
                continue
            if _map[i, j] == WALL:
                # non define add some bullshit
                heatmap[i, j] = 9999999
                continue
            heatmap[i, j] = _T_env + _k_temp * (max((1/<double>dist_from_heater[i, j])*head_const, 0) - max((1/<double>dist_from_cooler[i, j])*cool_const, 0))
    return heatmap


@cython.boundscheck(False)
cdef int _find_points(np.int64_t[:, :] map, np.int64_t[:, :] points, int value, int a, int b):
    """Function for find point with values in map and add it to array. (for example heaters)"""
    cdef int maxSize = a * b
    cdef int size = 1
    cdef int i, j
    for i in range(a):
        for j in range(b):
            if map[i, j] == value:
                points[0, size] = i
                points[1, size] = j
                size += 1
            continue
    points[0, 0] = size
    points[1, 0] = size
    return size


@cython.boundscheck(False)
@cython.cdivision(True)
cdef void _bfs_from_points(np.int64_t[:, :] map, int a, int b, int value, np.int64_t[:, :] points, np.int64_t[:, :] dist_from_points, int size):
    """BFS from find points, it save distances from points to new map of distances."""
    size = size % (a*b+1)
    cdef int queue_point = 1
    cdef int x, y, dx, dy
    while True:
        if queue_point != size:
            x = points[0][queue_point]
            y = points[1][queue_point]
            queue_point = (queue_point + 1) % (a*b+1)
            dx = -1
            dy = -1
            if map[x,y] == value:
                dist_from_points[x, y] = 0
            for i in range(3):
                for j in range(3):
                    if dx == 0 and dy == 0:
                        dy += 1
                        continue
                    if (is_in(x + dx, y + dy, a, b) and map[x + dx, y + dy] != WALL and
                                map[x + dx, y + dy] != HEATER and map[x + dx, y + dy] != COOLER and dist_from_points[x+dx,y+dy] == -1):
                        dist_from_points[x+dx,y+dy] = dist_from_points[x, y] + 1
                        points[0, size] = x+dx
                        points[1, size] = y+dy
                        size = (size + 1) % (a*b+1)
                    dy += 1
                dx += 1
                dy = -1
        else:
            break


cdef int is_in(int x, int y, int maxX, int maxY):
    """True if point is in map."""
    return 0 <= x < maxX and 0 <= y < maxY
