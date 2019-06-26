import random

def random_int_to(a):
    r = random.random() * (a + 1) % (a + 1)
    return int(r)
