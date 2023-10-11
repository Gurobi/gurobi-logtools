from unittest import TestCase, main

from gurobi_logtools.parsers.simplex import SimplexParser
from gurobi_logtools.parsers.util import parse_block

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
    {
        "Type": "simplex",
        "Iteration": 0,
        "Objective": 0.0,
        "PInf": 0.0,
        "DInf": 0.0,
        "Time": 0,
    },
    {
        "Type": "simplex",
        "Iteration": 0,
        "Objective": 440.0,
        "PInf": 0.0,
        "DInf": 51.02,
        "Time": 0,
    },
    {
        "Type": "simplex",
        "Iteration": 17,
        "Objective": -1.5907818,
        "PInf": 0.0,
        "DInf": 0.0,
        "Time": 0,
    },
]


class TestSimplex(TestCase):
    def setUp(self):
        self.simplex_parser = SimplexParser()

    def test_get_summary_progress(self):
        parse_block(self.simplex_parser, example_log_simplex)
        self.assertEqual(self.simplex_parser.get_summary(), expected_summary_simplex)
        self.assertEqual(self.simplex_parser.get_progress(), expected_progress_simplex)


if __name__ == "__main__":
    main()
