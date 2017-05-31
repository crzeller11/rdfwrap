from collections import namedtuple
from random import seed as set_seed
from time import time

from color import Color, create_knn, closest_color
from chroma_wanderer import random_walk, random_colors, color_episodes
from permspace import PermutationSpace, Namespace
from rdfwrap import NXRDF

ExperimentResult = namedtuple('ExperimentResult', ['answer', 'total_episodes', 'num_fallbacks'])

def run_brute_force(parameters, episode_graph):
    query = '''
    SELECT DISTINCT ?time ?name ?r ?g ?b
        WHERE {
            ?episode nxrdf:episode ?time ;
                     nxrdf:color_name ?name ;
                     nxrdf:red ?r ;
                     nxrdf:green ?g ;
                     nxrdf:blue ?b .
        }
        ORDER BY ASC(?time)
    '''

    # metrics
    total_episodes = 0

    min_distance = 3 * 255
    min_color = None
    for result in episode_graph.query(query):
        episode_color = Color(result[2].value, result[3].value, result[4].value)
        distance = parameters.target_color - episode_color
        if distance < min_distance:
            min_distance = distance
            min_color = episode_color
        total_episodes += 1

    return ExperimentResult(answer=min_color, total_episodes=total_episodes, num_fallbacks=0)

def run_exact_label(parameters, episode_graph):
    label_color = closest_color(parameters.target_color, num_colors=parameters.num_labels)

    query = '''
    SELECT DISTINCT ?time ?name ?r ?g ?b
        WHERE {{
            ?episode nxrdf:episode ?time ;
                     nxrdf:color_name "{}" ;
                     nxrdf:red ?r ;
                     nxrdf:green ?g ;
                     nxrdf:blue ?b .
        }}
        ORDER BY ASC(?time)
    '''.format(label_color.name)

    # metrics
    total_episodes = 0

    min_distance = 3 * 255
    min_color = None
    for result in episode_graph.query(query):
        episode_color = Color(result[2].value, result[3].value, result[4].value)
        distance = parameters.target_color - episode_color
        if distance < min_distance:
            min_distance = distance
            min_color = episode_color
        total_episodes += 1

    return ExperimentResult(answer=min_color, total_episodes=total_episodes, num_fallbacks=0)

def run_neighbor_labels(parameters, episode_graph):
    label_color = closest_color(parameters.target_color, num_colors=parameters.num_labels)

    knn = create_knn(parameters.num_labels, parameters.num_neighbors)

    neighbor_query = '''
    SELECT DISTINCT ?neighbor_name
        WHERE {{
            ?parent nxrdf:neighbor ?neighbor ;
                    nxrdf:color_name "{}" .
            ?neighbor nxrdf:color_name ?neighbor_name .
        }}
        ORDER BY ASC(?time)
    '''.format(label_color.name)

    neighbors = knn.query(neighbor_query)

    total_episodes = 0

    min_distance = 3 * 255
    min_color = None

    for row in neighbors:
        neighbor_name = row[0].value

        query = '''
        SELECT DISTINCT ?time ?name ?r ?g ?b
            WHERE {{
                ?episode nxrdf:episode ?time ;
                         nxrdf:color_name "{}" ;
                         nxrdf:red ?r ;
                         nxrdf:green ?g ;
                         nxrdf:blue ?b .
            }}
            ORDER BY ASC(?time)
        '''.format(neighbor_name)

        for result in episode_graph.query(query):
            episode_color = Color(result[2].value, result[3].value, result[4].value)
            distance = parameters.target_color - episode_color
            if distance < min_distance:
                min_distance = distance
                min_color = episode_color
            total_episodes += 1

    return ExperimentResult(answer=min_color, total_episodes=total_episodes, num_fallbacks=0)

def run_experiment(parameters):
    set_seed(parameters.random_seed)

    # create episodes of color
    if parameters.color_sequence_type == 'random':
        color_list = random_colors(parameters.num_episodes)
    elif parameters.color_sequence_type == 'walk':
        color_list = random_walk(parameters.num_episodes)
    episode_graph = color_episodes(color_list, num_labels=parameters.num_labels)

    total_episodes = 0
    num_fallbacks = 0
    result = ExperimentResult(answer=None, total_episodes=total_episodes, num_fallbacks=num_fallbacks)

    start_time = time()

    if parameters.algorithm in ['exact-heuristic', 'neighbor-heuristic']:
        result = run_exact_label(parameters, episode_graph)
        total_episodes += result.total_episodes

    if result.answer is None and parameters.algorithm == 'neighbor-heuristic':
        result = run_neighbor_labels(parameters, episode_graph)
        total_episodes += result.total_episodes
        num_fallbacks += 1

    if result.answer is None:
        result = run_brute_force(parameters, episode_graph)
        total_episodes = result.total_episodes
        if parameters.algorithm != 'brute-force':
            num_fallbacks += 1

    end_time = time()
    runtime = end_time - start_time # seconds

    result = ExperimentResult(
            answer=result.answer,
            total_episodes=total_episodes,
            num_fallbacks=num_fallbacks,
    )

    print(runtime, result.total_episodes, result.num_fallbacks, str(result.answer))

def main():
    parameter_space = PermutationSpace(['num_episodes', 'num_labels', 'target_color_hex', 'random_seed', 'num_neighbors', 'num_trials', 'algorithm'],
            random_seed=8675309,

            #num_episodes=[10 ** n for n in range(1, 4)],
            num_episodes=5,

            #num_labels=range(10, 101, 10),
            num_labels=10,

            target_color_hex='#808080',

            target_color=(lambda target_color_hex: Color.from_hex(target_color_hex)),

            algorithm=['brute-force', 'exact-heuristic', 'neighbor-heuristic'],

            #color_sequence_type=['random', 'walk'],
            color_sequence_type='random',

            #num_trials=range(10),
            num_trials=1,

            num_neighbors=range(1, 6),
    )
    parameter_space.add_filter(
            (lambda algorithm, num_neighbors:
                not (algorithm in ['brute-force', 'exact-heuristic'] and num_neighbors > 1)))
    for parameters in parameter_space:
        print(parameters)
        run_experiment(parameters)

if __name__ == '__main__':
    main()
