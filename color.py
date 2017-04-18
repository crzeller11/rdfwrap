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
