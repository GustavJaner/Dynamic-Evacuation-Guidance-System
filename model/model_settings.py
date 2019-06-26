DISPSIZE = 15  # constant size of the plot display
MAXSTEPS = 10  # maximum amount of simulation steps
SIMRATE = 1000  # simulation rate in milliseconds
SQWIDTH = 1  # width of a square. Only supports 1 atm
LENGTH = 10  # side length of the actual map
PEOPLE = 10  # amount of people in the simulation
PWIDTH = 4  # how many people fit within a square

indices = {"fire": int(0), "people": int(1), "smoke": int(2), "temp": 3, "material": 4}
c_burn = 0.01
c_smoke = 0.01
t_fire = 0.2
c_conduct = 0.05
c_rad = 0.1
speed = 60
frequency = 200
dt = 1 / frequency * speed
