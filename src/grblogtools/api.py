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
import itertools
from pathlib import Path

import pandas as pd

from grblogtools.helpers import (
    add_categorical_descriptions,
    fill_default_parameters_nosuffix,
    strip_model_and_seed,
)
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

            if section == "nodelog":
                log = parser.nodelog_parser.get_progress()
            elif section == "rootlp":
                log = parser.continuous_parser.get_progress()
            elif section == "norel":
                log = parser.norel_parser.get_progress()
            else:
                raise ValueError(f"Unknown section '{section}'")

            progress.append(
                pd.DataFrame(log).assign(LogFilePath=logfile, LogNumber=lognumber)
            )

        return pd.merge(
            left=pd.concat(progress),
            right=self.common_log_data(),
            how="left",
            on=["LogFilePath", "LogNumber"],
        )

    def common_log_data(self):
        """Extract common data to be joined to progress and summary dataframes.
        This could be cached in future and invalidated by .parse()"""
        common = pd.DataFrame(
            [
                {
                    "LogFilePath": logfile,
                    "LogNumber": lognumber,
                    "ModelFilePath": parser.header_parser.get_summary().get(
                        "ModelFilePath"
                    ),
                    "Seed": parser.header_parser.get_parameters().get("Seed", 0),
                    "Version": parser.header_parser.get_summary().get("Version"),
                }
                for logfile, lognumber, parser in self.parsers
            ]
        )
        common = common.dropna(axis="columns", how="all")
        # FIXME might not have some required columns for the below assignments
        common = common.assign(
            ModelFile=lambda df: df["ModelFilePath"].apply(
                lambda p: Path(p).parts[-1].partition(".")[0]
            ),
            Model=lambda df: df["ModelFile"],
            Log=lambda df: df.apply(strip_model_and_seed, axis=1),
        )
        return common

    def summary(self, prettyparams=False):
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
            .drop(columns=["Version", "Seed"], errors="ignore")
            .rename(columns=lambda c: c + " (Parameter)")
        )
        # Convert parameters to categorical if required.
        if prettyparams:
            parameters = add_categorical_descriptions(parameters)
        # FIXME this renaming is unnecessary
        summary = summary.rename(columns={"ReadingTime": "ReadTime"}).join(parameters)
        summary = pd.merge(
            left=summary.drop(columns=["ModelFilePath", "Version"], errors="ignore"),
            right=self.common_log_data(),
            how="left",
            on=["LogFilePath", "LogNumber"],
            suffixes=(None, "_dupe"),
        )
        assert not [c for c in summary.columns if "_dupe" in c]
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


def parse(*patterns: str) -> ParseResult:
    """Main entry point function.

    Args:
        patterns (str): glob pattern(s) matching log files.

    """
    result = ParseResult()
    logfiles = itertools.chain(*(glob.glob(pattern) for pattern in patterns))
    for logfile in sorted(set(logfiles)):
        result.parse(logfile)
    return result


def get_dataframe(logfiles, timelines=False, prettyparams=False):
    """Compatibility function for the legacy API.

    If one log file contains more than one run, all runs are parsed, each reported
    as a separate row in the summay and timelines dataframes.

    Args:
        logfiles (str): A glob pattern of the log files.
        timelines (bool, optional): Return the norel, the relaxation, and the
            search tree progress if set to True. Defaults to False.
    """
    result = parse(*logfiles)
    summary = result.summary(prettyparams=prettyparams)
    if not timelines:
        return summary
    return summary, dict(
        norel=result.progress("norel"),
        rootlp=result.progress("rootlp"),
        nodelog=result.progress("nodelog"),
    )
