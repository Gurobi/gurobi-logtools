import glob
import tempfile

import pandas as pd
import pytest
from pandas.api.types import is_integer_dtype
from pandas.testing import assert_frame_equal, assert_series_equal

import grblogtools.api as glt


@pytest.fixture(scope="module")
def glass4_summary():
    """Summary data from API call."""
    return glt.parse("data/*.log").summary()


@pytest.fixture(scope="module")
def glass4_progress():
    """Progress data from API call."""
    return {
        "norel": glt.parse("data/*.log").progress("norel"),
        "rootlp": glt.parse("data/*.log").progress("rootlp"),
        "nodelog": glt.parse("data/*.log").progress("nodelog"),
    }


@pytest.fixture(scope="module")
def testlog_summary():
    return glt.parse("tests/assets/*.log").summary()


@pytest.fixture(scope="module")
def testlog_progress():
    return {
        "norel": glt.parse("tests/assets/*.log").progress("norel"),
        "rootlp": glt.parse("tests/assets/*.log").progress("rootlp"),
        "nodelog": glt.parse("tests/assets/*.log").progress("nodelog"),
    }


@pytest.fixture(scope="module")
def merged_log():
    with tempfile.NamedTemporaryFile("w") as fp:
        for path in sorted(glob.glob("data/912-glass4-*.log")):
            with open(path) as infile:
                fp.writelines(infile.readlines())
        fp.flush()
        yield fp.name


def test_merged_log(merged_log):
    summary = glt.parse(merged_log).summary()
    result = summary[["Seed", "Runtime", "LogFilePath", "LogNumber"]]
    expected = pd.DataFrame(
        [
            {"Seed": 0, "Runtime": 35.66, "LogFilePath": merged_log, "LogNumber": 1},
            {"Seed": 1, "Runtime": 42.79, "LogFilePath": merged_log, "LogNumber": 2},
            {"Seed": 2, "Runtime": 11.37, "LogFilePath": merged_log, "LogNumber": 3},
        ]
    )
    assert_frame_equal(result, expected)


def test_summary(testlog_summary):
    assert len(testlog_summary) == 7
    assert set(testlog_summary.columns).issuperset(
        {"Status", "ObjVal", "ReadTime", "RelaxObj"}
    )


def test_progress(testlog_progress):
    assert len(testlog_progress) == 3
    assert len(testlog_progress["norel"]) == 15
    assert set(testlog_progress["norel"].columns).issuperset(
        {"Time", "BestBd", "Incumbent"}
    )
    assert len(testlog_progress["rootlp"]) == 406
    assert set(testlog_progress["rootlp"].columns).issuperset(
        {"Iteration", "PInf", "DInf", "PObj", "DObj"}
    )
    assert len(testlog_progress["nodelog"]) == 133
    assert set(testlog_progress["nodelog"].columns).issuperset(
        {"Depth", "IntInf", "Incumbent", "BestBd", "ItPerNode"}
    )


def test_summary_glass4(glass4_summary):
    assert len(glass4_summary) == 63
    assert set(glass4_summary.columns).issuperset(
        {"Status", "ObjVal", "ReadTime", "RelaxObj", "Seed"}
    )


def test_progress_glass4(glass4_progress):
    assert len(glass4_progress) == 3
    assert len(glass4_progress["norel"]) == 0
    assert len(glass4_progress["rootlp"]) == 0

    assert set(glass4_progress["nodelog"].columns).issuperset(
        {"Depth", "IntInf", "Incumbent", "BestBd", "ItPerNode"}
    )


def test_logfile(glass4_summary):
    logfiles = glass4_summary["LogFilePath"]
    assert len(logfiles.unique()) == len(logfiles)
    assert logfiles.str.startswith("data/").all()
    assert logfiles.str.endswith(".log").all()
    assert_series_equal(
        glass4_summary["LogFile (Parameter)"].apply(lambda l: "data/" + l),
        logfiles,
        check_names=False,
    )
    # log names are stripped of the model name and seed
    log = glass4_summary["Log"]
    assert log.str.startswith("912").all()
    assert not log.str.contains("glass4").any()
    assert not log.str.endswith("-").any()
    assert len(log.unique()) == 21  # different seeds get same label


def test_modelfile(glass4_summary):
    modelfiles = glass4_summary["ModelFilePath"]
    assert len(modelfiles.unique()) == 1
    assert glass4_summary["ModelFile"].eq("glass4").all()
    assert glass4_summary["Model"].eq("glass4").all()


def test_parameters(glass4_summary):
    seeds = glass4_summary["Seed"]
    assert is_integer_dtype(seeds)
    assert seeds.notnull().all()
    assert set(seeds.unique()) == {0, 1, 2}
    assert "TimeLimit (Parameter)" in glass4_summary.columns
    parameters = glass4_summary[
        [f"{c} (Parameter)" for c in ["Heuristics", "MIPFocus", "Presolve"]]
    ]
    assert parameters.notnull().all().all()


def test_legacy_api(glass4_summary):
    glass4_summary = glt.get_dataframe(["data/*.log"])
    assert glass4_summary.shape[0] == 63
    assert set(glass4_summary.columns).issuperset({"Status", "ObjVal"})
