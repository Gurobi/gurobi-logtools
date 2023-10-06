from unittest import TestCase, main

from gurobi_logtools.parsers.header import HeaderParser
from gurobi_logtools.parsers.util import parse_lines

example_log_0 = """
Gurobi Optimizer version 9.5.0 build v9.5.0rc5 (mac64[arm])
Copyright (c) 2021, Gurobi Optimization, LLC

Read MPS format model from file /Library/gurobi950/macos_universal2/examples/data/glass4.mps
Reading time = 0.00 seconds
glass4: 396 rows, 322 columns, 1815 nonzeros
Thread count: 8 physical cores, 8 logical processors, using up to 8 threads
"""

expected_summary_0 = {
    "Version": "9.5.0",
    "ModelFilePath": "/Library/gurobi950/macos_universal2/examples/data/glass4.mps",
    "ReadingTime": 0.0,
    "PhysicalCores": 8,
    "LogicalProcessors": 8,
    "Threads": 8,
    "ModelName": "glass4",
    "Rows": 396,
    "Columns": 322,
    "Nonzeros": 1815,
}

expected_parameters_0 = {}

example_log_1 = """
Set parameter Presolve to value 0
Set parameter NonConvex to value 2
Gurobi Optimizer version 9.5.0 build v9.5.0rc5 (mac64[rosetta2])
Thread count: 8 physical cores, 8 logical processors, using up to 8 threads
"""

expected_summary_1 = {
    "Version": "9.5.0",
    "PhysicalCores": 8,
    "LogicalProcessors": 8,
    "Threads": 8,
}

expected_parameters_1 = {
    "Presolve": 0,
    "NonConvex": 2,
}

example_log_2 = """
Set parameter CSManager to value "localhost:61000"
Set parameter CSAuthToken
Compute Server job ID: 4e90605d-8ec1-4b56-8351-d8a5355ff641
Capacity available on 'localhost' - connecting...
Established HTTP unencrypted connection
Set parameter ConcurrentMIP to value 2
Set parameter FuncPieces to value 1
Set parameter FuncPieceLength to value 0.001
Gurobi Optimizer version 9.5.0 build v9.5.0rc5 (mac64[rosetta2])
Gurobi Compute Server Worker version 9.5.0 build v9.5.0rc5 (mac64[arm])
Thread count: 8 physical cores, 8 logical processors, using up to 8 threads
"""

expected_summary_2 = {
    "JobID": "4e90605d-8ec1-4b56-8351-d8a5355ff641",
    "Version": "9.5.0",
    "Platform": "mac64[arm]",
    "PhysicalCores": 8,
    "LogicalProcessors": 8,
    "Threads": 8,
}

expected_parameters_2 = {
    "CSManager": '"localhost:61000"',
    "FuncPieces": 1,
    "FuncPieceLength": 0.001,
    "ConcurrentMIP": 2,
}


class TestHeader(TestCase):
    def setUp(self):
        pass

    def test_first_line_matched(self):
        expected_start_lines = [
            "Gurobi Optimizer version 9.5.0 build v9.5.0rc5 (mac64[arm])",
            "Set parameter Presolve to value 0",
            'Set parameter CSManager to value "localhost:61000"',
        ]

        for i, example_log in enumerate([example_log_0, example_log_1, example_log_2]):
            with self.subTest(example_log=example_log):
                header_parser = HeaderParser()
                for line in example_log.strip().split("\n"):
                    if header_parser.parse(line):
                        self.assertEqual(line, expected_start_lines[i])
                        break
                else:
                    self.assertRaises("No start line found.")

    def test_get_summary(self):
        example_logs = [example_log_0, example_log_1, example_log_2]
        expected_summaries = [
            expected_summary_0,
            expected_summary_1,
            expected_summary_2,
        ]
        expected_parameter_sets = [
            expected_parameters_0,
            expected_parameters_1,
            expected_parameters_2,
        ]
        for example_log, expected_summary, expected_parameters in zip(
            example_logs, expected_summaries, expected_parameter_sets
        ):
            with self.subTest(example_log=example_log):
                header_parser = HeaderParser()
                lines = example_log.strip().split("\n")
                parse_lines(header_parser, lines)
                self.assertEqual(header_parser.get_summary(), expected_summary)
                self.assertEqual(header_parser.get_parameters(), expected_parameters)

    def test_start_patterns(self):
        """Check the header parser properly guards later patterns. This is
        important so that when parsing multiple logs, the header parser does
        not interrupt.

        The below presolve line can be caught by the model name/size parser
        in the header, but it should only be picked up if the HeaderParser
        has seen a proper log start line."""

        parser = HeaderParser()
        parse_lines(parser, ["Presolved: 390 rows, 316 columns, 1803 nonzeros"])
        assert not parser.get_summary()

    def test_tuner_log(self):
        parser = HeaderParser()
        parse_lines(parser, ["Solving model misc07"])
        assert parser.get_summary() == {"ModelName": "misc07"}

    def test_changed_params(self):
        """Test non-default algorithm parameters (ignore seed and logfile)"""
        parser = HeaderParser()
        parser.parse("Set parameter Method to value 2")
        parser.parse("Set parameter Threads to value 4")
        parser.parse("Set parameter Seed to value 238476")
        parser.parse("Set parameter LogFile to value log.log")
        parser.parse("Set parameter TimeLimit to value 60")
        assert parser.changed_params() == {"Method": 2, "Threads": 4, "TimeLimit": 60}


if __name__ == "__main__":
    main()
