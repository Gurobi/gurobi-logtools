import re
from typing import Union

from gurobi_logtools.parsers.util import typeconvert_groupdict


class NoRelParser:
    norel_log_start = re.compile(r"Starting NoRel heuristic")
    norel_primal_regex = re.compile(
        r"Found heuristic solution:\sobjective\s(?P<Incumbent>[^\s]+)"
    )
    # Order is important in this list as regexes are checked in order
    norel_elapsed = [
        re.compile(
            r"Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s\s\(best\sbound\s(?P<BestBd>[^\s]+)[\)|,.*]"
        ),
        re.compile(r"Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s"),
    ]

    def __init__(self):
        self._progress = []
        self._incumbent = None
        self._started = False

    def get_summary(self) -> dict:
        """Return the summary based on the timeline information.

        It assumes that the best bound is always found in the last line, if exists.
        """
        if not self._progress:
            return {}
        last_log = self._progress[-1]
        result = {"NoRelTime": last_log["Time"]}
        if "BestBd" in last_log:
            result["NoRelBestBd"] = last_log["BestBd"]
        if self._incumbent is not None:
            result["NoRelBestSol"] = self._incumbent
        return result

    def parse(self, line: str) -> dict[str, Union[str, int, float, None]]:
        """Parse the given log line to populate summary and progress data.

        Args:
            line (str): A line in the log file.

        Returns:
            dict[str, Union[str, int, float, None]]: A dictionary containing the parsed data. Empty if the line does not
            match any pattern.
        """
        if not self._started:
            match = self.norel_log_start.match(line)
            if match:
                self._started = True
                return {"Init": "norel"}
            return {}

        match = self.norel_primal_regex.match(line)
        if match:
            self._incumbent = float(match.group("Incumbent"))
            return {"Incumbent": self._incumbent}

        for regex in self.norel_elapsed:
            match = regex.match(line)
            if match:
                entry = typeconvert_groupdict(match)
                if self._incumbent is not None:
                    entry["Incumbent"] = self._incumbent
                self._progress.append(entry)
                return entry.copy()

        return {}

    def get_progress(self) -> list:
        """Return the progress of the norel heuristic."""
        return self._progress
