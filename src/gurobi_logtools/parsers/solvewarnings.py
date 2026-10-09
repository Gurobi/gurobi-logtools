import re
from typing import Any

from gurobi_logtools.parsers.util import Parser, ParseResult


class SolveWarningsParser(Parser):
    warning_pattern: re.Pattern[str] = re.compile(r"^Warning:\s+(.*)$")

    def __init__(self) -> None:
        """Initialize the SolveWarnings parser."""
        self._warnings: dict[str, None] = {}

    def parse(self, line: str) -> ParseResult:
        """Parse the given log line to capture warnings.

        Args:
            line (str): A line in the log file.

        Returns:
            ParseResult: A ParseResult with matched=True if a warning was found.
        """
        match = self.warning_pattern.match(line)
        if match:
            warning_text = match.group(1).strip()
            self._warnings[warning_text] = None
            return ParseResult(matched=True)

        return ParseResult(matched=False)

    def get_summary(self) -> dict[str, Any]:
        """Return the collected warnings in the summary.

        Returns:
            Dict[str, Any]: A dictionary with 'Warnings' key containing
                the list of unique warnings found in the log.
        """
        if not self._warnings:
            return {}

        return {"Warnings": list(self._warnings.keys())}
