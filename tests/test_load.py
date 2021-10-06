import grblogtools as glt


def test_get_dataframe():
    """Just check we read without errors."""
    summary = glt.get_dataframe(["data/*.log"])


def test_read_with_timelines():
    """Check timelines argument."""
    summary, timelines = glt.get_dataframe(["data/*.log"], timelines=True)
    assert set(timelines.keys()) == {"norel", "rootlp", "nodelog"}


def test_norel_timeline():
    """Check norel logs before the root node. Note that this reports norel's
    clock, so read + presolve time would need to be added for 'real' time."""
    summary, timelines = glt.get_dataframe(
        ["data/912-NoRelHeurWork60-glass4-0.log"],
        timelines=True,
    )
    norel = timelines["norel"]
    assert norel.shape[0] == 15
    assert norel["Log"].unique()[0] == "912-NoRelHeurWork60"
    assert norel["Time"].min() == 5.0
    assert norel["Time"].max() == 93.0
    assert (norel["Incumbent"].max() - 1.450014e09) <= 1e05
    assert (norel["Incumbent"].min() - 1.2000e09) <= 1e05
    assert (norel["BestBd"].max() - 8.00002e08) <= 1e05
    assert (norel["BestBd"].min() - 8.00002e08) <= 1e05
    # Sometimes a bound isn't reported.
    assert norel["BestBd"].isnull().sum() == 1
