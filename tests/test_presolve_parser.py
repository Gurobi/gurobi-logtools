from unittest import TestCase, main

from grblogtools.helpers import parse_lines
from grblogtools.presolve_parser import PresolveParser

example_log_0 = """
Gurobi Optimizer version 9.5.0 build v9.5.0rc5 (mac64[arm])
Copyright (c) 2021, Gurobi Optimization, LLC

Read MPS format model from file /Library/gurobi950/macos_universal2/examples/data/glass4.mps
Reading time = 0.00 seconds
glass4: 396 rows, exit columns, 1815 nonzeros
Thread count: 8 physical cores, 8 logical processors, using up to 8 threads
Optimize a model with 396 rows, 322 columns and 1815 nonzeros
Model fingerprint: 0x18b19fdf
Variable types: 20 continuous, 302 integer (0 binary)
Coefficient statistics:
  Matrix range     [1e+00, 8e+06]
  Objective range  [1e+00, 1e+06]
  Bounds range     [1e+00, 8e+02]
  RHS range        [1e+00, 8e+06]
Presolve removed 6 rows and 6 columns
Presolve time: 0.01s
Presolved: 390 rows, 316 columns, 1803 nonzeros
Variable types: 19 continuous, 297 integer (297 binary)
Found heuristic solution: objective 3.133356e+09
"""

expected_log_0 = {
    "ModelFilePath": "/Library/gurobi950/macos_universal2/examples/data/glass4.mps",
    "ReadingTime": 0.0,
    "NumConstrs": 396,
    "NumVars": 322,
    "NumNZs": 1815,
    "Fingerprint": "0x18b19fdf",
    "PresolvedNumConVars": 19,
    "PresolvedNumIntVars": 297,
    "PresolvedNumBinVars": 297,
    "MinCoeff": 1.0,
    "MaxCoeff": 8000000.0,
    "MinObjCoeff": 1.0,
    "MaxObjCoeff": 1000000.0,
    "MinBound": 1.0,
    "MaxBound": 800.0,
    "MinRHS": 1.0,
    "MaxRHS": 8000000.0,
    "PresolveTime": 0.01,
    "PresolvedNumConstrs": 390,
    "PresolvedNumVars": 316,
    "PresolvedNumNZs": 1803,
}

example_log_1 = """
Set parameter Presolve to value 0
Set parameter NonConvex to value 2
Gurobi Optimizer version 9.5.0 build v9.5.0rc5 (mac64[rosetta2])
Thread count: 8 physical cores, 8 logical processors, using up to 8 threads
Optimize a model with 1 rows, 3 columns and 3 nonzeros
Model fingerprint: 0x83663ee2
Model has 2 quadratic constraints
Coefficient statistics:
  Matrix range     [1e+00, 1e+00]
  QMatrix range    [1e+00, 1e+00]
  Objective range  [1e+00, 1e+00]
  Bounds range     [0e+00, 0e+00]
  RHS range        [1e+01, 1e+01]
  QRHS range       [1e+00, 2e+00]

Continuous model is non-convex -- solving as a MIP

Variable types: 6 continuous, 0 integer (0 binary)
"""

expected_log_1 = {
    "Presolve": 0,
    "NonConvex": 2,
    "Version": "9.5.0",
    "NumConstrs": 1,
    "NumVars": 3,
    "NumNZs": 3,
    "Fingerprint": "0x83663ee2",
    "NumQConstrs": 2,
    "MinCoeff": 1.0,
    "MaxCoeff": 1.0,
    "MinQCCoeff": 1.0,
    "MaxQCCoeff": 1.0,
    "MinObjCoeff": 1.0,
    "MaxObjCoeff": 1.0,
    "MinBound": 0.0,
    "MaxBound": 0.0,
    "MinRHS": 10.0,
    "MaxRHS": 10.0,
    "MinQCRHS": 1.0,
    "MaxQCRHS": 2.0,
    "PresolvedNumConVars": 6,
    "PresolvedNumIntVars": 0,
    "PresolvedNumBinVars": 0,
}

example_log_2 = """
Set parameter ConcurrentMIP to value 2
Set parameter FuncPieces to value 1
Set parameter FuncPieceLength to value 0.001
Gurobi Optimizer version 9.5.0 build v9.5.0rc5 (mac64[rosetta2])
Thread count: 8 physical cores, 8 logical processors, using up to 8 threads
Optimize a model with 1 rows, 4 columns and 2 nonzeros
Model fingerprint: 0x741a3617
Model has 2 general constraints
Variable types: 4 continuous, 0 integer (0 binary)
Coefficient statistics:
  Matrix range     [1e+00, 4e+00]
  Objective range  [1e+00, 2e+00]
  Bounds range     [0e+00, 0e+00]
  RHS range        [9e+00, 9e+00]

Concurrent MIP optimizer: 2 concurrent instances (4 threads per instance)

Presolve added 6 rows and 7263 columns
Presolve time: 0.02s
Presolved: 7 rows, 7267 columns, 21791 nonzeros
Presolved model has 2 SOS constraint(s)
Variable types: 7267 continuous, 0 integer (0 binary)
"""

expected_log_2 = {
    "ConcurrentMIP": 2,
    "FuncPieces": 1,
    "FuncPieceLength": 0.001,
    "Version": "9.5.0",
    "NumConstrs": 1,
    "NumVars": 4,
    "NumNZs": 2,
    "Fingerprint": "0x741a3617",
    "NumGenConstrs": 2,
    "PresolvedNumConVars": 7267,
    "PresolvedNumIntVars": 0,
    "PresolvedNumBinVars": 0,
    "MinCoeff": 1.0,
    "MaxCoeff": 4.0,
    "MinObjCoeff": 1.0,
    "MaxObjCoeff": 2.0,
    "MinBound": 0.0,
    "MaxBound": 0.0,
    "MinRHS": 9.0,
    "MaxRHS": 9.0,
    "ConcurrentJobs": 2,
    "PresolveTime": 0.02,
    "PresolvedNumConstrs": 7,
    "PresolvedNumVars": 7267,
    "PresolvedNumNZs": 21791,
}


class TestHeaderLog(TestCase):
    def setUp(self):
        pass

    def test_start_parsing(self):
        expected_start_lines = [
            "Read MPS format model from file /Library/gurobi950/macos_universal2/examples/data/glass4.mps",
            "Set parameter Presolve to value 0",
            "Set parameter ConcurrentMIP to value 2",
        ]

        for i, example_log in enumerate([example_log_0, example_log_1, example_log_2]):
            with self.subTest(example_log=example_log):
                presolve_parser = PresolveParser()
                for line in example_log.strip().split("\n"):
                    if presolve_parser.start_parsing(line):
                        self.assertEqual(line, expected_start_lines[i])
                        break

    def test_get_log(self):
        expected_logs = [expected_log_0, expected_log_1, expected_log_2]
        for i, example_log in enumerate([example_log_0, example_log_1, example_log_2]):
            with self.subTest(example_log=example_log):
                presolve_parser = PresolveParser()
                lines = example_log.strip().split("\n")
                parse_lines(presolve_parser, lines)
                self.assertEqual(presolve_parser.get_log(), expected_logs[i])


if __name__ == "__main__":
    main()
