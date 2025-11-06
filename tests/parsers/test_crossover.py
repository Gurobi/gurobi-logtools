from unittest import TestCase, main

from gurobi_logtools.parsers.crossover import CrossoverParser
from gurobi_logtools.parsers.util import parse_block

example_log_lp_crossover = """
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
expected_summary_lp_crossover = {
    "PushPhasePInf": 0.0000000e00,
    "PushPhaseDInf": 1.8540725e-14,
    "PushPhaseEndTime": 9,
    "CrossoverRuntime": 1.23,
    "CrossoverWork": 1.78,
}
expected_progress_lp_crossover = [
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

example_log_mip_crossover = """
Root barrier log...

Ordering time: 1.14s
Ordering time: 1.27s

Barrier statistics:
 Dense cols : 201
 AA' NZ     : 1.977e+07
 Factor NZ  : 8.279e+07 (roughly 700 MB of memory)
 Factor Ops : 5.196e+11 (roughly 1 second per iteration)
 Threads    : 8

                  Objective                Residual
Iter       Primal          Dual         Primal    Dual     Compl     Time
   0   4.86463581e+06 -1.30471069e+08  7.02e+02 1.00e+00  4.97e+04     9s
   1   3.13237056e+06 -1.43636295e+08  4.08e+02 1.16e+03  2.58e+04    12s
   2   2.31892437e+06 -1.27549140e+08  2.91e+02 2.55e+02  1.58e+04    15s
   3   4.58425844e+05 -8.79225494e+07  4.82e+01 2.59e+01  3.33e+03    19s
   4   2.00813609e+05 -3.07297304e+07  6.40e+00 1.37e-09  6.56e+02    23s
   5   1.76837736e+05 -1.31786225e+07  2.55e+00 4.53e-10  2.50e+02    26s
   6   1.56963641e+05 -3.44238199e+06  2.65e-01 8.37e-11  5.42e+01    30s
   7   1.48413596e+05 -1.06649816e+06  7.88e-02 2.76e-11  1.76e+01    33s
   8   1.34536474e+05 -1.20226765e+05  1.45e-05 7.79e-12  3.62e+00    37s
   9   1.10347277e+05  4.34240772e+04  4.60e-06 3.83e-12  9.51e-01    40s
  10   1.04513492e+05  6.36116125e+04  3.14e-06 4.34e-12  5.81e-01    44s
  11   1.00197588e+05  7.69208277e+04  1.99e-06 3.28e-12  3.31e-01    47s
  12   9.67427540e+04  8.44838350e+04  1.01e-06 8.10e-12  1.74e-01    51s
  13   9.52255402e+04  8.86563497e+04  6.49e-07 5.26e-12  9.33e-02    54s
  14   9.45888483e+04  9.02434079e+04  4.93e-07 6.46e-11  6.17e-02    58s
  15   9.41820610e+04  9.15694715e+04  3.05e-07 1.03e-11  3.71e-02    61s
  16   9.39145028e+04  9.25757385e+04  1.18e-07 1.43e-10  1.90e-02    65s
  17   9.36979461e+04  9.32796950e+04  3.80e-08 1.77e-10  5.94e-03    69s
  18   9.36143950e+04  9.34103091e+04  1.29e-08 8.80e-11  2.90e-03    72s
  19   9.35971205e+04  9.34810815e+04  9.80e-09 4.17e-11  1.65e-03    75s
  20   9.35824919e+04  9.34990283e+04  7.49e-09 2.27e-11  1.19e-03    79s
  21   9.35613019e+04  9.35090066e+04  4.16e-09 2.41e-11  7.43e-04    82s
  22   9.35474353e+04  9.35208133e+04  2.11e-09 1.04e-10  3.78e-04    86s
  23   9.35369896e+04  9.35251228e+04  8.44e-10 3.32e-10  1.69e-04    90s
  24   9.35343700e+04  9.35268691e+04  5.60e-10 4.27e-10  1.07e-04    93s
  25   9.35323142e+04  9.35275712e+04  3.23e-10 4.49e-10  6.74e-05    97s
  26   9.35315300e+04  9.35283115e+04  2.41e-10 4.80e-10  4.57e-05   100s
  27   9.35306611e+04  9.35288057e+04  1.49e-10 7.22e-10  2.63e-05   104s
  28   9.35294622e+04  9.35290701e+04  1.99e-11 5.50e-10  5.57e-06   108s
  29   9.35293909e+04  9.35291339e+04  1.04e-09 2.50e-10  3.65e-06   111s
  30   9.35293171e+04  9.35291751e+04  1.24e-09 4.42e-10  2.02e-06   115s
  31   9.35292487e+04  9.35291996e+04  5.66e-09 2.06e-10  6.97e-07   119s
  32   9.35292254e+04  9.35292115e+04  3.34e-09 1.89e-10  1.97e-07   122s
  33   9.35292158e+04  9.35292148e+04  5.85e-09 2.48e-10  1.49e-08   126s
  34   9.35292153e+04  9.35292152e+04  6.58e-09 1.26e-10  1.63e-09   130s

