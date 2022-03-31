import re

from grblogtools.parsers.util import convert_data_types, typeconvert_groupdict


class HeaderParser:
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
        re.compile(
            r"Gurobi Compute Server Worker version (?P<Version>\d{1,2}\.[^\s]+) build (.*) \((?P<Platform>[^\)]+)\)$"
        ),
        re.compile(r"Compute Server job ID: (?P<JobID>.*)$"),
        re.compile(r"Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
    ]

    header_other_patterns = [
        re.compile(r"Read (MPS|LP) format model from file (?P<ModelFilePath>.*)$"),
        re.compile(r"Reading time = (?P<ReadingTime>[\d\.]+) seconds"),
        re.compile(
            r"Thread count: (?P<PhysicalCores>\d+) physical cores, (?P<LogicalProcessors>\d+) logical processors, using up to (?P<Threads>\d+) threads"
        ),
        re.compile(
            r"(?P<ModelName>.*): (?P<Rows>\d+) rows, (?P<Columns>\d+) columns, (?P<Nonzeros>\d+) nonzeros"
        ),
    ]

    # Special case for parameter changes
    parameter_change_pattern = re.compile(
        r"Set parameter (?P<ParamName>[^\s]+) to value (?P<ParamValue>.*)$"
    )

    def __init__(self):
        """Initialize the Header parser.

        Parameters are stored separately from the summary data as they are
        handled differently in the final output.
        """
        self._summary = {}
        self._parameters = {}
        self._started = False

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        match = HeaderParser.parameter_change_pattern.match(line)
        if match:
            self._parameters[match.group("ParamName")] = convert_data_types(
                match.group("ParamValue")
            )
            return True

        for pattern in HeaderParser.header_start_patterns:
            match = pattern.match(line)
            if match:
                self._started = True
                self._summary.update(typeconvert_groupdict(match))
                return True

        if self._started:
            for pattern in HeaderParser.header_other_patterns:
                match = pattern.match(line)
                if match:
                    self._summary.update(typeconvert_groupdict(match))
                    return True

        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return self._summary

    def get_parameters(self) -> dict:
        """Return all changed parameters detected in the header."""
        return self._parameters
