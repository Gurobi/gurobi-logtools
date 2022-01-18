from unittest import TestCase, main

from grblogtools.parsers.termination import TerminationParser

example_log_0 = """
Barrier performed 302 iterations in 500.18 seconds
Sub-optimal termination - objective 5.14914644e+03
"""
expected_summary_0 = {
    "Status": "SUBOPTIMAL",
    "ObjVal": 5149.14644,
}

example_log_1 = """
Barrier performed 7 iterations in 4.02 seconds (4.19 work units)
Barrier solve interrupted - model solved by another algorithm


Solved with dual simplex
Solved in 69986 iterations and 4.03 seconds (3.91 work units)
Optimal objective  2.174035714e+02
"""
expected_summary_1 = {
    "Status": "OPTIMAL",
    "ObjVal": 217.4035714,
}

example_log_2 = """
Barrier solved model in 17 iterations and 4.83 seconds (6.45 work units)
Optimal objective 8.000024e+08

Root relaxation: objective 8.000024e+08, 72 iterations, 30.00 seconds

Explored 5135 nodes (36786 simplex iterations) in 93.70 seconds
Thread count was 8 (of 8 available processors)

Solution count 10: 1.20001e+09 1.40001e+09 1.45001e+09 ... 1.60001e+09

Optimal solution found (tolerance 1.00e-04)
Best objective 1.200012600000e+09, best bound 1.200006450000e+09, gap 0.0005%
"""

expected_summary_2 = {
    "Status": "OPTIMAL",
    "ObjVal": 1200012600.0,
    "SolCount": 10,
    "ObjBound": 1200006450.0,
    "MIPGap": 5e-06,
    "Threads": 8,
    "Cores": 8,
}


class TestTermination(TestCase):
    def setUp(self):
        pass

    def test_get_summary(self):
        for example_log, expected_summary in zip(
            [example_log_0, example_log_1, example_log_2],
            [expected_summary_0, expected_summary_1, expected_summary_2],
        ):
            with self.subTest(example_log=example_log):
                parser = TerminationParser()
                lines = iter(example_log.strip().split("\n"))
                for line in lines:
                    parser.parse(line)
                self.assertEqual(parser.get_summary(), expected_summary)


if __name__ == "__main__":
    main()
