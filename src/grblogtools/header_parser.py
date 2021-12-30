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
        re.compile("Set parameter (?P<ParamName>[^\s]+) to value (?P<ParamValue>.*)$"),
        re.compile("Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
    ]

    # Possible intermediate patterns to be parsed
    header_intermediate_patterns = [
        re.compile("Set parameter (?P<ParamName>[^\s]+) to value (?P<ParamValue>.*)$"),
        re.compile(
            "Gurobi Compute Server Worker version (?P<Version>\d{1,2}\.[^\s]+) build (.*) \((?P<Platform>[^\)]+)\)$"
        ),
        re.compile("Compute Server job ID: (?P<JobID>.*)$"),
        re.compile("Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
        re.compile("Read (MPS|LP) format model from file (?P<ModelFilePath>.*)$"),
        re.compile("Reading time = (?P<ReadingTime>[\d\.]+) seconds"),
        re.compile(
            "Thread count was (?P<Threads>\d+) \(of (?P<Cores>\d+) available processors\)"
        ),
        re.compile(
            "Thread count: (?P<PhysicalCores>\d+) physical cores, (?P<LogicalProcessors>\d+) logical processors, using up to (?P<Threads>\d+) threads"
        ),
    ]

    def __init__(self):
        """Initialize the Header parser."""
        self._summary = {}

    def _update_summary(self, match):
        dict_ = match.groupdict()
        if "ParamName" in dict_:
            # Add the keyword "Param" at the beginning of the ParamName to make
            # it clear it is a parameter
            self._summary.update(
                {"Param" + dict_["ParamName"]: convert_data_types(dict_["ParamValue"])}
            )
        else:
            self._summary.update(
                {
                    sub_match: convert_data_types(value)
                    for sub_match, value in dict_.items()
                }
            )

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
                # The start line encodes information that should be stored
                self._update_summary(match)
                return True
        return False

    def continue_parsing(self, line: str) -> bool:
        """Parse the given line.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True.
        """
        if not line.strip():
            return True

        for pattern in HeaderParser.header_intermediate_patterns:
            match = pattern.match(line)
            if match:
                self._update_summary(match)
                break
        return True

    def get_summary(self) -> dict:
        """Return the current parsed summary.

        It returns an empty dictionary if the parser is not initialized yet.
        """
        return self._summary
