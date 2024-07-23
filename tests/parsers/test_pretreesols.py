from unittest import TestCase, main

from gurobi_logtools.parsers.continuous import ContinuousParser
from gurobi_logtools.parsers.presolve import PresolveParser
from gurobi_logtools.parsers.pretree_solutions import PreTreeSolutionParser
from gurobi_logtools.parsers.util import parse_lines

example_log_0 = """
Optimize a model with 396 rows, 322 columns and 1815 nonzeros
Model fingerprint: 0x18b19fdf
Variable types: 20 continuous, 302 integer (0 binary)
Coefficient statistics:
  Matrix range     [1e+00, 8e+06]
  Objective range  [1e+00, 1e+06]
  Bounds range     [1e+00, 8e+02]
  RHS range        [1e+00, 8e+06]
Presolve removed 6 rows and 6 columns
Found heuristic solution: objective 1.133356e+09
Presolve time: 0.01s
Found heuristic solution: objective 2.133356e+09
Presolved: 390 rows, 316 columns, 1803 nonzeros
Variable types: 19 continuous, 297 integer (297 binary)
Found heuristic solution: objective 3.133356e+09
"""

expected_summary = {"PreTreeSolutions": 3}

expected_progress = [
    {"Incumbent": 1133356000.0},
    {"Incumbent": 2133356000.0},
    {"Incumbent": 3133356000.0},
]

example_log_1 = """
Iter       Primal          Dual         Primal    Dual     Compl     Time
    0   4.56435085e+07  1.53061018e+04  1.69e+05 8.58e+00  1.59e+03     2s
    1   3.76722276e+07 -5.41297282e+05  8.07e+04 9.12e+00  8.17e+02     2s
   17   2.17403572e+02  2.17403571e+02  3.93e-14 7.11e-15  7.71e-13     5s

Barrier solved model in 17 iterations and 4.83 seconds (6.45 work units)
Found heuristic solution: objective 1.133356e+09
Optimal objective 2.17403572e+02

Crossover log...

    57249 DPushes remaining with DInf 0.0000000e+00                 8s
        0 DPushes remaining with DInf 0.0000000e+00                 9s

Found heuristic solution: objective 2.133356e+09

     9342 PPushes remaining with PInf 1.2118572e-05                 9s
        0 PPushes remaining with PInf 0.0000000e+00                 9s

   Push phase complete: Pinf 0.0000000e+00, Dinf 1.8540725e-14      9s

Extra simplex iterations after uncrush: 1
Found heuristic solution: objective 3.133356e+09

Iteration    Objective       Primal Inf.    Dual Inf.      Time
    51765    2.1740357e+02   0.000000e+00   0.000000e+00      9s

Solved in 51765 iterations and 9.18 seconds (13.22 work units)
Optimal objective  2.174035714e+02
"""

example_logs = (example_log_0, example_log_1)
parsers = (PresolveParser, ContinuousParser)


class TestPresolve(TestCase):
    def setUp(self):
        pass

    def test_get_summary_presolve(self):
        for example_log, Parser in zip(example_logs, parsers):
            with self.subTest(example_log=example_log):
                pretree_sols_parser = PreTreeSolutionParser()
                presolve_parser = Parser(pretree_sols_parser)
                lines = example_log.strip().split("\n")
                parse_lines(presolve_parser, lines)
                self.assertEqual(pretree_sols_parser.get_summary(), expected_summary)

    def test_get_progress_presolve(self):
        for example_log, Parser in zip(example_logs, parsers):
            with self.subTest(example_log=example_log):
                pretree_sols_parser = PreTreeSolutionParser()
                presolve_parser = Parser(pretree_sols_parser)
                lines = example_log.strip().split("\n")
                parse_lines(presolve_parser, lines)
                pretree_sols_parser.get_progress()
                self.assertEqual(pretree_sols_parser.get_progress(), expected_progress)


if __name__ == "__main__":
    main()
