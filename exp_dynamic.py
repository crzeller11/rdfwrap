from math import ceil, floor
from random import seed as set_seed, randrange, random

from color import Color, closest_color, find_label_index
from experiment import Experiment
from permspace import PermutationSpace
from algorithms import run_dynamic_experiment

# generates a randomized nested list of time, num_label pairs
def generate_changes(num_episodes, num_labels): # add number of changes?
    init_labels = ceil(num_labels / 10)
    episodes_per = num_episodes / (num_labels - init_labels + 1)
    return [[floor(i * episodes_per), init_labels + i] for i in range(num_labels - init_labels + 1)]

def create_dynamic_experiment():
    set_seed(8675309)
    num_random_seeds = 50
    num_target_colors = 50
    target_colors = [Color(randrange(256), randrange(256), randrange(256)) for i in range(num_target_colors)]
    random_seeds = [random() for i in range(num_random_seeds)]
    # parameter space is an instance of Permutation space. Allows us to manipulate many variables in experiment.
    parameter_space = PermutationSpace(
            ['random_seed_index', 'num_episodes', 'num_labels', 'target_color', 'trial', 'algorithm', 'num_neighbors', 'always_use_neighbors'],
            num_episodes=[1000, 10000, 100000],
            num_labels=[20, 50, 100],
            random_seed_index=range(num_random_seeds),
            random_seed=(lambda random_seed_index: random_seeds[random_seed_index]),
            num_neighbors=[0, 2, 5, 10],
            always_use_neighbors=[True, False],
            trial=range(1),
            algorithm=['brute-force', 'exact-heuristic', 'neighbor-heuristic'],
            color_sequence_type='random',
            target_color=target_colors,
            changes=(lambda num_episodes, num_labels: generate_changes(num_episodes, num_labels)),
            target_label=(lambda num_labels, target_color: closest_color(target_color, num_colors=num_labels).name),
            target_label_index=(lambda target_label: find_label_index(target_label)),
            target_label_episode=(lambda changes, target_label_index: [episode for episode, label in changes if label >= target_label_index][0]),
    )
    parameter_space.add_filter(lambda algorithm, num_neighbors: (algorithm not in ('brute-force', 'exact-heuristic') or num_neighbors == 0))
    parameter_space.add_filter(lambda algorithm, always_use_neighbors: (algorithm not in ('brute-force', 'exact-heuristic') or always_use_neighbors))
    parameter_space.add_filter(lambda algorithm, num_neighbors: (algorithm != 'neighbor-heuristic' or num_neighbors > 0))
    return Experiment('dynamic', parameter_space, run_dynamic_experiment)

def main(random_seed_index=None):
    exp = create_dynamic_experiment()

    # uncomment to simply print parameters
    #exp.function = (lambda parameters: parameters)

    if random_seed_index is None:
        exp.run()
    elif random_seed_index < 49:
        exp.run_between(
            Namespace(random_seed_index=random_seed_index),
            Namespace(random_seed_index=random_seed_index+1),
        )
    else:
        exp.run_from(Namespace(random_seed_index=random_seed_index))

if __name__ == '__main__':
    if len(argv) == 1:
        main()
    elif len(argv) != 2:
        print('Error: incorrect usage: {}'.format(' '.join(argv)))
        exit(1)
    else:
        main(int(argv[1]))
