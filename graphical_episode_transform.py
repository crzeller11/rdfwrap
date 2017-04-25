from rdfwrap import NXRDF
from chroma_wanderer import walk

def graphical_episode_transform(): # takes in list of colors
    g = NXRDF()
    colors = walk(10) # list of 10 colors
    edges = ['red', 'green', 'blue', 'time', 'type', 'episode']
    for color in colors:
        color = g.add_node(color)
        for edge in edges:
            g.add_edge(color, edge, '')
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
-episode

Color episodes that uses the graph library and creates the same graph with disconnecting components like the ones
listed above
'''
