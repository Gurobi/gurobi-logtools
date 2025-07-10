from .helpers import read_single


def test_cuts():
    row = read_single("1202-TimeLimit500-k16x240-0.log")
    cuts = {key: row[key] for key in row.keys() if key.startswith("Cuts: ")}
    assert len(cuts) == 11
