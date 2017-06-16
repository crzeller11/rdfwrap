from random import seed as set_seed, randrange, random
from time import time

from rdflib.plugins.sparql import prepareQuery

from chroma_wanderer import random_walk, random_colors, color_episodes
from color import Color, create_knn, closest_color
from experiment import Experiment
from permspace import PermutationSpace, Namespace
from rdfwrap import NXRDF

EXACT_LABEL_QUERY = prepareQuery('''
SELECT DISTINCT ?time ?name ?r ?g ?b
    WHERE {
        ?episode nxrdf:episode ?time ;
                 nxrdf:color_name ?name ;
                 nxrdf:red ?r ;
                 nxrdf:green ?g ;
                 nxrdf:blue ?b .
    }
    ORDER BY ASC(?time)
''', initNs={'nxrdf':NXRDF.NAMESPACE})

NEIGHBOR_LABELS_QUERY = prepareQuery('''
SELECT DISTINCT ?neighbor_name
    WHERE {
        ?parent nxrdf:neighbor ?neighbor ;
                nxrdf:color_name ?name .
        ?neighbor nxrdf:color_name ?neighbor_name .
    }
    ORDER BY ASC(?time)
''', initNs={'nxrdf':NXRDF.NAMESPACE})

# finds the color closest to target color and minimum distance
def min_color_total_episodes(total_episodes, min_distance, min_color, parameters, results):
    for result in results:
        episode_color = Color(result[2].value, result[3].value, result[4].value)
        distance = parameters.target_color - episode_color
        if distance < min_distance:
            min_distance = distance # min distance is the RGB distance btwn min_color and target_color
            min_color = episode_color # min color is the closest color to target color
        total_episodes += 1
    return min_color, total_episodes

def run_brute_force(parameters, episode_graph):
    # query isolates all colors in graph
    # metrics
    total_episodes = 0
    min_distance = 3 * 255
    min_color = None
    # FIXME: Do we need to restate these every time?

    # for every color in graph, find closest color to target color, distance btwn two colors, and # episodes
    results = episode_graph.query(EXACT_LABEL_QUERY)
    min_color, total_episodes = min_color_total_episodes(total_episodes, min_distance, min_color, parameters, results)

    # return min color and total episodes
    return min_color, total_episodes

def run_exact_heuristic(parameters, episode_graph):
    # find semantic label of target color
    label_color = closest_color(parameters.target_color, num_colors=parameters.num_labels)

    # metrics
    total_episodes = 0
    min_distance = 3 * 255
    min_color = None

    # loop through all colors with same label as target, find closest to target color, distance btwn them, and # episodes
    results = episode_graph.query(EXACT_LABEL_QUERY, initBindings={'name':label_color.name})
    min_color, total_episodes = min_color_total_episodes(total_episodes, min_distance, min_color, parameters, results)

    return min_color, total_episodes

def run_neighbor_heuristic(parameters, episode_graph):
    # find semantic label of target color
    label_color = closest_color(parameters.target_color, num_colors=parameters.num_labels)

    # isolate all neighbor labels of target semantic label
    knn = create_knn(parameters.num_labels, parameters.num_neighbors)
    neighbors = knn.query(NEIGHBOR_LABELS_QUERY, initBindings={'name':label_color.name})

    # metrics
    total_episodes = 0
    min_distance = 3 * 255
    min_color = None

    # loop through each neighbor label
    for row in neighbors:
        neighbor_name = row[0].value

        # loop through each color within neighbor label and find min color and total episodes
        results = episode_graph.query(EXACT_LABEL_QUERY, initBindings={'name':neighbor_name})
        min_color, total_episodes = min_color_total_episodes(total_episodes, min_distance, min_color, parameters, results)

    # return min color and total episodes
    return min_color, total_episodes

# function runs experiment according to parameters set within parameter space
def run_static_experiment(parameters):
    set_seed(parameters.random_seed)

    # create episodes of color
    if parameters.color_sequence_type == 'random':
        color_list = random_colors(parameters.num_episodes)
    elif parameters.color_sequence_type == 'walk':
        color_list = random_walk(parameters.num_episodes)
    episode_graph = color_episodes(color_list, num_labels=parameters.num_labels)

    # initializations
    answer = None
    total_episodes = 0
    num_fallbacks = 0

    start_time = time() # start clock

    # if current algorithm is exact or neighbor heuristic, run exact label algorithm first and add an episode to total
    if parameters.algorithm in ['exact-heuristic', 'neighbor-heuristic']:
        answer, section_episodes = run_exact_heuristic(parameters, episode_graph)
        total_episodes += section_episodes

    # if exact heuristic yields no result and algorithm is neighbor heuristic, add one to episodes and fallbacks
    if answer is None and parameters.algorithm == 'neighbor-heuristic':
        answer, section_episodes = run_neighbor_heuristic(parameters, episode_graph)
        total_episodes += section_episodes
        num_fallbacks += 1

    # if no answer, run brute force algorithm
    if answer is None:
        answer, section_episodes = run_brute_force(parameters, episode_graph)
        total_episodes += section_episodes
        if parameters.algorithm != 'brute-force':
            num_fallbacks += 1

    end_time = time() # end clock
    runtime = end_time - start_time # record total time in seconds

    # return results
    return Namespace(
        answer=answer,
        total_episodes=total_episodes,
        num_fallbacks=num_fallbacks,
        runtime=runtime,
    )

def create_static_experiment_pilot():
    set_seed(8675309)
    num_target_colors = 5
    num_random_seeds = 5
    target_colors = [Color(randrange(256), randrange(256), randrange(256)) for i in range(num_target_colors)]
    random_seeds = [random() for i in range(num_random_seeds)]
    # parameter space is an instance of Permutation space. Allows us to manipulate many variables in experiment.
    parameter_space = PermutationSpace(['random_seed_index', 'num_episodes', 'num_labels', 'target_color', 'algorithm'],
            num_episodes=[1000, 10000, 100000],
            num_labels=[10, 20, 50, 100, 200],
            random_seed_index=range(num_random_seeds),
            random_seed=(lambda random_seed_index: random_seeds[random_seed_index]),
            num_neighbors=0,
            algorithm=['brute-force', 'exact-heuristic'],
            target_color=target_colors,
            target_color_hex=(lambda target_color: str(target_color)),
            color_sequence_type='random',
    )
    return Experiment('static-experiment-pilot', parameter_space, run_static_experiment)
