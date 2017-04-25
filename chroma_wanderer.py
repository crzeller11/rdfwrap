from collections import OrderedDict
from random import randrange

from color import Color

class KNN:
    def __init__(self, means=None, names=None):
        if means is None:
            means = []
        if names is None:
            names = []
        self.means = dict(zip(means, names))
    def classify(self, point):
        return min(self.means.keys(), key=(lambda mean: abs(point - mean)))
    @staticmethod
    def from_file(file, limit=5):
        colors = []
        with open(file) as fd:
            for line in fd:
                line = line.strip()
                if line[0] == '#':
                    continue
                name, hexstr = line.split('\t')
                color = Color.from_hex(hexstr)
                colors.append((color, name))
        colors = list(reversed(colors))
        return KNN(color for color, name in colors[:limit])

def step(color, max_dist=8):
    rand = randrange(3)
    if rand == 0:
        new_primary = color.r + randrange(-max_dist, max_dist + 1)
        while not 0 <= new_primary <= 255:
            new_primary = color.r + randrange(-max_dist, max_dist + 1)
        return Color(new_primary, color.g, color.b)
    elif rand == 1:
        new_primary = color.g + randrange(-max_dist, max_dist + 1)
        while not 0 <= new_primary <= 255:
            new_primary = color.g + randrange(-max_dist, max_dist + 1)
        return Color(color.r, new_primary, color.b)
    else:
        new_primary = color.b + randrange(-max_dist, max_dist + 1)
        while not 0 <= new_primary <= 255:
            new_primary = color.b + randrange(-max_dist, max_dist + 1)
        return Color(color.r, color.g, new_primary)

def walk(n, start=None):
    if start is None:
        cur_color = Color(randrange(256), randrange(256), randrange(256))
    else:
        cur_color = start
    result = []
    for i in range(n):
        result.append(cur_color)
        cur_color = step(cur_color)
    return result



def main():
    for time, color in enumerate(walk(10)):
        print(time, color)


if __name__ == '__main__':
    main()
