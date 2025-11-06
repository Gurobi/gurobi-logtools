import re
from typing import Dict

from gurobi_logtools.parsers.util import (
    Parser,
    float_pattern,
    typeconvert_groupdict,
    ParseResult,
)


class PdhgParser(Parser):
    # The pattern indicating the initialization of the parser
    pdhg_start_pattern = re.compile(
        r"Start PDHG using (?P<PdhgThreads>\d+) threads",
    )

    # The pattern indicating the pdhg progress
    pdhg_progress_pattern = re.compile(
        r"\s*(?P<Iteration>\d+)(?P<Indicator>\s|\*)\s+(?P<PObj>[^\s]+)\s+(?P<DObj>[^\s]+)\s+(?P<PRes>[^\s]+)\s+(?P<DRes>[^\s]+)\s+(?P<Compl>[^\s]+)\s+(?P<Time>\d+)s",
    )

    # The pattern indicating the termination of the pdhg algorithm
    pdhg_termination_patterns = [
        re.compile(
            rf"PDHG solved model in (?P<PdhgIterCount>[^\s]+) iterations and (?P<Runtime>{float_pattern}) seconds \((?P<Work>{float_pattern}) work units\)",
        ),
        re.compile(
            rf"PDHG performed (?P<PdhgIterCount>\d+) iterations in (?P<Runtime>{float_pattern}) seconds \((?P<Work>{float_pattern}) work units\)",
        ),
        re.compile(
            r"PDHG solved model in (?P<PdhgIterCount>[^\s]+) iterations and (?P<Runtime>[^\s]+) seconds",
        ),
        re.compile(
            r"PDHG performed (?P<PdhgIterCount>\d+) iterations in (?P<Runtime>[^\s]+) seconds",
        ),
    ]

    def __init__(self):
        """Initialize the pdhg parser."""
        self._summary = {}
        self._progress = []
        self._started = False

    def parse(self, line: str) -> ParseResult:
        """Parse the given log line to populate summary and progress data.

        Args:
            line (str): A line in the log file.

        Returns:
          Dict[str, Any]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.

        """
        if not self._started:
            start_match = PdhgParser.pdhg_start_pattern.match(line)
            if start_match:
                self._started = True
                parse_result = typeconvert_groupdict(start_match)
                self._summary.update(parse_result)
                return ParseResult(parse_result)
            return ParseResult(matched=False)

        progress_match = PdhgParser.pdhg_progress_pattern.match(line)
        if progress_match:
            entry = {"Type": "pdhg"}
            entry.update(typeconvert_groupdict(progress_match))
            self._progress.append(entry)
            return ParseResult(entry)

        for pdhg_termination_pattern in PdhgParser.pdhg_termination_patterns:
            pdhg_termination_match = pdhg_termination_pattern.match(line)
            if pdhg_termination_match:
                parse_result = typeconvert_groupdict(pdhg_termination_match)
                self._summary.update(parse_result)
                return ParseResult(parse_result)

        return ParseResult(matched=False)

    def get_summary(self) -> Dict:
        """Return the current parsed summary."""
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in the PDHG method."""
        return self._progress
