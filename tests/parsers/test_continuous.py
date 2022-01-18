from unittest import TestCase, main

from grblogtools.parsers.continuous import ContinuousParser
from grblogtools.parsers.util import parse_lines

example_log_simplex = """
Iteration    Objective       Primal Inf.    Dual Inf.      Time
       0    0.0000000e+00   0.000000e+00   0.000000e+00      0s
       0    4.4000000e+02   0.000000e+00   5.102000e+01      0s
      17   -1.5907818e+00   0.000000e+00   0.000000e+00      0s

Solved in 17 iterations and 0.01 seconds
Optimal objective -1.590781794e+00
"""
expected_summary_simplex = {"IterCount": 17, "Runtime": 0.01}
expected_progress_simplex = [
    {"Iteration": 0, "Objective": 0.0, "PInf": 0.0, "DInf": 0.0, "Time": 0},
    {"Iteration": 0, "Objective": 440.0, "PInf": 0.0, "DInf": 51.02, "Time": 0},
    {"Iteration": 17, "Objective": -1.5907818, "PInf": 0.0, "DInf": 0.0, "Time": 0},
]

example_log_barrier = """
Iter       Primal          Dual         Primal    Dual     Compl     Time
    0   4.56435085e+07  1.53061018e+04  1.69e+05 8.58e+00  1.59e+03     2s
    1   3.76722276e+07 -5.41297282e+05  8.07e+04 9.12e+00  8.17e+02     2s
   17   2.17403572e+02  2.17403571e+02  3.93e-14 7.11e-15  7.71e-13     5s

Barrier solved model in 17 iterations and 4.83 seconds (6.45 work units)
Optimal objective 2.17403572e+02

Crossover log...

    57249 DPushes remaining with DInf 0.0000000e+00                 8s
        0 DPushes remaining with DInf 0.0000000e+00                 9s

     9342 PPushes remaining with PInf 1.2118572e-05                 9s
        0 PPushes remaining with PInf 0.0000000e+00                 9s

   Push phase complete: Pinf 0.0000000e+00, Dinf 1.8540725e-14      9s

Extra simplex iterations after uncrush: 1
Iteration    Objective       Primal Inf.    Dual Inf.      Time
    51765    2.1740357e+02   0.000000e+00   0.000000e+00      9s

Solved in 51765 iterations and 9.18 seconds (13.22 work units)
Optimal objective  2.174035714e+02
"""
expected_summary_barrier = {
    "BarIterCount": 17,
    "Runtime": 4.83,
    "PushPhasePInf": 0.0000000e00,
    "PushPhaseDInf": 1.8540725e-14,
    "PushPhaseEndTime": 9,
}
expected_progress_barrier = [
    {
        "Iteration": 0,
        "Indicator": " ",
        "PObj": 45643508.5,
        "DObj": 15306.1018,
        "PRes": 169000.0,
        "DRes": 8.58,
        "Compl": 1590.0,
        "Time": 2,
    },
    {
        "Iteration": 1,
        "Indicator": " ",
        "PObj": 37672227.6,
        "DObj": -541297.282,
        "PRes": 80700.0,
        "DRes": 9.12,
        "Compl": 817.0,
        "Time": 2,
    },
    {
        "Iteration": 17,
        "Indicator": " ",
        "PObj": 217.403572,
        "DObj": 217.403571,
        "PRes": 3.93e-14,
        "DRes": 7.11e-15,
        "Compl": 7.71e-13,
        "Time": 5,
    },
]

example_log_concurrent = """
Iter       Primal          Dual         Primal    Dual     Compl     Time
   0   4.56435085e+07  1.53061018e+04  1.69e+05 8.58e+00  1.59e+03     2s

Barrier performed 7 iterations in 4.02 seconds (4.19 work units)
Barrier solve interrupted - model solved by another algorithm


Solved with dual simplex
Solved in 69986 iterations and 4.03 seconds (3.91 work units)
Optimal objective  2.174035714e+02
"""
expected_summary_concurrent = {"BarIterCount": 7, "IterCount": 69986, "Runtime": 4.03}
expected_progress_concurrent = [
    {
        "Iteration": 0,
        "Indicator": " ",
        "PObj": 45643508.5,
        "DObj": 15306.1018,
        "PRes": 169000.0,
        "DRes": 8.58,
        "Compl": 1590.0,
        "Time": 2,
    },
]

example_log_relaxation = """
Root relaxation: objective 4.473603e+00, 25 iterations, 0.01 seconds
"""
expected_summary_relaxation = {
    "RelaxObj": 4.473603,
    "RelaxIterCount": 25,
    "RelaxTime": 0.01,
}
expected_progress_relaxation = []

example_log_mip = """
Root simplex log...

Iteration    Objective       Primal Inf.    Dual Inf.      Time
       0    4.2600000e+02   0.000000e+00   0.000000e+00     33s
     473    4.2600000e+02   0.000000e+00   0.000000e+00     33s
     473    4.2600000e+02   0.000000e+00   0.000000e+00     33s

Root relaxation: objective 4.260000e+02, 473 iterations, 0.38 seconds
"""
expected_summary_mip = {
    "RelaxObj": 426.0,
    "RelaxIterCount": 473,
    "RelaxTime": 0.38,
}
expected_progress_mip = [
    {"Iteration": 0, "Objective": 426.0, "PInf": 0.0, "DInf": 0.0, "Time": 33},
    {"Iteration": 473, "Objective": 426.0, "PInf": 0.0, "DInf": 0.0, "Time": 33},
    {"Iteration": 473, "Objective": 426.0, "PInf": 0.0, "DInf": 0.0, "Time": 33},
]


class TestContinuous(TestCase):
    def setUp(self):
        pass

    def test_start_parsing(self):
        expected_start_lines = [
            "Iteration    Objective       Primal Inf.    Dual Inf.      Time",
            "Iter       Primal          Dual         Primal    Dual     Compl     Time",
            "Root relaxation: objective 4.473603e+00, 25 iterations, 0.01 seconds",
        ]
        for i, example_log in enumerate(
            [example_log_simplex, example_log_barrier, example_log_relaxation]
        ):
            with self.subTest(example_log=example_log):
                continuous_parser = ContinuousParser()
                for line in example_log.strip().split("\n"):
                    if continuous_parser.start_parsing(line):
                        self.assertEqual(line, expected_start_lines[i])
                        break
                else:
                    self.assertRaises("No start line found.")

    def test_get_summary_progress(self):
        for example_log, expected_summary, expected_progress in zip(
            [
                example_log_simplex,
                example_log_barrier,
                example_log_concurrent,
                example_log_relaxation,
                example_log_mip,
            ],
            [
                expected_summary_simplex,
                expected_summary_barrier,
                expected_summary_concurrent,
                expected_summary_relaxation,
                expected_summary_mip,
            ],
            [
                expected_progress_simplex,
                expected_progress_barrier,
                expected_progress_concurrent,
                expected_progress_relaxation,
                expected_progress_mip,
            ],
        ):
            with self.subTest(example_log=example_log):
                continuous_parser = ContinuousParser()
                lines = example_log.strip().split("\n")
                parse_lines(continuous_parser, lines)
                self.assertEqual(continuous_parser.get_summary(), expected_summary)
                self.assertEqual(continuous_parser.get_progress(), expected_progress)


if __name__ == "__main__":
    main()
