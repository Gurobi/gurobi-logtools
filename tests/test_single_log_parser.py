from grblogtools.helpers import parse_lines
from grblogtools.single_log_parser import SingleLogParser


def test_mip_norel_log():
    parser = SingleLogParser()
    with open("tests/assets/mip_norel.log") as infile:
        parse_lines(parser, infile)
    # Check that something is populated for all parsers.
    assert parser.header_parser.get_summary()
    assert parser.presolve_parser.get_summary()
    assert parser.norel_parser.get_summary()
    assert parser.norel_parser.timeline
    assert parser.continuous_parser.get_summary()
    assert parser.continuous_parser.get_progress()
    assert parser.nodelog_parser.get_summary()
    assert parser.nodelog_parser.timeline
    # Combined summary data.
    summary = parser.get_summary()
    assert summary["Version"] == "9.1.2"
    assert summary["NumVars"] == 322
    assert summary["PresolvedNumIntVars"] == 297
    assert summary["NoRelBestSol"] == 1.200013e09
    assert summary["NodeCount"] == 5135
    assert summary["Status"] == "OPTIMAL"
    assert summary["ObjVal"] == 1.2000126e09
    assert summary["Runtime"] == 93.70


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
    assert parser.termination_parser.get_summary()  # fail
    # Combined summary data.
    summary = parser.get_summary()
    assert summary["Version"] == "9.5.0"
    assert summary["Model"] == "savsched1"  # fail
    assert summary["OrderingTime"] == 0.41  # fail
    assert summary["BarIterCount"] == 17
    assert summary["Runtime"] == 4.83
    assert summary["Status"] == "OPTIMAL"  # fail


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
    assert parser.termination_parser.get_summary()  # fail
    # Combined summary data.
    summary = parser.get_summary()
    assert summary["Version"] == "9.5.0"
    assert summary["IterCount"] == 75321
    assert summary["Runtime"] == 300.00
    assert summary["Status"] == "TIME_LIMIT"  # fail
