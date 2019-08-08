import numpy as np
from scipy.ndimage import gaussian_filter

from utils import *

t_max = 2000
temp_factor = 30000
burn_factor = 0.001
t_min = -20

class FireDynamics:
    t_burn = 300

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

    def burn_temp_coeff(self):
        coeff = np.copy(self.temp)
        coeff = t_max / (coeff + 1) * self.fire
        return coeff

    def update_material(self):
        burn_rate = self.burn_temp_coeff() * self.fire * burn_factor
        self.matrix[:, :, indices["material"]] -= dt * burn_rate

    def update_fire(self):
        new_fire = np.ones(self.fire.shape)
        # new_fire[self.material <= 0] = 0
        new_fire[self.temp <= self.t_burn] = 0
        self.matrix[:, :, indices["fire"]] = new_fire


    def update_temperature(self):
        gaussian_sigma_low = 0.1
        gaussian_sigma_high = 0.6
        heating_curve = 0.2
        temp_conduct = gaussian_filter(self.temp, sigma=gaussian_sigma_low, mode='nearest', order=0) - gaussian_filter(
            self.temp, sigma=gaussian_sigma_high, mode='nearest', order=0)

        temp_burn = self.burn_temp_coeff() ** heating_curve * self.temp

        new_temp = self.temp + dt * (temp_burn - temp_conduct)
        new_temp[new_temp >= t_max] = t_max
        new_temp[new_temp <= t_min] = t_min
        new_temp[get_attribute(self.grid, "walls") != wall_categories[no_walls_symbol]] *= 0.1


        self.matrix[:, :, indices["temp"]] = new_temp


    def update_smoke(self):
        sigma_val = 2
        smoke_around = gaussian_filter(self.smoke, sigma=sigma_val, mode='nearest', order=0)
        smoke_diff = smoke_around - self.smoke

        val = self.smoke + (smoke_diff + self.fire) * dt

        val[get_attribute(self.grid, "walls") != wall_categories[no_walls_symbol]] = - 1 / sigma_val ** 2

        self.matrix[:, :, indices["smoke"]] = val
        print(np.max(self.smoke))


    def bound_grid(self):
        pass

    def fire_map(self, matrix):
        arr = np.copy(matrix[:, :, indices["fire"]])
        arr = arr * (arr > 100)
        return arr
