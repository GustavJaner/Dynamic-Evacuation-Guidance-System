import numpy as np
from scipy.ndimage import gaussian_filter

from config import *
from utils import *


class FireDynamics:

    def __init__(self):
        self.grid = 0
        self.material = 0
        self.temp = 0
        self.fire = 0
        self.smoke = 0

    def update_fire_dynamics(self, grid):
        self.grid = grid
        self.matrix = np.copy(grid)

        self.material = get_attribute(self.grid, "material")
        self.temp = get_attribute(self.grid, "temp")
        self.fire = get_attribute(self.grid, "fire")
        self.smoke = get_attribute(self.grid, "smoke")

        self.spread_fire()
        self.bound_grid()
        return self.matrix

    def spread_fire(self):
        self.update_smoke()
        self.update_temperature()
        self.update_fire()
        self.update_material()

    def update_material(self):
        self.matrix[:, :, indices["material"]] -= self.fire * dt * c_burn

    def update_fire(self):
        self.matrix[:, :, indices["fire"]] = self.material * self.temp * (self.temp > t_fire)

    def update_temperature(self):
        temp_conduct = gaussian_filter(self.temp, sigma=0.1, mode='nearest', order=2)
        temp_rad = gaussian_filter(self.temp, sigma=7, mode='nearest')
        temp_diff = (self.temp + dt * temp_rad) / (1 + dt)

        self.matrix[:, :, indices["temp"]] = temp_diff
        self.matrix[:, :, indices["temp"]] += temp_conduct * dt * 0.0001
        self.matrix[:, :, indices["temp"]] += self.material * self.fire * dt

    def update_smoke(self):
        smoke_around = gaussian_filter(self.smoke, sigma=(1, 1), mode='nearest', order=0)
        smoke_diff = smoke_around - self.smoke
        self.matrix[:, :, indices["smoke"]] += dt * smoke_diff
        self.matrix[:, :, indices["smoke"]] += self.fire * dt

    def bound_grid(self):
        pass

    def fire_map(self, matrix):
        arr = np.copy(matrix[:, :, indices["fire"]])
        arr = arr * (arr > 100)
        return arr
