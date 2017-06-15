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

def color_episodes(colors, num_labels, graph=None, start_time=0):
    if graph is None:
        graph = NXRDF()
    for time, color in enumerate(colors, start=start_time):
        node = graph.add_node()
        graph.add_edge(node, 'episode', time)
        graph.add_edge(node, 'color_code', color)
        graph.add_edge(node, 'color_name', closest_color(color, num_labels).name)
        graph.add_edge(node, 'red', color.r)
        graph.add_edge(node, 'green', color.g)
        graph.add_edge(node, 'blue', color.b)
        graph.add_edge(node, 'type', 'color')
    return graph

def color_episodes_with_changes(colors, changes):
    # changes is a list of [time, num_label] pairs; for example
    # changes = [
    #     [0, 10],  # start with 10 labels
    #     [17, 11], # at time 17, use 11 labels
    #     [60, 12], # at time 60, use 12 labels
    # ]
    graph = NXRDF()
    if changes[-1][0] < len(colors):
        changes = changes + [[len(colors), changes[-1][1]]]
    print(changes)
    for [start, num_labels], [end, _] in zip(changes[:-1], changes[1:]):
        graph = color_episodes(colors[start:end], num_labels, graph, start_time=start)
    return graph

def main():
    for time, color in enumerate(random_walk(10, seed=8675309)):
        print(time, color)

if __name__ == '__main__':
    main()
