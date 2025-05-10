import re

from gurobi_logtools.parsers.util import float_pattern, typeconvert_groupdict


class SimplexParser:
    # The pattern indicating the initialization of the parser
    simplex_start_pattern = re.compile(
        r"Iteration(\s+)Objective(\s+)Primal Inf.(\s+)Dual Inf.(\s+)Time"
    )

    # The pattern indicating the simplex progress
    simplex_progress_pattern = re.compile(
        r"\s*(?P<Iteration>\d+)\s+(?P<Objective>[^\s]+)\s+(?P<PInf>[^\s]+)\s+(?P<DInf>[^\s]+)\s+(?P<Time>\d+)s"
    )

    # The pattern indicating the termination of the simplex method
    simplex_termination_patterns = [
        re.compile(
            r"(Solved|Stopped) in (?P<IterCount>[^\s]+) iterations and (?P<Runtime>{0}) seconds \((?P<Work>{0}) work units\)".format(
                float_pattern
            )
        ),
        re.compile(
            r"(Solved|Stopped) in (?P<IterCount>[^\s]+) iterations and (?P<Runtime>[^\s]+) seconds"
        ),
    ]

    def __init__(self):
        """Initialize the Simplex parser."""
        self._summary = {}
        self._progress = []
        self._started = False

    def parse(self, line: str) -> dict[str, str | float | int | None]:
        """Parse the given log line to populate summary and progress data.

        Args:
            line (str): A line in the log file.

        Returns:
            dict[str, str | None | int | float]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.
        """
        # Check this first since the termination line might appear
        # without any progress log in the concurrent case.

        for regex in self.simplex_termination_patterns:
            match = regex.match(line)
            if match:
                parse_result = typeconvert_groupdict(match)
                self._summary.update(parse_result)
                return parse_result.copy()

        if not self._started:
            match = SimplexParser.simplex_start_pattern.match(line)
            if match:
                self._started = True
                return {"Init": "simplex"}
            return {}

        progress_match = SimplexParser.simplex_progress_pattern.match(line)
        if progress_match:
            parse_result = {"Type": "simplex"}
            parse_result.update(typeconvert_groupdict(progress_match))
            self._progress.append(parse_result)
            return parse_result.copy()

        return {}

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in simplex method if exists."""
        return self._progress
