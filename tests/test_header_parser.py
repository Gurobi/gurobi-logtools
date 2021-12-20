from unittest import TestCase, main

from grblogtools import get_dataframe
from grblogtools.helpers import ParserFlag
from grblogtools.header_parser import HeaderLogParser


class TestHeaderLog(TestCase):
    def setUp(self):
        self._path_to_log = "data/912-Cuts0-glass4-0.log"
        self._header_parser = HeaderLogParser()

    def test_get_flag(self):
        correct_start_lines = [
            "Gurobi 9.1.2 (linux64, gurobi_cl) logging started Fri Jul 30 13:53:48 2021",
            "Compute Server job ID: 7a51ec41-f72d-4b31-95ba-28407986eda3",
            "Gurobi Compute Server Worker version 9.5.0 build v9.1.1rc0 (linux64)",
            "Logging started Fri Jul 30 13:53:48 2021",
            "Logging started",
            "Gurobi 10.0.0 (linux64, gurobi_cl) logging started Fri Jul 30 13:53:48 2021",
        ]

        wrong_start_lines = [
            "Gurobi 900.1.2 (linux64, gurobi_cl) logging started Fri Jul 30 13:53:48 2021",
            "Compute Server job: 7a51ec41-f72d-4b31-95ba-28407986eda3",
            "Gurobi Compute Server Worker version 9.5.0 build v9.1.1rc0 linux64",
            "Logging starte",
        ]
        for line in correct_start_lines:
            flag = self._header_parser.get_flag(line)
            self.assertEqual(ParserFlag.START.name, flag)

        # Reset the flag status
        self._header_parser.set_flag(ParserFlag.UNKNOWN.name)

        for line in wrong_start_lines:
            flag = self._header_parser.get_flag(line)
            self.assertEqual(ParserFlag.UNKNOWN.name, flag)

    def test_parse(self):
        # TODO: Remove the regression part associated with the get_dataframe() method
        expected_log = {
            "Version": "9.1.2",
            "Platform": "linux64, gurobi_cl",
            "Time": "Fri Jul 30 13:53:48 2021",
        }
        # Reset the flag status
        self._header_parser.set_flag(ParserFlag.UNKNOWN.name)

        df = get_dataframe([self._path_to_log])
        with open(self._path_to_log, "r") as f:
            lines = f.readlines()

        current_parser = None
        for line in lines:
            if current_parser:
                flag = current_parser.parse(line)

            if self._header_parser.get_flag(line) == ParserFlag.START.name:
                current_parser = self._header_parser

        self.assertEqual(flag, ParserFlag.END.name)
        header_log = self._header_parser.get_log()
        for column, value in header_log.items():
            self.assertEqual(df[column].values[0], value)
            self.assertEqual(expected_log[column], value)


if __name__ == "__main__":
    main()
