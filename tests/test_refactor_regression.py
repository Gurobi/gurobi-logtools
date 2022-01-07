"""
Temporary test against the current 'correct' outputs (for fearless refactoring).
There's always a chance the current code has bugs, so a failure of this test is
not necessarily an issue, it's more an indication to re-check so that nothing is
inadvertently lost along the way.

Uses feather format to store the comparison dataframe (for type consistency),
so pyarrow needs to be installed. This is also temporarily added to the tox config.

It would be best to remove this test after the refactor.

Notes:
- NoRel timeline is already tested specifically in test_load.test_norel_timeline
"""

import pathlib

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

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


def test_summary():
    expected = normalize(
        pd.read_feather(HERE / "assets/summary.feather").sort_values("LogFilePath")
    )
    expected = expected.drop(columns=["ModelType", "Model", "Log"])  # post-processing?
    expected = expected.drop(
        columns=["RelaxIterCount", "RelaxObj", "RelaxTime"]
    )  # coming from cont. parser
    expected = expected.drop(
        columns=[c for c in expected.columns if c.startswith("Cuts")]
    )  # coming from nodelog parser
    summary = normalize(glt.get_dataframe(["data/*.log"]).sort_values("LogFilePath"))
    assert_frame_equal(summary[expected.columns], expected)


@pytest.mark.xfail(reason="not implemented in new api yet")
def test_nodelog_timelines():
    _, timelines = glt.get_dataframe(["data/912-glass4-*.log"], timelines=True)
    nodelog = normalize(timelines["nodelog"].sort_values(["LogFilePath", "Time"]))
    expected = normalize(
        pd.read_feather(HERE / "assets/nodelog.feather").sort_values(
            ["LogFilePath", "Time"]
        )
    )
    assert_frame_equal(nodelog[expected.columns], expected)


@pytest.mark.skip(reason="no rootlp log data to test against")
def test_rootlp_timelines():
    """RootLP timeline has no test data (TODO add an example log)"""
    _, timelines = glt.get_dataframe(["data/912-glass4-*.log"], timelines=True)
    rootlplog = timelines["rootlp"]


if __name__ == "__main__":

    from grblogtools import get_dataframe

    # Execute this to update the feather files from a target version somewhere.
    summary = get_dataframe(["data/*.log"])
    summary["Time"] = pd.to_datetime(summary["Time"])
    summary["Seed"] = summary["Seed"].astype(int)
    summary.to_feather(HERE / "assets/summary.feather")
    _, timelines = get_dataframe(["data/*.log"], timelines=True)
    timelines["nodelog"].to_feather(HERE / "assets/nodelog.feather")
