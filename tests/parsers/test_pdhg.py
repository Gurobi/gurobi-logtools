from unittest import TestCase, main

from gurobi_logtools.parsers.pdhg import PdhgParser
from gurobi_logtools.parsers.util import parse_block

example_log_pdhg = """
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
"""
expected_summary_pdhg = {
    "PdhgThreads": 1,
    "PdhgIterCount": 17,
    "Runtime": 4.83,
    "Work": 6.45,
}
expected_progress_pdhg = [
    {
        "Type": "pdhg",
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
        "Type": "pdhg",
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
        "Type": "pdhg",
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


class TestPdhg(TestCase):
    def setUp(self):
        self.pdhg_parser = PdhgParser()

    def test_get_summary_progress(self):
        parse_block(self.pdhg_parser, example_log_pdhg)
        self.assertEqual(self.pdhg_parser.get_summary(), expected_summary_pdhg)
        self.assertEqual(self.pdhg_parser.get_progress(), expected_progress_pdhg)


if __name__ == "__main__":
    main()
