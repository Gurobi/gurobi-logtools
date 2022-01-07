import glob
from pathlib import Path

import pandas as pd

from grblogtools.helpers import fill_default_parameters
from grblogtools.single_log_parser import SingleLogParser


class ParseResult:
    def __init__(self):
        self.parsers = []

    def summary(self):
        summary = pd.DataFrame(
            [
                dict(parser.get_summary(), LogFilePath=logfile)
                for logfile, parser in self.parsers
            ]
        )
        # Post-processing to match old API
        parameters = pd.DataFrame(
            [parser.header_parser.get_parameters() for _, parser in self.parsers]
        )
        seed = parameters[["Seed"]].fillna(0).astype(int)
        parameters = parameters.drop(columns=["Seed"]).rename(
            columns=lambda c: c + " (Parameter)"
        )
        summary = (
            summary.rename(columns={"ReadingTime": "ReadTime"})
            .join(parameters)
            .join(seed)
            .assign(
                #         Model=lambda df: df["ModelFilePath"],
                ModelFile=lambda df: df["ModelFilePath"].apply(
                    lambda p: Path(p).parts[-1].partition(".")[0]
                ),
                #         Log=lambda df: df["LogFilePath"],
            )
        )
        # TODO fill_default_parameters could be much cleaner now, without column regexes
        summary = fill_default_parameters(summary)
        return summary

    def parse(self, logfile: str) -> None:
        """Parse a single log from one file."""
        parser = SingleLogParser()
        with open(logfile) as infile:
            lines = iter(infile)
            for line in lines:
                if parser.start_parsing(line):
                    for line in lines:
                        parser.continue_parsing(line)
        self.parsers.append((logfile, parser))


def parse(arg) -> ParseResult:
    result = ParseResult()
    for logfile in glob.glob(arg):
        result.parse(logfile)
    return result


def get_dataframe(logfiles):
    result = parse(*logfiles)
    return result.summary()
