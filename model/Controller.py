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
        self.map = Grid()
        self.map.make_random_person()
        self.map.make_random_person()

        self.map.make_random_fire()
        self.map.make_random_fire()

    def initialize_animation(self):
        self.animation = Animation(self.map)

    def start_simulation(self):
        print("Start simulation")
        for i in range(self.num_steps):
            self.update(i)
        self.end_simulation()

    def update(self, i):
        self.map.simulate_step()
        self.animation.update_data(self.map)

    def end_simulation(self):
        ani = self.animation.make_animation(self.num_steps)
        plt.show()
        print("End simulation")
