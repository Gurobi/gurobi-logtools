from unittest import TestCase, main

from gurobi_logtools.parsers.crossover import CrossoverParser
from gurobi_logtools.parsers.util import parse_block

example_log_crossover = """
Start PDHG using 1 threads

                       Objective                Residual
     Iter       Primal          Dual         Primal    Dual     Compl     Time
        0   4.56435085e+07  1.53061018e+04  1.69e+05 8.58e+00  1.59e+03     2s
        1   3.76722276e+07 -5.41297282e+05  8.07e+04 9.12e+00  8.17e+02     2s
       17   2.17403572e+02  2.17403571e+02  3.93e-14 7.11e-15  7.71e-13     5s

PDHG solved model in 17 iterations and 4.83 seconds (6.45 work units)
Optimal objective 2.17403572e+02

Crossover log...

    57249 DPushes remaining with DInf 0.0000000e+00                 8s
        0 DPushes remaining with DInf 0.0000000e+00                 9s

     9342 PPushes remaining with PInf 1.2118572e-05                 9s
        0 PPushes remaining with PInf 0.0000000e+00                 9s

   Push phase complete: Pinf 0.0000000e+00, Dinf 1.8540725e-14      9s
Crossover time: 1.23 seconds (1.78 work units)
"""
expected_summary_crossover = {
    "PushPhasePInf": 0.0000000e00,
    "PushPhaseDInf": 1.8540725e-14,
    "PushPhaseEndTime": 9,
    "CrossoverRuntime": 1.23,
    "CrossoverWork": 1.78,
}
expected_progress_crossover = [
    {
        "Type": "crossover",
        "RemainingDPushes": 57249,
        "PushPhaseDInf": 0.0,
        "Time": 8,
    },
    {
        "Type": "crossover",
        "RemainingDPushes": 0,
        "PushPhaseDInf": 0.0,
        "Time": 9,
    },
    {
        "Type": "crossover",
        "RemainingPPushes": 9342,
        "PushPhasePInf": 1.2118572e-05,
        "Time": 9,
    },
    {
        "Type": "crossover",
        "RemainingPPushes": 0,
        "PushPhasePInf": 0.0,
        "Time": 9,
    },
]


class TestCrossover(TestCase):
    def setUp(self):
        self.crossover_parser = CrossoverParser()

    def test_get_summary_progress(self):
        parse_block(self.crossover_parser, example_log_crossover)
        self.assertEqual(
            self.crossover_parser.get_summary(), expected_summary_crossover
        )
        self.assertEqual(
            self.crossover_parser.get_progress(), expected_progress_crossover
        )


if __name__ == "__main__":
    main()