Barrier solved model in 34 iterations and 129.72 seconds (266.27 work units)
Optimal objective 9.35292153e+04


Root crossover log...

   15377 DPushes remaining with DInf 4.1212817e-02               130s
    1232 DPushes remaining with DInf 2.4035060e-03               130s
       0 DPushes remaining with DInf 3.0197351e-01               130s

     468 PPushes remaining with PInf 1.4668106e-03               130s
       0 PPushes remaining with PInf 0.0000000e+00               130s

  Push phase complete: Pinf 0.0000000e+00, Dinf 1.0410863e-01    130s
Crossover time: 0.63 seconds (1.92 work units)

Root simplex log...

Iteration    Objective       Primal Inf.    Dual Inf.      Time
    4242    9.3529215e+04   0.000000e+00   1.041086e-01    130s
    4305    9.3529215e+04   0.000000e+00   0.000000e+00    130s
    4305    9.3529215e+04   0.000000e+00   0.000000e+00    130s

Root relaxation: objective 9.352922e+04, 4305 iterations, 128.70 seconds (268.84 work units)
"""
expected_summary_mip_crossover = {
    "PushPhasePInf": 0.0000000e00,
    "PushPhaseDInf": 1.0410863e-01,
    "PushPhaseEndTime": 130,
    "CrossoverRuntime": 0.63,
    "CrossoverWork": 1.92,
}
expected_progress_mip_crossover = [
    {
        "Type": "crossover",
        "RemainingDPushes": 15377,
        "PushPhaseDInf": 4.1212817e-02,
        "Time": 130,
    },
    {
        "Type": "crossover",
        "RemainingDPushes": 1232,
        "PushPhaseDInf": 2.4035060e-03,
        "Time": 130,
    },
    {
        "Type": "crossover",
        "RemainingDPushes": 0,
        "PushPhaseDInf": 3.0197351e-01,
        "Time": 130,
    },
    {
        "Type": "crossover",
        "RemainingPPushes": 468,
        "PushPhasePInf": 1.4668106e-03,
        "Time": 130,
    },
    {
        "Type": "crossover",
        "RemainingPPushes": 0,
        "PushPhasePInf": 0.0,
        "Time": 130,
    },
]


class TestCrossover(TestCase):
    def test_get_summary_progress(self):
        for example_log, expected_summary, expected_progress in zip(
            [
                example_log_lp_crossover,
                example_log_mip_crossover,
            ],
            [
                expected_summary_lp_crossover,
                expected_summary_mip_crossover,
            ],
            [
                expected_progress_lp_crossover,
                expected_progress_mip_crossover,
            ],
        ):
            crossover_parser = CrossoverParser()
            parse_block(crossover_parser, example_log)
            self.assertEqual(crossover_parser.get_summary(), expected_summary)
            self.assertEqual(crossover_parser.get_progress(), expected_progress)


if __name__ == "__main__":
    main()
