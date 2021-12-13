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
import grblogtools as glt

from pandas.testing import assert_frame_equal

HERE = pathlib.Path(__file__).parent


def test_summary():
    expected = (
        pd.read_feather(HERE / "assets/summary.feather")
        .sort_values("LogFilePath")
        .reset_index(drop=True)
    )
    summary = (
        glt.get_dataframe(["data/*.log"])
        .sort_values("LogFilePath")
        .reset_index(drop=True)
    )
    assert_frame_equal(summary[expected.columns], expected)


def test_nodelog_timelines():
    _, timelines = glt.get_dataframe(["data/912-glass4-*.log"], timelines=True)
    nodelog = (
        timelines["nodelog"].sort_values(["LogFilePath", "Time"]).reset_index(drop=True)
    )
    expected = (
        pd.read_feather(HERE / "assets/nodelog.feather")
        .sort_values(["LogFilePath", "Time"])
        .reset_index(drop=True)
    )
    assert_frame_equal(nodelog[expected.columns], expected)


@pytest.mark.skip(reason="no rootlp log data to test against")
def test_rootlp_timelines():
    """RootLP timeline has no test data (TODO add an example log)"""
    _, timelines = glt.get_dataframe(["data/912-glass4-*.log"], timelines=True)
    rootlplog = timelines["rootlp"]


if __name__ == "__main__":

    # Execute this to update the feather files from a target version somewhere.
    summary = glt.get_dataframe(["data/*.log"])
    summary.to_feather(HERE / "assets/summary.feather")
    _, timelines = glt.get_dataframe(["data/912-glass4-*.log"], timelines=True)
    timelines["nodelog"].to_feather(HERE / "assets/nodelog.feather")
