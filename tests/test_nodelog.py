from grblogtools.nodelog import NodeLogParser
from grblogtools.nodelog import NodeLogParser


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
Thread count was 8 (of 8 available processors)
"""


def test_nodelog_parser():
    """ Pass all test lines in sequence and test timeline. """
    parser = NodeLogParser()
    lines = nodelog_section_test_data.strip().split("\n")
    parser.parse_lines(lines)
    # 'Explored' line ends parsing so future lines are not passed at all.
    assert parser.ignored_lines == 0
    assert parser.timeline == [
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
    ]
