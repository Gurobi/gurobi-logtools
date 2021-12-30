from grblogtools.helpers import parse_block
from grblogtools.single_log_parser import SingleLogParser

full_log_data = """
Gurobi 9.1.2 (linux64, gurobi_cl) logging started Fri Jul 30 13:53:48 2021
Read MPS format model from file /Library/gurobi950/macos_universal2/examples/data/glass4.mps
Optimize a model with 396 rows, 322 columns and 1815 nonzeros
Model fingerprint: 0x18b19fdf
Variable types: 20 continuous, 302 integer (0 binary)
Presolve removed 6 rows and 6 columns
Presolve time: 0.01s
Presolved: 390 rows, 316 columns, 1803 nonzeros
Variable types: 19 continuous, 297 integer (297 binary)
Found heuristic solution: objective 3.133356e+09

Starting NoRel heuristic
Elapsed time for NoRel heuristic: 5s
Found heuristic solution: objective 3.033354e+09
Found heuristic solution: objective 1.450014e+09
Elapsed time for NoRel heuristic: 10s (best bound 8.00002e+08)

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

Some other stuff...
"""


def test_single_log_parser():
    parser = SingleLogParser()
    parse_block(parser, full_log_data)
    # Test just that something is populated for all parsers.
    assert parser.header_parser.get_log()
    assert parser.presolve_parser.get_log()
    assert parser.norel_parser.summary
    assert parser.norel_parser.timeline
    assert parser.norel_parser.ignored_lines == 1
    assert parser.nodelog_parser.summary
    assert parser.nodelog_parser.timeline
    assert parser.nodelog_parser.ignored_lines == 0
    # Combined summary data
    summary = parser.get_summary()
    assert summary["Version"] == "9.1.2"
    assert summary["NumVars"] == 322
    assert summary["PresolvedNumIntVars"] == 297
    assert summary["NoRelBestSol"] == 1.450014e09
    assert summary["NodeCount"] == 188145
