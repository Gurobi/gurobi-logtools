from unittest import TestCase, main

from grblogtools.parsers.termination import TerminationParser

example_log = """
Barrier solved model in 17 iterations and 4.83 seconds (6.45 work units)
Optimal objective 8.000024e+08

Root relaxation: objective 8.000024e+08, 72 iterations, 30.00 seconds

Explored 5135 nodes (36786 simplex iterations) in 93.70 seconds
Thread count was 8 (of 8 available processors)

Solution count 10: 1.20001e+09 1.40001e+09 1.45001e+09 ... 1.60001e+09

Optimal solution found (tolerance 1.00e-04)
Best objective 1.200012600000e+09, best bound 1.200006450000e+09, gap 0.0005%
"""

expected_summary = {
    "Status": "OPTIMAL",
    "SolCount": 10,
    "Threads": 8,
    "Cores": 8,
}


class TestTermination(TestCase):
    def setUp(self):
        pass

    def test_get_summary(self):
        parser = TerminationParser()
        lines = iter(example_log.strip().split("\n"))
        for line in lines:
            parser.parse(line)
        self.assertEqual(parser.get_summary(), expected_summary)


if __name__ == "__main__":
    main()
