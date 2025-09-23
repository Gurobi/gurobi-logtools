import re
from typing import Any, Dict

from gurobi_logtools.parsers.util import (
    ParseResult,
    Parser,
    convert_data_types,
    typeconvert_groupdict,
)


class NonDefaultParamsParser:
    start_pattern = re.compile("Non-default parameters:")
    param_change_pattern = re.compile(r"^(?P<ParamName>\w+)\s+(?P<ParamValue>.+)$")
    blank_line = re.compile("^$")

    def __init__(self):
        self._summary: Dict[str, Any] = {}
        self._parameters = {}
        self._active = False

    def parse(self, line: str):
        if not self._active:
            if self.start_pattern.match(line):
                self._active = True
                return ParseResult(matched=True)
            return ParseResult(matched=False)
        elif self.blank_line.match(line):
            self._active = False
            return ParseResult(matched=True)
        else:
            match = self.param_change_pattern.match(line)
            if match:
                self._parameters[match.group("ParamName")] = convert_data_types(
                    match.group("ParamValue"),
                )
                return ParseResult(self._parameters)
            return ParseResult(matched=False)


class HeaderParser(Parser):
    header_start_patterns = [
        re.compile(
            r"Gurobi (?P<Version>\d{1,2}\.[^\s]+) \((?P<Platform>[^\)]+)\) logging started (?P<Time>.*)$",
        ),
        re.compile(r"Logging started (?P<Time>.*)$"),
        re.compile(
            r"Gurobi Compute Server Worker version (?P<Version>\d{1,2}\.[^\s]+) build (.*) \((?P<Platform>[^\)]+)\)$",
        ),
        re.compile(r"Compute Server job ID: (?P<JobID>.*)$"),
        re.compile(r"Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
        re.compile(
            r"Gurobi Compute Server Worker version (?P<Version>\d{1,2}\.[^\s]+) build (.*) \((?P<Platform>[^\)]+)\)$",
        ),
        re.compile(r"Compute Server job ID: (?P<JobID>.*)$"),
        re.compile(r"Gurobi Optimizer version (?P<Version>\d{1,2}\.[^\s]+)"),
        re.compile(r"Solving model (?P<ModelName>.*)$"),
    ]

    header_other_patterns = [
        re.compile(r"Read (MPS|LP) format model from file (?P<ModelFilePath>.*)$"),
        re.compile(r"Reading time = (?P<ReadingTime>[\d\.]+) seconds"),
        re.compile(
            r"Thread count: (?P<PhysicalCores>\d+) physical cores, (?P<LogicalProcessors>\d+) logical processors, using up to (?P<Threads>\d+) threads",
        ),
        re.compile(
            r"(?P<ModelName>.*): (?P<Rows>\d+) rows, (?P<Columns>\d+) columns, (?P<Nonzeros>\d+) nonzeros",
        ),
    ]

    # Special case for parameter changes
    parameter_change_pattern = re.compile(
        r"Set parameter (?P<ParamName>[^\s]+) to value (?P<ParamValue>.*)$",
    )

    def __init__(self):
        """Initialize the Header parser.

        Parameters are stored separately from the summary data as they are
        handled differently in the final output.
        """
        self._summary: Dict[str, Any] = {}
        self._parameters = {}
        self._started = False
        self.nondefault_params_parser = NonDefaultParamsParser()

    def parse(self, line: str) -> ParseResult:
        """Parse the given log line to populate summary data.

        Args:
            line (str): A line in the log file.

        Returns:
           Dict[str, Any]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.

        """
        match = self.parameter_change_pattern.match(line)
        if match:
            self._parameters[match.group("ParamName")] = convert_data_types(
                match.group("ParamValue"),
            )
            return ParseResult(self._parameters)

        for pattern in self.header_start_patterns:
            match = pattern.match(line)
            if match:
                self._started = True
                parse_result = typeconvert_groupdict(match)
                self._summary.update(parse_result)
                return ParseResult(parse_result)

        if self._started:
            parse_result_ = self.nondefault_params_parser.parse(line)
            if parse_result_:
                return parse_result_
            for pattern in self.header_other_patterns:
                match = pattern.match(line)
                if match:
                    parse_result = typeconvert_groupdict(match)
                    self._summary.update(parse_result)
                    return ParseResult(parse_result)

        return ParseResult(matched=False)

    def get_summary(self) -> Dict:
        """Return the current parsed summary."""
        summary = self._summary.copy()
        summary["ChangedParams"] = self.changed_params()
        return summary

    def get_parameters(self) -> Dict:
        """Return all changed parameters detected in the header."""
        return {**self._parameters, **self.nondefault_params_parser._parameters}

    def changed_params(self) -> Dict:
        omit_params = {"Seed", "LogFile"}
        return {k: v for k, v in self.get_parameters().items() if k not in omit_params}

    def _make_file_name(self) -> str:
        paramstr = "".join(f"{k}{v}-" for k, v in sorted(self.changed_params().items()))
        version = self._summary.get("Version", "unknown").replace(".", "") + "-"
        model_name = self._summary.get("ModelName", "unknown")
        seed = self.get_parameters().get("Seed", 0)
        return f"{version}{paramstr}{model_name}-{seed}.log"
