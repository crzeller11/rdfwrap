from sys import argv

from permspace import Namespace
from experiments import create_static_experiment

def main(random_seed_index):
    exp = create_static_experiment()

    # uncomment to simply print parameters
    #exp.function = (lambda parameters: parameters)

    if random_seed_index < 49:
        exp.run_between(
            Namespace(random_seed_index=random_seed_index),
            Namespace(random_seed_index=random_seed_index+1),
        )
    else:
        exp.run_from(Namespace(random_seed_index=random_seed_index))


if __name__ == '__main__':
    if len(argv) != 2:
        print('Error: incorrect usage: {}'.format(' '.join(argv)))
        exit(1)
    else:
        main(int(argv[1]))
