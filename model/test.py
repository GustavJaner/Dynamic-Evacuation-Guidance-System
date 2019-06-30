import numpy as np

class Test:
    def __init__(self):
        # self.fin = open("map.txt", "r")
        self.row_size = self.row_size()
        self.col_size = self.col_size()
        self.map = np.chararray((self.row_size, self.col_size))
        self.transcode_map()

    def row_size(self):
        row = 0
        for line in open("map.txt", "r"):
            row += 1

        return row

    def col_size(self):
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

print("row_size=%d" % map.row_size)
print("col_size=%d" % map.col_size)
