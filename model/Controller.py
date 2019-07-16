import matplotlib.pyplot as plt

from Grid import Grid
from Animation import Animation

class Controller:
    'State of the simulation'

    def __init__(self, num_steps=1000):
        self.initialize_model()
        self.initialize_animation()
        self.num_steps = num_steps

    def initialize_model(self):
        self.grid = Grid()
        self.grid.print_map()
        self.grid.make_random_person()
        self.grid.make_random_person()

        self.grid.make_random_fire()
        self.grid.make_random_fire()

    def initialize_animation(self):
        self.animation = Animation(self.grid)

    def start_simulation(self):
        print("Start simulation")
        for i in range(self.num_steps):
            self.update(i)
        self.end_simulation()

    def update(self, i):
        self.grid.simulate_step()
        self.animation.update_data(self.grid)

    def end_simulation(self):
        ani = self.animation.make_animation(self.num_steps)
        plt.show()
        print("End simulation")
