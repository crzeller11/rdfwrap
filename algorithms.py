from random import seed as set_seed
from time import time
from textwrap import dedent

from rdflib.plugins.sparql import prepareQuery

from chroma_wanderer import random_walk, random_colors, color_episodes, color_episodes_with_changes
from color import Color, create_knn, closest_color
from permspace import Namespace
from rdfwrap import NXRDF

EXACT_LABEL_QUERY = prepareQuery(
    dedent('''
        SELECT DISTINCT ?time ?name ?r ?g ?b
        WHERE {
            ?episode nxrdf:episode ?time ;
                     nxrdf:color_name ?name ;
                     nxrdf:red ?r ;
                     nxrdf:green ?g ;
                     nxrdf:blue ?b .
        }
        ORDER BY ASC(?time)
    '''),
    initNs={'nxrdf':NXRDF.NAMESPACE}
)

NEIGHBOR_LABELS_QUERY = prepareQuery(
    dedent('''
        SELECT DISTINCT ?neighbor_name
        WHERE {
            ?parent nxrdf:neighbor ?neighbor ;
                    nxrdf:name ?name .
            ?neighbor nxrdf:name ?neighbor_name .
        }
    '''),
    initNs={'nxrdf':NXRDF.NAMESPACE}
)

# finds the color closest to target color and minimum distance
def min_color_total_episodes(total_episodes, min_distance, min_color, parameters, results):
    min_time = -1
    for result in results:
        episode_color = Color(result[2].value, result[3].value, result[4].value)
        distance = parameters.target_color - episode_color
        if distance < min_distance:
            min_distance = distance # min distance is the RGB distance btwn min_color and target_color
            min_color = episode_color # min color is the closest color to target color
            min_time = result[0]
        total_episodes += 1
    return min_time, min_color, total_episodes

def run_brute_force(parameters, episode_graph):
    # query isolates all colors in graph
    # metrics
    total_episodes = 0
    min_time = -1
    min_distance = 3 * 255
    min_color = None

    # for every color in graph, find closest color to target color, distance btwn two colors, and # episodes
    results = episode_graph.query(EXACT_LABEL_QUERY)
    min_time, min_color, total_episodes = min_color_total_episodes(total_episodes, min_distance, min_color, parameters, results)

    # return min color and total episodes
    return min_time, min_color, total_episodes

def run_exact_heuristic(parameters, episode_graph):
    # find semantic label of target color
    label_color = closest_color(parameters.target_color, num_colors=parameters.num_labels)

    # metrics
    total_episodes = 0
    min_time = -1
    min_distance = 3 * 255
    min_color = None

    # loop through all colors with same label as target, find closest to target color, distance btwn them, and # episodes
    results = episode_graph.query(EXACT_LABEL_QUERY, initBindings={'name':label_color.name})
    min_time, min_color, total_episodes = min_color_total_episodes(total_episodes, min_distance, min_color, parameters, results)

    return min_time, min_color, total_episodes

def run_neighbor_heuristic(parameters, episode_graph):
    # find semantic label of target color
    label_color = closest_color(parameters.target_color, num_colors=parameters.num_labels)

    # isolate all neighbor labels of target semantic label
    knn = create_knn(parameters.num_labels, parameters.num_neighbors)
    neighbors = knn.query(NEIGHBOR_LABELS_QUERY, initBindings={'name':label_color.name})

    # metrics
    total_episodes = 0
    min_time = -1
    min_distance = 3 * 255
    min_color = None

    # loop through each neighbor label
    for row in neighbors:
        neighbor_name = row[0].value

        # loop through each color within neighbor label and find min color and total episodes
        results = episode_graph.query(EXACT_LABEL_QUERY, initBindings={'name':neighbor_name})
        min_time, min_color, total_episodes = min_color_total_episodes(total_episodes, min_distance, min_color, parameters, results)

    # return min color and total episodes
    return min_time, min_color, total_episodes

# making the graph is now different
# function runs experiment according to parameters set within parameter space
def run_static_experiment(parameters):
    parameters.changes = [[0, parameters.num_labels]]
    return run_dynamic_experiment(parameters)

def run_dynamic_experiment(parameters):
    set_seed(parameters.random_seed)

    # create episodes of color
    if parameters.color_sequence_type == 'random':
        color_list = random_colors(parameters.num_episodes)
    elif parameters.color_sequence_type == 'walk':
        color_list = random_walk(parameters.num_episodes)
    episode_graph = color_episodes_with_changes(color_list, parameters.changes)

    # initializations
    answer = None
    total_episodes = 0
    num_algorithms = 0

    start_time = time() # start clock

    # if current algorithm is exact or neighbor heuristic, run exact label algorithm first and add an episode to total
    if parameters.algorithm in ['exact-heuristic', 'neighbor-heuristic']:
        answer_episode, answer, section_episodes = run_exact_heuristic(parameters, episode_graph)
        total_episodes += section_episodes
        num_algorithms += 1

    # if exact heuristic yields no result and algorithm is neighbor heuristic, add one to episodes and fallbacks
    if parameters.algorithm == 'neighbor-heuristic' and (parameters.always_use_neighbors or answer is None):
        answer_episode, answer, section_episodes = run_neighbor_heuristic(parameters, episode_graph)
        total_episodes += section_episodes
        num_algorithms += 1

    # if no answer, run brute force algorithm
    if answer is None:
        answer_episode, answer, section_episodes = run_brute_force(parameters, episode_graph)
        total_episodes += section_episodes
        num_algorithms += 1

    end_time = time() # end clock
    runtime = end_time - start_time # record total time in seconds

    num_fallbacks = num_algorithms - 1

    # return results
    return Namespace(
        answer=answer,
        answer_episode=answer_episode,
        total_episodes=total_episodes,
        num_fallbacks=num_fallbacks,
        runtime=runtime,
    )
