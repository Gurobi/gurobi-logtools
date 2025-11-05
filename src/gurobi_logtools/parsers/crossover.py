import re
from typing import Dict

from gurobi_logtools.parsers.util import (
    Parser,
    float_pattern,
    typeconvert_groupdict,
    ParseResult,
)


class CrossoverParser(Parser):
    # The pattern indicating the initialization of the parser
    crossover_start_pattern = re.compile(
        r"Crossover log...",
    )

    # The pattern indicating the crossover progress
    crossover_progress_patterns = [
        re.compile(
            r"\s*(?P<RemainingDPushes>\d+) DPushes remaining with DInf (?P<PushPhaseDInf>[^\s]+)\s+(?P<Time>\d+)s",
        ),
        re.compile(
            r"\s*(?P<RemainingPPushes>\d+) PPushes remaining with PInf (?P<PushPhasePInf>[^\s]+)\s+(?P<Time>\d+)s",
        ),
    ]

    # The pattern indicating the termination of the crossover algorithm
    crossover_push_phase_end_pattern = re.compile(
        r"\s*Push phase complete: Pinf (?P<PushPhasePInf>[^\s]+), Dinf (?P<PushPhaseDInf>[^\s]+)\s+(?P<PushPhaseEndTime>\d+)s",
    )

    # The pattern indicating the termination of the crossover algorithm
    crossover_termination_patterns = [
        re.compile(
            rf"Crossover time: (?P<CrossoverRuntime>{float_pattern}) seconds \((?P<CrossoverWork>{float_pattern}) work units\)",
        ),
        re.compile(
            rf"Crossover time: (?P<CrossoverRuntime>{float_pattern}) seconds",
        ),
    ]

    def __init__(self):
        """Initialize the crossover parser."""
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
            match = CrossoverParser.crossover_start_pattern.match(line)
            if match:
                self._started = True
                return ParseResult(matched=True)
        else:
            for (
                crossover_progress_pattern
            ) in CrossoverParser.crossover_progress_patterns:
                progress_match = crossover_progress_pattern.match(line)
                if progress_match:
                    entry = {"Type": "crossover"}
                    entry.update(typeconvert_groupdict(progress_match))
                    self._progress.append(entry)
                    return ParseResult(entry)

            crossover_push_phase_end_match = (
                CrossoverParser.crossover_push_phase_end_pattern.match(line)
            )
            if crossover_push_phase_end_match:
                parse_result = typeconvert_groupdict(crossover_push_phase_end_match)
                self._summary.update(parse_result)
                return ParseResult(parse_result)

        for (
            crossover_termination_pattern
        ) in CrossoverParser.crossover_termination_patterns:
            crossover_termination_match = crossover_termination_pattern.match(line)
            if crossover_termination_match:
                # In MIP logs, the crossover part is less detailed, consisting only of the termination line
                self._started = True
                parse_result = typeconvert_groupdict(crossover_termination_match)
                self._summary.update(parse_result)
                return ParseResult(parse_result)

        return ParseResult(matched=False)

    def get_summary(self) -> Dict:
        """Return the current parsed summary."""
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in the crossover method."""
        return self._progress
