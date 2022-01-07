import re

from grblogtools.helpers import typeconvert_groupdict


class TerminationParser:

    patterns = [
        re.compile(r"Solution count (?P<SolCount>\d+)"),
        re.compile(
            r"Best objective (?P<ObjVal>[^,]+), best bound (?P<ObjBound>[^,]+), gap (?P<MIPGap>.*)$"
        ),
        re.compile(
            r"Thread count was (?P<Threads>\d+) \(of (?P<Cores>\d+) available processors\)"
        ),
    ]

    re_termination_status = {
        "OPTIMAL": re.compile(
            r"(?P<OPTIMAL>Optimal solution found)(?: \(tolerance .*\))"
        ),
        "TIME_LIMIT": re.compile(r"(?P<TIME_LIMIT>Time limit reached)"),
    }

    def __init__(self):
        self._summary = {}

    def _parse(self, line: str) -> bool:
        """No specific section start, so start and continue are the same."""
        for pattern in self.patterns:
            match = pattern.match(line)
            if match:
                self._summary.update(typeconvert_groupdict(match))
                return True
        for status, pattern in self.re_termination_status.items():
            match = pattern.match(line)
            if match:
                self._summary["Status"] = status
                return True
        return False

    def start_parsing(self, line: str) -> bool:
        return self._parse(line)

    def continue_parsing(self, line: str) -> bool:
        return self._parse(line)

    def get_summary(self) -> dict:
        return self._summary
