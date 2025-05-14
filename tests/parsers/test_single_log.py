from datetime import datetime

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


def test_multiknapsack():
    parser = SingleLogParser()
    with open("tests/assets/multiknapsack.log") as infile:
        parse_lines(parser, infile)
    # Test relevant bits are populated.
    assert parser.header_parser.get_summary()
    assert parser.presolve_parser.get_summary()
    assert parser.norel_parser.get_summary()
    assert parser.norel_parser.get_progress()
    assert parser.continuous_parser.get_summary()
    assert not parser.continuous_parser.get_progress()
    assert parser.pretree_solution_parser.get_summary()
    assert parser.pretree_solution_parser.get_progress()
    assert parser.nodelog_parser.get_summary()
    assert parser.nodelog_parser.get_progress()
    assert parser.termination_parser.get_summary()
    # Combined summary data.
    summary = parser.get_summary()
    assert summary["Version"] == "9.5.0"
    assert summary["IterCount"] == 2566
    assert summary["Runtime"] == 1.27
    assert summary["Status"] == "OPTIMAL"
    assert summary["ModelType"] == "MIP"

    pretreesols_progress = parser.pretree_solution_parser.get_progress()
    assert len(pretreesols_progress) == 2


def test_multiknapsack_iter():
    parser = SingleLogParser()

    parsed_lines = [
        {},
        {
            "Platform": "mac64[x86], gurobi_cl",
            "Time": datetime(2024, 7, 5, 19, 18, 47),
            "Version": "9.5.0",
        },
        {},
        {"LogFile": '"multiknapsack.log"'},
        {},
        {},
        {"Version": "9.5.0"},
        {},
        {},
        {"ModelFilePath": "multiknapsack.mps.bz2"},
        {"ReadingTime": 2.31},
        {"Columns": 1000, "ModelName": "", "Nonzeros": 1000000, "Rows": 1000},
        {},
        {},
        {"LogicalProcessors": 8, "PhysicalCores": 4, "Threads": 8},
        {},
        {"NumConstrs": 1000, "NumNZs": 1000000, "NumVars": 1000},
        {"Fingerprint": "0x1dcb478a"},
        {
            "PresolvedNumBinVars": 0,
            "PresolvedNumConVars": 0,
            "PresolvedNumIntVars": 1000,
        },
        {},
        {"MaxCoeff": 1.0, "MinCoeff": 8e-07},
        {"MaxObjCoeff": 1.0, "MinObjCoeff": 0.0003},
        {"MaxBound": 0.0, "MinBound": 0.0},
        {"MaxRHS": 10000.0, "MinRHS": 2.0},
        {"Incumbent": 2.650807},
        {},
        {"PresolveTime": 0.63},
        {
            "PresolvedNumConstrs": 249,
            "PresolvedNumNZs": 249000,
            "PresolvedNumVars": 1000,
        },
        {
            "PresolvedNumBinVars": 0,
            "PresolvedNumConVars": 0,
            "PresolvedNumIntVars": 1000,
        },
        {},
        {"Init": "norel"},
        {"Incumbent": 15.6561779},
        {"Incumbent": 20.2661725},
        {"Incumbent": 21.6309598},
        {"Incumbent": 23.7055101},
        {"Incumbent": 24.1081356},
        {"BestBd": 24.6734, "Incumbent": 24.1081356, "Time": 8},
        {"BestBd": 24.6734, "Incumbent": 24.1081356, "Time": 15},
        {"BestBd": 24.6734, "Incumbent": 24.1081356, "Time": 21},
        {"BestBd": 24.6734, "Incumbent": 24.1081356, "Time": 29},
        {},
        {"RelaxIterCount": 32, "RelaxObj": 24.67344, "RelaxTime": 0.02},
        {},
        {"Incumbent": 15.5735142},
        {},
        {},
        {"Init": "treesearch"},
        {},
        {
            "BestBd": 24.67344,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.584,
            "Incumbent": 15.57351,
            "IntInf": 5,
            "ItPerNode": None,
            "Obj": 24.67344,
            "RemainingNodes": 0,
            "Time": 0,
        },
        {
            "BestBd": 24.67344,
            "CurrentNode": 0,
            "Gap": 0.0345,
            "Incumbent": 23.8510977,
            "ItPerNode": None,
            "NewSolution": "H",
            "RemainingNodes": 0,
            "Time": 0,
        },
        {
            "BestBd": 24.67344,
            "CurrentNode": 0,
            "Gap": 0.023399999999999997,
            "Incumbent": 24.1081356,
            "ItPerNode": None,
            "NewSolution": "H",
            "RemainingNodes": 0,
            "Time": 0,
        },
        {
            "BestBd": 24.54405,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.0181,
            "Incumbent": 24.10814,
            "IntInf": 7,
            "ItPerNode": None,
            "Obj": 24.54405,
            "RemainingNodes": 0,
            "Time": 1,
        },
        {
            "BestBd": 24.54405,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.0181,
            "Incumbent": 24.10814,
            "IntInf": 5,
            "ItPerNode": None,
            "Obj": 24.54405,
            "RemainingNodes": 0,
            "Time": 1,
        },
        {
            "BestBd": 24.54405,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.0181,
            "Incumbent": 24.10814,
            "IntInf": 7,
            "ItPerNode": None,
            "Obj": 24.54405,
            "RemainingNodes": 0,
            "Time": 1,
        },
        {
            "BestBd": 24.49025,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.0159,
            "Incumbent": 24.10814,
            "IntInf": 6,
            "ItPerNode": None,
            "Obj": 24.49025,
            "RemainingNodes": 0,
            "Time": 1,
        },
        {
            "BestBd": 24.48961,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.0158,
            "Incumbent": 24.10814,
            "IntInf": 7,
            "ItPerNode": None,
            "Obj": 24.48961,
            "RemainingNodes": 0,
            "Time": 1,
        },
        {
            "BestBd": 24.45227,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.0143,
            "Incumbent": 24.10814,
            "IntInf": 8,
            "ItPerNode": None,
            "Obj": 24.45227,
            "RemainingNodes": 0,
            "Time": 1,
        },
        {
            "BestBd": 24.40551,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.0123,
            "Incumbent": 24.10814,
            "IntInf": 8,
            "ItPerNode": None,
            "Obj": 24.40551,
            "RemainingNodes": 0,
            "Time": 1,
        },
        {
            "BestBd": 24.40551,
            "CurrentNode": 0,
            "Depth": 0,
            "Gap": 0.0123,
            "Incumbent": 24.10814,
            "IntInf": 8,
            "ItPerNode": None,
            "Obj": 24.40551,
            "RemainingNodes": 2,
            "Time": 1,
        },
        {},
        {"Init": "cutreport"},
        {"Gomory": 8},
        {"Gomory": 8, "Lift-and-project": 1},
        {},
        {"IterCount": 2566, "NodeCount": 838, "Runtime": 1.27, "Work": 0.53},
        {"Cores": 8, "Threads": 8},
        {},
        {"Cores": 8, "SolCount": 5, "Threads": 8},
        {},
        {"Cores": 8, "SolCount": 5, "Status": "OPTIMAL", "Threads": 8},
        {"MIPGap": 0.0, "ObjBound": 24.10813557868, "ObjVal": 24.10813557868},
    ]

    with open("tests/assets/multiknapsack.log") as infile:
        lines = iter(infile)
        res = [parser.parse(line) for line in lines]
        assert res == parsed_lines
