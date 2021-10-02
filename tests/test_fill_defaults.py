from pandas.api.types import is_integer_dtype

import grblogtools as glt


def test_parameter_values():
    summary = glt.get_dataframe(["data/*.log"])
    mipfocus = summary["MIPFocus (Parameter)"]
    assert not mipfocus.isnull().any()
    assert is_integer_dtype(mipfocus)
    assert set(mipfocus.unique()) == {0, 1, 2, 3}
