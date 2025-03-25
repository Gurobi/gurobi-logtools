import glob
import os
import tempfile
from pathlib import Path

import gurobi_logtools as glt
import pandas as pd
import pytest
from pandas.api.types import is_integer_dtype
from pandas.testing import assert_frame_equal, assert_series_equal


@pytest.fixture(scope="module")
def glass4_summary():
    """Summary data from API call."""
    return glt.parse("data/*glass4*.log").summary()


@pytest.fixture(scope="module")
def glass4_progress():
    """Progress data from API call."""
    return {
        "norel": glt.parse("data/*.log").progress("norel"),
        "rootlp": glt.parse("data/*.log").progress("rootlp"),
        "nodelog": glt.parse("data/*.log").progress("nodelog"),
        "pretreesols": glt.parse("data/*.log").progress("pretreesols"),
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
        "pretreesols": glt.parse("tests/assets/*.log").progress("pretreesols"),
    }


@pytest.fixture(scope="module")
def merged_log():
    with tempfile.NamedTemporaryFile("w", delete=False) as fp:
        for path in sorted(glob.glob("data/912-glass4-*.log")):
            with open(path) as infile:
                fp.writelines(infile.readlines())
        fp.flush()
        yield fp.name
    Path(fp.name).unlink()


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
    assert len(testlog_summary) == 8
    assert set(testlog_summary.columns).issuperset(
        {"Status", "ObjVal", "ReadingTime", "RelaxObj"}
    )


def test_progress(testlog_progress):
    assert len(testlog_progress) == 4
    assert len(testlog_progress["norel"]) == 19
    assert set(testlog_progress["norel"].columns).issuperset(
        {"Time", "BestBd", "Incumbent"}
    )
    assert len(testlog_progress["rootlp"]) == 409
    assert set(testlog_progress["rootlp"].columns).issuperset(
        {"Iteration", "PInf", "DInf", "PObj", "DObj"}
    )
    assert len(testlog_progress["nodelog"]) == 145
    assert set(testlog_progress["nodelog"].columns).issuperset(
        {"Depth", "IntInf", "Incumbent", "BestBd", "ItPerNode", "ModelFile", "Version"}
    )
    assert len(testlog_progress["pretreesols"]) == 4
    assert set(testlog_progress["pretreesols"].columns).issuperset(
        {"Incumbent", "ModelFile", "Version"}
    )


def test_summary_glass4(glass4_summary):
    assert len(glass4_summary) == 63
    assert set(glass4_summary.columns).issuperset(
        {"Status", "ObjVal", "ReadingTime", "RelaxObj", "Seed"}
    )


def test_progress_glass4(glass4_progress):
    assert len(glass4_progress) == 4
    assert len(glass4_progress["norel"]) == 0
    assert len(glass4_progress["rootlp"]) == 0

    assert set(glass4_progress["nodelog"].columns).issuperset(
        {"Depth", "IntInf", "Incumbent", "BestBd", "ItPerNode"}
    )
    assert len(glass4_progress["pretreesols"]) == 51
    assert set(glass4_progress["pretreesols"].columns).issuperset(
        {"Incumbent", "ModelFile", "Version"}
    )


