import re
from typing import Dict, Union

from gurobi_logtools.parsers.barrier import BarrierParser
from gurobi_logtools.parsers.pretree_solutions import PreTreeSolutionParser
from gurobi_logtools.parsers.simplex import SimplexParser
from gurobi_logtools.parsers.util import Parser, typeconvert_groupdict


class ContinuousParser(Parser):
    # The pattern indicating the start or the termination of the barrier/simplex
    # in case of solving a MIP. In some cases, the log might only include this one
    # line
    mip_relaxation_pattern = re.compile(
        r"Root relaxation: objective (?P<RelaxObj>[^,]+), (?P<RelaxIterCount>\d+) iterations, (?P<RelaxTime>[^\s]+) seconds",
    )

    barrier_interruption_pattern = re.compile(
        r"Barrier solve interrupted - model solved by another algorithm",
    )

    continuous_termination_patterns = [
        re.compile(
            r"(?P<SUBOPTIMAL>Sub-optimal termination)(?: - objective (?P<ObjVal>.*))$",
        ),
        re.compile(r"(?P<OPTIMAL>Optimal objective\s+(?P<ObjVal>.*))$"),
    ]

    def __init__(self, pretree_solution_parser: PreTreeSolutionParser):
        """Initialize the Continuous parser."""
        self._barrier_parser = BarrierParser()
        self._simplex_parser = SimplexParser()

        self._summary: Dict[str, Union[str, int, float, None]] = {}

        self._current_pattern: Union[str, None] = None

        self._pretree_solution_parser = pretree_solution_parser

    def parse(self, line: str) -> Dict[str, Union[str, int, float, None]]:
        """Parse the given log line to populate summary and progress data.

        It defers to the simplex and the barrier parsers as needed.

        Args:
            line (str): A line in the log file.

        Returns:
           Dict[str, Union[str, int, float, None]]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.

        """
        if parse_result := self._pretree_solution_parser.parse(line):
            return parse_result.copy()

        mip_relaxation_match = ContinuousParser.mip_relaxation_pattern.match(line)
        if mip_relaxation_match:
            self._current_pattern = "relaxation"
            parse_result = typeconvert_groupdict(mip_relaxation_match)
            self._summary.update(parse_result)
            return parse_result.copy()

        for pattern in ContinuousParser.continuous_termination_patterns:
            match = pattern.match(line)
            if match:
                parse_result = typeconvert_groupdict(match)
                for key, value in parse_result.items():
                    if key in ["OPTIMAL", "SUBOPTIMAL"]:
                        self._summary.update({"Status": key})
                    else:
                        self._summary.update({key: value})
                return parse_result.copy()

        if self._current_pattern is None:
            if parse_result := self._barrier_parser.parse(line):
                self._current_pattern = "barrier"
                return parse_result.copy()
            if parse_result := self._simplex_parser.parse(line):
                self._current_pattern = "simplex"
                return parse_result.copy()

            return {}

        if self._current_pattern == "barrier":
            matched = self._barrier_parser.parse(line)
            # If the barrier gets interrupted during the concurrent or there are
            # extra simplex iterations, switch to simplex
            if not matched and (
                ContinuousParser.barrier_interruption_pattern.match(line)
                or self._simplex_parser.parse(line)
            ):
                parse_result = {"Init": "simplex"}
                self._current_pattern = "simplex"
                return parse_result
            return matched.copy()

        if self._current_pattern == "simplex":
            parse_result = self._simplex_parser.parse(line)
            return parse_result.copy()

        return {}

    def get_summary(self) -> Dict:
        """Return the current parsed summary."""
        self._summary.update(self._barrier_parser.get_summary())
        self._summary.update(self._simplex_parser.get_summary())
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in the continuous method."""
        return self._barrier_parser.get_progress() + self._simplex_parser.get_progress()
