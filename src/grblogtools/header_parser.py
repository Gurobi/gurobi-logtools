import re
import datetime


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
        self._log = {}
        self._date_time_format = "%a %b %d %H:%M:%S %Y"

    def start_parsing(self, line: str) -> bool:
        """Return True if the parser should start parsing the log lines.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the parser should call the continue_parsing() method
                on future log lines until it hits its termination.
        """
        for possible_start in HeaderLogParser.header_log_starts:
            match = possible_start.match(line)
            if match:
                self._log = match.groupdict()
                return True
        return False

    def continue_parsing(self, line: str) -> bool:
        """Return False as the header only includes one (start) line.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return False as the header comprises of the start line only.
        """
        return False

    def get_log(self) -> dict:
        """Return the current parsed log.

        It returns an empty dictionary if the parser is not initialized yet.
        """
        # If the key Time exists and its value is not an empty string
        if "Time" in self._log and self._log["Time"] != "":
            self._log["Time"] = datetime.datetime.strptime(
                self._log["Time"], self._date_time_format
            )
        return self._log
