import re
from typing import Any, Dict

from gurobi_logtools.parsers.util import Parser, typeconvert_groupdict


class PreTreeSolutionParser(Parser):
    pretree_solution_regex = re.compile(
        r"Found heuristic solution:\sobjective\s(?P<Incumbent>[^\s]+)",
    )

    def __init__(self):
        """Initialize the pre-tree solutions parser (does not include NoRel solutions).

        The PresolveParser extends beyond the lines associated with the presolved
        model. Specifically, it includes information for all lines appearing between
        the HeaderParser and the NoRelParser or the RelaxationParser.
        """
        self._progress = []
        self._summary: Dict[str, Any] = {}
        # self._started = False

    def parse(self, line: str) -> Dict[str, Any]:
        """Parse the given log line to populate summary data.

        Args:
            line (str): A line in the log file.

        Returns:
           Dict[str, Any]: A dictionary containing the parsed data.
        """
        match = self.pretree_solution_regex.match(line)
        if match:
            parse_result = typeconvert_groupdict(match)
            self._progress.append(parse_result)
            return parse_result.copy()
        return {}

    def get_summary(self) -> Dict:
        """Return the current parsed summary."""
        return {"PreTreeSolutions": len(self._progress)}

    def get_progress(self) -> list:
        """Return the progress of the search tree."""
        return self._progress
