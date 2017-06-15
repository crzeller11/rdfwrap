from collections import namedtuple
from random import seed as set_seed
from time import time
from datetime import datetime

from rdflib.plugins.sparql import prepareQuery

from color import Color, create_knn, closest_color
from chroma_wanderer import random_walk, random_colors, color_episodes
from permspace import PermutationSpace, Namespace
from rdfwrap import NXRDF

ExperimentResult = namedtuple('ExperimentResult', ['answer', 'total_episodes', 'num_fallbacks', 'runtime'])

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

    # return instance in ExperimentResult with min color and total episodes
    return ExperimentResult(answer=min_color, total_episodes=total_episodes, num_fallbacks=0, runtime=0)

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

    return ExperimentResult(answer=min_color, total_episodes=total_episodes, num_fallbacks=0, runtime=0)

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
        min_color, total_episodes = min_color_total_episodes(total_episodes, min_distance, min_color, parameters, episode_graph.query(query))

    # return instance of ExperimentResult with the min color and total episodes
    return ExperimentResult(answer=min_color, total_episodes=total_episodes, num_fallbacks=0, runtime=0)

# function runs experiment according to parameters set within parameter space
def run_experiment(parameters):
    set_seed(parameters.random_seed)

    # create episodes of color
    if parameters.color_sequence_type == 'random':
        color_list = random_colors(parameters.num_episodes)
    elif parameters.color_sequence_type == 'walk':
        color_list = random_walk(parameters.num_episodes)
    episode_graph = color_episodes(color_list, num_labels=parameters.num_labels)

    # initializations
    total_episodes = 0
    num_fallbacks = 0
    result = ExperimentResult(answer=None, total_episodes=total_episodes, num_fallbacks=num_fallbacks, runtime=0)

    start_time = time() # start clock

    # if current algorithm is exact or neighbor heuristic, run exact label algorithm first and add an episode to total
    if parameters.algorithm in ['exact-heuristic', 'neighbor-heuristic']:
        result = run_exact_heuristic(parameters, episode_graph)
        total_episodes += result.total_episodes

    # if exact heuristic yields no result and algorithm is neighbor heuristic, add one to episodes and fallbacks
    if result.answer is None and parameters.algorithm == 'neighbor-heuristic':
        result = run_neighbor_heuristic(parameters, episode_graph)
        total_episodes += result.total_episodes
        num_fallbacks += 1

    # if no answer, run brute force algorithm
    if result.answer is None:
        result = run_brute_force(parameters, episode_graph)
        total_episodes = result.total_episodes
        if parameters.algorithm != 'brute-force':
            num_fallbacks += 1

    end_time = time() # end clock
    runtime = end_time - start_time # record total time in seconds

    # record results
    result = ExperimentResult(
            answer=result.answer,
            total_episodes=total_episodes,
            num_fallbacks=num_fallbacks,
            runtime=runtime,
    )

    # return metrics
    return result

def main():
    # parameter space is an instance of Permutation space. Allows us to manipulate many variables in experiment.
    parameter_space = PermutationSpace(['num_episodes', 'num_labels', 'target_color_hex', 'random_seed', 'num_neighbors', 'num_trials', 'algorithm'],
            num_episodes=[1, 10, 100, 1000, 10000, 100000],
            # num_episodes=[10 ** n for n in range(1, 4)],

            num_labels=[5, 20, 45, 70, 150],
            # num_labels=range(10, 101, 10),

            target_color_hex=['#808080', '#FFD8F9', '#104E8B', '#8B0000', '#3383FF'],

            random_seed=[8675309, 5487810, 1332113, 8749701, 8718348], # will work across a variability of different types of colors

            num_neighbors=range(1, 6),

            num_trials=20,
            # num_trials=range(10),

            algorithm=['brute-force', 'exact-heuristic', 'neighbor-heuristic'],

            target_color=(lambda target_color_hex: Color.from_hex(target_color_hex)),

            color_sequence_type='random',
            # color_sequence_type=['random', 'walk'],

            timestamp=(lambda: datetime.now().isoformat(sep=' ')),
    )

    # filter to parameter space so the # of neighbors doesn't exceed 1 for brute-force and exact-heuristic algorithms
    parameter_space.add_filter(
            (lambda algorithm, num_neighbors:
                not (algorithm in ['brute-force', 'exact-heuristic'] and num_neighbors > 1)))

    with open('results-' + datetime.now().isoformat(), 'a') as fd:
        for parameters in parameter_space:
            results = run_experiment(parameters)
            parameters.update(**results._asdict())
            fd.write(str(parameters) + '\n')

if __name__ == '__main__':
    main()
