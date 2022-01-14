import re

from grblogtools.parsers.util import typeconvert_groupdict


class BarrierParser:
    # The pattern indicating the initialization of the parser
    barrier_start_pattern = re.compile(
        r"Iter(\s+)Primal(\s+)Dual(\s+)Primal(\s+)Dual(\s+)Compl(\s+)Time"
    )

    # The pattern indicating the barrier progress
    barrier_progress_pattern = re.compile(
        r"\s*(?P<Iteration>\d+)(?P<Indicator>\s|\*)\s+(?P<PObj>[^\s]+)\s+(?P<DObj>[^\s]+)\s+(?P<PRes>[^\s]+)\s+(?P<DRes>[^\s]+)\s+(?P<Compl>[^\s]+)\s+(?P<Time>\d+)s"
    )

    # The pattern indicating the crossover
    barrier_crossover_pattern = re.compile(
        r"\s*Push phase complete: Pinf (?P<PushPhasePInf>[^\s]+), Dinf (?P<PushPhaseDInf>[^\s]+)\s+(?P<PushPhaseEndTime>\d+)s"
    )

    # The pattern indicating the termination of the barrier algorithm
    barrier_termination_patterns = [
        re.compile(
            r"Barrier solved model in (?P<BarIterCount>[^\s]+) iterations and (?P<Runtime>[^\s]+) seconds"
        ),
        re.compile(
            r"Barrier performed (?P<BarIterCount>\d+) iterations in (?P<Runtime>[^\s]+) seconds"
        ),
    ]

    def __init__(self):
        """Initialize the Barrier parser."""
        self._summary = {}
        self._progress = []

    def start_parsing(self, line: str) -> bool:
        """Return True if the parser should start parsing the future log lines.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line matches the parser start patterns.
        """
        if BarrierParser.barrier_start_pattern.match(line):
            return True
        return False

    def continue_parsing(self, line: str) -> bool:
        """Parse the given line.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the parser should continue parsing future log lines.
        """
        progress_match = BarrierParser.barrier_progress_pattern.match(line)
        if progress_match:
            self._progress.append(typeconvert_groupdict(progress_match))
            return True

        for barrier_termination_pattern in BarrierParser.barrier_termination_patterns:
            barrier_termination_match = barrier_termination_pattern.match(line)
            if barrier_termination_match:
                self._summary.update(typeconvert_groupdict(barrier_termination_match))
                return True

        crossover_match = BarrierParser.barrier_crossover_pattern.match(line)
        if crossover_match:
            self._summary.update(typeconvert_groupdict(crossover_match))
            return True

        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in barrier method."""
        return self._progress
