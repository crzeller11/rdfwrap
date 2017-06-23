from sys import argv

from permspace import Namespace
from experiments import create_static_experiment_pilot

def main(random_seed_index):
    exp = create_static_experiment_pilot()
    exp.function = (lambda parameters: parameters)
    exp.run_between(
        Namespace(random_seed_index=random_seed_index),
        Namespace(random_seed_index=random_seed_index+1),
    )

if __name__ == '__main__':
    if len(argv) != 2:
        print('Error: uncorrect usage: {}'.format(' '.join(argv)))
        exit(1)
    else:
        main(int(argv[1]))
