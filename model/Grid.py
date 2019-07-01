import numpy as np
from scipy.ndimage import gaussian_filter

from rand_int import random_int_to
from model_settings import *

class Grid:
    cell_width = 1
    cell_height = 1
    t_base = 0
    mat_init = 1

    def __init__(self):
        self.num_rows = self.get_num_row()
        self.num_cols = self.get_num_col()
        self.map = self.transcode_map()
        self.matrix = np.zeros((self.num_rows, self.num_cols, len(indices)))
        self.populate()

    def get_num_row(self):
        row = 0
        for line in open("map.txt", "r"):
            row += 1
        return row

    def get_num_col(self):
        col = 0
        line = open("map.txt", "r").readline()
        for ch in line:
            if(ch != '\n'):
                col += 1
        return col

    def transcode_map(self):
        map = np.chararray((self.num_rows, self.num_cols))
        i = 0
        j = 0
        for line in open("map.txt", "r"):
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

    def initialize_people(self):
        self.matrix[:, :, indices["people"]] = 0

    def initialize_fire(self):
        self.matrix[:, :, indices["fire"]] = 0

    def initialize_smoke(self):
        self.matrix[:, :, indices["smoke"]] = 0

    def initialize_temperature(self):
        self.matrix[:, :, indices["temp"]] = Grid.t_base

    def initialize_material(self):
        self.matrix[:, :, indices["material"]] = np.random.random((self.num_rows, self.num_cols)) * Grid.mat_init


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

    def get_random_1d_neighbor(self, n, i):
        r = -n
        while i + r < 0 or i + r >= n:
            r = random_int_to(2) - 1
        return i + r

    def get_random_neighbor(self, i, j):
        r1 = self.get_random_1d_neighbor(self.num_rows, i)
        r2 = self.get_random_1d_neighbor(self.num_cols, j)
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

    def spread_fire(self):
        material = self.get_attribute("material")
        temp = self.get_attribute("temp")
        fire = self.get_attribute("fire")
        smoke = self.get_attribute("smoke")

        self.update_smoke(fire, smoke)
        self.update_temperature(fire, material, temp)
        self.update_fire(material, temp)
        self.update_material(fire)

        self.bound_grid(0, 1)

    def update_material(self, fire):
        self.matrix[:, :, indices["material"]] -= fire * dt * c_burn

    def update_fire(self, material, temp):
        self.matrix[:, :, indices["fire"]] = material * temp * (temp > t_fire)

    def update_temperature(self, fire, material, temp):
        temp_conduct = gaussian_filter(temp, sigma=0.1, mode='nearest', order=2)
        temp_rad = gaussian_filter(temp, sigma=7, mode='nearest')
        temp_diff = (temp + dt * temp_rad) /(1 + dt)

        self.matrix[:, :, indices["temp"]] = temp_diff
        self.matrix[:, :, indices["temp"]] += temp_conduct * dt * 0.0001
        self.matrix[:, :, indices["temp"]] += material * fire * dt

    def update_smoke(self, fire, smoke):
        smoke_around = gaussian_filter(smoke, sigma=(1, 1), mode='nearest', order=0)
        smoke_diff = smoke_around - smoke
        self.matrix[:, :, indices["smoke"]] += dt * smoke_diff
        self.matrix[:, :, indices["smoke"]] += fire * dt

    def simulate_step(self):
        people = []
        people_grid = self.get_attribute("people")
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                people_in_cell = people_grid[i, j]
                if people_in_cell > 0:
                    (n1, n2) = self.get_random_neighbor(i, j)
                    people.append((n1, n2, people_in_cell))
                    people_grid[i, j] = 0
        for (r, c, v) in people:
            # val = v - self.matrix[p1, p2, 0] - self.matrix[p1, p2, 2]
            people_grid[r, c] += v
        self.spread_fire()
