import numpy as np

from FireDynamics import FireDynamics
from PeopleDynamics import PeopleDynamics
from model_settings import *
from utils import *


class Grid:
    cell_width = 1
    cell_height = 1
    t_base = 0
    mat_init = 1

    def __init__(self):
        self.num_rows = self.get_num_row()
        self.num_cols = self.get_num_col()
        self.map = self.transcode_map()
        self.fire_dynamics = FireDynamics()
        self.people_dynamics = PeopleDynamics(self)

        self.matrix = np.zeros((self.num_rows, self.num_cols, len(indices)))
        self.make_walls()
        self.populate()

    def get_num_row(self):
        row = 0
        for line in open(map_file, "r"):
            row += 1
        return row

    def get_num_col(self):
        col = 0
        line = open(map_file, "r").readline()
        for ch in line:
            if(ch != '\n'):
                col += 1
        return col

    def transcode_map(self):
        map = np.chararray((self.num_rows, self.num_cols), unicode=True)
        i = 0
        j = 0
        for line in open(map_file, "r"):
            j = 0
            for ch in line:
                if(ch != '\n'):
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

    # TODO
    # cannot spawn person on wall (+cannot move to wall)
    def make_random_person(self):
        cell = self.get_random_cell()
        cell[indices["people"]] = 1

    def make_random_fire(self):
        cell = self.get_random_cell()
        cell[indices["fire"]] = 1
        cell[indices["temp"]] = 1

    def bound_grid(self, min_val, max_val):
        for i in range(5):
            mask_lower = self.matrix[:, :, i] < min_val
            mask_greater = self.matrix[:, :, i] > max_val
            self.matrix[mask_lower, i] = min_val
            self.matrix[mask_greater, i] = max_val

    def get_random_neighbor(self, i, j):
        r1 = get_random_1d_neighbor(self.num_rows, i)
        r2 = get_random_1d_neighbor(self.num_cols, j)
        return r1, r2

    def get_attribute(self, attribute, row=-1, column=-1):
        if row < 0 and column < 0:
            return self.matrix[:, :, indices[attribute]]
        elif row < 0:
            return self.matrix[:, column, indices[attribute]]
        elif column < 0:
            return self.matrix[row, :, indices[attribute]]
        else:
            return self.matrix[row, column, indices[attribute]]

    def get_random_cell(self):
        r1 = random_int_to(self.num_rows - 1)
        r2 = random_int_to(self.num_cols - 1)
        return self.matrix[r1, r2]

    def simulate_step(self):
        self.matrix = self.people_dynamics.update_people_dynamics()
        self.matrix = self.fire_dynamics.update_fire_dynamics(self.matrix)

    def print_map(self):
        print(np.matrix(self.map))

    def make_walls(self):
        int_map = np.zeros(self.map.shape)
        for w in wall_symbols:
            int_map = int_map + (self.map == w) * wall_categories[w]
        self.matrix[:, :, indices["walls"]] = int_map
