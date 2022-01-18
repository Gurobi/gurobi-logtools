import re

from grblogtools.parsers.barrier import BarrierParser
from grblogtools.parsers.simplex import SimplexParser
from grblogtools.parsers.util import typeconvert_groupdict


class ContinuousParser:
    # The pattern indicating the start or the termination of the barrier/simplex
    # in case of solving an MIP. In some cases, the log might only include this one
    # line
    mip_relaxation_pattern = re.compile(
        r"Root relaxation: objective (?P<RelaxObj>[^,]+), (?P<RelaxIterCount>\d+) iterations, (?P<RelaxTime>[^\s]+) seconds"
    )

    def __init__(self):
        """Initialize the Continuous parser."""
        self._barrier_parser = BarrierParser()
        self._simplex_parser = SimplexParser()

        self._summary = {}
        self._progress = []

        self._current_pattern = None

    def start_parsing(self, line: str) -> bool:
        """Return True if the parser should start parsing the future log lines.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line matches the parser start patterns.
        """
        if self._barrier_parser.start_parsing(line):
            self._current_pattern = "barrier"
            return True

        if self._simplex_parser.start_parsing(line):
            self._current_pattern = "simplex"
            return True

        mip_relaxation_match = ContinuousParser.mip_relaxation_pattern.match(line)
        if mip_relaxation_match:
            self._current_pattern = "relaxation"
            self._summary.update(typeconvert_groupdict(mip_relaxation_match))
            return True

        return False

    def continue_parsing(self, line: str) -> bool:
        """Parse the given line.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the parser should continue parsing future log lines.
        """
        mip_relaxation_match = ContinuousParser.mip_relaxation_pattern.match(line)
        if mip_relaxation_match:
            self._summary.update(typeconvert_groupdict(mip_relaxation_match))
            return False

        if self._current_pattern == "barrier":
            matched = self._barrier_parser.continue_parsing(line)
            # If the barrier gets interrupted during the concurrent, switch to
            # the simplex
            if not matched and self._barrier_parser.is_interrupted(line):
                self._current_pattern = "simplex"
            return matched
        if self._current_pattern == "simplex":
            return self._simplex_parser.continue_parsing(line)
        if self._current_pattern == "relaxation":
            return False

        return True

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        self._summary.update(self._barrier_parser.get_summary())
        self._summary.update(self._simplex_parser.get_summary())
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in the continuous method."""
        return (
            self._barrier_parser.get_progress()
            + self._simplex_parser.get_progress()
            + self._progress
        )
