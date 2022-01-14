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

    def start_parsing(self, line: str) -> bool:
        """Return True if the parser should start parsing the future log lines.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line matches the parser start patterns.
        """
        if SimplexParser.simplex_start_pattern.match(line):
            return True
        return False

    def continue_parsing(self, line: str) -> bool:
        """Parse the given line.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the parser should continue parsing future log lines.
        """
        progress_match = SimplexParser.simplex_progress_pattern.match(line)
        if progress_match:
            self._progress.append(typeconvert_groupdict(progress_match))
            return True

        simplex_termination_pattern = SimplexParser.simplex_termination_pattern.match(
            line
        )
        if simplex_termination_pattern:
            # This line does not necessary indicate that there is no future relevant
            # log lines
            self._summary.update(typeconvert_groupdict(simplex_termination_pattern))
            return True

        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in simplex method if exists."""
        return self._progress
