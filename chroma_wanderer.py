from random import randrange, seed as set_seed

from color import Color, closest_color
from rdfwrap import NXRDF

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

def random_walk(n, start=None, seed=None):
    if seed is not None:
        set_seed(seed)
    if start is None:
        cur_color = Color(randrange(256), randrange(256), randrange(256))
    else:
        cur_color = start
    result = []
    for i in range(n):
        result.append(cur_color)
        cur_color = step(cur_color)
    return result

def random_colors(n, seed=None):
    if seed is not None:
        set_seed(seed)
    result = []
    for i in range(n):
        result.append(Color(randrange(256), randrange(256), randrange(256)))
    return result

def color_episodes(colors, num_labels):
    g = NXRDF()
    for time, color in enumerate(colors):
        node = g.add_node()
        g.add_edge(node, 'episode', time)
        g.add_edge(node, 'color_code', color)
        g.add_edge(node, 'color_name', closest_color(color, num_labels).name)
        g.add_edge(node, 'red', color.r)
        g.add_edge(node, 'green', color.g)
        g.add_edge(node, 'blue', color.b)
        g.add_edge(node, 'type', 'color')
    return g

def main():
    for time, color in enumerate(random_walk(10, seed=8675309)):
        print(time, color)

if __name__ == '__main__':
    main()
