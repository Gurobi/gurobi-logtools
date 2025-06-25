import pytest

import gurobi_logtools as glt


@pytest.fixture
def k16x240_results():
    return glt.parse("data/*k16x240*.log")


def test_plot_summary(k16x240_results):
    glt.plot(k16x240_results.summary(), type="box")


def test_plot_nodelog(k16x240_results):
    glt.plot(k16x240_results.progress("nodelog"), y="Gap", color="Log", type="line")
