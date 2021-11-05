import grblogtools as glt

from pandas.api.types import is_categorical_dtype
from pandas.api.types import is_float_dtype
from pandas.api.types import is_integer_dtype


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
