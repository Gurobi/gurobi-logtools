import numpy as np
import pandas as pd
import pytest

import gurobi_logtools as glt


@pytest.fixture(scope="module")
def _1201_mobj1_multiobjsummary():
    return glt.parse("./tests/assets/multiobjective/1201-mobj1.log").multiobj_summary()


@pytest.fixture(scope="module")
def _1203_mobj2_multiobjsummary():
    return glt.parse("./tests/assets/multiobjective/1203-mobj2.log").multiobj_summary()


def _get_summary_values(column):
    logpaths = [
        "tests/assets/multiobjective/1201-mobj1.log",
        "tests/assets/multiobjective/1203-mobj2.log",
    ]

    summary = glt.parse(logpaths, warnings_action="ignore").summary()

    return summary.set_index("LogFilePath")[column][logpaths].values


def test_numbobjpasses():
    np.testing.assert_array_equal(_get_summary_values("NumObjPasses"), [3, 2])


def test_numbobj():
    np.testing.assert_array_equal(_get_summary_values("NumObj"), [4, 2])


def test_runtime():
    np.testing.assert_array_equal(_get_summary_values("Runtime"), [2.000e-02, 3.566e01])


def test_work():
    np.testing.assert_array_equal(_get_summary_values("Work"), [0, 59.56])


def test_solcount():
    np.testing.assert_array_equal(_get_summary_values("SolCount"), [3, 8])


def test_presolvetime():
    np.testing.assert_array_equal(_get_summary_values("PresolveTime"), [0, 0.37])


def test_presolvednumconstrs():
    np.testing.assert_array_equal(
        _get_summary_values("PresolvedNumConstrs"), [1, 29551]
    )


def test_presolvednumvars():
    np.testing.assert_array_equal(_get_summary_values("PresolvedNumVars"), [20, 55420])


def test_presolvednumnzs():
    np.testing.assert_array_equal(_get_summary_values("PresolvedNumNZs"), [20, 221888])


def test_1201_mobj1_multiobjsummary_row1(_1201_mobj1_multiobjsummary):
    values = _1201_mobj1_multiobjsummary.iloc[0]
    expected = pd.Series(
        {
            "ObjNPass": 1,
            "ChangedParams": {},
            "PreTreeSolutions": 1,
            "NodeCount": 0,
            "IterCount": 0,
            "CumulativeRuntime": 0.01,
            "Work": 0.0,
            "ObjVal": 10.0,
            "ObjBound": 10.0,
            "MIPGap": 0.0,
            "Threads": 1,
            "Cores": 12,
            "SolCount": 1,
            "Status": "OPTIMAL",
            "LogFilePath": "./tests/assets/multiobjective/1201-mobj1.log",
            "LogNumber": 1,
            "MIPStartObjVal": np.nan,
            "PresolveTime": np.nan,
            "PresolvedNumConstrs": np.nan,
            "PresolvedNumVars": np.nan,
            "PresolvedNumNZs": np.nan,
        }
    )
    pd.testing.assert_series_equal(
        values.sort_index(), expected.sort_index(), check_names=False
    )


def test_1201_mobj1_multiobjsummary_row2(_1201_mobj1_multiobjsummary):
    values = _1201_mobj1_multiobjsummary.iloc[1]
    expected = pd.Series(
        {
            "ObjNPass": 2,
            "ChangedParams": {},
            "PreTreeSolutions": 0,
            "NodeCount": 0,
            "IterCount": 0,
            "CumulativeRuntime": 0.02,
            "Work": 0.0,
            "ObjVal": 10.5,
            "ObjBound": 10.5,
            "MIPGap": 0.0,
            "Threads": 1,
            "Cores": 12,
            "SolCount": 2,
            "Status": "OPTIMAL",
            "LogFilePath": "./tests/assets/multiobjective/1201-mobj1.log",
            "LogNumber": 1,
            "MIPStartObjVal": 6.25,
            "PresolveTime": 0.0,
            "PresolvedNumConstrs": 0.0,
            "PresolvedNumVars": 0.0,
            "PresolvedNumNZs": 0.0,
        }
    )
    pd.testing.assert_series_equal(
        values.sort_index(), expected.sort_index(), check_names=False
    )


