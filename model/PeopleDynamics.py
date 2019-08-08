import numpy as np

from config import *


class PeopleDynamics:

    def __init__(self, grid):
        self.grid = 0
        self.people = 0
        self.walls = 0
        self.people = 0
        self.grid = grid

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
        people_list = []
        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                people_in_cell = self.people[i, j]
                while people_in_cell > 0:
                    people_list.append(self.move_people_in_cell(i, j))
                    people_in_cell -= 1
                self.matrix[i, j, indices["people"]] = 0
        return people_list

    def move_people_in_cell(self, i, j):
        if (self.grid.get_attribute("walls", i, j) == wall_categories[exit_symbol]):
            return (i, j)
        (n1, n2) = self.grid.get_attraction_neighbor(i, j)  # self.grid.get_random_neighbor(i, j)
        direction = np.array([n1, n2]) - np.array([i, j], dtype=float)
        while self.forbidden_cell(n1, n2):
            direction *= 0.9
            val = np.array([i, j]) + direction
            (n1, n2) = [int(round(val[0])), int(round(val[1]))]
        if (n1, n2) == (i, j):
            (n1, n2) = self.grid.get_random_neighbor(i, j)
            while self.forbidden_cell(n1, n2):
                (n1, n2) = self.grid.get_random_neighbor(i, j)
        return n1, n2, 1

    def forbidden_cell(self, i, j):
        if self.walls[i, j] != wall_categories[no_walls_symbol]:
            return True
        if self.fire[i, j] == 1:
            return True
        return False
