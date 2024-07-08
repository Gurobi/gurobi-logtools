import re

from gurobi_logtools.parsers.util import typeconvert_groupdict

class PretreeSolutionParser:

    pretree_solution_regex = re.compile(
        r"Found heuristic solution:\sobjective\s(?P<Incumbent>[^\s]+)"
    )

    def __init__(self):
        """Initialize the pre-tree solutions parser (does not include NoRel solutions).

        The PresolveParser extends beyond the lines associated with the presolved
        model. Specifically, it includes information for all lines appearing between
        the HeaderParser and the NoRelParser or the RelaxationParser.
        """
        self._progress = []
        self._summary = {}
        #self._started = False

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        match = self.pretree_solution_regex.match(line)
        if match:
            self._progress.append(typeconvert_groupdict(match))
            return True
        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return {
            "PreTreeSolutions": len(self._progress)
        }
    
    def get_progress(self) -> list:
        """Return the progress of the search tree."""
        return self._progress