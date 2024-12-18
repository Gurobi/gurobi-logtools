from unittest import TestCase, main

from gurobi_logtools.parsers.termination import TerminationParser
from gurobi_logtools.parsers.util import parse_block

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


interrupted_log = """
Explored 3818 nodes (2594430 simplex iterations) in 9431.94 seconds
Thread count was 8 (of 8 available processors)

Solution count 4: -1.72151e+08 -1.71457e+08 -1.70301e+08 -1.49849e+08

Solve interrupted
Best objective -1.721508552690e+08, best bound -1.763085601859e+08, gap 2.4152%
"""

interrupted_summary = {
    "Status": "INTERRUPTED",
    "SolCount": 4,
    "Threads": 8,
    "Cores": 8,
    "ErrorCode": None,
}

memlimit_log = """
Explored 66258 nodes (470922 simplex iterations) in 18.39 seconds (16.82 work units)
Thread count was 8 (of 8 available processors)

Solution count 10: 1.50001e+09 1.50001e+09 1.50001e+09 ... 1.66668e+09

Memory limit reached
Best objective 1.500012100000e+09, best bound 1.000006566284e+09, gap 33.3334%
"""

memlimit_summary = {
    "Status": "MEM_LIMIT"
}

worklimit_log = """
Explored 30881 nodes (135045 simplex iterations) in 19.60 seconds (10.00 work units)
Thread count was 8 (of 8 available processors)

Solution count 10: 1.50001e+09 1.50001e+09 1.50001e+09 ... 1.66668e+09

Work limit reached
Best objective 1.500012100000e+09, best bound 8.997791698421e+08, gap 40.0152%
"""

worklimit_summary = {
    "Status": "WORK_LIMIT"
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

    def test_interrupted(self):
        parser = TerminationParser()
        parse_block(parser, interrupted_log)
        self.assertEqual(parser.get_summary(), interrupted_summary)

    def test_memlimit(self):
        parser = TerminationParser()
        parse_block(parser, memlimit_log)
        self.assertEqual(parser.get_summary(), memlimit_summary)

    def test_worklimit(self):
        parser = TerminationParser()
        parse_block(parser, worklimit_log)
        self.assertEqual(parser.get_summary(), worklimit_summary)


if __name__ == "__main__":
    main()
