import re

from grblogtools.parsers.barrier import BarrierParser
from grblogtools.parsers.simplex import SimplexParser
from grblogtools.parsers.util import typeconvert_groupdict


class ContinuousParser:
    # The pattern indicating the start or the termination of the barrier/simplex
    # in case of solving a MIP. In some cases, the log might only include this one
    # line
    mip_relaxation_pattern = re.compile(
        r"Root relaxation: objective (?P<RelaxObj>[^,]+), (?P<RelaxIterCount>\d+) iterations, (?P<RelaxTime>[^\s]+) seconds"
    )

    barrier_interruption_pattern = re.compile(
        r"Barrier solve interrupted - model solved by another algorithm"
    )

    continuous_termination_patterns = [
        re.compile(
            r"(?P<SUBOPTIMAL>Sub-optimal termination)(?: - objective (?P<ObjVal>.*))$"
        ),
        re.compile(r"(?P<OPTIMAL>Optimal objective\s+(?P<ObjVal>.*))$"),
    ]

    def __init__(self):
        """Initialize the Continuous parser."""
        self._barrier_parser = BarrierParser()
        self._simplex_parser = SimplexParser()

        self._summary = {}

        self._current_pattern = None

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary and progress data.

        It defers to the simplex and the barrier parsers as needed.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        mip_relaxation_match = ContinuousParser.mip_relaxation_pattern.match(line)
        if mip_relaxation_match:
            self._current_pattern = "relaxation"
            self._summary.update(typeconvert_groupdict(mip_relaxation_match))
            return True

        for pattern in ContinuousParser.continuous_termination_patterns:
            match = pattern.match(line)
            if match:
                for key, value in typeconvert_groupdict(match).items():
                    if key in ["OPTIMAL", "SUBOPTIMAL"]:
                        self._summary.update({"Status": key})
                    else:
                        self._summary.update({key: value})
                return True

        if self._current_pattern is None:
            if self._barrier_parser.parse(line):
                self._current_pattern = "barrier"
                return True
            if self._simplex_parser.parse(line):
                self._current_pattern = "simplex"
                return True

            return False

        if self._current_pattern == "barrier":
            matched = self._barrier_parser.parse(line)
            # If the barrier gets interrupted during the concurrent or there are
            # extra simplex iterations, switch to simplex
            if not matched and (
                ContinuousParser.barrier_interruption_pattern.match(line)
                or self._simplex_parser.parse(line)
            ):
                self._current_pattern = "simplex"
                return True
            return matched

        if self._current_pattern == "simplex":
            match = self._simplex_parser.parse(line)
            return match

        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        self._summary.update(self._barrier_parser.get_summary())
        self._summary.update(self._simplex_parser.get_summary())
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in the continuous method."""
        return self._barrier_parser.get_progress() + self._simplex_parser.get_progress()
