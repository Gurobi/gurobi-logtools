import grblogtools.api as glt


def test_api():
    summary = glt.parse("data/*.log").summary()
    assert summary.shape[0] == 64
    assert set(summary.columns).issuperset({"Status", "ObjVal"})


def test_legacy_api():
    summary = glt.get_dataframe(["data/*.log"])
    assert summary.shape[0] == 64
    assert set(summary.columns).issuperset({"Status", "ObjVal"})
