from unittest import TestCase, main

from grblogtools.parsers.continuous import ContinuousParser
from grblogtools.parsers.util import parse_block

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
    def test_get_summary_progress(self):
        for example_log, expected_summary, expected_progress in zip(
            [
                example_log_concurrent,
                example_log_relaxation,
                example_log_mip,
            ],
            [
                expected_summary_concurrent,
                expected_summary_relaxation,
                expected_summary_mip,
            ],
            [
                expected_progress_concurrent,
                expected_progress_relaxation,
                expected_progress_mip,
            ],
        ):
            with self.subTest(example_log=example_log):
                continuous_parser = ContinuousParser()
                parse_block(continuous_parser, example_log)
                self.assertEqual(continuous_parser.get_summary(), expected_summary)
                self.assertEqual(continuous_parser.get_progress(), expected_progress)


if __name__ == "__main__":
    main()
