import pytest
from gurobi_logtools.parsers.multiobj import MultiObjParser
from gurobi_logtools.parsers.util import parse_lines


@pytest.fixture(scope="module")
def test_data_parser():
    test_data = """
---------------------------------------------------------------------------
Multi-objectives: starting optimization with 4 objectives (3 combined)...
---------------------------------------------------------------------------

Multi-objectives: applying initial presolve...
---------------------------------------------------------------------------

Presolve time: 0.02s
Presolved: 8151 rows, 14131 columns, 26582 nonzeros

Multi-objectives: optimize objective 1 (OBJ0) ...
---------------------------------------------------------------------------

Found heuristic solution: objective 152294.00000
Presolve removed 4002 rows and 6237 columns
Presolve time: 0.04s
Presolved: 4149 rows, 7894 columns, 16006 nonzeros
Variable types: 962 continuous, 6932 integer (6439 binary)
Found heuristic solution: objective 151751.00000
Starting NoRel heuristic
Found heuristic solution: objective 98039.000000
Elapsed time for NoRel heuristic: 1s (best bound 16002.5)
Found heuristic solution: objective 17957.000000
Elapsed time for NoRel heuristic: 2s (best bound 16173.9)
Found heuristic solution: objective 16831.999719
NoRel heuristic complete

Root relaxation: objective 1.617393e+04, 5304 iterations, 0.04 seconds (0.08 work units)

    Nodes    |    Current Node    |     Objective Bounds      |     Work
 Expl Unexpl |  Obj  Depth IntInf | Incumbent    BestBd   Gap | It/Node Time

     0     0 16173.9297    0   11 16831.9997 16173.9297  3.91%     -    2s
     0     0 16819.3906    0    8 16831.9997 16819.3906  0.07%     -    2s
     0     0     cutoff    0      16831.9997 16831.9997  0.00%     -    2s

Cutting planes:
  Gomory: 16
  Lift-and-project: 1

Explored 1 nodes (10778 simplex iterations) in 2.54 seconds (1.52 work units)
Thread count was 16 (of 16 available processors)

Solution count 5: 16832 17957 98039 ... 152294

Optimal solution found (tolerance 1.00e-04)
Best objective 1.683199971851e+04, best bound 1.683199971851e+04, gap 0.0000%
---------------------------------------------------------------------------

Multi-objectives: optimize objective 2 (OBJ1) ...
---------------------------------------------------------------------------


Loaded user MIP start with objective 5.1739e+08

Presolve removed 18 rows and 2253 columns
Presolve time: 0.04s
Presolved: 8134 rows, 11878 columns, 27958 nonzeros
Variable types: 3984 continuous, 7894 integer (7401 binary)
Found heuristic solution: objective 1.080214e+07
Starting NoRel heuristic
Found heuristic solution: objective 1.035354e+07
Elapsed time for NoRel heuristic: 1s (best bound 3012119.8)
Found heuristic solution: objective 6919720.0000
NoRel heuristic complete

Root relaxation: objective 5.011792e+06, 13353 iterations, 0.30 seconds (0.82 work units)

    Nodes    |    Current Node    |     Objective Bounds      |     Work
 Expl Unexpl |  Obj  Depth IntInf | Incumbent    BestBd   Gap | It/Node Time

     0     0 5011792.43    0   90 6919720.00 5011792.43  27.6%     -    4s
H    0     0                    6919719.9613 5386903.32  22.2%     -    5s
H   49    41                    6736609.0000 5519431.92  18.1%   129    6s
H 1703   611                    5989536.0000 5685947.39  5.07%  53.8    9s

Cutting planes:
  Gomory: 12
  MIR: 47

Explored 1845 nodes (112268 simplex iterations) in 10.00 seconds (15.70 work units)
Thread count was 16 (of 16 available processors)

Solution count 6: 5.98954e+06 6.73661e+06 6.91972e+06 ... 5.1739e+08

Time limit reached
Best objective 5.989536000000e+06, best bound 5.691475302964e+06, gap 4.9764%

---------------------------------------------------------------------------
Multi-objectives: stopped in 10.01 seconds (15.70 work units), solution count 10
Time Limit reached
"""

    parser = MultiObjParser()
    parse_lines(parser, test_data.split("\n"))
    return parser


def test_pretree_progress(test_data_parser):
    expected = [
        {"Incumbent": 152294.0, "ObjCnt": 1},
        {"Incumbent": 151751.0, "ObjCnt": 1},
        {"Incumbent": 10802140.0, "ObjCnt": 2},
    ]
    assert test_data_parser.get_objn_progress("pretreesols") == expected


def test_norel_progress(test_data_parser):
    expected = [
        {"Time": 1, "BestBd": 16002.5, "Incumbent": 98039.0, "ObjCnt": 1},
        {"Time": 2, "BestBd": 16173.9, "Incumbent": 17957.0, "ObjCnt": 1},
        {"Time": 1, "BestBd": 3012119.8, "Incumbent": 10353540.0, "ObjCnt": 2},
    ]
    assert test_data_parser.get_objn_progress("norel") == expected


