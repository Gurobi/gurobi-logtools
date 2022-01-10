import re

from grblogtools.helpers import convert_data_types, typeconvert_groupdict


class HeaderParser:
    # Possible patterns indicating the initialization of the parser
    header_start_patterns = [
        re.compile(
            r"Gurobi (?P<Version>\d{1,2}\.[^\s]+) \((?P<Platform>[^\)]+)\) logging started (?P<Time>.*)$"
        ),
        re.compile(r"Logging started (?P<Time>.*)$"),
        re.compile(
            r"Gurobi Compute Server Worker version (?P<Version>\d{1,2}\.[^\s]+) build (.*) \((?P<Platform>[^\)]+)\)$"
        ),
        re.compile(r"Compute Server job ID: (?P<JobID>.*)$"),
        re.compile(r"Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
    ]

    # Possible intermediate patterns to be parsed
    header_intermediate_patterns = [
        re.compile(
            r"Gurobi Compute Server Worker version (?P<Version>\d{1,2}\.[^\s]+) build (.*) \((?P<Platform>[^\)]+)\)$"
        ),
        re.compile(r"Compute Server job ID: (?P<JobID>.*)$"),
        re.compile(r"Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
        re.compile(r"Read (MPS|LP) format model from file (?P<ModelFilePath>.*)$"),
        re.compile(r"Reading time = (?P<ReadingTime>[\d\.]+) seconds"),
        re.compile(
            r"Thread count was (?P<Threads>\d+) \(of (?P<Cores>\d+) available processors\)"
        ),
        re.compile(
            r"Thread count: (?P<PhysicalCores>\d+) physical cores, (?P<LogicalProcessors>\d+) logical processors, using up to (?P<Threads>\d+) threads"
        ),
    ]

    # Special case for parameter changes
    parameter_change_pattern = re.compile(
        r"Set parameter (?P<ParamName>[^\s]+) to value (?P<ParamValue>.*)$"
    )

    def __init__(self):
        """Initialize the Header parser.

        Parameters are stored separately from the summary data as they are
        handled differently in the final output."""
        self._summary = {}
        self._parameters = {}

    def check_parameter_change(self, line: str) -> bool:
        """Return True and store the changed value if a parameter is changed.

        Args:
            line (str): A line in the log file

        Returns:
            bool: return True if the line indicated a parameter change
        """
        match = HeaderParser.parameter_change_pattern.match(line)
        if match:
            self._parameters[match.group("ParamName")] = convert_data_types(
                match.group("ParamValue")
            )
            return True
        return False

    def start_parsing(self, line: str) -> bool:
        """Return True if the parser should start parsing the future log lines.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line matches one of the parser's start
                patterns.
        """
        if self.check_parameter_change(line):
            return True
        for possible_start in HeaderParser.header_start_patterns:
            match = possible_start.match(line)
            if match:
                # The start line encodes information that should be stored
                self._summary.update(typeconvert_groupdict(match))
                return True
        return False

    def continue_parsing(self, line: str) -> bool:
        """Parse the given line.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the line was match by any pattern.
        """

        if self.check_parameter_change(line):
            return True

        for pattern in HeaderParser.header_intermediate_patterns:
            match = pattern.match(line)
            if match:
                self._summary.update(typeconvert_groupdict(match))
                return True

        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary.

        It returns an empty dictionary if the parser is not initialized yet.
        """
        return self._summary

    def get_parameters(self) -> dict:
        """Return all changed parameters detected in the header."""
        return self._parameters
