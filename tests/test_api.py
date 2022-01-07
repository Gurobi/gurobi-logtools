import pytest
from pandas.api.types import is_integer_dtype
from pandas.testing import assert_series_equal

import grblogtools.api as glt


@pytest.fixture
def glass4_summary():
    """Summary data from API call."""
    return glt.parse("data/*.log").summary()


def test_summary_basic(glass4_summary):
    assert len(glass4_summary) == 63
    assert set(glass4_summary.columns).issuperset({"Status", "ObjVal", "ReadTime"})


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


def test_modelfile(glass4_summary):
    modelfiles = glass4_summary["ModelFilePath"]
    assert len(modelfiles.unique()) == 1
    assert glass4_summary["ModelFile"].eq("glass4").all()


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