def test_logfile(glass4_summary):
    logfiles = glass4_summary["LogFilePath"]
    assert len(logfiles.unique()) == len(logfiles)
    assert logfiles.str.startswith("data" + os.sep).all()
    assert logfiles.str.endswith(".log").all()
    assert_series_equal(
        glass4_summary["LogFile (Parameter)"].apply(lambda l: Path("data") / l),
        logfiles.apply(Path),
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


def test_legacy_api():
    glass4_summary = glt.get_dataframe(["data/*.log"])
    assert glass4_summary.shape[0] == 63
    assert set(glass4_summary.columns).issuperset({"Status", "ObjVal"})


def test_legacy_api_twopattern():
    """Check multiple file patterns can be passed and duplicate files are
    filtered out."""
    glass4_summary = glt.get_dataframe(
        [
            "data/912-glass4-*.log",
            "data/912-Cuts0-glass4-*.log",
            "data/912-Cuts0-glass4-*.log",
        ]
    )
    assert glass4_summary.shape[0] == 6
    assert set(glass4_summary.columns).issuperset({"Status", "ObjVal"})


def test_listpattern():
    result = glt.parse(
        [
            "data/912-glass4-*.log",
            "data/912-Cuts0-glass4-*.log",
            "data/912-Cuts0-glass4-*.log",
        ]
    )
    glass4_summary = result.summary()
    assert glass4_summary.shape[0] == 6
    assert set(glass4_summary.columns).issuperset({"Status", "ObjVal"})


def test_gurobipy_logs():
    """API logs differ in some cases: sometimes no model file is read, and
    parameter settings may appear before the header. At the moment this test
    just asserts no errors."""
    glt.parse("tests/assets/gurobipy/empty.log").summary()
    glt.parse("tests/assets/gurobipy/read.log").summary()
    glt.parse("tests/assets/gurobipy/*.log").summary()


def test_work():
    """Check if work is correctly parsed for different log files."""
    result = glt.parse("tests/assets/*.log")
    summary = result.summary()

    # Check if work column present
    assert set(summary.columns).issuperset({"Work"})

    # Check if Runtime and Work found
    assert summary["Work"].count() == 7


def test_changed_params():
    result = glt.parse("tests/assets/*.log")
    summary = result.summary()
    assert set(summary.columns).issuperset({"ChangedParams"})
    assert summary["ChangedParams"].apply(lambda d: isinstance(d, dict)).all()
    assert summary["ChangedParams"].count() == 8


def test_create_label():
    # Test expected workflow for creating custom labels

    def label(row):
        params = row["ChangedParams"]
        if params:
            paramstr = "-".join(
                f"{k}={v}" for k, v in sorted(params.items()) if k != "TimeLimit"
            )
        else:
            paramstr = "Default"
        version = row["Version"].replace(".", "")
        return f"{version}-{paramstr}"

    summary = (
        glt.parse("tests/assets/*.log")
        .summary()
        .assign(Label=lambda df: df.apply(label, axis="columns"))
    )
    assert set(summary["Label"]) == {
        "950-CrossoverBasis=1-Method=2",
        "950-Default",
        "950-Method=0",
        "950-Method=2",
        "950-Method=3",
        "950-NonConvex=2",
        "912-NoRelHeurWork=60",
    }


def test_rewrite_filenames():
    # Test workflow for rewriting file names

    with tempfile.TemporaryDirectory() as tempdirname:
        results = glt.parse(
            "tests/assets/combined/*.log", write_to_dir=Path(tempdirname) / "logs"
        )
        split_log_files = sorted(Path(tempdirname).joinpath("logs").glob("*.log"))
        expected_names = [
            "912-MIPFocus1-Presolve1-TimeLimit600-glass4-0",
            "912-MIPFocus1-Presolve1-TimeLimit600-glass4-1",
            "912-MIPFocus1-Presolve1-TimeLimit600-glass4-2",
            "912-MIPFocus2-Presolve1-TimeLimit600-glass4-0",
            "912-MIPFocus2-Presolve1-TimeLimit600-glass4-1",
            "912-MIPFocus2-Presolve1-TimeLimit600-glass4-2",
            "912-Presolve1-glass4-0",
            "912-Presolve1-glass4-1",
            "912-Presolve1-glass4-2",
            "912-glass4-0",
            "912-glass4-1",
            "912-glass4-2",
        ]
        assert len(split_log_files) == len(expected_names)

        for log_file, expected_name in zip(split_log_files, expected_names):
            lines = log_file.read_text().split("\n")
            start_lines = [
                line
                for line in lines
                if line.startswith("Gurobi Optimizer version 9.1.2")
            ]
            end_lines = [line for line in lines if line.startswith("Best objective")]

            # Log file has expected name and contains exactly one complete run
            assert log_file.stem == expected_name
            assert len(start_lines) == 1
            assert len(end_lines) == 1


def test_no_logfile_error():
    with pytest.raises(FileNotFoundError):
        glt.parse("/file/with/a/tyop")
