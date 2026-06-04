from unittest import TestCase, main

from gurobi_logtools.parsers.nlbarrier import NonLinearBarrierParser
from gurobi_logtools.parsers.util import parse_block

example_log_nlbarrier = """
Ordering time: 0.05s

NL barrier statistics:
  Hessian NZ  : 3.702e+04
  Jacobian NZ : 5.336e+05
  Factor NZ   : 2.711e+06
  Factor Ops  : 2.358e+07
  Threads     : 16

                           Residuals
Iter     Objective      Primal     Dual      Compl     Step     Time
   0   4.34213397e+08  8.28e+02  2.00e+03  5.54e+03  0.00e+00     1s
   1   1.16203011e+09  5.54e+02  1.96e+03  5.43e+03  3.31e-01     2s
   2   2.55211279e+09  4.42e+02  1.94e+03  5.37e+03  2.02e-01     2s
   3   6.26087199e+09  3.45e+02  1.79e+03  4.95e+03  2.18e-01     2s
   4   1.59558942e+10  2.96e+02  1.70e+03  4.66e+03  1.43e-01     2s

NL barrier solved model in 48 iterations and 6.36 seconds (9.02 work units)
First-order optimal solution
Solution objective 5.665143444362e+10
"""

expected_summary_barrier = {"NLBarIterCount": 48, "Runtime": 6.36, "Work": 9.02}

expected_progress_barrier = [
    {
        "Type": "nlbarrier",
        "Iteration": 0,
        "Indicator": " ",
        "Objective": 434213397.0,
        "PRes": 828.0,
        "DRes": 2000.0,
        "Compl": 5540.0,
        "Step": 0.0,
        "Time": 1,
    },
    {
        "Type": "nlbarrier",
        "Iteration": 1,
        "Indicator": " ",
        "Objective": 1162030110.0,
        "PRes": 554.0,
        "DRes": 1960.0,
        "Compl": 5430.0,
        "Step": 0.331,
        "Time": 2,
    },
    {
        "Type": "nlbarrier",
        "Iteration": 2,
        "Indicator": " ",
        "Objective": 2552112790.0,
        "PRes": 442.0,
        "DRes": 1940.0,
        "Compl": 5370.0,
        "Step": 0.202,
        "Time": 2,
    },
    {
        "Type": "nlbarrier",
        "Iteration": 3,
        "Indicator": " ",
        "Objective": 6260871990.0,
        "PRes": 345.0,
        "DRes": 1790.0,
        "Compl": 4950.0,
        "Step": 0.218,
        "Time": 2,
    },
    {
        "Type": "nlbarrier",
        "Iteration": 4,
        "Indicator": " ",
        "Objective": 15955894200.0,
        "PRes": 296.0,
        "DRes": 1700.0,
        "Compl": 4660.0,
        "Step": 0.143,
        "Time": 2,
    },
]


class TestBarrier(TestCase):
    def setUp(self):
        self.nlbarrier_parser = NonLinearBarrierParser()

    def test_get_summary_progress(self):
        parse_block(self.nlbarrier_parser, example_log_nlbarrier)
        self.assertEqual(self.nlbarrier_parser.get_summary(), expected_summary_barrier)
        self.assertEqual(
            self.nlbarrier_parser.get_progress(), expected_progress_barrier
        )


if __name__ == "__main__":
    main()
