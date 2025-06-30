import plotly.express as px
import pytest

import gurobi_logtools as glt


@pytest.fixture
def k16x240_results():
    return glt.parse("data/*k16x240*.log")


def test_plot_summary(k16x240_results):
    glt.plot(k16x240_results.summary(), type="box")


def test_plot_nodelog(k16x240_results):
    glt.plot(k16x240_results.progress("nodelog"), y="Gap", color="Log", type="line")


def test_register_custom_palette():
    palette = ("#DD2113", "#4E5059", "#00ff00")
    glt.register_custom_palette("test", palette)
    retrieved = glt.colors._get_palette("Custom", "test")
    assert list(palette) == list(retrieved)


def test_reset_custom_palette():
    palette = ("#DD2113", "#4E5059", "#00ff00")
    glt.register_custom_palette("test", palette)
    glt.reset_custom_palettes()
    retrieved = glt.colors._get_palette("Custom", "test")
    assert retrieved == px.colors.qualitative.Plotly
