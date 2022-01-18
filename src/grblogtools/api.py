"""Top level API for parsing log files.

Examples:

    import grblogtools.api as glt
    result = glt.parse("data/*.log")
    result.summary()  # summary dataframe (like get_dataframe)

Similar for dataframes

"""

import glob
from pathlib import Path

import pandas as pd

from grblogtools.helpers import fill_default_parameters_nosuffix
from grblogtools.parsers.single_log import SingleLogParser


def strip_model_and_seed(row):
    """
    If the log path contains the model name, return everything to the left.
    Otherwise, just return the log stem.

    i.e. with Model = 'glass4'
        data/912-Cuts0-glass4-0.log -> 912-Cuts0
        data/some-log.log -> some-log
    """
    log_stem = Path(row["LogFilePath"]).stem
    run, mid, _ = log_stem.partition(row["Model"])
    if mid and run:
        return run.rstrip("-")
    return log_stem


class ParseResult:
    def __init__(self):
        self.parsers = []

    def progress(self, section="nodelog") -> dict:
        """Return the optimization search progress of the given section in the log.

        Args:
            section (str): Possible values are 'norel', 'rootlp', and 'nodelog'.
                Defaults to 'nodelog'.
        Returns:
            pf.DataFrame: A data frame representing the progress of the given section
                in the log.
        """
        return pd.DataFrame(
            [
                dict(row, LogFilePath=logfile, LogNumber=lognumber)
                for logfile, lognumber, parser in self.parsers
                for row in {
                    "nodelog": parser.nodelog_parser.get_progress(),
                    "rootlp": parser.continuous_parser.get_progress(),
                    "norel": parser.norel_parser.get_progress(),
                }[section]
            ]
        )

    def summary(self):
        """Construct and return a summary dataframe for all parsed logs.
        Some post-processing performed."""
        summary = pd.DataFrame(
            [
                dict(parser.get_summary(), LogFilePath=logfile, LogNumber=lognumber)
                for logfile, lognumber, parser in self.parsers
            ]
        )
        parameters = pd.DataFrame(
            [parser.header_parser.get_parameters() for _, _, parser in self.parsers]
        )
        # Fill defaults and add suffix to parameter columns.
        parameters = (
            fill_default_parameters_nosuffix(parameters.join(summary["Version"]))
            .drop(columns="Version")
            .rename(columns=lambda c: c if c == "Seed" else c + " (Parameter)")
        )
        summary = (
            summary.rename(columns={"ReadingTime": "ReadTime"})
            .join(parameters)
            .assign(
                ModelFile=lambda df: df["ModelFilePath"].apply(
                    lambda p: Path(p).parts[-1].partition(".")[0]
                ),
                Model=lambda df: df["ModelFile"],
                Log=lambda df: df.apply(strip_model_and_seed, axis=1),
            )
        )
        return summary

    def parse(self, logfile: str) -> None:
        """Parse a single file. The log file may contain multiple run logs."""
        parser = SingleLogParser()
        subsequent = SingleLogParser()
        lognumber = 1
        with open(logfile) as infile:
            lines = iter(infile)
            for line in lines:
                if not parser.parse(line):
                    assert not subsequent.started
                    if subsequent.parse(line):
                        # The current parser did not match but an empty parser
                        # matched a header line.
                        self.parsers.append((logfile, lognumber, parser))
                        lognumber += 1
                        parser = subsequent
                        subsequent = SingleLogParser()

        self.parsers.append((logfile, lognumber, parser))


def parse(arg: str) -> ParseResult:
    """Main entry point function.

    Args:
        arg (str): A glob pattern matchine log files.

    TODO extend this, a list of patterns, or a vararg of patterns, should also work.
    """
    result = ParseResult()
    for logfile in glob.glob(arg):
        result.parse(logfile)
    return result


def get_dataframe(logfiles, timelines=False):
    """Compatibility function for the legacy API.

    Args:
        logfiles (str): A glob pattern of the log files.
        timeliens (bool, optional): Return the norel, the relaxation, and the
            search tree progress if set to True. Defaults to False.
    """
    result = parse(*logfiles)
    if not timelines:
        return result.summary()
    return result.summary(), dict(
        norel=result.progress("norel"),
        rootlp=result.progress("rootlp"),
        nodelog=result.progress("nodelog"),
    )
