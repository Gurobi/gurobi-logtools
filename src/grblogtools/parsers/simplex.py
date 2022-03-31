import re

from grblogtools.parsers.util import typeconvert_groupdict


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
    simplex_termination_pattern = re.compile(
        r"(Solved|Stopped) in (?P<IterCount>[^\s]+) iterations and (?P<Runtime>[^\s]+) seconds"
    )

    def __init__(self):
        """Initialize the Simplex parser."""
        self._summary = {}
        self._progress = []
        self._started = False

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary and progress data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        # Check this first since the termination line might appear
        # without any progress log in the concurrent case.
        match = SimplexParser.simplex_termination_pattern.match(line)
        if match:
            self._summary.update(typeconvert_groupdict(match))
            return True

        if not self._started:
            match = SimplexParser.simplex_start_pattern.match(line)
            if match:
                self._started = True
                return True
            return False

        progress_match = SimplexParser.simplex_progress_pattern.match(line)
        if progress_match:
            entry = {"Type": "simplex"}
            entry.update(typeconvert_groupdict(progress_match))
            self._progress.append(entry)
            return True

        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in simplex method if exists."""
        return self._progress
