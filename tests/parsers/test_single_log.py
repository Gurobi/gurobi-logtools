from gurobi_logtools.parsers.single_log import SingleLogParser
from gurobi_logtools.parsers.util import parse_lines


def test_mip_norel_log():
    parser = SingleLogParser()
    with open("tests/assets/mip_norel.log") as infile:
        parse_lines(parser, infile)
    # Check that something is populated for all parsers.
    assert parser.header_parser.get_summary()
    assert parser.presolve_parser.get_summary()
    assert parser.norel_parser.get_summary()
    assert parser.norel_parser.get_progress()
    assert parser.continuous_parser.get_summary()
    assert parser.continuous_parser.get_progress()
    assert parser.nodelog_parser.get_summary()
    assert parser.nodelog_parser.get_progress()
    assert parser.termination_parser.get_summary()
    # Combined summary data.
    summary = parser.get_summary()
    assert summary["Version"] == "9.1.2"
    assert summary["Platform"] == "mac64, gurobi_cl"
    assert summary["NumVars"] == 322
    assert summary["PresolvedNumIntVars"] == 297
    assert summary["NoRelBestSol"] == 1.200013e09
    assert summary["NodeCount"] == 5135
    assert summary["Status"] == "OPTIMAL"
    assert summary["ObjVal"] == 1.2000126e09
    assert summary["Runtime"] == 93.70
    assert summary["ModelType"] == "MIP"

    norel_progress = parser.norel_parser.get_progress()
    assert len(norel_progress) == 15
    rootlp_progress = parser.continuous_parser.get_progress()
    assert len(rootlp_progress) == 2
    nodelog_progress = parser.nodelog_parser.get_progress()
    assert len(nodelog_progress) == 7


def test_lp_barrier():
    parser = SingleLogParser()
    with open("tests/assets/lp_barrier.log") as infile:
        parse_lines(parser, infile)
    # Test relevant bits are populated.
    assert parser.header_parser.get_summary()
    assert parser.presolve_parser.get_summary()
    assert parser.continuous_parser.get_summary()
    assert not parser.norel_parser.get_summary()
    assert not parser.nodelog_parser.get_summary()
    # Combined summary data.
    summary = parser.get_summary()
    assert summary["Version"] == "9.5.0"
    assert summary["ModelName"] == "savsched1.mps"
    assert summary["OrderingTime"] == 0.41
    assert summary["BarIterCount"] == 17
    assert summary["Runtime"] == 9.18
    assert summary["Status"] == "OPTIMAL"
    assert summary["ModelType"] == "LP"

    rootlp_progress = parser.continuous_parser.get_progress()
    assert len(rootlp_progress) == 19


def test_lp_simplex():
    parser = SingleLogParser()
    with open("tests/assets/lp_simplex.log") as infile:
        parse_lines(parser, infile)
    # Test relevant bits are populated.
    assert parser.header_parser.get_summary()
    assert parser.presolve_parser.get_summary()
    assert parser.continuous_parser.get_summary()
    assert not parser.norel_parser.get_summary()
    assert not parser.nodelog_parser.get_summary()
    assert parser.termination_parser.get_summary()
    # Combined summary data.
    summary = parser.get_summary()
    assert summary["Version"] == "9.5.0"
    assert summary["IterCount"] == 75321
    assert summary["Runtime"] == 300.00
    assert summary["Status"] == "TIME_LIMIT"
    assert summary["ModelType"] == "LP"

    rootlp_progress = parser.continuous_parser.get_progress()
    assert len(rootlp_progress) == 60
