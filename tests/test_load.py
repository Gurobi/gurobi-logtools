import grblogtools as glt


def test_get_dataframe():
    """Just check we read without errors."""
    summary = glt.get_dataframe(["data/*.log"])


def test_read_with_timelines():
    """Check timelines argument."""
    summary, timelines, rootlp = glt.get_dataframe(["data/*.log"], timelines=True)
