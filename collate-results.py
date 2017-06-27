#!/usr/bin/env python3

import re
from csv import DictReader, DictWriter
from os import listdir, getcwd
from collections import defaultdict
from argparse import ArgumentParser
from datetime import datetime

def main():
    arg_parser = ArgumentParser(usage='%(prog)s CSV ...')
    arg_parser.add_argument('csvs', metavar='CSV', nargs='+', help='result files')
    args = arg_parser.parse_args()

    experiment_name = None
    latest = None
    fieldnames = None
    result_files = []

    for file in args.csvs:
        match = re.match(r'^(?P<experiment_name>[a-z0-9_-]*)-(?P<timestamp>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.-]*)-results.csv$', file)
        assert match, 'file does not conform to "<experiment>-<timestamp>-results.csv" naming: {}'.format(file)
        date = datetime.strptime(match.group('timestamp'), '%Y-%m-%dT%H:%M:%S.%f')
        if experiment_name is None:
            experiment_name = match.group('experiment_name')
            latest = date
            with open(file) as fd:
                fieldnames = DictReader(fd, delimiter='\t').fieldnames
        else:
            assert experiment_name == match.group('experiment_name'), 'file has different experiment name: {}'.format(file)
            if latest < date:
                latest = date
            with open(file) as fd:
                assert fieldnames == DictReader(fd, delimiter='\t').fieldnames, 'file has different fields: {}'.format(file)
        result_files.append(file)

    assert fieldnames is not None, 'could not determine field names'

    output_file = '{}-{}-collated.csv'.format(experiment_name, latest.isoformat())
    with open(output_file, 'w') as out_fd:
        writer = DictWriter(out_fd, fieldnames=fieldnames)
        writer.writeheader()
        for file in result_files:
            with open(file) as in_fd:
                reader = DictReader(in_fd, delimiter='\t')
                for row in reader:
                    writer.writerow(row)

if __name__ == '__main__':
    main()
