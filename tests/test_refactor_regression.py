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
import pytest
from pandas.testing import assert_frame_equal

import grblogtools as glt_legacy
import grblogtools.api as glt

HERE = pathlib.Path(__file__).parent


def stem(path: str) -> str:
    return pathlib.Path(path).parts[-1]


def normalize(df):
    """Convert full log file paths to file name only, and remove index in
    case it was affected by sorting."""
    return df.assign(LogFilePath=lambda df: df["LogFilePath"].apply(stem)).reset_index(
        drop=True
    )


@pytest.fixture
def glass4_legacy_summary():
    summary = glt_legacy.get_dataframe(["data/*.log"])
    summary["Time"] = pd.to_datetime(summary["Time"])
    summary["Seed"] = summary["Seed"].astype(int)
    return summary


@pytest.fixture
def glass4_legacy_nodelogs():
    _, timelines = glt_legacy.get_dataframe(["data/*.log"], timelines=True)
    return timelines["nodelog"]


@pytest.fixture
def lp_legacy_rootlogs():
    _, timelines = glt_legacy.get_dataframe(["tests/assets/lp*.log"], timelines=True)
    return timelines["rootlp"]


def test_summary(glass4_legacy_summary):
    expected = normalize(glass4_legacy_summary.sort_values("LogFilePath"))
    expected = expected.drop(columns=["ModelType"])  # post-processing?
    summary = normalize(glt.get_dataframe(["data/*.log"]).sort_values("LogFilePath"))
    assert_frame_equal(summary[expected.columns], expected)


@pytest.mark.xfail
def test_nodelog_timelines(glass4_legacy_nodelogs):
    expected = normalize(glass4_legacy_nodelogs.sort_values(["LogFilePath", "Time"]))
    _, timelines = glt.get_dataframe(["data/912-glass4-*.log"], timelines=True)
    nodelog = normalize(timelines["nodelog"].sort_values(["LogFilePath", "Time"]))
    assert_frame_equal(nodelog[expected.columns], expected)


@pytest.mark.xfail
def test_rootlp_timelines(lp_legacy_rootlogs):
    expected = normalize(lp_legacy_rootlogs.sort_values(["LogFilePath", "Time"]))
    _, timelines = glt.get_dataframe(["tests/assets/lp*.log"], timelines=True)
    rootlog = normalize(timelines["nodelog"].sort_values(["LogFilePath", "Time"]))
    assert_frame_equal(rootlog[expected.columns], expected)
