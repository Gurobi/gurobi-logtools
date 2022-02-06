import re

from grblogtools.parsers.util import typeconvert_groupdict


class BarrierParser:
    # The pattern indicating the initialization of the parser
    barrier_start_pattern = re.compile(
        r"Iter(\s+)Primal(\s+)Dual(\s+)Primal(\s+)Dual(\s+)Compl(\s+)Time"
    )

    barrier_ordering_pattern = re.compile(r"Ordering time: (?P<OrderingTime>[\d\.]+)s")

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
        self._started = False

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary and progress data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        barrier_ordering_match = BarrierParser.barrier_ordering_pattern.match(line)
        if barrier_ordering_match:
            self._summary.update(typeconvert_groupdict(barrier_ordering_match))
            return True

        if not self._started:
            match = BarrierParser.barrier_start_pattern.match(line)
            if match:
                self._started = True
                return True
            return False

        progress_match = BarrierParser.barrier_progress_pattern.match(line)
        if progress_match:
            entry = {"Type": "barrier"}
            entry.update(typeconvert_groupdict(progress_match))
            self._progress.append(entry)
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
        """Return the detailed progress in the barrier method."""
        return self._progress
