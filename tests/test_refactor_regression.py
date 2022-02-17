"""
Temporary test against the current 'correct' outputs (for fearless refactoring).
There's always a chance the current code has bugs, so a failure of this test is
not necessarily an issue, it's more an indication to re-check so that nothing is
inadvertently lost along the way.

Tests against the legacy code which is still kept in this repo.

It would be best to remove this test after the refactor.

Notes:
- NoRel timeline is already tested specifically in test_load.test_norel_timeline
"""

import pathlib

import pandas as pd
from pandas.testing import assert_frame_equal

import grblogtools.api as glt
import grblogtools.grblogtools as glt_legacy

HERE = pathlib.Path(__file__).parent


def stem(path: str) -> str:
    return pathlib.Path(path).parts[-1]


def normalize(df):
    """Convert log file paths to file name, and remove index."""
    return df.assign(LogFilePath=lambda df: df["LogFilePath"].apply(stem)).reset_index(
        drop=True
    )


def test_summary():
    """Check summary dataframe from glass4 examples logs are unchanged.

    Changes from current version are:
        - Seed is always an integer (default-filled with zeros)
        - Time is parsed as a datetime type, not stored as string
    """
    glob_files = "data/*.log"
    expected = normalize(
        glt_legacy.get_dataframe([glob_files])
        .rename(columns={"ReadTime": "ReadingTime"})
        .assign(
            Time=lambda df: pd.to_datetime(df["Time"]),
            Seed=lambda df: df["Seed"].astype(int),
        )
        .sort_values("LogFilePath")
    )
    summary = normalize(glt.get_dataframe([glob_files]).sort_values("LogFilePath"))
    assert_frame_equal(summary[expected.columns], expected)


def test_nodelog_timelines():
    """Check nodelog timelines for glass4 with defaults parameters are unchanged."""
    glob_files = "data/912-glass4-*.log"
    _, timelines = glt_legacy.get_dataframe([glob_files], timelines=True)
    expected = normalize(
        timelines["nodelog"]
        .assign(
            Seed=lambda df: df["Seed"].astype(int),
        )
        .sort_values(["LogFilePath", "Time"])
    )
    _, timelines = glt.get_dataframe([glob_files], timelines=True)
    nodelog = normalize(timelines["nodelog"].sort_values(["LogFilePath", "Time"]))
    assert_frame_equal(nodelog[expected.columns], expected)


def test_rootlp_timelines():
    """Check timelines for LP test data are unchanged."""
    glob_files = "tests/assets/lp*.log"
    _, timelines = glt_legacy.get_dataframe([glob_files], timelines=True)
    expected = normalize(
        timelines["rootlp"]
        .assign(
            Type=lambda df: df["Type"].replace("crossover", "simplex"),
            Model=lambda df: df["Model"].apply(lambda p: p.split(".")[0]),
        )
        .sort_values(["LogFilePath", "Time"])
    ).drop(columns="Indicator")
    _, timelines = glt.get_dataframe([glob_files], timelines=True)
    rootlog = normalize(timelines["rootlp"].sort_values(["LogFilePath", "Time"]))
    assert_frame_equal(rootlog[expected.columns], expected)
