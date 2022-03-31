import pytest

import grblogtools as glt


@pytest.fixture
def glass4_results():
    return glt.parse("data/912*glass4*.log")


def test_plot_summary(glass4_results):
    glt.plot(glass4_results.summary(), type="box")


def test_plot_nodelog(glass4_results):
    glt.plot(glass4_results.progress("nodelog"), y="Gap", color="Log", type="line")
