import re

from grblogtools.helpers import ParserFlag


class HeaderLogParser:
    # Each might represent the start of the header parser depending on how Gurobi
    # is run
    header_log_starts = [
        re.compile(
            "Gurobi (?P<Version>\d{1,2}\.[^\s]+) \((?P<Platform>[^\)]+)\) logging started (?P<Time>.*)$"
        ),
        re.compile("Logging started (?P<Time>.*)$"),
        re.compile(
            "Gurobi Compute Server Worker version (?P<Version>\d{1,2}\.[^\s]+) build (.*) \((?P<Platform>[^\)]+)\)$"
        ),
        re.compile("Compute Server job ID: (?P<JobID>.*)$"),
    ]

    def __init__(self):
        """Initialize the log parser for the header.

        Note: All header log is captured in one line.
        """
        # The integer value representing the current parser status
        self.flag = ParserFlag.UNKNOWN.value
        self._log = {}

    def get_flag(self, line: str) -> str:
        """Return the current status of the header parser.

        Args:
            line (str): A line in the log file.

        Returns:
            str: The current parsing status.
        """
        if self.flag == 0:
            for possible_start in HeaderLogParser.header_log_starts:
                if match := possible_start.match(line):
                    # Populate the log as the header log is captured on the start line
                    self._log = {
                        sub_match: value
                        for sub_match, value in match.groupdict().items()
                    }
                    # Change the status to START
                    self.flag = 1
                    break
        return ParserFlag(self.flag).name

    def set_flag(self, status: str):
        """Set the current parsing status to the given status name."""
        self.flag = ParserFlag[status].value

    def parse(self, line: str) -> str:
        """Return the current parsing status after parsing the given line."""
        # Set the flag to END
        self.flag = 3
        return ParserFlag(self.flag).name

    def get_log(self) -> dict:
        """Return the current parsed log."""
        return self._log
