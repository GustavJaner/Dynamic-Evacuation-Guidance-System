import numpy as np

class Test:
    def __init__(self):
        # self.fin = open("map.txt", "r")
        self.num_rows = self.num_rows()
        self.num_cols = self.num_cols()
        self.map = np.chararray((self.num_rows, self.num_cols))
        self.transcode_map()

    def num_rows(self):
        row = 0
        for line in open("map.txt", "r"):
            row += 1
        return row

    def num_cols(self):
        col = 0
        line = open("map.txt", "r").readline()
        for ch in line:
            if(ch != '\n'):
                col += 1
        return col

    def transcode_map(self):
        i = 0
        j = 0
        for line in open("map.txt", "r"):
            j = 0
            for ch in line:
                if(ch != '\n'):
                    self.map[i][j] = ch
                    j += 1
            i += 1

    def print_map(self):
        print(np.matrix(self.map))

# *******************

map = Test()
map.print_map()

print("num_rows=%d" % map.num_rows)
print("num_cols=%d" % map.num_cols)
