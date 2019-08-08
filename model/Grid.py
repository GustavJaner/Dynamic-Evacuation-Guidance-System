import numpy as np
from scipy.sparse.csgraph import dijkstra

from FireDynamics import FireDynamics
from PeopleDynamics import PeopleDynamics
from utils import *


class Grid:
    cell_width = 1
    cell_height = 1
    t_base = 0
    mat_init = 1

    def __init__(self):
        self.dijkstra_dist = 0
        self.dijkstra_pred = 0
        self.ng = 0
        self.num_rows = self.get_num_row()
        self.num_cols = self.get_num_col()
        self.map = self.transcode_map()
        self.fire_dynamics = FireDynamics()
        self.people_dynamics = PeopleDynamics(self)
        self.exit_indices = []

        self.matrix = np.zeros((self.num_rows, self.num_cols, len(indices)))
        self.make_walls()
        self.populate()
        self.make_dijkstra_array()

    def get_num_row(self):
        row = 0
        for line in open(map_file, "r"):
            row += 1
        return row

    def get_num_col(self):
        col = 0
        line = open(map_file, "r").readline()
        for ch in line:
            if (ch != '\n'):
                col += 1
        return col

    def transcode_map(self):
        map = np.chararray((self.num_rows, self.num_cols), unicode=True)
        i = 0
        j = 0
        for line in open(map_file, "r"):
            j = 0
            for ch in line:
                if (ch != '\n'):
                    map[i][j] = ch
                    j += 1
            i += 1

        return map

    def populate(self):
        self.initialize_people()
        self.initialize_fire()
        self.initialize_smoke()
        self.initialize_temperature()
        self.initialize_material()

    def fire_map(self):
        return self.fire_dynamics.fire_map(self.matrix)

    def initialize_people(self):
        print(indices["people"])
        self.matrix[:, :, indices["people"]] = 0

    def initialize_fire(self):
        self.matrix[:, :, indices["fire"]] = 0

    def initialize_smoke(self):
        self.matrix[:, :, indices["smoke"]] = 0

    def initialize_temperature(self):
        self.matrix[:, :, indices["temp"]] = Grid.t_base

    def initialize_material(self):
        # self.matrix[:, :, indices["material"]] = 1
        self.matrix[:, :, indices["material"]] = np.random.random((self.num_rows, self.num_cols)) * Grid.mat_init
        self.traverse_map()

    # TODO
    # hastags(#) and percentages(%) represent walls of different material
    def traverse_map(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if (self.map[i, j] == "#"):
                    self.matrix[i, j][indices["material"]] = 0
                if (self.map[i, j] == "%"):
                    self.matrix[i, j][indices["material"]] = 0

    def make_random_person(self):
        cell = self.place_random_person()
        cell[indices["people"]] = 1

    def place_random_person(self):
        (row, col) = self.get_random_coord()
        cell = self.map[row, col]

        while (cell == "#" or cell == "%" or cell == "."):
            (row, col) = self.get_random_coord()
            cell = self.map[row, col]

        return self.matrix[row, col]

    def make_random_fire(self):
        cell = self.place_random_fire()
        cell[indices["fire"]] = 1
        cell[indices["temp"]] = FireDynamics.t_burn * 2

    def place_random_fire(self):
        (row, col) = self.get_random_coord()
        cell = self.map[row, col]

        while (cell == "."):
            (row, col) = self.get_random_coord()
            cell = self.map[row, col]

        return self.matrix[row, col]

    def bound_grid(self, min_val, max_val):
        for i in range(5):
            mask_lower = self.matrix[:, :, i] < min_val
            mask_greater = self.matrix[:, :, i] > max_val
            self.matrix[mask_lower, i] = min_val
            self.matrix[mask_greater, i] = max_val

    def get_random_coord(self):
        row = random_int_to(self.num_rows - 1)
        col = random_int_to(self.num_cols - 1)
        return row, col

    def get_random_neighbor(self, i, j):
        row = get_random_1d_neighbor(self.num_rows, i)
        col = get_random_1d_neighbor(self.num_cols, j)
        return row, col

    def get_attraction_neighbor2(self, i, j):
        p = np.array([i, j])
        attraction_direction = 0
        size = np.shape(self.matrix)
        for x in range(size[0]):
            for y in range(size[1]):
                if self.map[x, y] == exit_symbol:
                    force_dir = self.attract_exit(p, x, y)
                    attraction_direction += force_dir
                if self.get_attribute("fire", x, y):
                    force_dir = self.repel_fire(p, x, y)
                    attraction_direction += force_dir
                if self.map[x, y] in just_wall_symbols:
                    force_dir = self.repel_wall(p, x, y)
                    attraction_direction += force_dir
        row = i + self.bound(attraction_direction[0], -1, 1)
        col = j + self.bound(attraction_direction[1], -1, 1)
        row = self.bound(int(round(row)), 0, size[0] - 1)
        col = self.bound(int(round(col)), 0, size[1] - 1)
        return row, col

    def get_row_col(self, index):
        col = index % self.num_cols
        row = index // self.num_cols
        return row, col

    def get_attraction_neighbor(self, i, j):
        best_index = self.to_index(i, j)
        if best_index in self.exit_indices:
            return (i, j)
        a = self.dijkstra_dist
        b = self.dijkstra_pred
        best = 100
        for bi in b:
            pred = bi[self.to_index(i, j)]
            if pred == -9999:
                continue
            elif a[pred] < best:
                best = a[pred]
                best_index = pred
        r, c = self.get_row_col(best_index)
        print(i, j, list(map(self.get_row_col, self.exit_indices)), r, c)

        # print(i, j, r, c, best_index)
        return r, c

        p = np.array([i, j])
        attraction_direction = 0
        for x in range(self.num_rows):
            for y in range(self.num_cols):
                if self.map[x, y] == exit_symbol:
                    force_dir = self.attract_exit(p, x, y)
                    attraction_direction += force_dir
                if self.get_attribute("fire", x, y):
                    force_dir = self.repel_fire(p, x, y)
                    attraction_direction += force_dir
                if self.map[x, y] in just_wall_symbols:
                    force_dir = self.repel_wall(p, x, y)
                    attraction_direction += force_dir
        row = i + self.bound(attraction_direction[0], -1, 1)
        col = j + self.bound(attraction_direction[1], -1, 1)
        row = self.bound(int(round(row)), 0, self.num_rows - 1)
        col = self.bound(int(round(col)), 0, self.num_cols - 1)
        return row, col

    def bound(self, a, lower, upper):
        if a < lower:
            return lower
        if a > upper: return upper
        return a

    def make_dijkstra(self):
        a, b = self.make_dijkstra_array()
        result = np.ones_like(a[0]) * 100
        for ai in a:
            result = np.minimum(ai, result)
        self.dijkstra_dist = result
        self.dijkstra_pred = b

    def to_index(self, i, j):
        index = i * self.num_cols + j
        return index

    def make_dijkstra_array(self):
        n = self.num_cols * self.num_rows
        offset1 = self.num_cols - 1
        offset2 = self.num_cols - 1
        self.exit_indices = []
        from scipy.sparse import csr_matrix
        dijkstra_array = n * np.zeros((n, n))
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                terrain = self.map[i, j]
                index = i * self.num_cols + j
                # fff = self.to_index(i, j)
                dijkstra_array[index, index] = 0
                fire_here = self.get_attribute("fire", i, j)
                if (terrain == no_walls_symbol or terrain == exit_symbol) and fire_here == 0:
                    # if self.get_attribute("people", i, j) > 0:
                    if (terrain == exit_symbol):
                        self.exit_indices.append(index)
                    coords = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1), (i, j - 1), (i, j + 1), (i + 1, j - 1),
                              (i + 1, j), (i + 1, j + 1)]
                    offsets = [offset1, offset1 + 1, offset1 + 2, -1, 1, offset2, offset2 + 1, offset2 + 2]
                    for ii, (a, b) in enumerate(coords):
                        if a < 0 or b < 0:
                            pass
                        elif a >= self.num_rows or b >= self.num_cols:
                            pass
                        elif self.map[a, b] in wall_symbols:
                            pass
                        elif self.get_attribute("fire", a, b) != 0:
                            dijkstra_array[index + offsets[ii], index] = 1
                        else:
                            # dijkstra_array[index, index + offsets[ii]] = 1
                            dijkstra_array[index + offsets[ii], index] = 1

        G_sparse = csr_matrix(dijkstra_array)
        a, b = dijkstra(G_sparse, directed=False, limit=100, indices=self.exit_indices, return_predecessors=True)
        return a, b

    def attract_exit(self, p, x, y):
        exp = 2
        exit = np.array([x, y])
        r = exit - p
        dividor = np.sum(np.abs(r ** exp))
        dividor = dividor ** (1 / exp)
        if dividor != 0:
            force_dir = 10 / dividor * r
        else:
            force_dir = np.array([0, 0])
        return force_dir

    def repel_wall(self, p, x, y):
        exp = 2
        wall = np.array([x, y])
        r = wall - p
        dividor = np.sum(np.abs(r ** exp))
        dividor = dividor ** (1 / exp)
        if dividor != 0:
            force_dir = 0.02 / dividor * r
        else:
            force_dir = np.array([0, 0])
        return -1 * force_dir

    def repel_fire(self, p, x, y):
        exp = 2
        fire = np.array([x, y])
        r = fire - p
        dividor = np.sum(np.abs(r ** exp))
        dividor = dividor ** (1 / exp)
        if dividor != 0:
            force_dir = 0.1 / dividor * r
        else:
            force_dir = np.array([0, 0])
        return -1 * force_dir

    def get_attribute(self, attribute, row=-1, column=-1):
        if row < 0 and column < 0:
            return self.matrix[:, :, indices[attribute]]
        elif row < 0:
            return self.matrix[:, column, indices[attribute]]
        elif column < 0:
            return self.matrix[row, :, indices[attribute]]
        else:
            return self.matrix[row, column, indices[attribute]]

    def simulate_step(self):
        self.matrix = self.people_dynamics.update_people_dynamics()
        self.matrix = self.fire_dynamics.update_fire_dynamics(self.matrix)

    def print_map(self):
        print(np.matrix(self.map))

    def make_walls(self):
        int_map = np.zeros(self.map.shape)
        for w in wall_symbols:
            int_map = int_map + (self.map == w) * wall_categories[w]
        int_map = int_map + (self.map == exit_symbol) * wall_categories[exit_symbol]
        self.matrix[:, :, indices["walls"]] = int_map
