import re

from grblogtools.helpers import ParserFlag


class HeaderLogParser:
    # Each can represent the start line for the header depending on how Gurobi
    # is ran
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

        It is assumed that all the heard log is encapsulated in one line.
        """
        # The integer value representing the current flag status
        self.flag = ParserFlag.UNKNOWN.value
        self._log = {}

    def get_flag(self, line: str) -> ParserFlag:
        """Return the current parsing status of the header log.

        Args:
            line (str): A line in the log file.

        Returns:
            str: The current parsing status.
        """
        if self.flag == 0:
            for possible_start in HeaderLogParser.header_log_starts:
                match = possible_start.match(line)
                if match:
                    # Populate the log as
                    self._log = {
                        sub_match: value
                        for sub_match, value in match.groupdict().items()
                    }
                    self.flag = 1
                    break
        return ParserFlag(self.flag).name

    def set_flag(self, status: str):
        """Set the current parsing status to the given status value."""
        self.flag = ParserFlag[status].value

    def parse(self, line: str) -> str:
        """Return the current parsing status after parsing the given line."""
        # Set the flag to END
        self.flag = 3
        return ParserFlag(self.flag).name

    def get_log(self) -> dict:
        """Return the current parsed log."""
        return self._log


if __name__ == "__main__":
    hearder = HeaderLogParser()