def test_1201_mobj1_multiobjsummary_row3(_1201_mobj1_multiobjsummary):
    values = _1201_mobj1_multiobjsummary.iloc[2]
    expected = pd.Series(
        {
            "ObjNPass": 3,
            "ChangedParams": {},
            "PreTreeSolutions": 0,
            "NodeCount": 0,
            "IterCount": 0,
            "CumulativeRuntime": 0.02,
            "Work": 0.0,
            "ObjVal": 7.0,
            "ObjBound": 7.0,
            "MIPGap": 0.0,
            "Threads": 1,
            "Cores": 12,
            "SolCount": 2,
            "Status": "OPTIMAL",
            "LogFilePath": "./tests/assets/multiobjective/1201-mobj1.log",
            "LogNumber": 1,
            "MIPStartObjVal": 6.0,
            "PresolveTime": 0.0,
            "PresolvedNumConstrs": 0.0,
            "PresolvedNumVars": 0.0,
            "PresolvedNumNZs": 0.0,
        }
    )
    pd.testing.assert_series_equal(
        values.sort_index(), expected.sort_index(), check_names=False
    )


def test_1203_mobj2_multiobjsummary_row1(_1203_mobj2_multiobjsummary):
    values = _1203_mobj2_multiobjsummary.iloc[0]
    expected = pd.Series(
        {
            "ObjNPass": 1,
            "ChangedParams": {},
            "PresolveTime": 1.1,
            "PresolvedNumConstrs": 323,
            "PresolvedNumVars": 607,
            "PresolvedNumNZs": 2440,
            "PresolvedNumConVars": 300,
            "PresolvedNumIntVars": 307,
            "PresolvedNumBinVars": 301,
            "RelaxObj": 0.0,
            "RelaxIterCount": 11,
            "RelaxTime": 0.0,
            "PreTreeSolutions": 0,
            "NodeCount": 1,
            "IterCount": 12,
            "CumulativeRuntime": 1.5,
            "Work": 3.3,
            "ObjVal": 0.0,
            "ObjBound": 0.0,
            "MIPGap": 0.0,
            "Threads": 16,
            "Cores": 16,
            "SolCount": 1,
            "Status": "OPTIMAL",
            "LogFilePath": "./tests/assets/multiobjective/1203-mobj2.log",
            "LogNumber": 1,
            "MIPStartObjVal": np.nan,
            "Cuts: Gomory": np.nan,
            "Cuts: Cover": np.nan,
            "Cuts: Implied bound": np.nan,
            "Cuts: MIR": np.nan,
            "Cuts: StrongCG": np.nan,
            "Cuts: Flow cover": np.nan,
            "Cuts: GUB cover": np.nan,
            "Cuts: Inf proof": np.nan,
            "Cuts: Network": np.nan,
            "Cuts: RLT": np.nan,
            "Cuts: Relax-and-lift": np.nan,
        }
    )
    pd.testing.assert_series_equal(
        values.sort_index(), expected.sort_index(), check_names=False
    )


def test_1203_mobj2_multiobjsummary_row2(_1203_mobj2_multiobjsummary):
    values = _1203_mobj2_multiobjsummary.iloc[1]
    expected = pd.Series(
        {
            "ObjNPass": 2,
            "ChangedParams": {},
            "PresolveTime": 0.76,
            "PresolvedNumConstrs": 27617,
            "PresolvedNumVars": 51852,
            "PresolvedNumNZs": 214277,
            "PresolvedNumConVars": 25738,
            "PresolvedNumIntVars": 26114,
            "PresolvedNumBinVars": 25793,
            "RelaxObj": -9769.057,
            "RelaxIterCount": 1340,
            "RelaxTime": 0.1,
            "PreTreeSolutions": 0,
            "NodeCount": 4829,
            "IterCount": 236448,
            "CumulativeRuntime": 35.65,
            "Work": 59.56,
            "ObjVal": 0.01015799677704,
            "ObjBound": 0.01015799677704,
            "MIPGap": 0.0,
            "Threads": 16,
            "Cores": 16,
            "SolCount": 8,
            "Status": "OPTIMAL",
            "LogFilePath": "./tests/assets/multiobjective/1203-mobj2.log",
            "LogNumber": 1,
            "MIPStartObjVal": 795.86,
            "Cuts: Gomory": 2.0,
            "Cuts: Cover": 34.0,
            "Cuts: Implied bound": 12.0,
            "Cuts: MIR": 57.0,
            "Cuts: StrongCG": 34.0,
            "Cuts: Flow cover": 41.0,
            "Cuts: GUB cover": 7.0,
            "Cuts: Inf proof": 1.0,
            "Cuts: Network": 1.0,
            "Cuts: RLT": 11.0,
            "Cuts: Relax-and-lift": 8.0,
        }
    )
    pd.testing.assert_series_equal(
        values.sort_index(), expected.sort_index(), check_names=False
    )
