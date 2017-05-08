from ast import literal_eval
from os.path import dirname, exists as file_exists, join as join_path, realpath

DIRECTORY = dirname(realpath(__file__))

COLOR_NAMES_FILE = join_path(DIRECTORY, 'color-centroids.tsv')
COLOR_DISTANCES_FILE = join_path(DIRECTORY, 'color-distances')

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    def __hash__(self):
        return hash(str(self))
    def __str__(self):
        return '#{:02x}{:02x}{:02x}'.format(self.r, self.g, self.b).upper()
    def __repr__(self):
        return str(self)
    def __eq__(self, other):
        return str(self) == str(other)
    def __sub__(self, other):
        return abs(self.r - other.r) + abs(self.g - other.g) + abs(self.b - other.b)
    @staticmethod
    def from_hex(hexstr):
        if len(hexstr) == 7 and hexstr[0] == '#':
            hexstr = hexstr[1:]
        return Color(*(int(hexstr[i:i+2], 16) for i in range(0, 5, 2)))

def create_distances():
    colors = []
    with open(COLOR_NAMES_FILE) as fd:
        for line in fd:
            line = line.strip()
            if line[0] == '#':
                continue
            count, name, hexstr = line.split('\t')
            color = Color.from_hex(hexstr)
            others = []
            for other, distances in colors:
                others.append([other, color - other])
            others = sorted(others, key=(lambda pair: pair[1]))
            colors.append([color, others])
    return colors

def write_distances(colors):
    str_colors = []
    for color, distances in colors:
        str_distances = []
        for other, distance in distances:
            str_distances.append([str(other), distance])
        str_colors.append([str(color), str_distances])
    with open(COLOR_DISTANCES_FILE, 'w') as fd:
        fd.write(repr(str_colors))

def read_distances():
    with open(COLOR_DISTANCES_FILE) as fd:
        colors = []
        str_colors = literal_eval(fd.read())
        for str_color, str_distances in str_colors:
            color = Color.from_hex(str_color)
            distances = []
            for str_other, distance in str_distances:
                other = Color.from_hex(str_other)
                distances.append([other, distance])
            colors.append([color, distances])
        return colors

def get_distances():
    if file_exists(COLOR_DISTANCES_FILE):
        return read_distances()
    elif file_exists(COLOR_NAMES_FILE):
        distances = create_distances()
        write_distances(distances)
        return distances
    assert False, 'Cannot find color information'

def main():
    get_distances()

if __name__ == '__main__':
    main()
