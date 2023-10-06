import pandas as pd
from pandas.api.types import is_categorical_dtype, is_float_dtype, is_integer_dtype
from pandas.testing import assert_frame_equal

import gurobi_logtools as glt
from gurobi_logtools.helpers import (
    fill_default_parameters,
    fill_default_parameters_nosuffix,
)


def test_parameter_values():
    summary = glt.get_dataframe(["data/*.log"])
    mipfocus = summary["MIPFocus (Parameter)"]
    assert not mipfocus.isnull().any()
    assert is_integer_dtype(mipfocus)
    assert set(mipfocus.unique()) == {0, 1, 2, 3}


def test_pretty_parameters():
    summary = glt.get_dataframe(["data/*.log"], prettyparams=True)
    presolve = summary["Presolve (Parameter)"]
    assert is_categorical_dtype(presolve)
    assert set(presolve.unique()) == {
        "-1: Automatic",
        "1: Conservative",
        "2: Aggressive",
    }
    assert is_float_dtype(summary["Heuristics (Parameter)"])


def test_fill_default_parameters():
    """Test that '* (Parameter)' columns are default-filled using the
    appropriate Version."""
    summary = pd.DataFrame(
        [
            {"Version": "9.1.2", "CrossoverBasis (Parameter)": 1, "Status": "OPTIMAL"},
            {"Version": "9.1.2", "MIPFocus (Parameter)": 1, "Status": "TIME_LIMIT"},
            {"Version": "9.5.0", "Heuristics (Parameter)": 0, "Status": "OPTIMAL"},
        ]
    )
    filled = fill_default_parameters(summary)
    expected = pd.DataFrame(
        [
            {
                "Version": "9.1.2",
                "CrossoverBasis (Parameter)": 1,
                "MIPFocus (Parameter)": 0,
                "Heuristics (Parameter)": 0.05,
                "Status": "OPTIMAL",
            },
            {
                "Version": "9.1.2",
                "CrossoverBasis (Parameter)": 0,
                "MIPFocus (Parameter)": 1,
                "Heuristics (Parameter)": 0.05,
                "Status": "TIME_LIMIT",
            },
            {
                "Version": "9.5.0",
                "CrossoverBasis (Parameter)": -1,
                "MIPFocus (Parameter)": 0,
                "Heuristics (Parameter)": 0.0,
                "Status": "OPTIMAL",
            },
        ]
    )
    assert_frame_equal(filled.sort_index(axis=1), expected.sort_index(axis=1))


def test_fill_default_parameters_nosuffix():
    """The only columns in this input frame are the"""
    parameters = pd.DataFrame(
        [
            {"Version": "9.1.2", "CrossoverBasis": 1},
            {"Version": "9.1.2", "MIPFocus": 1},
            {"Version": "9.5.0", "Heuristics": 0},
        ]
    )
    filled = fill_default_parameters_nosuffix(parameters)
    expected = pd.DataFrame(
        [
            {
                "Version": "9.1.2",
                "CrossoverBasis": 1,
                "MIPFocus": 0,
                "Heuristics": 0.05,
            },
            {
                "Version": "9.1.2",
                "CrossoverBasis": 0,
                "MIPFocus": 1,
                "Heuristics": 0.05,
            },
            {"Version": "9.5.0", "CrossoverBasis": -1, "MIPFocus": 0, "Heuristics": 0},
        ]
    )
    assert_frame_equal(filled.sort_index(axis=1), expected.sort_index(axis=1))