def test_nodelog_progress(test_data_parser):
    expected = [
        {
            "CurrentNode": 0,
            "RemainingNodes": 0,
            "Obj": 16173.9297,
            "Depth": 0,
            "IntInf": 11,
            "Incumbent": 16831.9997,
            "BestBd": 16173.9297,
            "Gap": 0.0391,
            "ItPerNode": None,
            "Time": 2,
            "ObjCnt": 1,
        },
        {
            "CurrentNode": 0,
            "RemainingNodes": 0,
            "Obj": 16819.3906,
            "Depth": 0,
            "IntInf": 8,
            "Incumbent": 16831.9997,
            "BestBd": 16819.3906,
            "Gap": 0.0007000000000000001,
            "ItPerNode": None,
            "Time": 2,
            "ObjCnt": 1,
        },
        {
            "CurrentNode": 0,
            "RemainingNodes": 0,
            "Pruned": "cutoff",
            "Depth": 0,
            "Incumbent": 16831.9997,
            "BestBd": 16831.9997,
            "Gap": 0.0,
            "ItPerNode": None,
            "Time": 2,
            "ObjCnt": 1,
        },
        {
            "Incumbent": 16831.99971851,
            "BestBd": 16831.99971851,
            "Gap": 0.0,
            "CurrentNode": 1,
            "Time": 2.54,
            "ObjCnt": 1,
        },
        {
            "CurrentNode": 0,
            "RemainingNodes": 0,
            "Obj": 5011792.43,
            "Depth": 0,
            "IntInf": 90,
            "Incumbent": 6919720.0,
            "BestBd": 5011792.43,
            "Gap": 0.276,
            "ItPerNode": None,
            "Time": 4,
            "ObjCnt": 2,
        },
        {
            "NewSolution": "H",
            "CurrentNode": 0,
            "RemainingNodes": 0,
            "Incumbent": 6919719.9613,
            "BestBd": 5386903.32,
            "Gap": 0.222,
            "ItPerNode": None,
            "Time": 5,
            "ObjCnt": 2,
        },
        {
            "NewSolution": "H",
            "CurrentNode": 49,
            "RemainingNodes": 41,
            "Incumbent": 6736609.0,
            "BestBd": 5519431.92,
            "Gap": 0.18100000000000002,
            "ItPerNode": 129,
            "Time": 6,
            "ObjCnt": 2,
        },
        {
            "NewSolution": "H",
            "CurrentNode": 1703,
            "RemainingNodes": 611,
            "Incumbent": 5989536.0,
            "BestBd": 5685947.39,
            "Gap": 0.0507,
            "ItPerNode": 53.8,
            "Time": 9,
            "ObjCnt": 2,
        },
        {
            "Incumbent": 5989536.0,
            "BestBd": 5691475.302964,
            "Gap": 0.049764,
            "CurrentNode": 1845,
            "Time": 10.0,
            "ObjCnt": 2,
        },
    ]

    assert test_data_parser.get_objn_progress("nodelog") == expected


def test_summary(test_data_parser):
    expected = [
        {
            "ObjCnt": 1,
            "ChangedParams": {},
            "PresolveTime": 0.04,
            "PresolvedNumConstrs": 4149,
            "PresolvedNumVars": 7894,
            "PresolvedNumNZs": 16006,
            "PresolvedNumConVars": 962,
            "PresolvedNumIntVars": 6932,
            "PresolvedNumBinVars": 6439,
            "NoRelTime": 2,
            "NoRelBestBd": 16173.9,
            "NoRelBestSol": 16831.999719,
            "RelaxObj": 16173.93,
            "RelaxIterCount": 5304,
            "RelaxTime": 0.04,
            "PreTreeSolutions": 2,
            "NodeCount": 1,
            "IterCount": 10778,
            "Runtime": 2.54,
            "Work": 1.52,
            "ObjVal": 16831.99971851,
            "ObjBound": 16831.99971851,
            "MIPGap": 0.0,
            "Cuts: Gomory": 16,
            "Cuts: Lift-and-project": 1,
            "Threads": 16,
            "Cores": 16,
            "SolCount": 5,
            "Status": "OPTIMAL",
        },
        {
            "ObjCnt": 2,
            "MIPStartObj": 517390000.0,
            "ChangedParams": {},
            "PresolveTime": 0.04,
            "PresolvedNumConstrs": 8134,
            "PresolvedNumNZs": 27958,
            "PresolvedNumVars": 11878,
            "PresolvedNumConVars": 3984,
            "PresolvedNumIntVars": 7894,
            "PresolvedNumBinVars": 7401,
            "NoRelTime": 1,
            "NoRelBestBd": 3012119.8,
            "NoRelBestSol": 6919720.0,
            "RelaxObj": 5011792.0,
            "RelaxIterCount": 13353,
            "RelaxTime": 0.3,
            "PreTreeSolutions": 1,
            "NodeCount": 1845,
            "IterCount": 112268,
            "Runtime": 10.0,
            "Work": 15.7,
            "ObjVal": 5989536.0,
            "ObjBound": 5691475.302964,
            "MIPGap": 0.049764,
            "Cuts: Gomory": 12,
            "Cuts: MIR": 47,
            "Threads": 16,
            "Cores": 16,
            "SolCount": 6,
            "Status": "TIME_LIMIT",
        },
    ]
    assert test_data_parser.get_objn_summaries() == expected
