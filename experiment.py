from datetime import datetime
from getpass import getuser
from os import getcwd
from socket import gethostname

from permspace import Namespace

class Experiment:
    def __init__(self, name, parameter_space, function):
        self.name = name
        self.parameter_space = parameter_space
        self.function = function
        self.machine_info = Namespace(
            _username=getuser(),
            _hostname=gethostname(),
            _pwd=getcwd(),
        )
        self.order = []
        self.order.extend(sorted(parameter_space.independents.keys()))
        self.order.extend(sorted(parameter_space.dependents_topo))
        self.order.extend(sorted(parameter_space.constants.keys()))
        self.order.extend(sorted(self.machine_info.keys()))
        self.order.extend(['_start_time', '_end_time'])
    def _run(self, iterator_modifier=None):
        print_headers = True
        start_time = datetime.now().isoformat()
        output_file = '{}-{}-results.csv'.format(self.name, start_time)
        with open(output_file, 'a') as fd:
            iterator = self.parameter_space
            if iterator_modifier is not None:
                iterator = iterator_modifier(iterator)
            for parameters in iterator:
                run_info = Namespace(
                    _start_time=datetime.now().isoformat(sep=' '),
                )
                results = self.function(parameters)
                run_info.update(_end_time=datetime.now().isoformat(sep=' '))
                if print_headers:
                    fd.write('\t'.join(self.order + sorted(results.keys())) + '\n')
                    print_headers = False
                csv_row = Namespace()
                csv_row.update(**parameters)
                csv_row.update(**results)
                csv_row.update(**self.machine_info)
                csv_row.update(**run_info)
                fd.write(csv_row.to_csv_row(self.order) + '\n')
    def run(self):
        self._run()
    def run_from(self, start=None):
        self._run((lambda iterator: iterator.iter_from(start)))
    def run_until(self, end=None):
        self._run((lambda iterator: iterator.iter_until(end)))
    def run_between(self, start=None, end=None):
        self._run((lambda iterator: iterator.iter_between(start, end)))
