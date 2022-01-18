import re
from typing import Any, Dict, List

from grblogtools.parsers.util import typeconvert_groupdict


class NoRelParser:
    norel_log_start = re.compile(r"Starting NoRel heuristic")
    norel_primal_regex = re.compile(
        r"Found heuristic solution:\sobjective\s(?P<Incumbent>[^\s]+)"
    )
    # Order is important in this list as regexes are checked in order.
    norel_elapsed = [
        re.compile(
            r"Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s\s\(best\sbound\s(?P<BestBd>[^\s]+)\)"
        ),
        re.compile(r"Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s"),
    ]

    def __init__(self):
        self.timeline: List[Dict[str, Any]] = []
        self._incumbent = None

    def get_summary(self) -> Dict[str, Any]:
        """Return summary dataframe based on the timeline information. Assumes
        that the best bound is always found in the last line (if one was found
        at all)."""
        if not self.timeline:
            return {}
        last_log = self.timeline[-1]
        result = {"NoRelTime": last_log["Time"]}
        if "BestBd" in last_log:
            result["NoRelBestBd"] = last_log["BestBd"]
        if self._incumbent is not None:
            result["NoRelBestSol"] = self._incumbent
        return result

    def start_parsing(self, line: str) -> bool:
        """Return true if the line indicates the start of the norel section."""
        return bool(self.norel_log_start.match(line))

    def continue_parsing(self, line: str) -> bool:
        """Parse a log line to populate data.

        Since the incumbent and time/bound come from separate lines, we need to
        retain a parsed incumbent value for recording against the next timestamp.

        Always returns true, since NoRel does not have an end line to speak of,
        except an empty line which does not seem like a great idea to rely on.
        """
        match = self.norel_primal_regex.match(line)
        if match:
            self._incumbent = float(match.group("Incumbent"))
            return True
        for regex in self.norel_elapsed:
            match = regex.match(line)
            if match:
                entry = typeconvert_groupdict(match)
                if self._incumbent is not None:
                    entry["Incumbent"] = self._incumbent
                self.timeline.append(entry)
                return True
        return False

    def get_progress(self) -> list:
        """Return the progress of the norel heuristic."""
        return self.timeline
