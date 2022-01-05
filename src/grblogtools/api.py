import glob

import pandas as pd

from grblogtools.single_log_parser import SingleLogParser


class ParseResult:
    def __init__(self):
        self.parsers = []

    def summary(self):
        return pd.DataFrame([parser.get_summary() for parser in self.parsers])

    def parse(self, logfile):
        parser = SingleLogParser()
        with open(logfile) as infile:
            lines = iter(infile)
            for line in lines:
                if parser.start_parsing(line):
                    for line in lines:
                        parser.continue_parsing(line)
        self.parsers.append(parser)


def parse(arg) -> ParseResult:
    result = ParseResult()
    for logfile in glob.glob(arg):
        result.parse(logfile)
    return result


def get_dataframe(logfiles):
    result = parse(*logfiles)
    return result.summary()
