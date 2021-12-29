import datetime
from unittest import TestCase, main

from grblogtools.header_parser import HeaderParser
from grblogtools.helpers import parse_lines


class TestHeaderLog(TestCase):
    def setUp(self):
        self._correct_start_lines = [
            "Gurobi 9.1.2 (linux64, gurobi_cl) logging started Fri Jul 30 13:53:48 2021",
            "Compute Server job ID: 7a51ec41-f72d-4b31-95ba-28407986eda3",
            "Gurobi Compute Server Worker version 9.5.0 build v9.1.1rc0 (linux64)",
            "Logging started Fri Jul 30 13:53:48 2021",
            "Logging started ",
            "Gurobi 10.0.0 (linux64, gurobi_cl) logging started Fri Jul 30 13:53:48 2021",
        ]

        self._wrong_start_lines = [
            "Gurobi 900.1.2 (linux64, gurobi_cl) logging started Fri Jul 30 13:53:48 2021",
            "Compute Server job: 7a51ec41-f72d-4b31-95ba-28407986eda3",
            "Gurobi Compute Server Worker version 9.5.0 build v9.1.1rc0 linux64",
            "Logging starte",
        ]

    def test_start_parsing(self):
        for line in self._correct_start_lines:
            with self.subTest(line=line):
                header_parser = HeaderParser()
                self.assertTrue(header_parser.start_parsing(line))

        for line in self._wrong_start_lines:
            with self.subTest(line=line):
                header_parser = HeaderParser()
                self.assertFalse(header_parser.start_parsing(line))

    def test_get_log(self):
        expected_logs = [
            {
                "Version": "9.1.2",
                "Platform": "linux64, gurobi_cl",
                "Time": datetime.datetime(2021, 7, 30, 13, 53, 48),
            },
            {"JobID": "7a51ec41-f72d-4b31-95ba-28407986eda3"},
            {"Version": "9.5.0", "Platform": "linux64"},
            {"Time": datetime.datetime(2021, 7, 30, 13, 53, 48)},
            {"Time": ""},
            {
                "Version": "10.0.0",
                "Platform": "linux64, gurobi_cl",
                "Time": datetime.datetime(2021, 7, 30, 13, 53, 48),
            },
        ]

        for i, line in enumerate(self._correct_start_lines):
            with self.subTest(line=line):
                header_parser = HeaderParser()
                parse_lines(header_parser, [line])
                returned_log = header_parser.get_log()
                self.assertEqual(returned_log, expected_logs[i])

        for line in self._wrong_start_lines:
            with self.subTest(line=line):
                header_parser = HeaderParser()
                parse_lines(header_parser, [line])
                returned_log = header_parser.get_log()
                self.assertEqual(returned_log, {})


if __name__ == "__main__":
    main()
