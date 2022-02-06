"""Top level API for parsing log files.

Usage example:
    import grblogtools.api as glt
    result = glt.parse("data/*.log")
    result.summary()
    result.progress(section="nodelog")

OR, use
    summary = glt.get_dataframe("data/*.log", timeline=False)
    summary, timeline = glt.get_dataframe("data/*.log", timeline=True)
"""

import glob
from pathlib import Path

import pandas as pd

from grblogtools.helpers import fill_default_parameters_nosuffix, strip_model_and_seed
from grblogtools.parsers.single_log import SingleLogParser


class ParseResult:
    def __init__(self):
        self.parsers = []
        self._common = None

    def progress(self, section="nodelog") -> dict:
        """Return the search progress for the given section in the log.

        Args:
            section (str): Possible values are norel, rootlp, and nodelog. Defaults
                to nodelog.

        Returns:
            pd.DataFrame: A data frame representing the progress of the given section
                in the log.
        """
        progress = []
        for logfile, lognumber, parser in self.parsers:
            runner = {
                "nodelog": parser.nodelog_parser.get_progress,
                "rootlp": parser.continuous_parser.get_progress,
                "norel": parser.norel_parser.get_progress,
            }[section]

            if self._common is not None:
                query = self._common.query(
                    f"LogNumber == {lognumber} & LogFilePath == '{logfile}'"
                ).iloc[0]
            for row in runner():
                extended_row = dict(row, LogFilePath=logfile, LogNumber=lognumber)
                if self._common is not None:
                    extended_row.update({key: query[key] for key in query.index})
                progress.append(extended_row)

        return pd.DataFrame(progress)

    def summary(self):
        """Construct and return a summary dataframe for all parsed logs."""
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

        # The columns to save in the progress dataframes if exists
        self._common = summary[
            [
                col
                for col in [
                    "ModelFile",
                    "Model",
                    "Log",
                    "LogFilePath",
                    "LogNumber",
                    "Seed",
                    "Version",
                ]
                if col in summary.columns
            ]
        ]
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

    If one log file contains more than one run, all runs are parsed, each reported
    as a separate row in the summay and timelines dataframes.

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
