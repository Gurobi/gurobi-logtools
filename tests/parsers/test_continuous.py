from unittest import TestCase, main

from gurobi_logtools.parsers.continuous import ContinuousParser
from gurobi_logtools.parsers.pretree_solutions import PreTreeSolutionParser
from gurobi_logtools.parsers.util import parse_block

example_log_barrier_with_simplex = """
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
expected_progress_last_entry = {
    "Type": "simplex",
    "Iteration": 51765,
    "Objective": 217.40357,
    "PInf": 0.0,
    "DInf": 0.0,
    "Time": 9,
}


example_log_concurrent = """
Iter       Primal          Dual         Primal    Dual     Compl     Time
   0   4.56435085e+07  1.53061018e+04  1.69e+05 8.58e+00  1.59e+03     2s

Barrier performed 7 iterations in 4.02 seconds (4.19 work units)
Barrier solve interrupted - model solved by another algorithm


Solved with dual simplex
Solved in 69986 iterations and 4.03 seconds (3.91 work units)
Optimal objective  2.174035714e+02
"""
expected_summary_concurrent = {
    "Status": "OPTIMAL",
    "ObjVal": 217.4035714,
    "BarIterCount": 7,
    "IterCount": 69986,
    "Runtime": 4.03,
    "Work": 3.91,
}
expected_progress_concurrent = [
    {
        "Type": "barrier",
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
    {
        "Type": "simplex",
        "Iteration": 0,
        "Objective": 426.0,
        "PInf": 0.0,
        "DInf": 0.0,
        "Time": 33,
    },
    {
        "Type": "simplex",
        "Iteration": 473,
        "Objective": 426.0,
        "PInf": 0.0,
        "DInf": 0.0,
        "Time": 33,
    },
    {
        "Type": "simplex",
        "Iteration": 473,
        "Objective": 426.0,
        "PInf": 0.0,
        "DInf": 0.0,
        "Time": 33,
    },
]


example_log_pdhg = """
Start PDHG using 1 threads

                       Objective                Residual
     Iter       Primal          Dual         Primal    Dual     Compl    Time
        0   0.00000000e+00 -5.22205640e+02  0.00e+00 0.00e+00  3.73e+01    0s
     1228  -4.64753114e+02 -4.64753116e+02  1.29e-05 1.23e-07  1.55e-07    0s

PDHG solved model in 1228 iterations and 0.00 seconds (0.00 work units)
Optimal objective -4.64753114e+02

Crossover log...

       0 DPushes remaining with DInf 0.0000000e+00                 0s

       1 PPushes remaining with PInf 0.0000000e+00                 0s
       0 PPushes remaining with PInf 0.0000000e+00                 0s

  Push phase complete: Pinf 0.0000000e+00, Dinf 0.0000000e+00      0s

Crossover time: 0.00 seconds (0.00 work units)
Iteration    Objective       Primal Inf.    Dual Inf.      Time
       4   -4.6475314e+02   0.000000e+00   0.000000e+00      0s

Solved in 4 iterations and 0.00 seconds (0.00 work units)
Optimal objective -4.647531429e+02
"""
expected_summary_pdhg = {
    "Status": "OPTIMAL",
    "IterCount": 4,
    "ObjVal": -464.7531429,
    "PdhgThreads": 1,
    "PdhgIterCount": 1228,
    "Runtime": 0.0,
    "Work": 0.0,
    "PushPhasePInf": 0.0,
    "PushPhaseDInf": 0.0,
    "PushPhaseEndTime": 0,
    "CrossoverRuntime": 0.0,
    "CrossoverWork": 0.0,
}
expected_progress_pdhg = [
    {
        "Type": "pdhg",
        "Iteration": 0,
        "Indicator": " ",
        "PObj": 0.0,
        "DObj": -522.205640,
        "PRes": 0.0,
        "DRes": 0.0,
        "Compl": 37.3,
        "Time": 0,
    },
    {
        "Type": "pdhg",
        "Iteration": 1228,
        "Indicator": " ",
        "PObj": -464.753114,
        "DObj": -464.753116,
        "PRes": 1.29e-05,
        "DRes": 1.23e-07,
        "Compl": 1.55e-07,
        "Time": 0,
    },
    {
        "Type": "crossover",
        "RemainingDPushes": 0,
        "PushPhaseDInf": 0.0,
        "Time": 0,
    },
    {
        "Type": "crossover",
        "RemainingPPushes": 1,
        "PushPhasePInf": 0.0,
        "Time": 0,
    },
    {
        "Type": "crossover",
        "RemainingPPushes": 0,
        "PushPhasePInf": 0.0,
        "Time": 0,
    },
    {
        "Type": "simplex",
        "Iteration": 4,
        "Objective": -464.75314,
        "PInf": 0.0,
        "DInf": 0.0,
        "Time": 0,
    },
]


class TestContinuous(TestCase):
    def test_last_progress_entry_barrier_with_simplex(self):
        continuous_parser = ContinuousParser(PreTreeSolutionParser())
        parse_block(continuous_parser, example_log_barrier_with_simplex)
        self.assertEqual(
            continuous_parser.get_progress()[-1],
            expected_progress_last_entry,
        )

    def test_get_summary_progress(self):
        for example_log, expected_summary, expected_progress in zip(
            [
                example_log_concurrent,
                example_log_relaxation,
                example_log_mip,
                example_log_pdhg,
            ],
            [
                expected_summary_concurrent,
                expected_summary_relaxation,
                expected_summary_mip,
                expected_summary_pdhg,
            ],
            [
                expected_progress_concurrent,
                expected_progress_relaxation,
                expected_progress_mip,
                expected_progress_pdhg,
            ],
        ):
            with self.subTest(example_log=example_log):
                continuous_parser = ContinuousParser(PreTreeSolutionParser())
                parse_block(continuous_parser, example_log)
                self.assertEqual(continuous_parser.get_summary(), expected_summary)
                self.assertEqual(continuous_parser.get_progress(), expected_progress)


if __name__ == "__main__":
    main()
