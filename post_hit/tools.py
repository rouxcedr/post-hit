"""
Bindings to different bioinformatics utilities used to process files.
"""


import os
from subprocess import PIPE, Popen


class GenericTool(object):
    pass


class ResultsIterator(object):
    def __init__(self, stream):
        self.stream = stream

    def __iter__(self):
        return self

    def __next__(self):
        line = self.stream.readline().decode("utf-8")
        if not line:
            self.stream.close()
            raise StopIteration()

        return line

    next = __next__


class BigBedToBed(GenericTool):
    def __init__(self, binary_path="/home/cedric/ucsc_tools/bigBedToBed"):
        self.binary_path = binary_path
        self.parameters = set(("chrom", "start", "end", "maxItems", "udcDir"))

    def call(self, input_filename, **kwargs):
        params = format_ucsc_params(self.binary_path, input_filename,
                                    self.parameters, kwargs)
        p = Popen(params, stdout=PIPE)
        return ResultsIterator(p.stdout)


class BigWigToWig(GenericTool):
    def __init__(self, binary_path="/home/cedric/ucsc_tools/bigWigToWig"):
        self.binary_path = binary_path
        self.parameters = set(("chrom", "start", "end", "udcDir"))

    def call(self, input_filename, **kwargs):
        params = format_ucsc_params(self.binary_path, input_filename,
                                    self.parameters, kwargs)
        p = Popen(params, stdout=PIPE)
        return ResultsIterator(p.stdout)


def format_ucsc_params(binary_path, input_filename, params_set, values):
    """Format parameters according to the UCSC utility syntax."""
    params = [binary_path]
    for param, value in values.items():
        if param not in params_set:
            raise ValueError("Invalid parameters '{}'".format(param))

        params.append("-{}={}".format(param, value))

    if not os.path.isfile(input_filename):
        raise IOError("Could not find file '{}'".format(input_filename))

    params.append(input_filename)
    # TODO Create a temporary file instead for compatibility on lesser
    # OSes.
    params.append("/dev/stdout")
    return [str(i) for i in params]
