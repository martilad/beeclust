import numpy as np


class BeeClust:

    def __init__(self, map, p_changedir=0.2, p_wall=0.8, p_meet=0.8, k_temp=0.9,
                 k_stay=50, T_ideal=35, T_heater=40, T_cooler=5, T_env=22, min_wait=2):
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
        # b.map obsahuje mapu jako numpy celočíselnou matici
        self.map = map
        # b.heatmap obsahuje tepelnou mapu jako numpy matici reálných čísel
        self.heatmap = np.full(self.map.shape, 0)
        self.recalculate_heat()
        # b.bees obsahuje seznam dvojic (x, y) reprezentující pozice včel
        self.bees = []
        # b.swarms obsahuje seznam seznamů dvojic (x, y) reprezentující pozice se sousedícími včelami (4 směry); 
        # například [[(0,0), (0,1), (0,2), (1,0)], [(2,3)], [(3,5), (4,5)]] pro mapu se sedmi včelami ve třech rojích; 
        # na pořadí v seznamech nezáleží
        self.swarms = []
        # b.score vypočítá průměrnou teplotu včel
        self.score = 0.

    # provede 1 krok simulace algoritmu a vrátí počet včel, které se pohnuly
    def tick(self):
        return 0

    # všechny včely zapomenou svoji dobu čekání a směr, kterým šly; v příštím kroku vylosují náhodně směr a v dalším kroku se opět dají do pohybu
    def forget(self):
        ...

    # b.recalculate_heat() vynutí přepočtení b.heatmap (například po změně mapy b.map bez tvorby nové simulace)
    def recalculate_heat(self):
        self.heatmap =  self.add_points_to_array(
                            self.add_points_to_array(
                                self.add_points_to_array(
                                    self.calculate_heat(
                                        self.bfs_from_points(self.map.shape, self.find_points(6)), 
                                        self.bfs_from_points(self.map.shape, self.find_points(7))),
                                    self.map == 5, 
                                    np.nan), 
                                self.map == 6, 
                                self.T_heater),
                            self.map==7,
                            self.T_cooler)
        print(np.round(self.heatmap, decimals=1))

    def add_points_to_array(self, array, mask, value):
        array[mask] = value
        return array

    def find_points(self, value):
        return np.array(np.where( self.map == value )).T        

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

    def neighborhood(self, x, y, maxX, maxY):
        neighborhood = []
        dx = -1
        dy = -1
        for i in range(3):
            for j in range(3):
                if dx == 0 and dy == 0:
                    dy += 1 
                    continue
                if self.is_in_not_wall(x+dx,y+dy, maxX, maxY): neighborhood.append((x+dx, y+dy))
                dy += 1
            dx += 1
            dy = -1
        return neighborhood

    def is_in_not_wall(self, x, y, maxX, maxY):
        return True if x >= 0 and y >= 0 and x < maxX and y < maxY and self.map[x][y] != 5 else False

    # T_local je teplota aktuální pozice včely
    def count_stay_time(self, T_local):
        return max(int(self.k_stay / (1 + abs(self.T_ideal - T_local))), self.min_wait)

    # Teplo se po mapě šíří ve všech 8 směrech (narozdíl od pohybu včel) a počítá se v reálných číslech typu float
    # Na pozici, kde je zeď, teplota není definována (NaN)
    # Na pozici, kde je ohřívač, je vždy teplota T_heater
    # Na pozici, kde je chladič, je vždy teplota T_cooler
    # Na pozicích, kde nic není nebo jsou tam včely, se teplota počítá podle vzorce:
    # vzdálenost ohřívače dist_heater (resp. chladiče) je vzdálenost nejbližšího ohřívače (resp. chladiče) 
    # v počtu kroků 8 směry s uvažováním zdí a ostatních chladičů/ohřívačů jako překážek
    # k_temp je nastavitelný koeficient ovlivňující tepelnou vodivost prostředí
    def calculate_heat(self, dist_heater, dist_cooler):
        return self.T_env + self.k_temp * (np.maximum(
                                                self.calculate_heating(dist_heater), 
                                                np.full(self.map.shape, 0)) - np.maximum(
                                                                                    self.calculate_cooling(dist_cooler), 
                                                                                    np.full(self.map.shape, 0)))

    def calculate_cooling(self, dist_cooler):
        return (np.divide(np.full(self.map.shape, 1), 
                                    dist_cooler, 
                                    out=np.full(self.map.shape, 0.), 
                                    where=dist_cooler!=0)) * (self.T_env - self.T_cooler)

    def calculate_heating(self, dist_heater):
        return (np.divide(np.full(self.map.shape, 1), 
                                    dist_heater, 
                                    out=np.full(self.map.shape, 0.), 
                                    where=dist_heater!=0)) * (self.T_heater - self.T_env)


some_numpy_map = np.zeros((10,10))
some_numpy_map[0][0] = 6
some_numpy_map[1][4] = 6
some_numpy_map[5][0] = 6
some_numpy_map[1][0] = 5
some_numpy_map[1][1] = 5
some_numpy_map[3][0] = 5
some_numpy_map[3][1] = 5
some_numpy_map[6][6] = 5
some_numpy_map[4][4] = 7
some_numpy_map[8][8] = 7
b = BeeClust(some_numpy_map)