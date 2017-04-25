from rdfwrap import NXRDF
from chroma_wanderer import walk


def graphical_episode_transform(): # takes in list of colors
    g = NXRDF()
    colors = walk(10) # list of 10 colors

    for time, color in enumerate(colors):
        node = g.add_node()
        g.add_edge(node, 'time', time)
        g.add_edge(node, 'color_code', color)
        g.add_edge(node, 'color_name', '') # isolate color name from color-centroids
        g.add_edge(node, 'red', color.r) # how to get the RGB values of the color?
        g.add_edge(node, 'green', color.g)
        g.add_edge(node, 'blue', color.b)
        g.add_edge(node, 'type', 'color')
        g.add_edge(node, 'episode', '') # what is the difference between time and episode?

    print(g.to_dot())
    g.write_png('temp.png')


graphical_episode_transform()


'''
Make a new function that creates small individual graphs
Possible edges:
- time
- red
- green
- blue
- type
- episode

Color episodes that uses the graph library and creates the same graph with disconnecting components like the ones
listed above
'''
