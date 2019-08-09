import numpy as np
from scipy.ndimage import gaussian_filter

from config import *


class PeopleDynamics:

    def __init__(self, grid):
        self.people = 0
        self.walls = 0
        self.people = 0
        self.grid = grid
        self.ng = 0
        self.i = 0

    def update_people_dynamics(self):
        self.matrix = np.copy(self.grid.matrix)

        self.walls = self.grid.get_attribute("walls")
        self.fire = self.grid.fire_map()
        self.people = self.grid.get_attribute("people")

        self.move_people()
        return self.matrix

    def move_people(self):
        people_list = self.calculate_people_movement()
        self.execute_people_movement(people_list)

    def execute_people_movement(self, people_list):
        for (r, c, v) in people_list:
            self.matrix[r, c, indices["people"]] = v

    def calculate_people_movement(self):
        # nice_grid = self.nice_grid()
        # self.grid.ng = nice_grid
        # if evacuation_alg == 'dijkstra':
        self.i += 1
        self.grid.make_dijkstra()
        people_list = []
        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                people_in_cell = self.people[i, j]
                while people_in_cell > 0:
                    if self.i % 3 == 0:
                        movement = self.move_people_in_cell(i, j)
                    else:
                        movement = (i, j, 1)
                    # movement = self.move_with_nice_grid(i, j, nice_grid)
                    people_list.append(movement)
                    people_in_cell -= 1
                self.matrix[i, j, indices["people"]] = 0
        return people_list

    def move_with_nice_grid(self, i, j, nice_grid):
        nice_grid[i, j] = -5
        grid_part = nice_grid[max(i - 1, 0):min(i + 2, self.matrix.shape[0]),
                    max(j - 1, 0):min(j + 2, self.matrix.shape[1])]
        mx = np.argmax(grid_part, axis=0)[0]
        my = np.argmax(grid_part, axis=1)[0]
        movement = (
                self.grid.bound(mx + i, 0, self.matrix.shape[0] - 1),
                self.grid.bound(my + j, 0, self.matrix.shape[1] - 1), 1)
        return movement

    def nice_grid(self):
        num_rows = self.matrix.shape[0]
        num_cols = self.matrix.shape[1]
        nice_grid = -2 * np.ones((num_rows, num_cols))
        wall_grid = -2 * np.ones((num_rows, num_cols))
        wall_grid[self.grid.get_attribute("walls") == wall_categories[no_walls_symbol]] = 0
        wall_grid[self.grid.get_attribute("walls") == wall_categories[exit_symbol]] = 0

        wall_grid = gaussian_filter(wall_grid, sigma=1, mode='nearest', order=0)

        fire_grid = 0 * np.ones((num_rows, num_cols))
        fire_grid -= 25 * self.grid.get_attribute("fire")
        fire_grid = gaussian_filter(fire_grid, sigma=5, mode='nearest', order=0)

        exit_grid = 0 * np.ones((num_rows, num_cols))
        exit_grid[self.grid.get_attribute("walls") == wall_categories[exit_symbol]] = 25
        exit_grid = gaussian_filter(exit_grid, sigma=5, mode='nearest', order=0)

        # nice_grid[self.grid.get_attribute("walls") == wall_categories[exit_symbol]] = 100
        nice_grid = wall_grid + fire_grid + exit_grid  # + gaussian_filter(nice_grid, sigma=16, mode='nearest', order=0)
        nice_grid -= np.min(nice_grid)
        nice_grid /= np.max(nice_grid)
        return nice_grid

    def move_people_in_cell(self, i, j):
        if (self.grid.get_attribute("walls", i, j) == wall_categories[exit_symbol]):
            return (i, j, 1)
        if evacuation_alg == 'magnetic':
            (n1, n2) = self.grid.get_attraction_neighbor_magnetic(i, j)
        else:
            (n1, n2) = self.grid.get_attraction_neighbor_dijkstra(i, j)
        if self.forbidden_cell(n1, n2):
            (n1, n2) = self.grid.get_attraction_neighbor_dijkstra(i, j)
        return n1, n2, 1

    def forbidden_cell(self, i, j):
        if self.walls[i, j] != wall_categories[no_walls_symbol] and self.walls[i, j] != wall_categories[exit_symbol]:
            return True
        if self.fire[i, j] == 1:
            return True
        return False
