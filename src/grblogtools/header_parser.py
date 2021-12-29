import re

from grblogtools.helpers import convert_data_types


class HeaderParser:
    # Possible patterns indicating the initialization of the parser
    header_start_patterns = [
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
        """Initialize the Header parser.

        The HeaderParser only includes one line.
        """
        self._log = {}

    def start_parsing(self, line: str) -> bool:
        """Return True if the parser should start parsing the future log lines.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line matches one of the parser's start
                patterns.
        """
        for possible_start in HeaderParser.header_start_patterns:
            match = possible_start.match(line)
            if match:
                # The start line encodes information that should to be stored
                self._log.update(
                    {
                        sub_match: convert_data_types(value)
                        for sub_match, value in match.groupdict().items()
                    }
                )
                return True
        return False

    def continue_parsing(self, line: str) -> bool:
        """Parse the given line.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True.
        """
        return True

    def get_log(self) -> dict:
        """Return the current parsed log.

        It returns an empty dictionary if the parser is not initialized yet.
        """
        return self._log
