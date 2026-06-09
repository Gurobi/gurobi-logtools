import re
from typing import Dict

from gurobi_logtools.parsers.util import (
    Parser,
    float_pattern,
    typeconvert_groupdict,
    ParseResult,
)


class NonLinearBarrierParser(Parser):
    # The pattern indicating the initialization of the parser
    nlbarrier_start_patterns = [
        re.compile(
            r"Iter(\s+)Objective(\s+)Primal(\s+)Dual(\s+)Compl(\s+)Step(\s+)Time",
        )
    ]

    # The pattern indicating the barrier progress
    nlbarrier_progress_patterns = [
        re.compile(
            r"\s*(?P<Iteration>\d+)(?P<Indicator>\s|\*)\s+(?P<Objective>[^\s]+)\s+(?P<PRes>[^\s]+)\s+(?P<DRes>[^\s]+)\s+(?P<Compl>[^\s]+)\s+(?P<Step>[^\s]+)\s+(?P<Time>\d+)s",
        )
    ]

    # The pattern indicating the termination of the barrier algorithm
    nlbarrier_termination_patterns = [
        re.compile(
            rf"NL barrier solved model in (?P<NLBarIterCount>[^\s]+) iterations and (?P<Runtime>{float_pattern}) seconds \((?P<Work>{float_pattern}) work units\)",
        ),
        re.compile(
            rf"NL barrier performed (?P<NLBarIterCount>\d+) iterations in (?P<Runtime>{float_pattern}) seconds \((?P<Work>{float_pattern}) work units\)",
        ),
    ]

    def __init__(self):
        """Initialize the Nonlinear Barrier parser."""
        self._summary = {}
        self._progress = []
        self._started = False

    def _handle_repeat_barrier_solve(self, parse_result: dict):
        # GH43 (dev)
        key = "BarIterCount"
        if key in self._summary.keys():
            self._summary[key] += float(parse_result.pop(key, 0))
        return parse_result

    def parse(self, line: str) -> ParseResult:
        """Parse the given log line to populate summary and progress data.

        Args:
            line (str): A line in the log file.

        Returns:
          Dict[str, Any]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.

        """

        if not self._started:
            for pattern in self.nlbarrier_start_patterns:
                match = pattern.match(line)
                if match:
                    self._started = True
                    return ParseResult(matched=True)
            return ParseResult(matched=False)

        for pattern in self.nlbarrier_progress_patterns:
            progress_match = pattern.match(line)
            if progress_match:
                entry = {"Type": "nlbarrier"}
                entry.update(typeconvert_groupdict(progress_match))
                self._progress.append(entry)
                return ParseResult(entry)

        for (
            nlbarrier_termination_pattern
        ) in NonLinearBarrierParser.nlbarrier_termination_patterns:
            nlbarrier_termination_match = nlbarrier_termination_pattern.match(line)
            if nlbarrier_termination_match:
                parse_result = typeconvert_groupdict(nlbarrier_termination_match)
                self._handle_repeat_barrier_solve(parse_result)  # modifies parse_result
                self._summary.update(parse_result)
                return ParseResult(parse_result)

        return ParseResult(matched=False)

    def get_summary(self) -> Dict:
        """Return the current parsed summary."""
        return self._summary

    def get_progress(self) -> list:
        """Return the detailed progress in the barrier method."""
        return self._progress
