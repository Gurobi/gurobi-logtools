from grblogtools.parsers.nodelog import NodeLogParser
from grblogtools.parsers.util import parse_block

nodelog_section_test_data = """
Variable types: 19 continuous, 297 integer (297 binary)
Found heuristic solution: objective 3.133356e+09

Root relaxation: objective 8.000024e+08, 72 iterations, 0.00 seconds

    Nodes    |    Current Node    |     Objective Bounds      |     Work
 Expl Unexpl |  Obj  Depth IntInf | Incumbent    BestBd   Gap | It/Node Time

     0     0 8.0000e+08    0   72          - 8.0000e+08  74.5%     -    0s
     0     0 8.0000e+08    0   72 3.1334e+09 8.0000e+08  74.5%     -    0s
H    0     0                    2.200019e+09 8.0000e+08  63.6%     -    0s
 29986 17212 1.5267e+09   68  108 1.6500e+09 8.8832e+08  46.2%   4.4   15s
 40414 18935 infeasible  300      1.6000e+09 9.0001e+08  43.0%   5.7   25s
*187499 14704             320    1.350013e+09 1.2000e+09  11.1%   7.3   35s

Explored 188145 nodes (1383139 simplex iterations) in 35.66 seconds
Best objective 1.200012600000e+09, best bound 1.200003400000e+09, gap 0.0008%
"""


nodelog_section_test_data_withcuts = """
    Nodes    |    Current Node    |     Objective Bounds      |     Work
 Expl Unexpl |  Obj  Depth IntInf | Incumbent    BestBd   Gap | It/Node Time

     0     0 8.0000e+08    0   72          - 8.0000e+08  74.5%     -    0s

Cutting planes:
  Gomory: 13
  Implied bound: 5
  MIR: 20
  Relax-and-lift: 8

Explored 188 nodes (1389 simplex iterations) in 5.2 seconds
Best objective 5.0000e+08, best bound 5.0000e+08, gap 0.0008%
"""


nodelog_section_test_data_statsonly = """
Cutting planes:
  Gomory: 13
  Implied bound: 5
  MIR: 20
  Relax-and-lift: 8

Explored 188 nodes (1389 simplex iterations) in 5.2 seconds
Best objective 5.0000e+08, best bound 5.0000e+08, gap 0.0008%
"""


def test_nodelog_parser_statsonly():
    parser = NodeLogParser()
    parse_block(parser, nodelog_section_test_data_statsonly)
    assert parser.get_summary() == {
        "Cuts: Gomory": 13,
        "Cuts: Implied bound": 5,
        "Cuts: MIR": 20,
        "Cuts: Relax-and-lift": 8,
        "NodeCount": 188,
        "IterCount": 1389,
        "Runtime": 5.2,
        "MIPGap": 8e-06,
        "ObjBound": 5e8,
        "ObjVal": 5e8,
    }
    assert parser.get_progress() == [
        {
            "Incumbent": 5e8,
            "BestBd": 5e8,
            "Gap": 8e-06,
            "CurrentNode": 188,
            "Time": 5.2,
        }
    ]


def test_nodelog_parser_withcuts():
    parser = NodeLogParser()
    parse_block(parser, nodelog_section_test_data_withcuts)
    assert parser.get_summary() == {
        "Cuts: Gomory": 13,
        "Cuts: Implied bound": 5,
        "Cuts: MIR": 20,
        "Cuts: Relax-and-lift": 8,
        "NodeCount": 188,
        "IterCount": 1389,
        "Runtime": 5.2,
        "MIPGap": 8e-06,
        "ObjBound": 5e8,
        "ObjVal": 5e8,
    }
    assert len(parser.get_progress()) == 2


def test_nodelog_parser():
    """Pass all test lines in sequence and test timeline."""
    parser = NodeLogParser()
    parse_block(parser, nodelog_section_test_data)
    assert parser.get_summary() == {
        "NodeCount": 188145,
        "IterCount": 1383139,
        "Runtime": 35.66,
        "MIPGap": 8e-06,
        "ObjBound": 1200003400.0,
        "ObjVal": 1200012600.0,
    }
    assert parser.get_progress() == [
        {
            "CurrentNode": 0,
            "RemainingNodes": 0,
            "Obj": 8e8,
            "Depth": 0,
            "IntInf": 72,
            "Incumbent": None,
            "BestBd": 8e8,
            "Gap": 0.745,
            "ItPerNode": None,
            "Time": 0.0,
        },
        {
            "CurrentNode": 0,
            "RemainingNodes": 0,
            "Obj": 8e8,
            "Depth": 0,
            "IntInf": 72,
            "Incumbent": 3.1334e09,
            "BestBd": 8e8,
            "Gap": 0.745,
            "ItPerNode": None,
            "Time": 0.0,
        },
        {
            "NewSolution": "H",
            "CurrentNode": 0,
            "RemainingNodes": 0,
            "Incumbent": 2.200019e9,
            "BestBd": 8e8,
            "Gap": 0.636,
            "ItPerNode": None,
            "Time": 0.0,
        },
        {
            "CurrentNode": 29986,
            "RemainingNodes": 17212,
            "Obj": 1.5267e9,
            "Depth": 68,
            "IntInf": 108,
            "Incumbent": 1.6500e9,
            "BestBd": 8.8832e08,
            "Gap": 0.462,
            "ItPerNode": 4.4,
            "Time": 15.0,
        },
        {
            "CurrentNode": 40414,
            "RemainingNodes": 18935,
            "Pruned": "infeasible",
            "Depth": 300,
            "Incumbent": 1.600e9,
            "BestBd": 9.0001e08,
            "Gap": 0.43,
            "ItPerNode": 5.7,
            "Time": 25.0,
        },
        {
            "NewSolution": "*",
            "CurrentNode": 187499,
            "RemainingNodes": 14704,
            "Depth": 320,
            "Incumbent": 1.350013e9,
            "BestBd": 1.2e9,
            "Gap": 0.111,
            "ItPerNode": 7.3,
            "Time": 35.0,
        },
        {
            "CurrentNode": 188145,
            "Incumbent": 1200012600.0,
            "BestBd": 1200003400.0,
            "Gap": 8e-06,
            "Time": 35.66,
        },
    ]
