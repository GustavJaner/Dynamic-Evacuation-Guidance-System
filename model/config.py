# Simulation
indices = {"fire": 0, "people": 1, "smoke": 2, "temp": 3, "material": 4, "walls": 5}
c_burn = 0.01
c_smoke = 0.01
t_fire = 0.2
c_conduct = 0.05
c_rad = 0.1
speed = 60
frequency = 200
dt = 1 / frequency * speed

# Map
map_file = "maps/map0.txt"
wall_symbols = "%#"
no_walls_symbol = '\''
wall_categories = {"%": 1, "#": 2, no_walls_symbol: 0}
