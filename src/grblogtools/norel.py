import re
from typing import List, Dict, Any

from .parser_helpers import ParserLinesMixin


class NoRelParser(ParserLinesMixin):
    """
    Methods:
        - log_start(line) -> parse a string, returing true if this string
          indicates the start of the norel section
        - parse(line) -> parse a string, return true if this parser should
          continue receiving future log lines

    Attributes:
        - summary -> dict of summary data (total time, best bound, best solution)
        - timeline -> list of dicts for log timeline entries (incumbent, bound, time)
        - ignored_lines -> count of lines after the log start which were recieved
          but not parsed
    """

    norel_log_start = re.compile(r"Starting NoRel heuristic")
    norel_primal_regex = re.compile(
        r"Found heuristic solution:\sobjective\s(?P<Incumbent>[^\s]+)"
    )
    norel_elapsed_time = re.compile(
        r"Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s"
    )
    norel_elapsed_bound = re.compile(
        r"Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s\s\(best\sbound\s(?P<BestBd>[^\s]+)\)"
    )

    def __init__(self):
        super().__init__()
        self.summary: Dict[str, Any] = {}
        self.timeline: List[Dict[str, Any]] = []
        self.ignored_lines: int = 0
        self._incumbent = None

    def log_start(self, line: str) -> bool:
        """Return true if the line indicates the start of the norel section."""
        return bool(self.norel_log_start.match(line))

    def _timeline_entry(self, arg):
        """ Type convert timeline data and include incumbent in the log record
        if there is one. """
        entry = {k: float(v) for k, v in arg.items()}
        if self._incumbent is not None:
            entry["Incumbent"] = self._incumbent
        self.timeline.append(entry)

    def parse(self, line: str) -> bool:
        """Parse a log line to populate data. Since the incumbent and time/bound
        come from separate lines, we need to retain a parsed incumbent value for
        recording against the next timestamp.

        Always returns true, since NoRel does not have an end line to speak of,
        except an empty line which does not seem like a great idea to rely on.
        """
        if match := self.norel_primal_regex.match(line):
            self.summary["NoRelBestSolution"] = float(match.group("Incumbent"))
            # store incumbent info to combine with the next timing line
            self._incumbent = float(match.group("Incumbent"))
        elif match := self.norel_elapsed_bound.match(line):
            self.summary["NoRelBestBound"] = float(match.group("BestBd"))
            self.summary["NoRelTime"] = float(match.group("Time"))
            self._timeline_entry(match.groupdict())
        elif match := self.norel_elapsed_time.match(line):
            self.summary["NoRelTime"] = float(match.group("Time"))
            self._timeline_entry(match.groupdict())
        else:
            if line.strip():
                self.ignored_lines += 1
        return True  # continue
