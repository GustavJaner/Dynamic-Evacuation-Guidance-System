import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from config import *


class Animation:
    color_yellow_offset = 0.2
    color_blue_offset = 0.6

    def __init__(self, grid):
        self.fig, self.ax = plt.subplots()
        self.grid = grid
        self.matrix = grid.matrix
        self.animation = 0
        self.a = self.to_image(self.grid)
        self.im = plt.imshow(self.to_image(self.grid), interpolation='none', vmin=0, vmax=1)
        self.data = []

    def make_animation(self, num_steps):
        return FuncAnimation(self.fig, self.update, frames=num_steps - 1, init_func=self.init,
                             interval=frequency, blit=True,
                             repeat=False)

    def make_smoke_color(self, state, image):
        smoke_max = 0.7
        smoke_gamma = 0.5
        smoke = state.get_attribute("smoke")
        self.bound_1d_array(smoke)
        smoke_val = smoke ** smoke_gamma
        mask = smoke_val >= smoke_max
        smoke_val[mask] = smoke_max
        smoke_val = (1 - smoke_val)
        image[:, :, 0] *= smoke_val
        image[:, :, 1] *= smoke_val
        image[:, :, 2] *= smoke_val

    def make_fire_color(self, state, image):
        fire_threshold = 0
        fire = state.get_attribute("fire")
        self.bound_1d_array(fire)
        image[:, :, 1] = 0
        image[:, :, 1] = 1 - [fire > fire_threshold] * fire ** 0.5
        image[:, :, 2][fire > fire_threshold] = 0

    def bound_1d_array(self, array):
        array[array > 1] = 1
        array[array < 0] = 0

    def make_people_color(self, state, image):
        image[:, :, 0] -= state.get_attribute("people")
        image[:, :, 1] -= state.get_attribute("people")
        image[:, :, 2] += state.get_attribute("people")

    def make_walls_color(self, state, image):
        image[:, :, :][state.get_attribute("walls") != wall_categories[no_walls_symbol]] = 0.5
        image[:, :, :][state.get_attribute("walls") == wall_categories[exit_symbol]] = [0, 1, 0]

    def make_image_colors(self, state):
        image = np.ones((self.grid.num_rows, self.grid.num_cols, 3))
        self.make_fire_color(state, image)
        self.make_people_color(state, image)
        self.make_smoke_color(state, image)
        self.make_walls_color(state, image)
        # image[:, :, 0] = state.ng

        self.bound_colors(image, 0, 1)
        return image

    def bound_colors(self, image, min_val, max_val):
        for i in range(3):
            mask_lower = image[:, :, i] < min_val
            mask_greater = image[:, :, i] > max_val
            image[mask_lower, i] = min_val
            image[mask_greater, i] = max_val

    def to_image(self, state):
        image = self.make_image_colors(state)
        return image

    def init(self):
        self.data.append(self.a)
        self.im.set_data(self.a)
        return [self.im]

    def update_data(self, state):
        self.data.append(self.to_image(state)) # state == updated grid

    def update(self, num):
        self.im.set_data(self.data[num])
        return [self.im]
