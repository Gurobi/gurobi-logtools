import gurobi_logtools as glt


def test_get_dataframe():
    """Just check we read without errors."""
    summary = glt.get_dataframe(["data/*.log"])


def test_read_with_timelines():
    """Check timelines argument."""
    summary, timelines = glt.get_dataframe(["data/*.log"], timelines=True)
    assert set(timelines.keys()) == {"norel", "rootlp", "nodelog", "pretreesols"}


def test_norel_timeline():
    """Check norel logs before the root node. Note that this reports norel's
    clock, so read + presolve time would need to be added for 'real' time."""
    _, timelines = glt.get_dataframe(
        ["tests/assets/mip_norel.log"],
        timelines=True,
    )
    norel = timelines["norel"]
    assert set(norel.columns) == {
        "Time",
        "BestBd",
        "Incumbent",
        "Log",
        "LogFilePath",
        "Model",
        "ModelFile",
        "Version",
        "LogNumber",
        "ModelFilePath",
        "Seed",
    }
    assert norel.shape[0] == 15
    assert len(norel["LogFilePath"].unique()) == 1
    assert norel["Time"].min() == 5.0
    assert norel["Time"].max() == 93.0
    assert (norel["Incumbent"].max() - 1.450014e09) <= 1e05
    assert (norel["Incumbent"].min() - 1.2000e09) <= 1e05
    assert (norel["BestBd"].max() - 8.00002e08) <= 1e05
    assert (norel["BestBd"].min() - 8.00002e08) <= 1e05
    # Sometimes a bound isn't reported.
    assert norel["BestBd"].isnull().sum() == 1


def test_newsolution_markers():
    _, timelines = glt.get_dataframe(
        ["data/1202-MIPFocus0-Presolve2-TimeLimit300-k16x240-3.log"], timelines=True
    )
    new_solutions = timelines["nodelog"]["NewSolution"]
    assert new_solutions.value_counts().to_dict() == {"H": 13, "*": 1}
